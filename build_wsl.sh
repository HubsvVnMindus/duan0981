#!/usr/bin/env bash
set -euo pipefail

# HTOOL NOVA - Buildozer build script for Windows + WSL2 Ubuntu.
# The project is copied into the Linux filesystem because Buildozer/python-for-android
# is much more reliable there than directly under /mnt/c.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIN_PROJECT_DIR="${1:-$SCRIPT_DIR}"

if ! command -v wslpath >/dev/null 2>&1; then
    echo "ERROR: This script must be started from WSL." >&2
    exit 1
fi

WIN_PROJECT_DIR="$(wslpath -u "$WIN_PROJECT_DIR" 2>/dev/null || printf '%s' "$WIN_PROJECT_DIR")"
BUILD_DIR="$HOME/htoolnova_build"

printf '\n=== HTOOL NOVA / WSL2 BUILD ===\n'
printf 'Source : %s\n' "$WIN_PROJECT_DIR"
printf 'Build  : %s\n\n' "$BUILD_DIR"

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 python3-pip python3-venv git zip unzip \
    openjdk-17-jdk build-essential autoconf automake libtool \
    pkg-config zlib1g-dev libffi-dev libssl-dev ccache

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy source to the native Linux filesystem.
cp -a "$WIN_PROJECT_DIR"/. "$BUILD_DIR"/
cd "$BUILD_DIR"

if [[ ! -f buildozer.spec || ! -f main.py || ! -f htool_core.py ]]; then
    echo "ERROR: Project files are incomplete." >&2
    exit 1
fi

if [[ ! -d .venv ]]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade buildozer "cython<3.0"

export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-17-openjdk-amd64}"
export PATH="$JAVA_HOME/bin:$HOME/.local/bin:$PATH"
export PIP_DISABLE_PIP_VERSION_CHECK=1

if ! command -v javac >/dev/null 2>&1; then
    echo "ERROR: Java compiler (javac) was not found." >&2
    exit 1
fi

# Let Buildozer download/manage its own Android SDK/NDK under ~/.buildozer.
# This avoids depending on an Android SDK installed in Windows.

echo
printf 'Java: '; java -version 2>&1 | head -n 1
printf 'Buildozer: '; buildozer --version

echo
echo "=== Starting APK build ==="
buildozer -v android debug

APK="$(find bin -maxdepth 1 -type f -name '*.apk' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n1 | cut -d' ' -f2-)"
if [[ -z "$APK" || ! -f "$APK" ]]; then
    echo "ERROR: Build finished but no APK was found in bin/." >&2
    exit 1
fi

# Copy APK(s) back to the original Windows project folder.
cp -f "$APK" "$WIN_PROJECT_DIR/"

printf '\n=== BUILD SUCCESS ===\n'
printf 'APK: %s\n' "$WIN_PROJECT_DIR/$(basename "$APK")"
printf '\nYou can install the APK on your Android phone.\n'
