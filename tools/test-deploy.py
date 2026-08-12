#!/usr/bin/env python3
"""Run deploy.py end to end against a throwaway FTPS server.

    npm run test:deploy

Two bugs have now reached production in the publish path, both invisible
locally because nothing ever opened a real connection: the script would upload
over plain FTP, and later it crashed reading `FTP_TLS.ssl_version`, a property
Python 3.12 removed, immediately after a successful handshake.

This starts a real FTPS server on loopback, points deploy.py at it, and checks
that every built file arrives with the right size. It exercises the TLS
handshake, the directory creation, the uploads and the stale-file report.

The self-signed certificate is generated per run and trusted only inside this
process. Production verification is untouched: deploy.py still builds its
context with `ssl.create_default_context()`.

Requires pyftpdlib and pyopenssl, pulled in on the fly by uv.
"""

import contextlib
import importlib.util
import io
import os
import pathlib
import socket
import ssl
import subprocess
import sys
import tempfile
import time
import multiprocessing

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

USER = "deploy-test"
PASSWORD = "deploy-test-password"


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def make_certificate(directory: pathlib.Path) -> pathlib.Path:
    """Self-signed certificate, valid for this run and nothing else."""
    certificate = directory / "test.pem"
    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
            "-keyout", str(certificate), "-out", str(certificate),
            "-days", "1", "-subj", "/CN=127.0.0.1",
        ],
        check=True,
        capture_output=True,
    )
    return certificate


def _serve(root: str, certificate: str, port: int) -> None:
    authorizer = DummyAuthorizer()
    authorizer.add_user(USER, PASSWORD, root, perm="elradfmwMT")

    handler = TLS_FTPHandler
    handler.certfile = certificate
    handler.authorizer = authorizer
    handler.tls_control_required = True
    handler.tls_data_required = True

    FTPServer(("127.0.0.1", port), handler).serve_forever()


@contextlib.contextmanager
def ftps_server(root: pathlib.Path, certificate: pathlib.Path, port: int):
    """A real FTPS server, refusing anything unencrypted, on loopback.

    In a separate process, not a thread. pyftpdlib implements CWD with
    os.chdir, which is process-wide: run in-process and the server moves the
    working directory out from under the client between two uploads, turning a
    present file into a missing one at random. A real deployment talks to
    another machine, and the harness has to reproduce that separation.
    """
    server = multiprocessing.Process(
        target=_serve, args=(str(root), str(certificate), port), daemon=True
    )
    server.start()

    # Wait for the socket rather than sleeping blindly.
    for _ in range(80):
        with contextlib.suppress(OSError):
            with socket.create_connection(("127.0.0.1", port), timeout=0.25):
                break
        time.sleep(0.05)

    try:
        yield
    finally:
        server.terminate()
        server.join(timeout=5)


def load_deploy_module():
    spec = importlib.util.spec_from_file_location("deploy", ROOT / "deploy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if not (DIST / "index.html").exists():
        print("No build found. Run npm run build first.")
        return 1

    with tempfile.TemporaryDirectory() as workspace:
        workspace = pathlib.Path(workspace)
        remote = workspace / "remote"
        remote.mkdir()

        # A leftover the build does not produce, so the stale report has
        # something real to find. This is how api.php survived on the server.
        (remote / "api.php").write_text("<?php // leftover from the old site")

        certificate = make_certificate(workspace)
        port = free_port()

        deploy = load_deploy_module()
        # Test-only: trust the throwaway certificate. deploy.py itself is not
        # modified, so production keeps full verification.
        deploy.ssl.create_default_context = lambda *a, **k: ssl._create_unverified_context()

        os.environ.update(
            FTP_HOST=f"127.0.0.1:{port}",
            FTP_USER=USER,
            FTP_PASS=PASSWORD,
            FTP_DIR="/",
        )
        # The real deploy.connect() runs, unmodified. Only the transport is
        # redirected: a subclass that defaults to the test port, since the
        # production call passes a host and no port. Replacing connect()
        # outright would leave the very function that carried the first two
        # bugs untested.
        class TestFTPS(deploy.ftplib.FTP_TLS):
            def connect(self, host="", port=0, timeout=-999, source_address=None):
                return super().connect(host, port or test_port, timeout, source_address)

        test_port = port
        deploy.ftplib.FTP_TLS = TestFTPS
        original_config = deploy.get_config
        deploy.get_config = lambda: {**original_config(), "host": "127.0.0.1"}

        previous_cwd = os.getcwd()
        output = io.StringIO()
        try:
            os.chdir(ROOT)
            with ftps_server(remote, certificate, port):
                with contextlib.redirect_stdout(output):
                    code = deploy.main()
        finally:
            os.chdir(previous_cwd)
            deploy.get_config = original_config

        log = output.getvalue()
        print(log)

        if code != 0:
            print("deploy.py returned a failure.")
            return 1

        expected = deploy.collect_files(str(DIST))
        missing, wrong_size = [], []
        for relative in expected:
            landed = remote / relative
            if not landed.exists():
                missing.append(relative)
            elif landed.stat().st_size != (DIST / relative).stat().st_size:
                wrong_size.append(relative)

        print(f"{len(expected)} files published, {len(missing)} missing, "
              f"{len(wrong_size)} truncated")

        problems = []
        if missing:
            problems.append(f"missing: {', '.join(missing[:5])}")
        if wrong_size:
            problems.append(f"wrong size: {', '.join(wrong_size[:5])}")
        if "TLSv1" not in log:
            problems.append("the log does not name a negotiated TLS version")
        if "api.php" not in log:
            problems.append("the stale-file report did not mention api.php")

        if problems:
            for problem in problems:
                print(f"FAIL: {problem}")
            return 1

    print("End-to-end publish verified over FTPS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
