#!/usr/bin/env python3
"""Deploy paniagua.dev over FTPS.

Usage:
    python3 deploy.py           publish the site
    python3 deploy.py --test    check the connection without uploading

Credentials are read from the environment, falling back to the local .env file
(not versioned). The password is never passed as a command-line argument:
arguments are visible to every user on the machine through `ps`.

To read the password from `pass` instead of .env:
    FTP_PASS=$(pass show projets/paniagua-dev/ftp) python3 deploy.py
"""

import ftplib
import os
import ssl
import sys

# Everything under this directory is published, recursively. Astro emits
# content-hashed filenames, so an explicit list would go stale on every build.
# Resolved against this file, not the caller's working directory, so the script
# publishes the same tree wherever it is invoked from.
DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

# Files that must never reach the server, whatever ends up in dist/.
NEVER_UPLOAD = {".env", "deploy.py"}


def collect_files(root):
    """Return every file under `root`, as paths relative to it, depth first.

    Directories come before their contents so the remote tree can be created
    in one pass without seeking back.
    """
    base = os.path.abspath(root)
    found = []
    for current, dirs, files in os.walk(base):
        dirs.sort()
        relative_dir = os.path.relpath(current, base)
        for name in sorted(files):
            if name in NEVER_UPLOAD:
                continue
            relative = name if relative_dir == "." else os.path.join(relative_dir, name)
            found.append(relative)
    return found


def load_env(filepath=".env"):
    """Read environment variables from a local .env file."""
    env_vars = {}
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip("\"'")
    return env_vars


def get_config():
    """Environment wins over .env, so a one-off override needs no file edit."""
    env_file = load_env()

    def get(key, default=None):
        return os.environ.get(key) or env_file.get(key) or default

    return {
        "host": get("FTP_HOST"),
        "user": get("FTP_USER"),
        "password": get("FTP_PASS"),
        "target_dir": get("FTP_DIR", "/"),
    }


def connect(config):
    """Open an FTPS session. Fail loudly if encryption is refused."""
    ftp = ftplib.FTP_TLS(context=ssl.create_default_context())
    ftp.connect(config["host"], timeout=30)
    ftp.auth()                      # AUTH TLS - encrypts the command channel
    ftp.login(user=config["user"], passwd=config["password"])
    ftp.prot_p()                    # encrypts the data channel as well
    return ftp


def negotiated_tls(ftp) -> str:
    """Name the protocol actually negotiated on the command channel.

    Read from the socket rather than from the FTP object. `FTP_TLS.ssl_version`
    was deprecated in Python 3.6 and removed in 3.12, and reading it there
    raises after a perfectly good handshake: the connection is up, and the
    script dies while announcing it.
    """
    sock = getattr(ftp, "sock", None)
    version = getattr(sock, "version", None)
    if callable(version):
        return version() or "TLS"
    return "TLS"


def ensure_dir(ftp, path):
    """Change into `path`, creating each missing segment along the way."""
    for segment in path.strip("/").split("/"):
        if not segment:
            continue
        try:
            ftp.cwd(segment)
        except ftplib.error_perm:
            print(f"  directory {segment}/ missing, creating it")
            ftp.mkd(segment)
            ftp.cwd(segment)


def upload_file(ftp, local_root, relative_path, remote_dir):
    """Upload one file, creating its remote subdirectory when needed.

    The local file is opened by absolute path. Relying on the process working
    directory made this fragile for no benefit: anything that changes the cwd
    mid-run, in this process or a library thread, turns a present file into a
    missing one.
    """
    name = os.path.basename(relative_path)
    subdir = os.path.dirname(relative_path)
    source = os.path.join(local_root, relative_path)

    if subdir:
        ftp.cwd(remote_dir)
        ensure_dir(ftp, subdir)

    with open(source, "rb") as f:
        ftp.storbinary(f"STOR {name}", f)

    print(f"  uploaded  {relative_path}  ({os.path.getsize(source):,} bytes)")

    if subdir:
        ftp.cwd(remote_dir)


def report_stale(ftp, published, remote_dir):
    """Name remote files that no build produced.

    Nothing is deleted here. This script publishes, it does not prune, and a
    remote delete driven by CI is how a site loses a file nobody meant to
    touch. But silence is worse: api.php and data.json outlived their removal
    from the repository precisely because no one was told they were still
    there.
    """
    ftp.cwd(remote_dir)
    try:
        listing = ftp.nlst()
    except ftplib.all_errors:
        return

    expected = {os.path.basename(path) for path in published}
    expected.update(part for path in published for part in path.split("/")[:-1])

    # Some servers answer NLST with full paths rather than bare names.
    stale = sorted(
        name for name in (os.path.basename(entry.rstrip("/")) for entry in listing)
        if name and name not in expected and name not in {".", "..", ".htaccess"}
    )
    if not stale:
        return

    print("\nRemote files this build did not produce:")
    for name in stale:
        print(f"  {name}")
    print("Delete them by hand if they are leftovers. Nothing was removed.")


def main():
    dry_run = "--test" in sys.argv
    config = get_config()

    # Named exactly as the variables are read, not derived from the config
    # keys: "password" would print FTP_PASSWORD and send someone hunting for a
    # variable that does not exist.
    variables = {"host": "FTP_HOST", "user": "FTP_USER", "password": "FTP_PASS"}
    missing = [k for k in variables if not config[k]]
    if missing:
        names = ", ".join(variables[k] for k in missing)
        print(f"Error: {names} not set.")
        print("Fill in the .env file, or export the variables before running.")
        return 1

    if not os.path.isdir(DIST):
        print(f"Error: {DIST} not found. Run npm run build first.")
        return 1

    files = collect_files(DIST)
    if not files:
        print(f"Error: {DIST} is empty.")
        return 1

    if "index.html" not in files:
        print(f"Error: index.html is missing from {DIST}. The build looks incomplete.")
        return 1

    print(f"Connecting to {config['host']} over FTPS")
    try:
        ftp = connect(config)
    except ssl.SSLError as e:
        print(f"TLS error: {e}")
        print("The server refuses encryption. Do NOT fall back to plain FTP:")
        print("ask the host to enable FTPS, or switch to SFTP.")
        return 1
    except ftplib.all_errors as e:
        print(f"Connection error: {e}")
        return 1

    try:
        with ftp:
            print(f"connected, channel encrypted ({negotiated_tls(ftp)})")
            ensure_dir(ftp, config["target_dir"])
            remote_dir = ftp.pwd()
            print(f"remote directory: {remote_dir}")

            if dry_run:
                print("\n--test: connection verified, nothing uploaded.")
                print(f"{len(files)} files would be published.")
                return 0

            print()
            for path in files:
                try:
                    upload_file(ftp, DIST, path, remote_dir)
                except ftplib.all_errors as e:
                    print(f"  FAILED    {path}: {e}")
                    return 1

            print(f"\nDeployment complete: {len(files)} files.")
            report_stale(ftp, files, remote_dir)
    except ftplib.all_errors as e:
        print(f"Transfer error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
