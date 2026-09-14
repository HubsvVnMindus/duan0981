HTOOL NOVA - BUILD APK BANG WINDOWS + WSL2
==========================================

MUC TIEU
--------
Project nay duoc dong goi de build APK tren PC Windows bang WSL2 Ubuntu.
File htool_core.py chua logic HTOOL goc. main.py chi la lop Android/Kivy
ket noi input/output voi logic goc.

CAU TRUC
--------
- main.py             : Android launcher/UI, khong chua logic nghiep vu HTOOL
- htool_core.py       : logic HTOOL goc
- buildozer.spec      : cau hinh APK
- build_wsl.sh        : script build ben trong Ubuntu WSL2
- build.bat            : file Windows, double-click de build
- setup_wsl.bat        : mo Ubuntu WSL2
- README_PC_WSL_VI.txt : huong dan nay

YEU CAU
-------
1. Windows 10/11 co WSL2.
2. Ubuntu trong WSL2.
3. Internet trong luc build.
4. Nen co it nhat 8-10 GB trong WSL cho lan build dau.

CAI WSL2 (PowerShell Administrator)
-----------------------------------
wsl --install -d Ubuntu

Sau khi cai xong, mo Ubuntu mot lan va tao username/password Linux.

BUILD APK - CACH DE NHAT
------------------------
1. Giai nen project vao mot thu muc, vi du:
   C:\HTOOL-NOVA\

2. Double-click:
   build.bat

3. Lan dau script se tu cai cac goi Ubuntu, Python, Buildozer,
   Java 17 va cac Android build tools can thiet.

4. Cho den khi thay:
   [SUCCESS] APK was created in this project folder.

5. File .apk se duoc copy tro lai ngay trong thu muc project Windows.

BUILD BANG LENH
---------------
Mo Ubuntu:
cd /mnt/c/HTOOL-NOVA
bash build_wsl.sh /mnt/c/HTOOL-NOVA

Neu duong dan co dau cach, uu tien dung build.bat.

APK DEBUG
---------
Lenh mac dinh la:
  buildozer -v android debug

APK debug phu hop de cai thu tren dien thoai. Neu muon ban release,
can tao keystore va cau hinh ky APK rieng.

CAI APK LEN DIEN THOAI
-----------------------
- Gui file .apk sang dien thoai.
- Mo file APK va cho phep cai ung dung tu nguon nay neu Android yeu cau.

LUU Y VE LOGIC
--------------
Khong di chuyen logic nghiep vu sang Kivy. HTOOL logic van nam trong
htool_core.py. Android launcher chay htool_core.py va chi thay co che
terminal input/output de phu hop voi APK.

NEU BUILD LOI
-------------
1. Chay lai build.bat.
2. Neu loi Python/package, xoa thu muc build trong WSL:
   rm -rf ~/htoolnova_build
   sau do build lai.
3. Neu Buildozer bao loi Android SDK/NDK, gui cho toi khoang 30-50 dong
   cuoi cua log loi de sua dung loi do, khong can gui lai toan bo project.
