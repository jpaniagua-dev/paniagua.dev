#!/usr/bin/env bash
#
# Copy the FTP credentials from `pass` into the repository's GitHub secrets,
# so the deploy workflow can publish.
#
#   ./tools/set-ci-secrets.sh
#
# Expected in the password store:
#   projets/paniagua-dev/ftp-host
#   projets/paniagua-dev/ftp-user
#   projets/paniagua-dev/ftp-pass
#   projets/paniagua-dev/ftp-dir    (optional, defaults to /)
#
# Secret names on GitHub are namespaced per project, because the account holds
# more than one site. The workflow maps them back to the plain names deploy.py
# expects.
#
# Each value is piped to `gh` on standard input. It never appears as a command
# argument, where `ps` would expose it to every user on the machine, and never
# in a shell history file.
#
# Run this yourself. It needs a GPG passphrase and a GitHub login, neither of
# which an agent can supply, and it writes to a repository you own.
#
# Prerequisites:
#   gh auth login          as the repository owner
#   pass show projets/paniagua-dev/ftp-host >/dev/null    to unlock GPG
#
# To undo: delete the secrets from the repository settings, or
#   gh secret delete FTP_PASS_PANIAGUA_DEV --repo "$REPO"

set -euo pipefail

REPO="${REPO:-jpaniagua-dev/paniagua.dev}"

command -v gh >/dev/null || { echo "gh is not installed." >&2; exit 1; }
command -v pass >/dev/null || { echo "pass is not installed." >&2; exit 1; }

gh auth status >/dev/null 2>&1 || {
  echo "gh is not authenticated. Run: gh auth login" >&2
  exit 1
}

put() {
  local entry="$1" name="$2" required="$3" value

  if ! value="$(pass show "projets/paniagua-dev/$entry" 2>/dev/null | head -n1)"; then
    if [[ "$required" == "required" ]]; then
      echo "Missing secret: projets/paniagua-dev/$entry" >&2
      echo "Store it first with: pass insert projets/paniagua-dev/$entry" >&2
      exit 1
    fi
    echo "  $name  skipped, no entry in pass"
    return
  fi

  printf '%s' "$value" | gh secret set "$name" --repo "$REPO" >/dev/null
  echo "  $name  set (${#value} characters)"
}

echo "Writing secrets to $REPO"
put ftp-host FTP_HOST_PANIAGUA_DEV required
put ftp-user FTP_USER_PANIAGUA_DEV required
put ftp-pass FTP_PASS_PANIAGUA_DEV required
put ftp-dir FTP_DIR_PANIAGUA_DEV optional

echo
echo "Done. The next push to main will build, verify and publish."
echo "Check the run at: https://github.com/$REPO/actions"
