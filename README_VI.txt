HTOOL NOVA - BUILD APK TRÊN TERMUX
===================================

Logic gốc được giữ trong htool_core.py. main.py chỉ làm cầu nối giao diện Android
cho input/output terminal; không viết lại các chức năng HTOOL.

1. GIẢI NÉN
-----------
unzip htoolnova_android_project.zip -d htoolnova
cd htoolnova

2. CÀI CÔNG CỤ TERMUX (nếu chưa có)
------------------------------------
pkg update
pkg install python git clang make cmake pkg-config libffi openssl zlib openjdk-17 unzip zip
pip install -U pip
pip install -U buildozer cython

3. DÙNG ANDROID SDK ĐÃ CÓ
--------------------------
Nếu bạn đã có SDK từ project X-Chess, dùng lại SDK đó.

export ANDROID_HOME=$HOME/android-sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME
export JAVA_HOME=$PREFIX/lib/jvm/java-17-openjdk
export PATH=$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

Kiểm tra:
java -version
javac -version
sdkmanager --version

Nếu chưa có command-line tools, cần cài Android SDK command-line tools vào:
$HOME/android-sdk/cmdline-tools/latest/

4. BUILD
--------
cd ~/htoolnova
bash build_apk.sh

Hoặc:
buildozer -v android debug

Lần build đầu có thể mất khá lâu vì Buildozer tải python-for-android,
Gradle và các Android components.

5. APK SAU KHI BUILD
---------------------
APK nằm trong thư mục:
bin/

Chép ra Download:
mkdir -p ~/storage/downloads
cp bin/*.apk ~/storage/downloads/

Sau đó mở Download bằng trình quản lý file và cài APK.

6. NẾU BÁO THIẾU SDK
---------------------
export ANDROID_HOME=$HOME/android-sdk
sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-35" "build-tools;35.0.0"

7. NẾU BUILD LỖI CACHE
----------------------
buildozer android clean
rm -rf .buildozer
buildozer -v android debug

8. LỖI ZLIB TRÊN TERMUX
------------------------
Nếu gặp lỗi "zlib headers must be installed" dù $PREFIX/include/zlib.h tồn tại,
đó là lỗi kiểm tra môi trường Buildozer/python-for-android trên Termux.
Trong trường hợp đó dùng patch zlib Termux mà bạn đã áp dụng cho X-Chess trước đây,
rồi chạy lại build.

9. DỮ LIỆU CỦA HTOOL
--------------------
Các file tương đối mà HTOOL tự tạo (ví dụ accounts.json, strategy_htool.json,
config/key files...) được lưu trong thư mục dữ liệu riêng của APK.

10. QUYỀN
---------
APK có INTERNET và ACCESS_NETWORK_STATE vì logic HTOOL hiện tại sử dụng requests,
websocket và các API mạng.
