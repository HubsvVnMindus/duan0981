#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"

export ANDROID_HOME="${ANDROID_HOME:-$HOME/android-sdk}"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export ANDROID_NDK_HOME="${ANDROID_NDK_HOME:-$ANDROID_HOME/ndk/28.0.13004108}"
export JAVA_HOME="${JAVA_HOME:-$PREFIX/lib/jvm/java-17-openjdk}"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

printf '\n=== HTOOL NOVA APK BUILD ===\n'
printf 'ANDROID_HOME=%s\n' "$ANDROID_HOME"
printf 'JAVA_HOME=%s\n\n' "$JAVA_HOME"

command -v buildozer >/dev/null 2>&1 || { echo 'Thiếu Buildozer: pip install -U buildozer cython'; exit 1; }
[ -x "$JAVA_HOME/bin/javac" ] || { echo 'Thiếu Java 17: pkg install openjdk-17'; exit 1; }

buildozer -v android debug

echo
echo '=== BUILD COMPLETE ==='
find bin -maxdepth 1 -type f -name '*.apk' -print
