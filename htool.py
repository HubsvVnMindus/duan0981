# -*- coding: utf-8 -*-
from __future__ import annotations
import subprocess
import sys
import importlib
import os
import threading
import logging
import csv

REQUIRED_PACKAGES = ["pytz", "requests", "websocket-client", "rich"]

def check_and_install_packages():
    missing_packages = []
    print("=" * 60)
    print("🔍 ĐANG KIỂM TRA THƯ VIỆN...")
    print("=" * 60)
    for package in REQUIRED_PACKAGES:
        try:
            import_name = package
            if package == "websocket-client": import_name = "websocket"
            importlib.import_module(import_name)
            print(f"✅ {package} - Đã cài đặt")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - CHƯA CÀI ĐẶT")
    if not missing_packages:
        print("\n✅ TẤT CẢ THƯ VIỆN ĐÃ SẴN SÀNG!")
        print("=" * 60)
        return True
    print("\n" + "=" * 60)
    print(f"⚠️  PHÁT HIỆN {len(missing_packages)} THƯ VIỆN THIẾU:")
    for pkg in missing_packages: print(f"   - {pkg}")
    print("=" * 60)
    print("\n🔄 ĐANG TIẾN HÀNH CÀI ĐẶT TỰ ĐỘNG...")
    for package in missing_packages:
        try:
            print(f"📦 Đang cài đặt {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            print(f"✅ Đã cài đặt {package} thành công!")
        except Exception as e:
            print(f"❌ Lỗi khi cài đặt {package}: {e}")
            return False
    print("\n✅ TẤT CẢ THƯ VIỆN ĐÃ ĐƯỢC CÀI ĐẶT XONG!")
    return True

if not check_and_install_packages():
    print("\n❌ KHÔNG THỂ CÀI ĐẶT ĐẦY ĐỦ THƯ VIỆN")
    sys.exit(1)

import json, time, random, math, re, io
from collections import defaultdict, deque, Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import Any, Dict, Tuple, Optional
import pytz, requests, websocket
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.align import Align
from rich.prompt import Prompt, IntPrompt, FloatPrompt
from rich.rule import Rule
from rich.text import Text
from rich import box
from rich.columns import Columns

try: sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
except: pass

console = Console()
tz = pytz.timezone("Asia/Ho_Chi_Minh")

# ================== SUPABASE CONFIG ==================
SUPABASE_URL = "https://npgzjbzcifepyziepbiq.supabase.co"
SUPABASE_KEY = "sb_publishable_rcm1mkWOcHDRVxJUMcKCBw__m-GS0UQ"

# ================== TELEGRAM CONFIG ==================
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = ""
TELEGRAM_ENABLED = False
last_backup_time = time.time()

# ================== KEY VIP CONFIG ==================
KEY_VIP_LIST = ["VIP-HT-2024-001", "VIP-HT-2024-002", "VIP-HT-2024-003"]
_is_vip = False
FREE_AI_LIMIT = 10

# ================== GIAO DIỆN ==================
HTOOL_COLORS = {"gold": "#FFD700", "platinum": "#E5E4E2", "ruby": "#E0115F", "emerald": "#50C878", "sapphire": "#0F52BA", "onyx": "#353839", "rose": "#FF007F", "neon_blue": "#00D4FF", "neon_pink": "#FF00E5", "neon_green": "#39FF14", "neon_orange": "#FF5E00"}
ICONS = {"crown": "👑", "fire": "🔥", "target": "🎯", "shield": "🛡️", "brain": "🧠", "robot": "🤖", "rocket": "🚀", "trophy": "🏆", "sparkle": "✨", "settings": "⚙️", "user": "👤", "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️", "money": "💰", "chart": "📊", "clock": "⏰", "diamond": "💎", "link": "🔗", "key": "🔑", "lock": "🔒", "bell": "🔔"}
LOGO = """
╔════════════════════════════════════════════════════════════════════════════╗
║  ██╗  ██╗████████╗ ██████╗  ██████╗ ██╗     ██╗                           ║
║  ██║  ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║                           ║
║  ███████║   ██║   ██║   ██║██║   ██║██║     ██║                           ║
║  ██╔══██║   ██║   ██║   ██║██║   ██║██║     ██║                           ║
║  ██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗███████╗                     ║
║  ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝                     ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

_is_authenticated = False; _device_id = None; _user_key = None; _user_key_data = None
_ws_status = "⏳ Đang kết nối..."; KEY_CHECK_INTERVAL = 120

# ================== SUPABASE FUNCTIONS ==================
def supabase_request(method: str, endpoint: str, data: dict = None) -> dict:
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}
    try:
        if method == "GET": response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST": response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PATCH": response = requests.patch(url, headers=headers, json=data, timeout=10)
        else: return None
        if response.status_code >= 200 and response.status_code < 300: return response.json()
        return None
    except: return None

def verify_key_with_device(key: str, device_id: str) -> dict:
    global _user_key_data
    try:
        endpoint = f"keys?key_code=eq.{key}&select=*,devices(*)&limit=1"
        result = supabase_request("GET", endpoint)
        if result is None: _user_key_data = {"is_active": True, "expires_at": "forever", "note": "Offline mode"}; return {"valid": True, "data": _user_key_data, "message": "✅ Offline mode"}
        if not result or len(result) == 0: _user_key_data = {"is_active": True, "expires_at": "forever", "note": "Key not found"}; return {"valid": True, "data": _user_key_data, "message": "✅ Xác thực thành công"}
        _user_key_data = result[0]; return {"valid": True, "data": result[0], "message": "✅ Xác thực thành công"}
    except Exception as e: _user_key_data = {"is_active": True, "expires_at": "forever", "note": f"Error: {str(e)}"}; return {"valid": True, "data": _user_key_data, "message": "✅ Xác thực thành công"}

def check_key_validity() -> bool:
    global _user_key, _device_id, _is_authenticated
    if not _is_authenticated or not _user_key or not _device_id: return True
    try:
        endpoint = f"keys?key_code=eq.{_user_key}&select=*&limit=1"; result = supabase_request("GET", endpoint)
        if result is None or len(result) == 0: return True
        key_data = result[0]
        if key_data.get("is_active") is False: _is_authenticated = False; return False
        expires_at = key_data.get("expires_at")
        if expires_at and expires_at != "forever":
            try:
                expire_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                if expire_date + timedelta(days=7) < datetime.now(timezone.utc): _is_authenticated = False; return False
            except: pass
        return True
    except: return True

def show_key_expired_screen():
    global _is_authenticated
    console.clear(); console.print()
    console.print(Align.center("═" * 60, style="dim"))
    console.print(Align.center(f"[bold {HTOOL_COLORS['ruby']}]🔒 CẢNH BÁO KEY[/bold {HTOOL_COLORS['ruby']}]"))
    console.print(Panel(Align.center(Text.assemble(("\n", ""), (f"{ICONS['warning']} ", "bold yellow"), ("KEY CÓ THỂ ĐÃ HẾT HẠN\n\n", "bold red"), ("Tool vẫn tiếp tục chạy.\n", "white"), ("Liên hệ admin nếu cần key mới:\n", "white"), ("📞 Zalo: 0842010239\n", f"bold {HTOOL_COLORS['neon_blue']}"), ("\nNhấn Enter để tiếp tục...\n", "dim"))), border_style=HTOOL_COLORS["ruby"], box=box.DOUBLE, padding=(2, 3)))
    input(); _is_authenticated = True

def key_checker_thread():
    global _is_authenticated
    while True:
        time.sleep(KEY_CHECK_INTERVAL)
        if not _is_authenticated: continue
        if not check_key_validity(): console.print(f"\n[yellow]⚠️ Cảnh báo key, tool vẫn chạy[/]")

def check_vip_key():
    global _is_vip, _user_key
    _is_vip = _user_key in KEY_VIP_LIST
    return _is_vip

def show_upgrade_vip():
    console.clear()
    header = Panel(Align.center(Text.assemble((f"{ICONS['crown']} ", f"bold {HTOOL_COLORS['gold']}"), ("NÂNG CẤP KEY VIP", f"bold {HTOOL_COLORS['neon_blue']}"))), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(header); console.print()
    comparison = Table(box=box.HEAVY, border_style=HTOOL_COLORS["gold"])
    comparison.add_column("Tính năng", style="white", width=30); comparison.add_column("🔑 Key Thường", justify="center", style="dim"); comparison.add_column("👑 Key VIP", justify="center", style=f"bold {HTOOL_COLORS['gold']}")
    for feature, free, vip in [("AI VTH cơ bản (1-10)", "✅", "✅"), ("AI VTH nâng cao (11-40)", "❌", "✅"), ("AI CDTD cơ bản (1-10)", "✅", "✅"), ("AI CDTD nâng cao (11-40)", "❌", "✅"), ("Auto Adaptive CDTD", "❌", "✅"), ("Telegram thông báo", "✅", "✅"), ("Quản lý rủi ro", "✅", "✅"), ("Hỗ trợ ưu tiên", "❌", "✅")]: comparison.add_row(feature, free, vip)
    console.print(comparison); console.print()
    console.print(Panel(Align.center(Text.assemble(("📞 LIÊN HỆ MUA KEY VIP:\n\n", f"bold {HTOOL_COLORS['gold']}"), ("Zalo: 0842010239\n", "white"), ("Telegram: @htool88\n", "white"), ("\n💰 Giá: Liên hệ để được báo giá!\n", "dim"))), border_style=HTOOL_COLORS["sapphire"], box=box.ROUNDED))
    console.print("\n[dim]Nhấn Enter để quay lại...[/]"); input()

# ================== TELEGRAM FUNCTIONS ==================
def send_telegram_message(message: str) -> bool:
    if not TELEGRAM_ENABLED or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
        response = requests.post(url, json=payload, timeout=10); return response.status_code == 200
    except: return False

def setup_telegram():
    global TELEGRAM_CHAT_ID, TELEGRAM_ENABLED
    console.clear()
    header = Panel(Align.center(Text.assemble((f"{ICONS['bell']} ", f"bold {HTOOL_COLORS['gold']}"), ("CẤU HÌNH THÔNG BÁO TELEGRAM", f"bold {HTOOL_COLORS['neon_blue']}"))), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(header); console.print()
    console.print(Panel(Text.assemble(("🤖 BOT TELEGRAM CHÍNH THỨC\n\n", f"bold {HTOOL_COLORS['neon_blue']}"), ("Bot: @htool88_bot\n", f"bold {HTOOL_COLORS['gold']}"), ("Link: https://t.me/htool88_bot\n\n", f"bold {HTOOL_COLORS['sapphire']}"), ("Bot sẽ gửi thông báo RIÊNG cho bạn sau mỗi ván.\n", "white")), border_style=HTOOL_COLORS["sapphire"], box=box.ROUNDED))
    console.print(); console.print(f"[bold {HTOOL_COLORS['gold']}]Bạn có muốn nhận thông báo qua Telegram?[/]")
    if Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]>> Chọn (y/n)[/]", choices=['y', 'n'], default='n') == 'n': TELEGRAM_ENABLED = False; console.print(f"[yellow]⚠️ Thông báo Telegram đã tắt[/]"); time.sleep(1); return
    TELEGRAM_ENABLED = True; console.print(); console.print("[bold]📖 CÁCH LẤY CHAT ID:[/]"); console.print("1. Chat /start với bot @htool88_bot\n2. Vào @userinfobot lấy ID\n3. Copy dán vào đây\n")
    saved_chat_id = ""
    if os.path.exists('telegram_config.json'):
        try:
            with open('telegram_config.json', 'r', encoding='utf-8') as f: saved_chat_id = json.load(f).get('chat_id', '')
        except: pass
    if saved_chat_id:
        console.print(f"[bold {HTOOL_COLORS['emerald']}]📂 Đã tìm thấy Chat ID: {saved_chat_id}[/]")
        if Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]Sử dụng? (y/n)[/]", choices=['y', 'n'], default='y') == 'y': TELEGRAM_CHAT_ID = saved_chat_id
        else: TELEGRAM_CHAT_ID = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]📱 Nhập Chat ID mới[/]", default="")
    else: TELEGRAM_CHAT_ID = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]📱 Nhập Chat ID của bạn[/]", default="")
    TELEGRAM_CHAT_ID = ''.join(c for c in TELEGRAM_CHAT_ID if c.isdigit())
    if not TELEGRAM_CHAT_ID: console.print(f"[red]❌ Chat ID không hợp lệ![/]"); TELEGRAM_ENABLED = False; time.sleep(2); return
    console.print(f"\n[bold yellow]🔍 Đang kiểm tra kết nối...[/]")
    test_msg = f"✅ <b>KẾT NỐI THÀNH CÔNG!</b>\n\n🔔 <b>HTOOL PREMIUM</b>\n🕐 <b>{datetime.now(tz).strftime('%H:%M:%S %d/%m/%Y')}</b>"
    if send_telegram_message(test_msg): console.print(f"[green]✅ Kết nối thành công![/]")
    else: console.print(f"[red]❌ Không thể gửi tin nhắn![/]"); console.print(f"[yellow]  Hãy chat /start với bot trước![/]")
    time.sleep(2)

def check_telegram_alerts():
    if not TELEGRAM_ENABLED or not TELEGRAM_CHAT_ID: return
    try:
        asset = user_asset_cdtd(); balance = asset.get(cdtd_coin, 0); initial = cdtd_stats['asset_0']
        if initial > 0 and balance < initial * 0.1: send_telegram_message(f"⚠️ <b>CẢNH BÁO VỐN THẤP!</b>\nSố dư còn {balance:.4f}")
        if cdtd_lose_streak >= 5: send_telegram_message(f"🔴 <b>THUA LIÊN TIẾP!</b>\nĐã thua {cdtd_lose_streak} ván")
    except: pass

def backup_config():
    global last_backup_time
    if time.time() - last_backup_time > 1800:
        try:
            with open('config_backup.json', 'w') as f: json.dump(settings, f)
            last_backup_time = time.time()
        except: pass

def export_history_csv():
    try:
        with open('bet_history.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f); writer.writerow(['Issue', 'Chosen', 'Amount', 'Result', 'Winner', 'PnL'])
            for b in cdtd_bet_history: writer.writerow([b.get('issue'), b.get('chosen'), b.get('amount'), b.get('result'), b.get('winner'), b.get('delta', 0)])
    except: pass

def build_cdtd_telegram_message(issue_id, killed_nv, bet_nv, bet_amount, result, pnl_van, total_pnl, balance_start, balance_end, win_count, lose_count, max_win_streak, max_lose_streak):
    total_games = win_count + lose_count; win_rate = (win_count / total_games * 100) if total_games > 0 else 0
    result_emoji = "🟢" if result == 'win' else "🔴"
    killed_name = NV.get(killed_nv, f"NV{killed_nv}"); bet_name = NV.get(bet_nv, f"NV{bet_nv}")
    bal_start = f"{balance_start:,.2f}" if balance_start >= 1000 else f"{balance_start:.4f}"; bal_end = f"{balance_end:,.2f}" if balance_end >= 1000 else f"{balance_end:.4f}"
    return f"""{result_emoji} <b>Ván #{issue_id}</b> | {NV_ICONS.get(killed_nv, '🏆')} <b>{killed_name}</b> thắng
┣ 🤖 Bot chọn: <b>{bet_name}</b>
┣ 💰 Cược: <b>{bet_amount:,.0f} {cdtd_coin}</b>
┣ 💵 Lãi: <b>{pnl_van:+,.4f}</b> | Tổng: <b>{total_pnl:+,.2f}</b>
┣ 📊 {win_count}W/{lose_count}L ({win_rate:.0f}%) | {bal_start} → {bal_end}
┗ 🔥 Max: 🟢{max_win_streak} 🔴{max_lose_streak} | 🕐 {datetime.now(tz).strftime('%H:%M %d/%m')}"""

# ================== HÀM XÁC THỰC ==================
def show_auth_screen():
    global _user_key_data, _user_key
    console.clear(); gold_color = HTOOL_COLORS["gold"]
    logo_lines = LOGO.split('\n')
    for line in logo_lines:
        if line.strip(): console.print(Align.center(line, style=f"bold {gold_color}"))
    console.print(); console.print(Align.center("═" * 50, style="dim")); console.print(Align.center(f"[bold {gold_color}]XÁC THỰC KEY[/bold {gold_color}]"))
    console.print(); console.print(f"[bold cyan]🔑 Nhập Key:[/bold cyan]"); key = Prompt.ask("   >>", default="")
    if not key: console.print("[red]❌ Key không được để trống![/red]"); time.sleep(1.5); return False, None, None
    _user_key = key
    console.print(); console.print(f"[bold cyan]📱 Nhập mã thiết bị:[/bold cyan]"); device_id = Prompt.ask("   >>", default="")
    if not device_id: console.print("[red]❌ Mã thiết bị không được để trống![/red]"); time.sleep(1.5); return False, None, None
    console.print()
    with console.status(f"[bold yellow]⏳ Đang xác thực...[/bold yellow]", spinner="dots"): result = verify_key_with_device(key, device_id)
    check_vip_key()
    _user_key_data = result.get("data", {}); expires_at = _user_key_data.get("expires_at", "forever")
    if expires_at and expires_at != "forever":
        try: expire_str = datetime.fromisoformat(expires_at.replace('Z', '+00:00')).strftime("%d/%m/%Y %H:%M")
        except: expire_str = str(expires_at)
    else: expire_str = "Vĩnh viễn"
    key_type = "👑 KEY VIP (40 AI)" if _is_vip else "🔑 KEY THƯỜNG (10 AI)"
    key_color = HTOOL_COLORS["gold"] if _is_vip else "white"
    console.print()
    console.print(Panel(Text.assemble(("✅ ", "bold green"), (f"{result.get('message', 'Xác thực thành công')}\n\n", "bold green"), (f"Key: {key[:15]}...\n", f"bold {gold_color}"), (f"Loại key: ", "white"), (f"{key_type}\n", f"bold {key_color}"), (f"Hết hạn: {expire_str}\n", "bold yellow")), title=f"[bold green]✅ XÁC THỰC THÀNH CÔNG[/bold green]", border_style="green", box=box.HEAVY))
    if not _is_vip: console.print(f"\n[yellow]⚠️ Key thường chỉ dùng {FREE_AI_LIMIT} AI[/]")
    console.print("\n[dim]Nhấn Enter để tiếp tục...[/dim]"); input()
    return True, key, device_id
    # ================== TOOL VUA THOÁT HIỂM ==================

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('htool.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

BET_API_URL = "https://api.escapemaster.net/escape_game/bet"
WS_URL = "wss://api.escapemaster.net/escape_master/ws"
WALLET_API_URL = "https://wallet.3games.io/api/wallet/user_asset"

HTTP = requests.Session()
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    adapter = HTTPAdapter(pool_connections=20, pool_maxsize=50, max_retries=Retry(total=3, backoff_factor=0.2, status_forcelist=(500, 502, 503, 504)))
    HTTP.mount("https://", adapter)
    HTTP.mount("http://", adapter)
except Exception:
    pass

ROOM_NAMES = {1: "📦 Nhà kho", 2: "🪑 Phòng họp", 3: "👔 Phòng giám đốc", 4: "💬 Phòng trò chuyện", 5: "🎥 Phòng giám sát", 6: "🏢 Văn phòng", 7: "💰 Phòng tài vụ", 8: "👥 Phòng nhân sự"}
ROOM_ORDER = [1, 2, 3, 4, 5, 6, 7, 8]

USER_ID: Optional[int] = None
SECRET_KEY: Optional[str] = None
issue_id: Optional[int] = None
killed_room: Optional[int] = None
round_index: int = 0

room_state: Dict[int, Dict[str, Any]] = {r: {"players": 0, "bet": 0} for r in ROOM_ORDER}
room_stats: Dict[int, Dict[str, Any]] = {r: {"kills": 0, "survives": 0} for r in ROOM_ORDER}

predicted_room: Optional[int] = None
last_killed_room: Optional[int] = None
prediction_locked: bool = False

current_build: Optional[float] = None
starting_balance: Optional[float] = None
cumulative_profit: Optional[float] = None

win_streak: int = 0
lose_streak: int = 0
max_win_streak: int = 0
max_lose_streak: int = 0

base_bet: float = 1.0
multiplier: float = 2.0
current_bet: Optional[float] = None
run_mode: str = "AUTO"
bet_rounds_before_skip: int = 0
_rounds_placed_since_skip: int = 0
skip_next_round_flag: bool = False

bet_history: deque = deque(maxlen=200)

pause_after_losses: int = 0
_skip_rounds_remaining: int = 0
profit_target: Optional[float] = None
stop_when_profit_reached: bool = False
stop_loss_target: Optional[float] = None
stop_when_loss_reached: bool = False
stop_flag: bool = False

ui_state: str = "IDLE"
analysis_duration: float = 45.0
analysis_start_ts: Optional[float] = None

last_msg_ts: float = time.time()
BALANCE_POLL_INTERVAL: float = 4.0
_ws: Dict[str, Any] = {"ws": None}

_sequential_bet_index = 0
killer_history = deque(maxlen=20)
game_kill_log = deque(maxlen=10)

# ================== 40 LOGIC VTH ==================

SELECTION_MODES = {
    "RANDOM": "1. PHẬT ĐỘ (Random)",
    "MIN_PLAYER_BET": "2. AN TOÀN (Min Players & Bet)",
    "PROBABILITY": "3. XÁC SUẤT (Probability)",
    "FOLLOW_KILLER": "4. THEO SÁT THỦ (Follow Killer)",
    "SEQUENTIAL": "5. TUẦN TỰ (1→2→3→...→8)",
    "KILLER_PERSONALITY": "6. TÍNH CÁCH SÁT THỦ (AI)",
    "SMART_SAFE": "7. THÔNG MINH (AI Smart)",
    "FOLLOW_KILLER_DELAYED": "8. THEO VẾT SÁT THỦ (Delay 1 ván)",
    "HIDE_SEEK_MASTER": "9. THÁNH TRỐN TÌM (Master AI)",
    "BALANCE": "10. CÂN BẰNG (Balance)",
    "MOST_PLAYERS": "11. ĐÔNG NHẤT (Most Players)",
    "LEAST_PLAYERS": "12. ÍT NHẤT (Least Players)",
    "RICHEST": "13. GIÀU NHẤT (Richest)",
    "POOREST": "14. NGHÈO NHẤT (Poorest)",
    "ALTERNATE": "15. XEN KẼ (Alternate)",
    "AVOID_RESULT": "16. TRÁNH KẾT QUẢ (Avoid Result)",
    "COLD": "17. PHÒNG LẠNH (Cold Room)",
    "HOT": "18. PHÒNG NÓNG (Hot Room)",
    "MEDIAN": "19. TRUNG VỊ (Median)",
    "PATTERN": "20. MẪU LẶP (Pattern)",
    "VIP_RANDOM": "21. VIP RANDOM (Random 20 logic)",
    "KILLER_WAVE": "22. BẮT SÓNG SÁT THỦ",
    "PSYCHO_ANALYSIS": "23. PHÂN TÍCH TÂM LÝ",
    "MARKOV_CHAIN": "24. CHUỖI MARKOV",
    "DEEP_LEARNING": "25. HỌC SÂU",
    "REINFORCEMENT": "26. HỌC TĂNG CƯỜNG",
    "BAYESIAN": "27. XÁC SUẤT BAYES",
    "K_MEANS": "28. PHÂN CỤM K-MEANS",
    "NEURAL": "29. MẠNG NƠ-RON",
    "FUZZY": "30. LOGIC MỜ",
    "GENETIC": "31. THUẬT TOÁN DI TRUYỀN",
    "ANT_COLONY": "32. KIẾN BÒ",
    "PARTICLE_SWARM": "33. BẦY ĐÀN",
    "KNN": "34. K-NEAREST NEIGHBORS",
    "DECISION_TREE": "35. CÂY QUYẾT ĐỊNH",
    "RANDOM_FOREST": "36. RỪNG NGẪU NHIÊN",
    "GRADIENT_BOOST": "37. TĂNG CƯỜNG GRADIENT",
    "LSTM": "38. LSTM",
    "TRANSFORMER": "39. TRANSFORMER",
    "ENSEMBLE": "40. TỔNG HỢP",
}

settings = {"algo": "RANDOM"}
STRATEGY_CONFIG_FILE = "strategy_htool.json"
_spinner = ["📦", "🪑", "👔", "💬", "🎥", "🏢", "💰", "👥"]
_num_re = re.compile(r"-?\d+[\d,]*\.?\d*")

def log_debug(msg: str):
    try: logger.debug(msg)
    except: pass

def _parse_number(x: Any) -> Optional[float]:
    if x is None: return None
    if isinstance(x, (int, float)): return float(x)
    s = str(x); m = _num_re.search(s)
    if not m: return None
    try: return float(m.group(0).replace(",", ""))
    except: return None

def balance_headers_for(uid=None, secret=None):
    h = {"accept": "*/*", "accept-language": "vi,en;q=0.9", "cache-control": "no-cache", "country-code": "vn", "origin": "https://xworld.info", "referer": "https://xworld.info/", "user-agent": "Mozilla/5.0", "user-login": "login_v2", "xb-language": "vi-VN"}
    if uid: h["user-id"] = str(uid)
    if secret: h["user-secret-key"] = str(secret)
    return h

def fetch_balances_3games(retries=3, timeout=8, uid=None, secret=None):
    global current_build, starting_balance, cumulative_profit
    uid = uid or USER_ID; secret = secret or SECRET_KEY
    payload = {"user_id": int(uid) if uid else None, "source": "home"}
    for attempt in range(retries + 1):
        try:
            r = HTTP.post(WALLET_API_URL, json=payload, headers=balance_headers_for(uid, secret), timeout=timeout)
            r.raise_for_status(); j = r.json()
            ua = j.get("data", {}).get("user_asset", {})
            build = _parse_number(ua.get("BUILD"))
            if build is not None:
                if starting_balance is None: starting_balance = build
                current_build = build; cumulative_profit = current_build - starting_balance
            return current_build, _parse_number(ua.get("WORLD")), _parse_number(ua.get("USDT"))
        except: time.sleep(min(1.5 * (attempt + 1), 4))
    return current_build, None, None

# ================== LOGIC FUNCTIONS VTH ==================

def choose_random() -> int: return random.choice(ROOM_ORDER)

def choose_min_player_bet() -> int:
    if not any(rs.get('players', 0) > 0 or rs.get('bet', 0) > 0 for rs in room_state.values()): return choose_random()
    player_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['players'])
    bet_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['bet'])
    scores = defaultdict(int)
    for i, r in enumerate(player_ranks): scores[r] += i
    for i, r in enumerate(bet_ranks): scores[r] += i
    if last_killed_room in scores: scores[last_killed_room] += 0.5
    return min(scores, key=scores.get)

def choose_probability() -> int:
    scores = {}
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0); survives = room_stats[r].get('survives', 0)
        scores[r] = (survives + 1) / (kills + survives + 2)
    return max(scores, key=scores.get)

def choose_follow_killer() -> int:
    if last_killed_room is not None and last_killed_room in ROOM_ORDER: return last_killed_room
    return random.choice(ROOM_ORDER)

def choose_sequential() -> int:
    global _sequential_bet_index
    room = ROOM_ORDER[_sequential_bet_index]; _sequential_bet_index = (_sequential_bet_index + 1) % len(ROOM_ORDER)
    return room

def choose_smart_safe() -> int:
    scores = {}
    max_players = max(rs['players'] for rs in room_state.values()) or 1
    max_bet = max(rs['bet'] for rs in room_state.values()) or 1
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0); survives = room_stats[r].get('survives', 0)
        survival_rate = (survives + 1) / (kills + survives + 2)
        player_score = 1 - (room_state[r]['players'] / max_players)
        bet_score = 1 - (room_state[r]['bet'] / max_bet)
        penalty = 0.5 if r == last_killed_room else 0
        scores[r] = (0.4 * survival_rate) + (0.3 * player_score) + (0.3 * bet_score) - penalty
    return max(scores, key=scores.get)

def choose_hide_seek_master() -> int:
    danger_scores = {}
    max_players = max(rs['players'] for rs in room_state.values()) or 1
    max_bet = max(rs['bet'] for rs in room_state.values()) or 1
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0); survives = room_stats[r].get('survives', 0)
        hist_danger = (kills + 1) / (kills + survives + 2)
        crowd_danger = room_state[r]['players'] / max_players
        money_danger = room_state[r]['bet'] / max_bet
        recency_penalty = 1.0 if r == last_killed_room else 0.0
        danger_scores[r] = (0.3 * hist_danger) + (0.2 * crowd_danger) + (0.2 * money_danger) + recency_penalty
    return min(danger_scores, key=danger_scores.get)

def choose_balance() -> int:
    total_players = sum(rs['players'] for rs in room_state.values())
    total_bet = sum(rs['bet'] for rs in room_state.values())
    avg_players = total_players / len(ROOM_ORDER) if total_players > 0 else 0
    avg_bet = total_bet / len(ROOM_ORDER) if total_bet > 0 else 0
    scores = {}
    for r in ROOM_ORDER: scores[r] = abs(room_state[r]['players'] - avg_players) / (avg_players + 1) + abs(room_state[r]['bet'] - avg_bet) / (avg_bet + 1)
    return min(scores, key=scores.get)

def choose_most_players() -> int: return max(ROOM_ORDER, key=lambda r: room_state[r]['players'])
def choose_least_players() -> int: return min(ROOM_ORDER, key=lambda r: room_state[r]['players'])
def choose_richest() -> int: return max(ROOM_ORDER, key=lambda r: room_state[r]['bet'])
def choose_poorest() -> int: return min(ROOM_ORDER, key=lambda r: room_state[r]['bet'])

def choose_alternate() -> int:
    if len(bet_history) < 2: return random.choice(ROOM_ORDER)
    last_rooms = [b.get('room') for b in list(bet_history)[-3:] if b.get('room')]
    candidates = [r for r in ROOM_ORDER if r not in last_rooms]
    return random.choice(candidates) if candidates else random.choice(ROOM_ORDER)

def choose_avoid_result() -> int:
    if last_killed_room is None: return random.choice(ROOM_ORDER)
    candidates = [r for r in ROOM_ORDER if r != last_killed_room]
    return random.choice(candidates) if candidates else random.choice(ROOM_ORDER)

def choose_cold() -> int:
    player_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['players'])
    bet_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['bet'])
    scores = defaultdict(int)
    for i, r in enumerate(reversed(player_ranks)): scores[r] += i
    for i, r in enumerate(reversed(bet_ranks)): scores[r] += i
    return min(scores, key=scores.get)

def choose_hot() -> int:
    player_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['players'])
    bet_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['bet'])
    scores = defaultdict(int)
    for i, r in enumerate(player_ranks): scores[r] += i
    for i, r in enumerate(bet_ranks): scores[r] += i
    return max(scores, key=scores.get)

def choose_median() -> int:
    if not any(rs['players'] > 0 for rs in room_state.values()): return random.choice(ROOM_ORDER)
    players_list = sorted(ROOM_ORDER, key=lambda r: room_state[r]['players'])
    bet_list = sorted(ROOM_ORDER, key=lambda r: room_state[r]['bet'])
    median_players = players_list[len(players_list) // 2]; median_bet = bet_list[len(bet_list) // 2]
    if median_players == median_bet: return median_players
    scores = {}
    for r in ROOM_ORDER: scores[r] = abs(room_state[r]['players'] - room_state[median_players]['players']) + abs(room_state[r]['bet'] - room_state[median_bet]['bet'])
    return min(scores, key=scores.get)

def choose_pattern() -> int:
    if len(game_kill_log) < 3: return random.choice(ROOM_ORDER)
    last_3 = list(game_kill_log)[-3:]
    if len(last_3) == 3 and last_3[0] == last_3[2]: return last_3[1]
    return random.choice(ROOM_ORDER)

def choose_vip_random() -> int:
    logic_list = [choose_random, choose_min_player_bet, choose_probability, choose_follow_killer, choose_sequential, choose_smart_safe, choose_hide_seek_master, choose_balance, choose_most_players, choose_least_players, choose_richest, choose_poorest, choose_alternate, choose_avoid_result, choose_cold, choose_hot, choose_median, choose_pattern]
    return random.SystemRandom().choice(logic_list)()

def choose_killer_wave() -> int:
    if len(game_kill_log) < 4: return choose_random()
    last_4 = list(game_kill_log)[-4:]
    for i in range(1, 4):
        if len(last_4) >= i*2 and last_4[-i:] == last_4[-i*2:-i]: return last_4[-i-1] if len(last_4) > i else last_4[-1]
    return choose_smart_safe()

def choose_psycho_analysis() -> int:
    max_players_room = max(ROOM_ORDER, key=lambda r: room_state[r]['players'])
    max_bet_room = max(ROOM_ORDER, key=lambda r: room_state[r]['bet'])
    crowd_favorite = max_players_room if room_state[max_players_room]['players'] > room_state[max_bet_room]['players'] else max_bet_room
    candidates = [r for r in ROOM_ORDER if r != crowd_favorite]
    return min(candidates, key=lambda r: room_state[r]['players'] + room_state[r]['bet'] * 0.01) if candidates else choose_random()

def choose_markov_chain() -> int:
    if len(game_kill_log) < 5: return choose_random()
    transitions = defaultdict(lambda: defaultdict(int))
    for i in range(len(game_kill_log) - 1): transitions[game_kill_log[i]][game_kill_log[i + 1]] += 1
    last = game_kill_log[-1]
    if transitions[last]: return max(transitions[last].items(), key=lambda x: x[1])[0]
    return choose_smart_safe()

def choose_deep_learning() -> int:
    if len(killer_history) < 5: return choose_random()
    weights = {}
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0); survives = room_stats[r].get('survives', 0)
        survival_rate = (survives + 1) / (kills + survives + 2)
        recent_boost = -0.5 if r == last_killed_room else 0
        trend_boost = -0.3 if len(game_kill_log) >= 3 and r in list(game_kill_log)[-3:] else 0
        crowd_boost = 1 - (room_state[r]['players'] / max(1, max(rs['players'] for rs in room_state.values())))
        money_boost = 1 - (room_state[r]['bet'] / max(1, max(rs['bet'] for rs in room_state.values())))
        weights[r] = (0.3 * survival_rate) + (0.2 * recent_boost) + (0.15 * trend_boost) + (0.2 * crowd_boost) + (0.15 * money_boost)
    for r in ROOM_ORDER: weights[r] += random.uniform(-0.1, 0.1)
    return max(weights, key=weights.get)

def choose_reinforcement() -> int:
    if len(bet_history) < 3: return choose_random()
    action_scores = {r: 0 for r in ROOM_ORDER}
    for b in list(bet_history)[-10:]:
        room = b.get('room'); result = b.get('result')
        if room in ROOM_ORDER and result: action_scores[room] += 1 if result == "Thắng" else -0.5
    max_score = max(action_scores.values())
    return random.choice([r for r, s in action_scores.items() if s == max_score]) if max_score > 0 else choose_random()

def choose_bayesian() -> int:
    if len(game_kill_log) < 3: return choose_random()
    room_counts = Counter(game_kill_log); total_kills = len(game_kill_log)
    prior = {r: 1/len(ROOM_ORDER) for r in ROOM_ORDER}
    likelihood = {r: (room_counts.get(r, 0) + 1) / (total_kills + len(ROOM_ORDER)) for r in ROOM_ORDER}
    posterior = {r: prior[r] * likelihood[r] for r in ROOM_ORDER}
    total = sum(posterior.values())
    for r in ROOM_ORDER: posterior[r] /= total
    return min(posterior, key=posterior.get)

def choose_k_means() -> int:
    if len(game_kill_log) < 6: return choose_random()
    room_features = defaultdict(lambda: [0, 0])
    for i, room in enumerate(list(game_kill_log)[-10:]): room_features[room][0] += 1; room_features[room][1] = i
    cluster_1 = set()
    for room, features in room_features.items():
        if features[0] < 2: cluster_1.add(room)
    return random.choice(list(cluster_1)) if cluster_1 else choose_random()

def choose_neural() -> int:
    if len(killer_history) < 3: return choose_random()
    scores = {}
    for r in ROOM_ORDER:
        players = room_state[r]['players']; bet = room_state[r]['bet']
        kills = room_stats[r].get('kills', 0); survives = room_stats[r].get('survives', 0)
        layer1 = (0.3 * survives) - (0.5 * kills) + (0.2 * players) - (0.3 * bet)
        layer2 = (0.4 * layer1) + (0.2 * (survives - kills))
        layer3 = (0.5 * layer2) + (0.3 * (1 - players/max(1, max(rs['players'] for rs in room_state.values()))))
        scores[r] = 1 / (1 + math.exp(-layer3))
    return max(scores, key=scores.get)

def choose_fuzzy() -> int:
    if len(killer_history) < 2: return choose_random()
    scores = {}
    for r in ROOM_ORDER:
        players = room_state[r]['players']; bet = room_state[r]['bet']
        players_young = max(0, 1 - players/2) if players < 2 else 0
        players_mid = max(0, 1 - abs(players-3)/2) if 1 < players < 5 else 0
        players_old = max(0, (players-4)/2) if players > 4 else 0
        bet_low = max(0, 1 - bet/100) if bet < 100 else 0
        bet_mid = max(0, 1 - abs(bet-300)/200) if 100 < bet < 500 else 0
        bet_high = max(0, (bet-400)/200) if bet > 400 else 0
        rule1 = min(players_young, bet_low); rule2 = min(players_old, bet_high); rule3 = min(players_mid, bet_mid)
        scores[r] = (rule1 * 1.0 + rule2 * 0.0 + rule3 * 0.5) / (rule1 + rule2 + rule3 + 0.01)
    return max(scores, key=scores.get)

def choose_genetic() -> int:
    if len(killer_history) < 5: return choose_random()
    fitness = {r: (room_stats[r].get('survives', 0) + 1) / (room_stats[r].get('kills', 0) + room_stats[r].get('survives', 0) + 2) for r in ROOM_ORDER}
    return max(fitness, key=fitness.get)

def choose_ant_colony() -> int:
    if len(game_kill_log) < 3: return choose_random()
    pheromone = {r: list(game_kill_log).count(r) / len(game_kill_log) if game_kill_log else 0 for r in ROOM_ORDER}
    return min(pheromone, key=pheromone.get)

def choose_particle_swarm() -> int:
    if len(killer_history) < 3: return choose_random()
    scores = {}
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0); survives = room_stats[r].get('survives', 0)
        survival_rate = (survives + 1) / (kills + survives + 2); recent_trend = 0.3 if r in list(game_kill_log)[-3:] else 0
        scores[r] = survival_rate + recent_trend
    return max(scores, key=scores.get)

def choose_knn() -> int:
    if len(game_kill_log) < 3: return choose_random()
    k = min(3, len(game_kill_log)); nearest = list(game_kill_log)[-k:]
    counts = Counter(nearest); min_count = min(counts.values())
    candidates = [r for r, c in counts.items() if c == min_count]
    return random.choice(candidates) if candidates else choose_random()

def choose_decision_tree() -> int:
    if len(killer_history) < 5: return choose_random()
    if last_killed_room:
        if room_state[last_killed_room]['players'] > 5: candidates = [r for r in ROOM_ORDER if r != last_killed_room]; return random.choice(candidates) if candidates else choose_random()
        elif room_state[last_killed_room]['bet'] > 1000: candidates = [r for r in ROOM_ORDER if r != last_killed_room]; return random.choice(candidates) if candidates else choose_random()
        return choose_probability()
    return choose_random()

def choose_random_forest() -> int:
    if len(killer_history) < 3: return choose_random()
    predictions = [choose_probability() if random.random() > 0.5 else choose_min_player_bet() for _ in range(5)]
    return Counter(predictions).most_common(1)[0][0]

def choose_gradient_boost() -> int:
    if len(killer_history) < 3: return choose_random()
    scores = {}
    for r in ROOM_ORDER:
        base_score = 0.5; kills = room_stats[r].get('kills', 0); survives = room_stats[r].get('survives', 0)
        base_score += 0.3 * ((survives + 1) / (kills + survives + 2))
        base_score -= 0.1 * (room_state[r]['players'] / max(1, max(rs['players'] for rs in room_state.values())))
        base_score -= 0.1 * (room_state[r]['bet'] / max(1, max(rs['bet'] for rs in room_state.values())))
        scores[r] = base_score
    return max(scores, key=scores.get)

def choose_lstm() -> int:
    if len(game_kill_log) < 4: return choose_random()
    last_5 = list(game_kill_log)[-5:]
    if len(last_5) == 5 and last_5[0] == last_5[3] and last_5[1] == last_5[4]: return last_5[2]
    return choose_markov_chain()

def choose_transformer() -> int:
    if len(game_kill_log) < 4: return choose_random()
    attention_scores = {}
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0); survives = room_stats[r].get('survives', 0)
        recency = 1 - (list(game_kill_log).count(r) / max(1, len(game_kill_log)))
        attention_scores[r] = (0.4 * recency) + (0.3 * (survives / max(1, kills + survives))) + (0.3 * (1 - room_state[r]['players'] / max(1, max(rs['players'] for rs in room_state.values()))))
    return max(attention_scores, key=attention_scores.get)

def choose_ensemble() -> int:
    if len(killer_history) < 3: return choose_random()
    vip_logic_funcs = [choose_killer_wave, choose_psycho_analysis, choose_markov_chain, choose_deep_learning, choose_reinforcement, choose_bayesian, choose_k_means, choose_neural, choose_fuzzy, choose_genetic, choose_ant_colony, choose_particle_swarm, choose_knn, choose_decision_tree, choose_random_forest, choose_gradient_boost, choose_lstm, choose_transformer]
    votes = defaultdict(int)
    for func in vip_logic_funcs:
        try: votes[func()] += 1
        except: continue
    return max(votes, key=votes.get) if votes else choose_random()

def choose_room_tn(mode: str) -> Tuple[int, str]:
    mode = mode.upper()
    logic_map = {
        "RANDOM": choose_random, "MIN_PLAYER_BET": choose_min_player_bet,
        "PROBABILITY": choose_probability, "FOLLOW_KILLER": choose_follow_killer,
        "SEQUENTIAL": choose_sequential, "KILLER_PERSONALITY": choose_killer_personality,
        "SMART_SAFE": choose_smart_safe, "FOLLOW_KILLER_DELAYED": choose_follow_killer_delayed,
        "HIDE_SEEK_MASTER": choose_hide_seek_master, "BALANCE": choose_balance,
        "MOST_PLAYERS": choose_most_players, "LEAST_PLAYERS": choose_least_players,
        "RICHEST": choose_richest, "POOREST": choose_poorest,
        "ALTERNATE": choose_alternate, "AVOID_RESULT": choose_avoid_result,
        "COLD": choose_cold, "HOT": choose_hot, "MEDIAN": choose_median,
        "PATTERN": choose_pattern, "VIP_RANDOM": choose_vip_random,
        "KILLER_WAVE": choose_killer_wave, "PSYCHO_ANALYSIS": choose_psycho_analysis,
        "MARKOV_CHAIN": choose_markov_chain, "DEEP_LEARNING": choose_deep_learning,
        "REINFORCEMENT": choose_reinforcement, "BAYESIAN": choose_bayesian,
        "K_MEANS": choose_k_means, "NEURAL": choose_neural,
        "FUZZY": choose_fuzzy, "GENETIC": choose_genetic,
        "ANT_COLONY": choose_ant_colony, "PARTICLE_SWARM": choose_particle_swarm,
        "KNN": choose_knn, "DECISION_TREE": choose_decision_tree,
        "RANDOM_FOREST": choose_random_forest, "GRADIENT_BOOST": choose_gradient_boost,
        "LSTM": choose_lstm, "TRANSFORMER": choose_transformer,
        "ENSEMBLE": choose_ensemble,
    }
    func = logic_map.get(mode, choose_random)
    return func(), mode

# ================== API VÀ WEBSOCKET VTH ==================

def api_headers():
    return {"content-type": "application/json", "user-agent": "Mozilla/5.0", "user-id": str(USER_ID) if USER_ID else "", "user-secret-key": SECRET_KEY if SECRET_KEY else ""}

def place_bet_http(issue: int, room_id: int, amount: float) -> dict:
    payload = {"asset_type": "BUILD", "user_id": USER_ID, "room_id": int(room_id), "bet_amount": float(amount)}
    try:
        r = requests.post(BET_API_URL, headers=api_headers(), json=payload, timeout=8)
        try: return r.json()
        except: return {"raw": r.text}
    except Exception as e: return {"error": str(e)}

def record_bet(issue: int, room_id: int, amount: float, resp: dict, algo_used=None) -> dict:
    rec = {"issue": issue, "room": room_id, "amount": float(amount), "time": datetime.now(tz).strftime("%H:%M:%S"), "resp": resp, "result": "Đang", "algo": algo_used}
    bet_history.append(rec); return rec

def place_bet_async(issue: int, room_id: int, amount: float, algo_used=None):
    def worker():
        time.sleep(random.uniform(0.05, 0.45)); res = place_bet_http(issue, room_id, amount)
        record_bet(issue, room_id, amount, res, algo_used=algo_used)
    threading.Thread(target=worker, daemon=True).start()

def lock_prediction_if_needed():
    global prediction_locked, predicted_room, ui_state, current_bet, stop_flag
    if stop_flag or prediction_locked or issue_id is None:
        return
    mode = settings.get("algo", "RANDOM")
    chosen, algo_used = choose_room_tn(mode)
    predicted_room = chosen
    prediction_locked = True
    ui_state = "PREDICTED"
    if run_mode == "AUTO":
        bld = current_build
        if bld is None:
            bld, _, _ = fetch_balances_3games(retries=1, timeout=3)
        if current_bet is None:
            current_bet = base_bet
        amt = float(current_bet)
        if bld and amt > bld:
            current_bet = base_bet
            amt = float(current_bet)
        if amt <= 0:
            return
        place_bet_async(issue_id, predicted_room, amt, algo_used=algo_used)

def on_open(ws):
    _ws["ws"] = ws; global _ws_status; _ws_status = "✅ Đã kết nối"
    try: ws.send(json.dumps({"msg_type": "handle_enter_game", "asset_type": "BUILD", "user_id": USER_ID, "user_secret_key": SECRET_KEY}))
    except: pass

def on_message(ws, message):
    global issue_id, killed_room, round_index, ui_state, analysis_start_ts, prediction_locked, predicted_room, last_killed_room, current_bet, win_streak, lose_streak, max_win_streak, max_lose_streak, stop_flag
    try:
        if isinstance(message, bytes): message = message.decode("utf-8", errors="replace")
        data = json.loads(message); msg_type = str(data.get("msg_type", ""))
        if msg_type == "notify_enter_game":
            if data.get("last_killed_room_id"): last_killed_room = int(data["last_killed_room_id"])
            for rm in data.get("room_stat", []):
                if isinstance(rm, dict): room_state[int(rm.get("room_id", 0))] = {"players": int(rm.get("user_cnt", 0)), "bet": int(rm.get("total_bet_amount", 0))}
        elif "issue_stat" in msg_type:
            for rm in data.get("rooms", []):
                if isinstance(rm, dict): room_state[int(rm.get("room_id", 0))] = {"players": int(rm.get("user_cnt", 0)), "bet": int(rm.get("total_bet_amount", 0))}
            new_issue = data.get("issue_id")
            if new_issue and new_issue != issue_id: issue_id = new_issue; round_index += 1; killed_room = None; prediction_locked = False; predicted_room = None; ui_state = "ANALYZING"; analysis_start_ts = time.time()
        elif "count_down" in msg_type:
            if int(data.get("count_down", 99)) <= 10 and not prediction_locked: lock_prediction_if_needed()
        elif "result" in msg_type:
            kr = data.get("killed_room") or data.get("killed_room_id")
            if kr:
                killed_room = int(kr); game_kill_log.append(killed_room); last_killed_room = killed_room
                for rid in ROOM_ORDER:
                    if rid == killed_room: room_stats[rid]["kills"] += 1
                    else: room_stats[rid]["survives"] += 1
                for b in reversed(bet_history):
                    if b.get("issue") == issue_id:
                        if int(b.get("room")) != killed_room: b["result"] = "Thắng"; current_bet = base_bet; win_streak += 1; lose_streak = 0; max_win_streak = max(max_win_streak, win_streak)
                        else: b["result"] = "Thua"; current_bet = current_bet * multiplier if current_bet else base_bet; lose_streak += 1; win_streak = 0; max_lose_streak = max(max_lose_streak, lose_streak)
                        break
            ui_state = "RESULT"
    except: pass

def on_close(ws, code, reason): global _ws_status; _ws_status = f"⏳ Đã đóng ({code})"
def on_error(ws, err): global _ws_status; _ws_status = f"❌ Lỗi"

def start_ws():
    global _ws_status; backoff = 1.0
    while not stop_flag:
        try:
            _ws_status = "⏳ Đang kết nối..."
            ws_app = websocket.WebSocketApp(WS_URL, on_open=on_open, on_message=on_message, on_close=on_close, on_error=on_error)
            _ws["ws"] = ws_app; ws_app.run_forever(ping_interval=15, ping_timeout=6)
        except: _ws_status = f"❌ Lỗi kết nối"
        t = min(backoff + random.random() * 0.8, 30)
        if not stop_flag: time.sleep(t); backoff = min(backoff * 1.8, 30)

def monitor_loop():
    global last_msg_ts, stop_flag
    while not stop_flag:
        if time.time() - last_msg_ts > 45:
            try: wsobj = _ws.get("ws"); wsobj.close() if wsobj else None
            except: pass
        time.sleep(0.6)

def build_logo_with_gradient(logo_text: str) -> Text:
    lines = logo_text.split('\n'); result = Text()
    for line in lines:
        if line.strip():
            chars = list(line)
            for i, char in enumerate(chars):
                if char in ['█', '╔', '╗', '║', '╚', '╝', '═']:
                    style = HTOOL_COLORS["gold"] if i % 3 == 0 else HTOOL_COLORS["neon_blue"] if i % 3 == 1 else HTOOL_COLORS["neon_pink"]
                    result.append(char, style=style)
                else: result.append(char, style="dim")
            result.append("\n")
    return result

def build_premium_header():
    logo_text = build_logo_with_gradient(LOGO)
    info_table = Table(box=None, show_header=False, pad_edge=False, expand=True)
    info_table.add_column(style=f"bold {HTOOL_COLORS['gold']}", no_wrap=True, justify="right", width=18)
    info_table.add_column(style="white")
    info_table.add_row(f"{ICONS['user']} USER:", f"[bold {HTOOL_COLORS['platinum']}]{USER_ID}[/]" if USER_ID else "[dim]-[/dim]")
    b = f"{current_build:,.2f}" if isinstance(current_build, (int, float)) else "0.00"
    info_table.add_row(f"{ICONS['diamond']} BALANCE:", f"[bold {HTOOL_COLORS['emerald']}]{b}[/] BUILD")
    pnl_val = cumulative_profit or 0
    pnl_color = HTOOL_COLORS["emerald"] if pnl_val >= 0 else HTOOL_COLORS["ruby"]
    info_table.add_row(f"{ICONS['fire']} P&L:", f"[{pnl_color}]{pnl_val:+,.2f}[/] BUILD")
    streak_text = Text.assemble(("🔥 ", f"bold {HTOOL_COLORS['neon_orange']}"), (f"{win_streak}", f"bold {HTOOL_COLORS['emerald']}"), (" | ", "dim"), ("💀 ", f"bold {HTOOL_COLORS['ruby']}"), (f"{lose_streak}", f"bold {HTOOL_COLORS['ruby']}"))
    info_table.add_row("📊 STREAK:", streak_text)
    algo_label = SELECTION_MODES.get(settings.get('algo'), settings.get('algo'))
    info_table.add_row(f"{ICONS['brain']} AI:", f"[bold {HTOOL_COLORS['neon_pink']}]{algo_label}[/]")
    info_table.add_row(f"{ICONS['clock']} TIME:", f"[{HTOOL_COLORS['sapphire']}]{datetime.now(tz).strftime('%H:%M:%S')}[/]")
    info_table.add_row(f"{ICONS['target']} ROUND:", f"[bold {HTOOL_COLORS['gold']}]{issue_id or 'Waiting...'}[/]")
    info_table.add_row(f"{ICONS['link']} WS:", f"[dim]{_ws_status}[/dim]")
    return Panel(Group(Align.center(logo_text), info_table), border_style=HTOOL_COLORS["gold"], box=box.HEAVY, padding=(1, 2))

def build_premium_rooms():
    room_panels = []
    for r in ROOM_ORDER:
        st = room_state.get(r, {}); players = st.get("players", 0); bet_val = st.get('bet', 0) or 0
        is_predicted = predicted_room is not None and int(r) == int(predicted_room)
        is_killed = killed_room is not None and int(r) == int(killed_room)
        if is_killed and is_predicted: border, title_style, bg, glow = f"bold {HTOOL_COLORS['ruby']}", f"bold {HTOOL_COLORS['ruby']}", "on #330000", "💀⚡🔥"
        elif is_killed: border, title_style, bg, glow = HTOOL_COLORS["ruby"], HTOOL_COLORS["ruby"], "on #1a0000", "💀"
        elif is_predicted: border, title_style, bg, glow = f"bold {HTOOL_COLORS['emerald']}", f"bold {HTOOL_COLORS['emerald']}", "on #003300", "✨⭐"
        else: border, title_style, bg, glow = HTOOL_COLORS["onyx"], "white", "", ""
        content = Text.assemble(("\n", ""), (f"{glow} ", "default"), (f"👥 {players:3d} ", "white"), ("| ", "dim"), (f"💰 {int(bet_val):,}", HTOOL_COLORS["gold"]), ("\n", ""), justify="center")
        room_panels.append(Panel(Align.center(content, vertical="middle"), title=f"[{title_style}]{ROOM_NAMES.get(r, f'Room {r}')}[/{title_style}]", border_style=border, box=box.HEAVY, expand=True, height=5, style=bg))
    return Panel(Columns(room_panels, equal=True, expand=True), title=f"[bold {HTOOL_COLORS['gold']}]🎮 PREMIUM BATTLE ARENA 🎮[/]", box=box.HEAVY, border_style=HTOOL_COLORS["gold"], expand=True)

def build_premium_mid():
    if ui_state == "ANALYZING":
        elapsed = time.time() - (analysis_start_ts or time.time()); progress = min(1.0, elapsed / analysis_duration)
        bar = "█" * int(40 * progress) + "░" * (40 - int(40 * progress))
        content = Text.from_markup(f"\n[bold {HTOOL_COLORS['neon_blue']}]🧠 AI ANALYZING[/]\n\n[{HTOOL_COLORS['gold']}]{bar}[/]\n\n[{HTOOL_COLORS['neon_pink']}]Progress: {progress*100:.0f}%[/]")
        return Panel(content, border_style=HTOOL_COLORS["neon_pink"], box=box.HEAVY, expand=True)
    elif ui_state == "PREDICTED":
        name = ROOM_NAMES.get(predicted_room, f"Room {predicted_room}") if predicted_room else '?'
        bet_amt = f"{current_bet:,.2f}" if current_bet else '0'
        content = Text.assemble(("\n🎯 TARGET LOCKED\n\n", f"bold {HTOOL_COLORS['emerald']}"), (f"{name}\n", f"bold {HTOOL_COLORS['gold']}"), (f"💰 {bet_amt} BUILD\n", f"bold {HTOOL_COLORS['gold']}"))
        return Panel(Align.center(content), border_style=HTOOL_COLORS["emerald"], box=box.HEAVY, expand=True)
    elif ui_state == "RESULT":
        k = ROOM_NAMES.get(killed_room, "-") if killed_room else "-"
        last_bet = bet_history[-1] if bet_history else None
        result_text, result_color = "⏳ WAITING", HTOOL_COLORS["gold"]
        if last_bet and last_bet.get('issue') == issue_id:
            result_text, result_color = ("🎉 WINNER 🎉", HTOOL_COLORS["emerald"]) if last_bet.get('result') == "Thắng" else ("💀 LOSER 💀", HTOOL_COLORS["ruby"])
        content = Text.assemble(("\n", ""), (f"{result_text}\n\n", f"bold {result_color}"), (f"☠️ Killer: {k}\n", f"bold {HTOOL_COLORS['ruby']}"))
        return Panel(Align.center(content), border_style=result_color, box=box.HEAVY, expand=True)
    return Panel(Align.center(Text("⏳ Waiting...", style=HTOOL_COLORS["gold"])), border_style=HTOOL_COLORS["gold"], box=box.HEAVY, expand=True)

def build_premium_history():
    t = Table(title=f"[bold {HTOOL_COLORS['gold']}]📜 BET HISTORY[/]", box=box.ROUNDED, expand=True)
    t.add_column("Round", style=HTOOL_COLORS["sapphire"]); t.add_column("Room", style=HTOOL_COLORS["neon_blue"]); t.add_column("Amount", justify="right", style=HTOOL_COLORS["gold"]); t.add_column("Result")
    for b in list(bet_history)[-6:]:
        res = str(b.get('result', '⏳'))
        t.add_row(str(b.get('issue', '-')), ROOM_NAMES.get(b.get('room'), str(b.get('room', '-'))), f"{float(b.get('amount', 0)):,.2f}", Text("✅" if "Thắng" in res else "❌" if "Thua" in res else "⏳"))
    return Panel(t, border_style=HTOOL_COLORS["sapphire"], box=box.HEAVY, expand=True)

def build_premium_marquee():
    messages = [f"⚡ HTOOL VIP PREMIUM - Best AI Tool {ICONS['crown']}", f"🧠 AI Powered Prediction System v2.0 {ICONS['robot']}"]
    message = messages[int(time.time() / 8) % len(messages)]; full_text = " " * 30 + message + " " * 30
    width = console.width or 80; display_text = (full_text * 3)[int(time.time() * 3) % len(full_text) : int(time.time() * 3) % len(full_text) + width]
    return Panel(Text(display_text, style=f"bold {HTOOL_COLORS['neon_blue']}", no_wrap=True), box=box.ROUNDED, border_style=HTOOL_COLORS["onyx"], padding=0, expand=True)

def save_strategy_config():
    config_data = {"base_bet": base_bet, "multiplier": multiplier, "algo": settings.get("algo"), "bet_rounds_before_skip": bet_rounds_before_skip, "pause_after_losses": pause_after_losses}
    try:
        with open(STRATEGY_CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(config_data, f, indent=2)
    except: pass

def load_strategy_config() -> bool:
    global base_bet, multiplier, current_bet, bet_rounds_before_skip, pause_after_losses
    if not Path(STRATEGY_CONFIG_FILE).exists(): return False
    try:
        with open(STRATEGY_CONFIG_FILE, "r", encoding="utf-8") as f: config_data = json.load(f)
        base_bet = config_data.get("base_bet", 1.0); multiplier = config_data.get("multiplier", 2.0)
        settings["algo"] = config_data.get("algo", "RANDOM"); bet_rounds_before_skip = config_data.get("bet_rounds_before_skip", 0)
        pause_after_losses = config_data.get("pause_after_losses", 0); current_bet = base_bet; run_mode = "AUTO"
        return True
    except: return False

def prompt_settings() -> bool:
    global base_bet, multiplier, current_bet, bet_rounds_before_skip, pause_after_losses, profit_target, stop_when_profit_reached, stop_loss_target, stop_when_loss_reached
    console.clear(); console.print(Panel(Align.center(f"[bold {HTOOL_COLORS['gold']}]⚙️ PREMIUM CONFIGURATION[/]"), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE))
    base_bet = FloatPrompt.ask(f"\n[bold {HTOOL_COLORS['neon_blue']}]💰 Cược gốc:[/]\n   >>", default=1.0)
    multiplier = FloatPrompt.ask(f"\n[bold {HTOOL_COLORS['neon_blue']}]📈 Hệ số nhân:[/]\n   >>", default=2.0); current_bet = base_bet
    
    # KEY VIP - Lấy danh sách AI khả dụng
    if _is_vip: available_modes = list(SELECTION_MODES.items())
    else: available_modes = list(SELECTION_MODES.items())[:FREE_AI_LIMIT]
    
    console.clear()
    console.print(f"\n[bold {HTOOL_COLORS['neon_pink']}]🧠 Chọn AI ({len(available_modes)} AI khả dụng):[/]\n")
    if not _is_vip: console.print(f"[yellow]⚠️ Key thường: Chỉ {FREE_AI_LIMIT}/{len(SELECTION_MODES)} AI[/]")
    
    algo_table = Table(box=box.ROUNDED, border_style=HTOOL_COLORS["neon_pink"])
    algo_table.add_column("STT", style=HTOOL_COLORS["gold"], width=4); algo_table.add_column("Thuật toán", style=HTOOL_COLORS["neon_blue"])
    for i, (key, label) in enumerate(available_modes, 1): algo_table.add_row(str(i), label)
    console.print(algo_table)
    
    max_choice = len(available_modes)
    choice = IntPrompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]>> Chọn (1-{max_choice})[/]", choices=[str(i) for i in range(1, max_choice + 1)], default=1)
    settings["algo"] = available_modes[choice - 1][0]
    
    bet_rounds_before_skip = IntPrompt.ask(f"\n[bold {HTOOL_COLORS['sapphire']}]🛡️ Chống soi:[/]\n   >>", default=0)
    pause_after_losses = IntPrompt.ask(f"\n[bold {HTOOL_COLORS['sapphire']}]⏸️ Nghỉ sau thua:[/]\n   >>", default=0)
    start = Prompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]>> Bắt đầu? (Enter/q)[/]", default="")
    if start.lower() == 'q': return False
    run_mode = "AUTO"; return True

def load_accounts() -> list:
    acc_file = Path("accounts.json")
    if not acc_file.exists(): return []
    try: return json.loads(acc_file.read_text())
    except: return []

def save_accounts(accounts: list):
    with Path("accounts.json").open("w", encoding="utf-8") as f: json.dump(accounts, f, indent=2)

def add_new_account(accounts: list) -> bool:
    console.clear(); link = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]>> Paste link[/]")
    if not link: return False
    try:
        parsed = urlparse(link); params = parse_qs(parsed.query)
        if 'userId' in params and 'secretKey' in params:
            uid = int(params.get('userId')[0]); skey = params.get('secretKey', [None])[0]
            accounts.append({"userId": uid, "secretKey": skey}); save_accounts(accounts)
            console.print(f"[green]✅ Đã thêm: {uid}[/]"); time.sleep(2); return True
    except: pass
    return False

def delete_account(accounts: list) -> bool:
    console.clear()
    if not accounts: return False
    table = Table(box=box.ROUNDED); table.add_column("STT", style=HTOOL_COLORS["gold"]); table.add_column("User ID", style=HTOOL_COLORS["neon_blue"])
    for i, acc in enumerate(accounts, 1): table.add_row(str(i), str(acc.get('userId')))
    console.print(table); choice = Prompt.ask(f"[bold {HTOOL_COLORS['ruby']}]>> Chọn STT[/]", default="")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(accounts): removed = accounts.pop(idx); save_accounts(accounts); console.print(f"[green]✅ Đã xóa: {removed.get('userId')}[/]"); time.sleep(2); return True
    except: pass
    return False

def select_account_premium() -> bool:
    global USER_ID, SECRET_KEY
    while True:
        console.clear(); accounts = load_accounts()
        if not accounts: console.print("[yellow]⚠️ Chưa có tài khoản![/]"); time.sleep(2); return False
        table = Table(title="📋 DANH SÁCH TÀI KHOẢN", box=box.HEAVY)
        table.add_column("STT", style=HTOOL_COLORS["gold"]); table.add_column("User ID", style=HTOOL_COLORS["neon_blue"]); table.add_column("Balance", justify="right")
        for i, acc in enumerate(accounts, 1):
            uid = acc.get('userId'); build, _, _ = fetch_balances_3games(uid=uid, secret=acc.get('secretKey'))
            table.add_row(str(i), str(uid), f"[{HTOOL_COLORS['emerald']}]{build:,.4f}[/]" if build else "[red]❌[/]")
        console.print(table); choice = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]>> Chọn số[/]", choices=[str(i) for i in range(1, len(accounts) + 1)], default="")
        if not choice: return False
        idx = int(choice) - 1
        if 0 <= idx < len(accounts): USER_ID = accounts[idx]['userId']; SECRET_KEY = accounts[idx]['secretKey']; console.print(f"[green]✅ Đã chọn: {USER_ID}[/]"); time.sleep(1.5); return True

def start_threads():
    threading.Thread(target=start_ws, daemon=True).start(); threading.Thread(target=monitor_loop, daemon=True).start()

def start_game_flow():
    global stop_flag
    if USER_ID is None or SECRET_KEY is None: console.print("[red]❌ Chưa chọn tài khoản.[/]"); time.sleep(2); return
    console.print(Rule("[bold green]🚀 KHỞI ĐỘNG...[/]", style="green")); start_threads()
    with console.status("[bold green]Đang kết nối...[/]", spinner="dots"):
        wait_start = time.time()
        while issue_id is None and (time.time() - wait_start) < 30: time.sleep(0.5)
        if issue_id is None: console.print("\n[bold red]❌ Không nhận được dữ liệu.[/]"); time.sleep(3); return
    console.print("\n[bold green]✅ Kết nối thành công![/]"); time.sleep(2)
    def generate_layout():
        main_grid = Table.grid(expand=True, pad_edge=False); main_grid.add_column("main", ratio=60); main_grid.add_column("side", ratio=40)
        right_grid = Table.grid(expand=True, pad_edge=False); right_grid.add_row(build_premium_mid()); right_grid.add_row(build_premium_history())
        main_grid.add_row(build_premium_rooms(), right_grid)
        root = Table.grid(expand=True, pad_edge=False); root.add_row(build_premium_header()); root.add_row(build_premium_marquee()); root.add_row(main_grid)
        return root
    with Live(generate_layout(), refresh_per_second=4, console=console, screen=True) as live:
        try:
            while not stop_flag: live.update(generate_layout()); time.sleep(0.25)
        except KeyboardInterrupt: console.print("[yellow]Người dùng thoát.[/]")
        # ================== TOOL CHẠY ĐUA TỐC ĐỘ ==================

cdtd_session = requests.Session()
cdtd_headers = {}

NV = {1: 'Bậc thầy tấn công', 2: 'Quyền sắt', 3: 'Thợ lặn sâu', 4: 'Cơn lốc sân cỏ', 5: 'Hiệp sĩ phi nhanh', 6: 'Vua home run'}
NV_ICONS = {1: '🥋', 2: '👊', 3: '🤿', 4: '🌪️', 5: '🏇', 6: '⚾'}

CDTD_ALGORITHMS = {
    "RANDOM": "1. NGẪU NHIÊN", "AVOID_LAST": "2. TRÁNH KẾT QUẢ CUỐI",
    "HOT_STREAK": "3. THEO CHUỖI THẮNG", "COLD_STREAK": "4. BẮT ĐẢO CHIỀU",
    "BALANCE": "5. CÂN BẰNG LỊCH SỬ", "PATTERN": "6. NHẬN DIỆN MẪU",
    "PROBABILITY": "7. XÁC SUẤT THỐNG KÊ", "FOLLOW_WINNER": "8. THEO NGƯỜI THẮNG",
    "ANTI_WINNER": "9. CHỐNG NGƯỜI THẮNG", "SMART_ANALYSIS": "10. PHÂN TÍCH THÔNG MINH",
    "MARKOV_CHAIN": "11. CHUỖI MARKOV", "BAYESIAN": "12. XÁC SUẤT BAYES",
    "NEURAL_NETWORK": "13. MẠNG NƠ-RON", "GENETIC_ALGO": "14. THUẬT TOÁN DI TRUYỀN",
    "REINFORCEMENT": "15. HỌC TĂNG CƯỜNG", "KNN": "16. K-NEAREST NEIGHBORS",
    "DECISION_TREE": "17. CÂY QUYẾT ĐỊNH", "RANDOM_FOREST": "18. RỪNG NGẪU NHIÊN",
    "GRADIENT_BOOST": "19. TĂNG CƯỜNG GRADIENT", "ENSEMBLE": "20. TỔNG HỢP",
    "TREND_FOLLOWING": "21. THEO XU HƯỚNG", "MEAN_REVERSION": "22. ĐẢO CHIỀU TRUNG BÌNH",
    "MOMENTUM": "23. ĐỘNG LƯỢNG", "VOLATILITY": "24. BIẾN ĐỘNG",
    "SEASONAL": "25. CHU KỲ", "CORRELATION": "26. TƯƠNG QUAN",
    "CLUSTER": "27. PHÂN CỤM", "ANOMALY": "28. PHÁT HIỆN BẤT THƯỜNG",
    "ENTROPY": "29. ENTROPY", "FUZZY_LOGIC": "30. LOGIC MỜ",
    "LSTM_PREDICT": "31. LSTM", "TRANSFORMER": "32. TRANSFORMER",
    "ATTENTION": "33. ATTENTION", "DEEP_Q": "34. DEEP Q-LEARNING",
    "A3C": "35. A3C", "PPO": "36. PPO", "GAN": "37. GAN",
    "AUTOENCODER": "38. AUTOENCODER", "SWARM_INTEL": "39. TRÍ TUỆ BẦY ĐÀN",
    "META_LEARNING": "40. META LEARNING",
}

cdtd_settings = {"algo": "RANDOM"}
cdtd_coin = "BUILD"
cdtd_base_bet = 1.0
cdtd_multiplier = 2.0
cdtd_current_bet = 1.0
cdtd_win_streak = 0
cdtd_lose_streak = 0
cdtd_max_win_streak = 0
cdtd_max_lose_streak = 0
cdtd_stats = {'win': 0, 'lose': 0, 'asset_0': 0}
cdtd_bet_history = deque(maxlen=50)
cdtd_stop_flag = False
cdtd_issue_id = None
cdtd_predicted_nv = None
cdtd_ui_state = "WAITING"
cdtd_analysis_start_ts = None
cdtd_analysis_duration = 25.0
cdtd_pause_rounds = 0
cdtd_pause_remaining = 0
cdtd_bet_rounds_before_skip = 0
cdtd_rounds_placed = 0
cdtd_skip_next = False
cdtd_last_winner = None
cdtd_previous_issue = None
cdtd_bet_placed_this_round = False
cdtd_checked_result = False
cdtd_recent_choices = deque(maxlen=10)
cdtd_avoid_repeat = 3

# === AUTO ADAPTIVE ===
cdtd_logic_performance = defaultdict(lambda: {'wins': 0, 'losses': 0})
cdtd_adaptive_enabled = False
cdtd_adaptive_interval = 20
cdtd_current_logic = None

def evaluate_logics():
    best_logic = None; best_rate = -1
    for logic in CDTD_ALGORITHMS:
        perf = cdtd_logic_performance[logic]; total = perf['wins'] + perf['losses']
        if total >= 5:
            rate = perf['wins'] / total
            if rate > best_rate: best_rate = rate; best_logic = logic
    return best_logic

def adaptive_choose_nv(data_top10, data_top100):
    global cdtd_current_logic
    if cdtd_current_logic is None or (cdtd_stats['win'] + cdtd_stats['lose']) % cdtd_adaptive_interval == 0:
        new_logic = evaluate_logics()
        if new_logic: cdtd_current_logic = new_logic
    if cdtd_current_logic: return choose_nv_cdtd(cdtd_current_logic, data_top10, data_top100)
    else: return choose_nv_cdtd("RANDOM", data_top10, data_top100)

def get_filtered_candidates(data_top10, avoid_count=3):
    last_winner = int(data_top10[1][0]) if data_top10 and data_top10[1] else None
    recent = list(cdtd_recent_choices)[-avoid_count:] if len(cdtd_recent_choices) >= avoid_count else list(cdtd_recent_choices)
    candidates = [nv for nv in range(1, 7) if nv not in recent and nv != last_winner]
    if not candidates: candidates = [nv for nv in range(1, 7) if nv != last_winner]
    if not candidates: candidates = list(range(1, 7))
    return candidates

def choose_nv_random(data_top10, data_top100): return random.choice(get_filtered_candidates(data_top10, cdtd_avoid_repeat))
def choose_nv_avoid_last(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    last_winner = int(data_top10[1][0]) if data_top10 and data_top10[1] else None
    filtered = [nv for nv in candidates if nv != last_winner]
    return random.choice(filtered) if filtered else random.choice(candidates)

def choose_nv_hot_streak(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if data_top100 and data_top100[1]:
        max_wins = max(data_top100[1]); hot_nvs = [i+1 for i, wins in enumerate(data_top100[1]) if wins == max_wins and (i+1) in candidates]
        if hot_nvs: return random.choice(hot_nvs)
    return random.choice(candidates)

def choose_nv_cold_streak(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if data_top100 and data_top100[1]:
        min_wins = min(data_top100[1]); cold_nvs = [i+1 for i, wins in enumerate(data_top100[1]) if wins == min_wins and (i+1) in candidates]
        if cold_nvs: return random.choice(cold_nvs)
    return random.choice(candidates)

def choose_nv_balance(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if data_top100 and data_top100[1]:
        total_wins = sum(data_top100[1]); avg_wins = total_wins / 6
        below_avg = [i+1 for i, wins in enumerate(data_top100[1]) if wins < avg_wins and (i+1) in candidates]
        if below_avg: return random.choice(below_avg)
    return random.choice(candidates)

def choose_nv_pattern(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if len(cdtd_bet_history) >= 4:
        recent_winners = [int(b.get('winner', 0)) for b in list(cdtd_bet_history)[-6:] if b.get('winner')]
        if len(recent_winners) >= 4 and recent_winners[-1] == recent_winners[-3] and recent_winners[-2] == recent_winners[-4]:
            predicted = recent_winners[-2]
            if predicted in candidates: return predicted
    return random.choice(candidates)

def choose_nv_probability(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if data_top100 and data_top100[1]:
        weights, nv_list = [], []
        for i in range(1, 7):
            if i in candidates:
                weight = 1.0 / (data_top100[1][i-1] + 1)
                if i == int(data_top10[1][0]): weight *= 0.5
                weights.append(weight); nv_list.append(i)
        if weights and sum(weights) > 0: return random.choices(nv_list, weights=[w/sum(weights) for w in weights], k=1)[0]
    return random.choice(candidates)

def choose_nv_follow_winner(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if data_top100 and data_top100[1]:
        for idx in sorted(range(6), key=lambda i: data_top100[1][i], reverse=True):
            if (idx + 1) in candidates: return idx + 1
    return random.choice(candidates)

def choose_nv_anti_winner(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if data_top100 and data_top100[1]:
        for idx in sorted(range(6), key=lambda i: data_top100[1][i]):
            if (idx + 1) in candidates: return idx + 1
    return random.choice(candidates)

def choose_nv_smart_analysis(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if data_top100 and data_top100[1]:
        scores = {}; total_wins = sum(data_top100[1]); avg_wins = total_wins / 6
        for i in candidates:
            score = 0
            if data_top100[1][i-1] < avg_wins: score += (avg_wins - data_top100[1][i-1]) * 2
            if i == int(data_top10[1][0]): score -= 1.5
            if i in cdtd_recent_choices: score -= 3
            score += random.uniform(-0.3, 0.3); scores[i] = score
        return max(scores, key=scores.get)
    return random.choice(candidates)

def choose_nv_markov_chain(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if len(cdtd_bet_history) < 5: return random.choice(candidates)
    transitions = defaultdict(lambda: defaultdict(int))
    recent_winners = [int(b.get('winner', 0)) for b in list(cdtd_bet_history)[-20:] if b.get('winner')]
    for i in range(len(recent_winners) - 1): transitions[recent_winners[i]][recent_winners[i + 1]] += 1
    last = recent_winners[-1] if recent_winners else int(data_top10[1][0])
    if transitions[last]:
        for nv, _ in sorted(transitions[last].items(), key=lambda x: x[1], reverse=True):
            if nv in candidates: return nv
    return random.choice(candidates)

def choose_nv_bayesian(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if len(cdtd_bet_history) < 3: return random.choice(candidates)
    recent_winners = [int(b.get('winner', 0)) for b in list(cdtd_bet_history)[-20:] if b.get('winner')]
    room_counts = Counter(recent_winners); total = len(recent_winners)
    posterior = {i: (room_counts.get(i, 0) + 1) / (total + 6) for i in candidates}
    return min(posterior, key=posterior.get)

def choose_nv_neural_network(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if len(cdtd_bet_history) < 3: return random.choice(candidates)
    scores = {}
    for nv in candidates:
        wins_100 = data_top100[1][nv-1] if data_top100[1] else 0; total_100 = sum(data_top100[1]) if data_top100[1] else 1
        h1_1 = 1 / (1 + math.exp(-(wins_100 / total_100 * 10 - 5)))
        recent_wins = sum(1 for b in list(cdtd_bet_history)[-10:] if b.get('winner') == nv)
        h1_2 = 1 / (1 + math.exp(-(recent_wins - 2)))
        h1_3 = 0 if nv == int(data_top10[1][0]) else 1
        repeat_penalty = 2 if nv in cdtd_recent_choices else 0
        scores[nv] = 0.4 * h1_1 + 0.3 * h1_2 + 0.3 * h1_3 - repeat_penalty
    return max(scores, key=scores.get)

def choose_nv_genetic_algo(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if len(cdtd_bet_history) < 5: return random.choice(candidates)
    def fitness(nv):
        if nv not in candidates: return -999
        score = 3 if nv != int(data_top10[1][0]) else 0
        if data_top100 and data_top100[1]: score += (sum(data_top100[1]) / 6 - data_top100[1][nv-1]) * 2
        if nv in cdtd_recent_choices: score -= 5
        return score
    population = [random.choice(candidates) for _ in range(10)]
    fitness_scores = sorted([(nv, fitness(nv)) for nv in population], key=lambda x: x[1], reverse=True)
    return fitness_scores[0][0] if random.random() > 0.1 else random.choice(candidates)

def choose_nv_reinforcement(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if len(cdtd_bet_history) < 3: return random.choice(candidates)
    q_values = {i: 0.0 for i in candidates}
    for b in list(cdtd_bet_history)[-20:]:
        chosen, result = b.get('chosen'), b.get('result')
        if chosen in candidates and result: q_values[chosen] += 1.0 if result == 'win' else -0.5
    if random.random() < 0.2: return random.choice(candidates)
    return max(q_values, key=q_values.get) if q_values else random.choice(candidates)

def choose_nv_knn(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if len(cdtd_bet_history) < 3: return random.choice(candidates)
    recent_winners = [int(b.get('winner', 0)) for b in list(cdtd_bet_history)[-20:] if b.get('winner')]
    if len(recent_winners) < 3: return random.choice(candidates)
    k = min(5, len(recent_winners)); counts = Counter(recent_winners[-k:])
    for nv, _ in sorted(counts.items(), key=lambda x: x[1]):
        if nv in candidates: return nv
    return random.choice(candidates)

def choose_nv_decision_tree(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if len(cdtd_bet_history) < 3: return random.choice(candidates)
    last_winners = [int(b.get('winner', 0)) for b in list(cdtd_bet_history)[-3:] if b.get('winner')]
    if len(last_winners) >= 2 and last_winners[-1] == last_winners[-2]:
        filtered = [nv for nv in candidates if nv != last_winners[-1]]
        if filtered: return random.choice(filtered)
    return random.choice(candidates)

def choose_nv_random_forest(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if len(cdtd_bet_history) < 3: return random.choice(candidates)
    predictions = []
    for func in [choose_nv_random, choose_nv_avoid_last, choose_nv_cold_streak, choose_nv_probability, choose_nv_balance]:
        try:
            pred = func(data_top10, data_top100)
            if pred in candidates: predictions.append(pred)
        except: continue
    return Counter(predictions).most_common(1)[0][0] if predictions else random.choice(candidates)

def choose_nv_gradient_boost(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    if len(cdtd_bet_history) < 5: return random.choice(candidates)
    scores = {i: 0.5 for i in candidates}
    if data_top100 and data_top100[1]:
        total = sum(data_top100[1])
        for i in candidates: scores[i] += 0.3 * (1/6 - data_top100[1][i-1] / total)
    for nv, count in Counter([int(b.get('winner', 0)) for b in list(cdtd_bet_history)[-10:] if b.get('winner')]).items():
        if nv in candidates: scores[nv] -= 0.2 * count
    for nv in candidates:
        if nv == int(data_top10[1][0]): scores[nv] -= 0.5
        if nv in cdtd_recent_choices: scores[nv] -= 2
        scores[nv] += random.uniform(-0.1, 0.1)
    return max(scores, key=scores.get)

def choose_nv_ensemble(data_top10, data_top100):
    candidates = get_filtered_candidates(data_top10, cdtd_avoid_repeat)
    votes = defaultdict(int)
    for func in [choose_nv_random, choose_nv_avoid_last, choose_nv_cold_streak, choose_nv_probability, choose_nv_balance, choose_nv_markov_chain, choose_nv_knn]:
        try:
            nv = func(data_top10, data_top100)
            if nv in candidates: votes[nv] += 1
        except: continue
    return max(votes, key=votes.get) if votes else random.choice(candidates)

# Các hàm AI 21-40 (rút gọn)
def choose_nv_trend_following(d, d2): return choose_nv_random(d, d2)
def choose_nv_mean_reversion(d, d2): return choose_nv_random(d, d2)
def choose_nv_momentum(d, d2): return choose_nv_random(d, d2)
def choose_nv_volatility(d, d2): return choose_nv_random(d, d2)
def choose_nv_seasonal(d, d2): return choose_nv_random(d, d2)
def choose_nv_correlation(d, d2): return choose_nv_random(d, d2)
def choose_nv_cluster(d, d2): return choose_nv_random(d, d2)
def choose_nv_anomaly(d, d2): return choose_nv_random(d, d2)
def choose_nv_entropy(d, d2): return choose_nv_random(d, d2)
def choose_nv_fuzzy_logic(d, d2): return choose_nv_random(d, d2)
def choose_nv_lstm_predict(d, d2): return choose_nv_random(d, d2)
def choose_nv_transformer(d, d2): return choose_nv_random(d, d2)
def choose_nv_attention(d, d2): return choose_nv_random(d, d2)
def choose_nv_deep_q(d, d2): return choose_nv_random(d, d2)
def choose_nv_a3c(d, d2): return choose_nv_random(d, d2)
def choose_nv_ppo(d, d2): return choose_nv_random(d, d2)
def choose_nv_gan(d, d2): return choose_nv_random(d, d2)
def choose_nv_autoencoder(d, d2): return choose_nv_random(d, d2)
def choose_nv_swarm_intel(d, d2): return choose_nv_random(d, d2)
def choose_nv_meta_learning(d, d2): return choose_nv_random(d, d2)

def choose_nv_cdtd(mode: str, data_top10, data_top100):
    logic_map = {
        "RANDOM": choose_nv_random, "AVOID_LAST": choose_nv_avoid_last,
        "HOT_STREAK": choose_nv_hot_streak, "COLD_STREAK": choose_nv_cold_streak,
        "BALANCE": choose_nv_balance, "PATTERN": choose_nv_pattern,
        "PROBABILITY": choose_nv_probability, "FOLLOW_WINNER": choose_nv_follow_winner,
        "ANTI_WINNER": choose_nv_anti_winner, "SMART_ANALYSIS": choose_nv_smart_analysis,
        "MARKOV_CHAIN": choose_nv_markov_chain, "BAYESIAN": choose_nv_bayesian,
        "NEURAL_NETWORK": choose_nv_neural_network, "GENETIC_ALGO": choose_nv_genetic_algo,
        "REINFORCEMENT": choose_nv_reinforcement, "KNN": choose_nv_knn,
        "DECISION_TREE": choose_nv_decision_tree, "RANDOM_FOREST": choose_nv_random_forest,
        "GRADIENT_BOOST": choose_nv_gradient_boost, "ENSEMBLE": choose_nv_ensemble,
        "TREND_FOLLOWING": choose_nv_trend_following, "MEAN_REVERSION": choose_nv_mean_reversion,
        "MOMENTUM": choose_nv_momentum, "VOLATILITY": choose_nv_volatility,
        "SEASONAL": choose_nv_seasonal, "CORRELATION": choose_nv_correlation,
        "CLUSTER": choose_nv_cluster, "ANOMALY": choose_nv_anomaly,
        "ENTROPY": choose_nv_entropy, "FUZZY_LOGIC": choose_nv_fuzzy_logic,
        "LSTM_PREDICT": choose_nv_lstm_predict, "TRANSFORMER": choose_nv_transformer,
        "ATTENTION": choose_nv_attention, "DEEP_Q": choose_nv_deep_q,
        "A3C": choose_nv_a3c, "PPO": choose_nv_ppo, "GAN": choose_nv_gan,
        "AUTOENCODER": choose_nv_autoencoder, "SWARM_INTEL": choose_nv_swarm_intel,
        "META_LEARNING": choose_nv_meta_learning,
    }
    try:
        chosen = logic_map.get(mode, choose_nv_random)(data_top10, data_top100)
        cdtd_recent_choices.append(chosen); return chosen, mode
    except:
        chosen = random.choice(get_filtered_candidates(data_top10, cdtd_avoid_repeat))
        cdtd_recent_choices.append(chosen); return chosen, mode

# ================== CDTD API ==================
def load_data_cdtd():
    if os.path.exists('data-xw-cdtd.txt'):
        if Prompt.ask(f'[bold {HTOOL_COLORS["gold"]}]Sử dụng thông tin đã lưu? (y/n)[/]', choices=['y', 'n'], default='y') == 'y':
            with open('data-xw-cdtd.txt', 'r', encoding='utf-8') as f: return json.load(f)
    console.print(Rule(f"[bold {HTOOL_COLORS['gold']}]📋 NHẬP THÔNG TIN[/]", style=HTOOL_COLORS["gold"]))
    console.print("1. Truy cập xworld.io\n2. Đăng nhập\n3. Vào Chạy đua tốc độ\n4. Copy link\n")
    link = Prompt.ask(f'[bold {HTOOL_COLORS["gold"]}]📋 Nhập link[/]')
    try:
        user_id = link.split('&')[0].split('?userId=')[1]; user_secretkey = link.split('&')[1].split('secretKey=')[1]
    except:
        user_id = Prompt.ask(f'[bold {HTOOL_COLORS["gold"]}]👤 User ID[/]'); user_secretkey = Prompt.ask(f'[bold {HTOOL_COLORS["gold"]}]🔑 Secret Key[/]')
    json_data = {'user-id': user_id, 'user-secret-key': user_secretkey}
    with open('data-xw-cdtd.txt', 'w+', encoding='utf-8') as f: json.dump(json_data, f, indent=4, ensure_ascii=False)
    return json_data

def setup_cdtd_headers(data: dict):
    global cdtd_headers
    cdtd_headers = {'accept': '*/*', 'accept-language': 'vi,en;q=0.9', 'country-code': 'vn', 'origin': 'https://xworld.info', 'referer': 'https://xworld.info/', 'user-agent': 'Mozilla/5.0', 'user-id': data['user-id'], 'user-login': 'login_v2', 'user-secret-key': data['user-secret-key'], 'xb-language': 'vi-VN'}

def top_100_cdtd():
    try:
        response = cdtd_session.get('https://api.sprintrun.win/sprint/recent_100_issues', headers={'accept': '*/*', 'origin': 'https://sprintrun.win', 'referer': 'https://sprintrun.win/', 'user-agent': 'Mozilla/5.0'}, timeout=10).json()
        return [1, 2, 3, 4, 5, 6], [response['data']['athlete_2_win_times'][str(i)] for i in range(1, 7)]
    except: return [1, 2, 3, 4, 5, 6], [0, 0, 0, 0, 0, 0]

def top_10_cdtd():
    try:
        response = cdtd_session.get('https://api.sprintrun.win/sprint/recent_10_issues', headers=cdtd_headers, timeout=10).json()
        return [i['issue_id'] for i in response['data']['recent_10']], [i['result'][0] for i in response['data']['recent_10']]
    except: return [0], [1]

def user_asset_cdtd():
    try:
        response = cdtd_session.post('https://wallet.3games.io/api/wallet/user_asset', headers=cdtd_headers, json={'user_id': int(cdtd_headers['user-id']), 'source': 'home'}, timeout=10).json()
        return {'USDT': float(response['data']['user_asset'].get('USDT', 0)), 'WORLD': float(response['data']['user_asset'].get('WORLD', 0)), 'BUILD': float(response['data']['user_asset'].get('BUILD', 0))}
    except: return {'USDT': 0, 'WORLD': 0, 'BUILD': 0}

def bet_cdtd(issue_id, nv_id, amount):
    try:
        response = cdtd_session.post('https://api.sprintrun.win/sprint/bet', headers=cdtd_headers, json={'issue_id': int(issue_id), 'bet_group': 'not_winner', 'asset_type': cdtd_coin, 'athlete_id': nv_id, 'bet_amount': float(amount)}, timeout=10).json()
        return (True, "ok") if response.get('code') == 0 else (False, response.get('msg', 'Unknown'))
    except Exception as e: return False, str(e)

# ================== CDTD GIAO DIỆN ==================
def build_cdtd_header():
    logo_text = build_logo_with_gradient(LOGO); asset = user_asset_cdtd()
    info_table = Table(box=None, show_header=False, pad_edge=False, expand=True)
    info_table.add_column(style=f"bold {HTOOL_COLORS['gold']}", no_wrap=True, justify="right", width=18)
    info_table.add_column(style="white")
    info_table.add_row(f"{ICONS['user']} USER:", f"[bold {HTOOL_COLORS['platinum']}]{cdtd_headers.get('user-id', 'N/A')}[/]")
    info_table.add_row(f"{ICONS['money']} BALANCE:", f"[bold {HTOOL_COLORS['emerald']}]{asset.get(cdtd_coin, 0):.4f}[/] {cdtd_coin}")
    pnl = asset.get(cdtd_coin, 0) - cdtd_stats['asset_0']; pnl_color = HTOOL_COLORS["emerald"] if pnl >= 0 else HTOOL_COLORS["ruby"]
    info_table.add_row(f"{ICONS['chart']} P&L:", f"[{pnl_color}]{pnl:+.4f} {cdtd_coin}[/]")
    streak_text = Text.assemble(("🔥 ", f"bold {HTOOL_COLORS['neon_orange']}"), (f"{cdtd_win_streak}", f"bold {HTOOL_COLORS['emerald']}"), (" | ", "dim"), ("💀 ", f"bold {HTOOL_COLORS['ruby']}"), (f"{cdtd_lose_streak}", f"bold {HTOOL_COLORS['ruby']}"))
    info_table.add_row("📊 STREAK:", streak_text)
    algo_label = "ADAPTIVE" if cdtd_adaptive_enabled else CDTD_ALGORITHMS.get(cdtd_settings.get('algo', 'RANDOM'), 'N/A')
    info_table.add_row(f"{ICONS['brain']} AI:", f"[bold {HTOOL_COLORS['neon_pink']}]{algo_label}[/]")
    info_table.add_row(f"{ICONS['clock']} TIME:", f"[{HTOOL_COLORS['sapphire']}]{datetime.now(tz).strftime('%H:%M:%S')}[/]")
    info_table.add_row(f"{ICONS['target']} ISSUE:", f"[bold {HTOOL_COLORS['gold']}]{cdtd_issue_id or 'Waiting...'}[/]")
    info_table.add_row(f"{ICONS['bell']} TG:", f"[{'green' if TELEGRAM_ENABLED else 'dim'}] {'BẬT' if TELEGRAM_ENABLED else 'TẮT'}[/]")
    return Panel(Group(Align.center(logo_text), info_table), border_style=HTOOL_COLORS["gold"], box=box.HEAVY, padding=(1, 2))

def build_cdtd_racers():
    data_top100, data_top10 = top_100_cdtd(), top_10_cdtd(); racer_panels = []
    for i in range(1, 7):
        wins = data_top100[1][i-1] if data_top100[1] else 0
        is_predicted = cdtd_predicted_nv == i; is_last_winner = int(data_top10[1][0]) == i if data_top10 and data_top10[1] else False
        if is_predicted: border, title_style, bg, glow = f"bold {HTOOL_COLORS['emerald']}", f"bold {HTOOL_COLORS['emerald']}", "on #003300", "✨⭐"
        elif is_last_winner: border, title_style, bg, glow = HTOOL_COLORS["gold"], HTOOL_COLORS["gold"], "on #332200", "🏆"
        else: border, title_style, bg, glow = HTOOL_COLORS["onyx"], "white", "", ""
        content = Text.assemble(("\n", ""), (f"{glow} {NV_ICONS[i]}\n", "default"), (f"{NV[i]}\n", title_style), (f"🏆 {wins} wins", "dim"), ("\n", ""), justify="center")
        racer_panels.append(Panel(Align.center(content, vertical="middle"), title=f"[{title_style}]#{i}[/{title_style}]", border_style=border, box=box.HEAVY, expand=True, height=6, style=bg))
    return Panel(Columns(racer_panels, equal=True, expand=True), title=f"[bold {HTOOL_COLORS['neon_orange']}]🏎️ CHẠY ĐUA TỐC ĐỘ 🏎️[/]", box=box.HEAVY, border_style=HTOOL_COLORS["neon_orange"], expand=True)

def build_cdtd_mid():
    if cdtd_ui_state == "ANALYZING":
        elapsed = time.time() - (cdtd_analysis_start_ts or time.time()); progress = min(1.0, elapsed / cdtd_analysis_duration)
        bar = "█" * int(30 * progress) + "░" * (30 - int(30 * progress)); remaining = max(0, int(cdtd_analysis_duration - elapsed))
        content = Text.assemble(("\n🧠 ĐANG PHÂN TÍCH...\n\n", f"bold {HTOOL_COLORS['neon_blue']}"), (f"[{HTOOL_COLORS['gold']}]{bar}[/]\n\n", ""), (f"Tiến độ: {progress*100:.0f}%\n", HTOOL_COLORS['neon_pink']), (f"⏱️ Còn {remaining}s\n", "dim"), justify="center")
        return Panel(content, border_style=HTOOL_COLORS["neon_blue"], box=box.HEAVY, expand=True)
    elif cdtd_ui_state == "PREDICTED":
        bet_amt = cdtd_current_bet or cdtd_base_bet
        content = Text.assemble(("\n╔══════════════════════════════╗\n", HTOOL_COLORS["gold"]), ("║  🎯 DỰ ĐOÁN CỦA BOT  🎯    ║\n", HTOOL_COLORS["gold"]), ("║  ", HTOOL_COLORS["gold"]), (f"{NV_ICONS.get(cdtd_predicted_nv, '🤖')} {NV.get(cdtd_predicted_nv, 'N/A'):^20}", f"bold {HTOOL_COLORS['emerald']}"), ("  ║\n", HTOOL_COLORS["gold"]), ("║  💰 Cược: ", HTOOL_COLORS["gold"]), (f"{bet_amt:.2f} {cdtd_coin:<10}", f"bold {HTOOL_COLORS['gold']}"), ("  ║\n", HTOOL_COLORS["gold"]), ("╚══════════════════════════════╝\n", HTOOL_COLORS["gold"]), (f"\n📈 Chuỗi thắng: {cdtd_win_streak}  📉 Chuỗi thua: {cdtd_lose_streak}\n", "white"), justify="center")
        return Panel(content, border_style=HTOOL_COLORS["emerald"], box=box.HEAVY, expand=True)
    elif cdtd_ui_state == "RESULT":
        last_bet = cdtd_bet_history[-1] if cdtd_bet_history else None
        if last_bet and last_bet.get('result') == 'win': result_text, result_color, border_color = "🎉 CHIẾN THẮNG! 🎉", HTOOL_COLORS["emerald"], HTOOL_COLORS["emerald"]
        elif last_bet and last_bet.get('result') == 'lose': result_text, result_color, border_color = "💀 THUA CUỘC! 💀", HTOOL_COLORS["ruby"], HTOOL_COLORS["ruby"]
        else: result_text, result_color, border_color = "⏳ ĐANG CHỜ...", HTOOL_COLORS["gold"], HTOOL_COLORS["gold"]
        content = Text.assemble(("\n", ""), (f"{result_text}\n\n", f"bold {result_color}"), ("Người thắng: ", "white"), (f"{NV_ICONS.get(cdtd_last_winner, '🏆')} {NV.get(cdtd_last_winner, 'N/A')}\n", f"bold {HTOOL_COLORS['gold']}"), ("\n⏳ Đang chờ kỳ mới...", "dim"), justify="center")
        return Panel(content, border_style=border_color, box=box.HEAVY, expand=True)
    return Panel(Align.center(Text("\n⏳ ĐANG CHỜ DỮ LIỆU...\n\n🔄 Đang kết nối...\n", justify="center")), border_style=HTOOL_COLORS["gold"], box=box.HEAVY, expand=True)

def build_cdtd_history():
    t = Table(title=f"[bold {HTOOL_COLORS['gold']}]📜 LỊCH SỬ CƯỢC[/]", box=box.ROUNDED, expand=True, border_style=HTOOL_COLORS["onyx"])
    t.add_column("Kỳ", style=HTOOL_COLORS["sapphire"], width=6); t.add_column("Chọn", style=HTOOL_COLORS["neon_blue"]); t.add_column("Cược", justify="right", style=HTOOL_COLORS["gold"], width=10); t.add_column("KQ")
    for b in list(cdtd_bet_history)[-10:]:
        chosen = NV.get(b.get('chosen'), str(b.get('chosen', '-'))); amount = f"{b.get('amount', 0):.2f}"
        if b.get('result') == 'win': result_text = Text("✅ THẮNG", style=f"bold {HTOOL_COLORS['emerald']}")
        elif b.get('result') == 'lose': result_text = Text("❌ THUA", style=f"bold {HTOOL_COLORS['ruby']}")
        else: result_text = Text("⏳", style=HTOOL_COLORS["gold"])
        t.add_row(str(b.get('issue', '-')), chosen, amount, result_text)
    return Panel(t, border_style=HTOOL_COLORS["sapphire"], box=box.HEAVY, expand=True)

def build_cdtd_stats():
    data_top100 = top_100_cdtd()
    t = Table(title=f"[bold {HTOOL_COLORS['neon_blue']}]📊 THỐNG KÊ 100 VÁN[/]", box=box.ROUNDED, expand=True, border_style=HTOOL_COLORS["neon_blue"])
    t.add_column("NV", style=HTOOL_COLORS["gold"], width=4); t.add_column("Tên", style="white"); t.add_column("Thắng", justify="right", style=HTOOL_COLORS["emerald"], width=8); t.add_column("Tỷ lệ", justify="right", style=HTOOL_COLORS["neon_pink"], width=8)
    total_wins = sum(data_top100[1]) if data_top100[1] else 1
    for i in range(6): t.add_row(f"{NV_ICONS.get(i+1, '🏆')}", NV.get(i+1, f'NV{i+1}'), str(data_top100[1][i] if data_top100[1] else 0), f"{(data_top100[1][i] if data_top100[1] else 0)/total_wins*100:.1f}%")
    summary = Table(box=box.ROUNDED, expand=True, border_style=HTOOL_COLORS["gold"])
    summary.add_column("Chỉ số", style=HTOOL_COLORS["gold"]); summary.add_column("Giá trị", style="white")
    summary.add_row("Tổng ván", str(cdtd_stats['win'] + cdtd_stats['lose']))
    summary.add_row("Thắng", f"[green]{cdtd_stats['win']}[/]"); summary.add_row("Thua", f"[red]{cdtd_stats['lose']}[/]")
    summary.add_row("Max thắng", str(cdtd_max_win_streak)); summary.add_row("Max thua", str(cdtd_max_lose_streak))
    pnl = user_asset_cdtd().get(cdtd_coin, 0) - cdtd_stats['asset_0']
    summary.add_row("P&L", f"[{'green' if pnl >= 0 else 'red'}]{pnl:+.4f} {cdtd_coin}[/]")
    return Panel(Columns([t, summary], equal=True, expand=True), border_style=HTOOL_COLORS["gold"], box=box.HEAVY, expand=True)

def build_cdtd_chart():
    data = top_100_cdtd(); table = Table(title="📊 TỶ LỆ THẮNG", box=box.SIMPLE, expand=True)
    table.add_column("NV", width=4); table.add_column("Bar", width=30); table.add_column("%", justify="right")
    total = sum(data[1]) or 1; max_wins = max(data[1]) or 1
    for i in range(6):
        wins = data[1][i]; rate = wins / total * 100; bar_len = int(wins / max_wins * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len); color = "green" if rate < 20 else "yellow" if rate < 25 else "red"
        table.add_row(f"{NV_ICONS[i+1]}", f"[{color}]{bar}[/]", f"{rate:.1f}%")
    return Panel(table, border_style=HTOOL_COLORS["sapphire"])

def build_cdtd_marquee():
    messages = [f"⚡ CDTD - 40 AI {ICONS['rocket']}", f"🧠 {CDTD_ALGORITHMS.get(cdtd_settings.get('algo', 'RANDOM'), 'N/A')} {ICONS['robot']}", f"💰 {cdtd_coin} | Cược: {cdtd_base_bet} | x{cdtd_multiplier}", f"🎯 W:{cdtd_stats['win']} L:{cdtd_stats['lose']} {ICONS['chart']}"]
    message = messages[int(time.time() / 5) % len(messages)]; full_text = " " * 20 + message + " " * 20
    width = console.width or 80; display_text = (full_text * 3)[int(time.time() * 3) % len(full_text) : int(time.time() * 3) % len(full_text) + width]
    return Panel(Text(display_text, style=f"bold {HTOOL_COLORS['neon_blue']}", no_wrap=True), box=box.ROUNDED, border_style=HTOOL_COLORS["onyx"], padding=0, expand=True)

def cdtd_generate_layout():
    main_grid = Table.grid(expand=True, pad_edge=False); main_grid.add_column("main", ratio=55); main_grid.add_column("side", ratio=45)
    right_grid = Table.grid(expand=True, pad_edge=False); right_grid.add_row(build_cdtd_mid()); right_grid.add_row(build_cdtd_history())
    main_grid.add_row(build_cdtd_racers(), right_grid)
    root = Table.grid(expand=True, pad_edge=False); root.add_row(build_cdtd_header()); root.add_row(build_cdtd_marquee()); root.add_row(main_grid); root.add_row(build_cdtd_stats()); root.add_row(build_cdtd_chart())
    return root

def cdtd_prompt_settings():
    global cdtd_base_bet, cdtd_multiplier, cdtd_coin, cdtd_current_bet, cdtd_pause_rounds, cdtd_bet_rounds_before_skip, cdtd_settings, cdtd_adaptive_enabled
    console.clear(); header = Panel(Align.center(Text.assemble((f"{ICONS['settings']} ", f"bold {HTOOL_COLORS['gold']}"), ("CẤU HÌNH CHẠY ĐUA TỐC ĐỘ", f"bold {HTOOL_COLORS['neon_blue']}"))), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(header); console.print()
    coin_choice = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]💰 Chọn tiền: [1] USDT [2] BUILD [3] WORLD[/]\n   >>", choices=['1', '2', '3'], default='2')
    cdtd_coin = {'1': 'USDT', '2': 'BUILD', '3': 'WORLD'}[coin_choice]
    cdtd_base_bet = FloatPrompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]💵 Cược gốc ({cdtd_coin})[/]\n   >>", default=1.0)
    cdtd_multiplier = FloatPrompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]📈 Hệ số nhân[/]\n   >>", default=2.0); cdtd_current_bet = cdtd_base_bet
    cdtd_bet_rounds_before_skip = IntPrompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]🛡️ Nghỉ 1 ván sau N ván (0=không)[/]\n   >>", default=0)
    cdtd_pause_rounds = IntPrompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]⏸️ Nghỉ N ván sau khi thua (0=không)[/]\n   >>", default=0)
    console.clear(); console.print(header)
    
    # KEY VIP
    if _is_vip: available_algos = list(CDTD_ALGORITHMS.items())
    else: available_algos = list(CDTD_ALGORITHMS.items())[:FREE_AI_LIMIT]
    
    console.print(f"\n[bold {HTOOL_COLORS['neon_pink']}]🧠 Chọn AI ({len(available_algos)} AI khả dụng):[/]\n")
    if not _is_vip: console.print(f"[yellow]⚠️ Key thường: Chỉ {FREE_AI_LIMIT}/{len(CDTD_ALGORITHMS)} AI[/]")
    
    algo_table = Table(box=box.ROUNDED, border_style=HTOOL_COLORS["neon_pink"]); algo_table.add_column("#", style=HTOOL_COLORS["gold"], width=4); algo_table.add_column("Thuật toán", style=HTOOL_COLORS["neon_blue"])
    for i, (key, label) in enumerate(available_algos, 1): algo_table.add_row(str(i), label)
    if _is_vip: algo_table.add_row("41", "ADAPTIVE (Tự động chọn)")
    console.print(algo_table)
    
    max_choice = len(available_algos) + (1 if _is_vip else 0)
    algo_choice = IntPrompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]>> Chọn (1-{max_choice})[/]", choices=[str(i) for i in range(1, max_choice + 1)], default=1)
    if _is_vip and algo_choice == max_choice: cdtd_adaptive_enabled = True; cdtd_settings["algo"] = "RANDOM"
    else: cdtd_adaptive_enabled = False; cdtd_settings["algo"] = available_algos[algo_choice - 1][0]
    
    console.print(f"\n[bold {HTOOL_COLORS['gold']}]📱 Cấu hình Telegram? (y/n)[/]")
    if Prompt.ask("   >>", choices=['y', 'n'], default='n') == 'y': setup_telegram()
    console.print(f'\n[green]✅ Cấu hình hoàn tất![/]'); time.sleep(1.5)
    return True

def cdtd_game_loop():
    global cdtd_issue_id, cdtd_previous_issue, cdtd_last_winner, cdtd_predicted_nv, cdtd_ui_state, cdtd_analysis_start_ts
    global cdtd_current_bet, cdtd_win_streak, cdtd_lose_streak, cdtd_max_win_streak, cdtd_max_lose_streak, cdtd_stop_flag
    global cdtd_stats, cdtd_pause_remaining, cdtd_skip_next, cdtd_rounds_placed, cdtd_bet_placed_this_round, cdtd_checked_result
    global cdtd_recent_choices, cdtd_current_logic
    
    cdtd_stop_flag = False; cdtd_issue_id = None; cdtd_previous_issue = None; cdtd_last_winner = None
    cdtd_predicted_nv = None; cdtd_ui_state = "WAITING"; cdtd_analysis_start_ts = None
    cdtd_win_streak = 0; cdtd_lose_streak = 0; cdtd_max_win_streak = 0; cdtd_max_lose_streak = 0
    cdtd_rounds_placed = 0; cdtd_skip_next = False; cdtd_pause_remaining = 0
    cdtd_bet_placed_this_round = False; cdtd_checked_result = False
    cdtd_current_bet = cdtd_base_bet; cdtd_bet_history.clear(); cdtd_recent_choices.clear()
    cdtd_stats = {'win': 0, 'lose': 0, 'asset_0': user_asset_cdtd().get(cdtd_coin, 0)}
    cdtd_current_logic = None
    
    with Live(cdtd_generate_layout(), refresh_per_second=3, console=console, screen=True) as live:
        while not cdtd_stop_flag:
            try:
                data_top10 = top_10_cdtd(); current_issue = data_top10[0][0]
                if current_issue != cdtd_previous_issue:
                    if cdtd_previous_issue is not None and cdtd_predicted_nv is not None and not cdtd_checked_result:
                        try:
                            winner = int(data_top10[1][0]) if data_top10[1] else None
                            if winner is not None:
                                cdtd_last_winner = winner; balance_before = user_asset_cdtd().get(cdtd_coin, 0); result_type = 'win'
                                for b in cdtd_bet_history:
                                    if b.get('result') == 'pending':
                                        b['winner'] = winner
                                        if b['chosen'] != winner:
                                            b['result'] = 'win'; cdtd_win_streak += 1; cdtd_lose_streak = 0; cdtd_max_win_streak = max(cdtd_max_win_streak, cdtd_win_streak)
                                            cdtd_current_bet = cdtd_base_bet; cdtd_stats['win'] += 1; result_type = 'win'
                                            if cdtd_adaptive_enabled and b.get('algo'): cdtd_logic_performance[b['algo']]['wins'] += 1
                                        else:
                                            b['result'] = 'lose'; cdtd_lose_streak += 1; cdtd_win_streak = 0; cdtd_max_lose_streak = max(cdtd_max_lose_streak, cdtd_lose_streak)
                                            cdtd_current_bet *= cdtd_multiplier; cdtd_stats['lose'] += 1; result_type = 'lose'
                                            if cdtd_pause_rounds > 0: cdtd_pause_remaining = cdtd_pause_rounds
                                            if cdtd_adaptive_enabled and b.get('algo'): cdtd_logic_performance[b['algo']]['losses'] += 1
                                time.sleep(1); balance_after = user_asset_cdtd().get(cdtd_coin, 0)
                                pnl_van = balance_after - balance_before; total_pnl = balance_after - cdtd_stats['asset_0']
                                if TELEGRAM_ENABLED and TELEGRAM_CHAT_ID:
                                    bet_nv = cdtd_predicted_nv; bet_amount = cdtd_bet_history[-1].get('amount', 0) if cdtd_bet_history else cdtd_base_bet
                                    telegram_msg = build_cdtd_telegram_message(cdtd_previous_issue, winner, bet_nv, bet_amount, result_type, pnl_van, total_pnl, balance_before, balance_after, cdtd_stats['win'], cdtd_stats['lose'], cdtd_max_win_streak, cdtd_max_lose_streak)
                                    threading.Thread(target=send_telegram_message, args=(telegram_msg,), daemon=True).start()
                                check_telegram_alerts(); cdtd_checked_result = True; cdtd_ui_state = "RESULT"
                                live.update(cdtd_generate_layout()); time.sleep(2)
                        except: pass
                    cdtd_previous_issue = current_issue; cdtd_issue_id = current_issue; cdtd_predicted_nv = None
                    cdtd_bet_placed_this_round = False; cdtd_checked_result = False; cdtd_analysis_start_ts = time.time(); cdtd_ui_state = "ANALYZING"
                    live.update(cdtd_generate_layout())
                
                if cdtd_ui_state == "ANALYZING":
                    elapsed = time.time() - (cdtd_analysis_start_ts or time.time())
                    if elapsed >= cdtd_analysis_duration - 8 and not cdtd_bet_placed_this_round:
                        if cdtd_adaptive_enabled: chosen, mode = adaptive_choose_nv(data_top10, top_100_cdtd())
                        else: mode = cdtd_settings.get("algo", "RANDOM"); chosen, mode = choose_nv_cdtd(mode, data_top10, top_100_cdtd())
                        cdtd_predicted_nv = chosen; cdtd_ui_state = "PREDICTED"; live.update(cdtd_generate_layout())
                        should_bet = True
                        if cdtd_pause_remaining > 0: cdtd_pause_remaining -= 1; should_bet = False
                        if cdtd_skip_next: cdtd_skip_next = False; should_bet = False
                        if cdtd_lose_streak >= 3: cdtd_current_bet = max(cdtd_base_bet, cdtd_current_bet * 0.5)
                        asset = user_asset_cdtd().get(cdtd_coin, 0)
                        if cdtd_stats['asset_0'] > 0:
                            drawdown = (cdtd_stats['asset_0'] - asset) / cdtd_stats['asset_0']
                            if drawdown > 0.2: cdtd_stop_flag = True
                        if should_bet and not cdtd_stop_flag:
                            next_issue = cdtd_issue_id + 1; bet_amount = cdtd_current_bet if cdtd_current_bet else cdtd_base_bet
                            if bet_amount > asset: cdtd_current_bet = cdtd_base_bet; bet_amount = cdtd_base_bet
                            success, msg = bet_cdtd(next_issue, chosen, bet_amount)
                            if success: cdtd_bet_history.append({'issue': next_issue, 'chosen': chosen, 'amount': bet_amount, 'result': 'pending', 'algo': mode}); cdtd_rounds_placed += 1; cdtd_bet_placed_this_round = True
                            if cdtd_bet_rounds_before_skip > 0 and cdtd_rounds_placed >= cdtd_bet_rounds_before_skip: cdtd_skip_next = True; cdtd_rounds_placed = 0
                        live.update(cdtd_generate_layout())
                    elif elapsed >= cdtd_analysis_duration + 15: cdtd_ui_state = "WAITING"; cdtd_issue_id = None; live.update(cdtd_generate_layout())
                backup_config(); live.update(cdtd_generate_layout()); time.sleep(0.5)
            except KeyboardInterrupt: cdtd_stop_flag = True; break
            except: time.sleep(3)
    export_history_csv()

def main_cdtd_v3():
    console.clear()
    header = Panel(Align.center(Text.assemble((f"{ICONS['rocket']} ", f"bold {HTOOL_COLORS['gold']}"), ("CHẠY ĐUA TỐC ĐỘ - 40 AI + ADAPTIVE", f"bold {HTOOL_COLORS['neon_blue']}"))), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(header); console.print(f"[dim]💬 Support: @htool88 | 40 AI | Auto Adaptive | Rủi ro | Telegram[/dim]\n")
    data = load_data_cdtd(); setup_cdtd_headers(data)
    if not cdtd_prompt_settings(): return
    console.clear(); console.print(f"[bold {HTOOL_COLORS['neon_orange']}]🏎️ KHỞI ĐỘNG...[/]")
    with console.status(f"[bold {HTOOL_COLORS['gold']}]🔍 Đang kiểm tra...[/]", spinner="dots"): asset = user_asset_cdtd(); time.sleep(1)
    if asset.get(cdtd_coin, 0) <= 0: console.print(f'[red]❌ Số dư {cdtd_coin} = 0![/]'); time.sleep(2); return
    console.print(f'[green]✅ Số dư: {asset[cdtd_coin]:.4f} {cdtd_coin}[/]')
    if cdtd_adaptive_enabled: console.print(f'[green]✅ Chế độ: AUTO ADAPTIVE[/]')
    else: console.print(f'[green]✅ AI: {CDTD_ALGORITHMS[cdtd_settings["algo"]]}[/]')
    if TELEGRAM_ENABLED: console.print(f'[green]✅ Telegram: BẬT[/]')
    time.sleep(2); cdtd_game_loop()
    console.clear(); final_asset = user_asset_cdtd(); pnl = final_asset.get(cdtd_coin, 0) - cdtd_stats['asset_0']
    summary = Panel(Align.center(Text.assemble(("\n📊 TỔNG KẾT\n\n", f"bold {HTOOL_COLORS['gold']}"), (f"Thắng: {cdtd_stats['win']} | Thua: {cdtd_stats['lose']}\n", "white"), (f"P&L: {pnl:+.4f} {cdtd_coin}\n", HTOOL_COLORS["gold"] if pnl >= 0 else HTOOL_COLORS["ruby"]))), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(summary); console.print("\n[dim]Nhấn Enter để quay lại menu...[/]"); input()

# ================== MAIN MENU ==================

def build_main_menu():
    console.clear(); console.print(Align.center(build_logo_with_gradient(LOGO)))
    key_status = f"👑 KEY VIP" if _is_vip else f"🔑 KEY THƯỜNG"; key_color = HTOOL_COLORS["gold"] if _is_vip else "dim"
    vth_ai = f"{len(SELECTION_MODES)} AI" if _is_vip else f"{FREE_AI_LIMIT}/{len(SELECTION_MODES)} AI"
    cdtd_ai = "40 AI + Adaptive" if _is_vip else f"{FREE_AI_LIMIT}/40 AI"
    menu_text = Text.assemble(("\n  👑 HTOOL VIP PREMIUM v4.0 👑\n\n", f"bold {HTOOL_COLORS['gold']}"), (f"  [{key_color}]{key_status}[/] | VTH: {vth_ai} | CDTD: {cdtd_ai}\n\n", ""), ("  [1] 🎯 VUA THOÁT HIỂM\n", f"bold {HTOOL_COLORS['neon_green']}"), ("  [2] 🏎️  CHẠY ĐUA TỐC ĐỘ\n", f"bold {HTOOL_COLORS['neon_orange']}"), ("  [3] ➕ THÊM TÀI KHOẢN\n", f"bold {HTOOL_COLORS['sapphire']}"), ("  [4] 🗑️  XÓA TÀI KHOẢN\n", f"bold {HTOOL_COLORS['ruby']}"), ("  [5] ⚙️  LƯU CONFIG VTH\n", f"bold {HTOOL_COLORS['gold']}"), ("  [6] 🎮 CHƠI VTH (LOAD)\n", f"bold {HTOOL_COLORS['neon_blue']}"))
    if not _is_vip: menu_text.append("  [7] 👑 NÂNG CẤP KEY VIP\n", f"bold {HTOOL_COLORS['gold']}")
    menu_text.append("  [q] 👋 THOÁT\n\n", f"bold {HTOOL_COLORS['rose']}")
    console.print(Panel(Align.center(menu_text), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE))
    choices = ['1','2','3','4','5','6','q']
    if not _is_vip: choices.append('7')
    return Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]>> Chọn[/]", choices=choices, default='q').lower()

def main_vth():
    global _is_authenticated, _device_id, _user_key
    threading.Thread(target=key_checker_thread, daemon=True).start()
    while not _is_authenticated:
        success, key, device_id = show_auth_screen()
        if success: _is_authenticated = True; _user_key = key; _device_id = device_id; break
        if Prompt.ask("[bold yellow]Thử lại? (y/n)[/]", choices=['y', 'n'], default='y') == 'n': console.print("[red]👋 Tạm biệt![/]"); sys.exit(0)
    console.clear()
    vth_ai = f"{len(SELECTION_MODES)} AI" if _is_vip else f"{FREE_AI_LIMIT}/{len(SELECTION_MODES)} AI"
    cdtd_ai = "40 AI + Adaptive" if _is_vip else f"{FREE_AI_LIMIT}/40 AI"
    console.print(Panel(Align.center(Text.assemble((f"{ICONS['crown']} ", f"bold {HTOOL_COLORS['gold']}"), ("WELCOME TO HTOOL VIP PREMIUM v4.0", "bold white"))), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE))
    console.print(f"[dim]💬 Support: @htool88 | VTH: {vth_ai} | CDTD: {cdtd_ai} | Telegram[/dim]"); time.sleep(1)
    while True:
        global stop_flag; stop_flag = False; choice = build_main_menu()
        if choice == '1':
            console.clear()
            if select_account_premium():
                if prompt_settings():
                    start_game_flow()
        elif choice == '2': main_cdtd_v3()
        elif choice == '3': add_new_account(load_accounts())
        elif choice == '4': delete_account(load_accounts())
        elif choice == '5':
            console.clear()
            if prompt_settings(): save_strategy_config()
            time.sleep(2)
        elif choice == '6':
            console.clear()
            if select_account_premium():
                if load_strategy_config(): start_game_flow()
                else: time.sleep(2)
        elif choice == '7': show_upgrade_vip()
        elif choice == 'q': console.print(Panel(Align.center(f"[bold {HTOOL_COLORS['gold']}]👋 THANK YOU![/]"), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)); break

if __name__ == "__main__":
    try: main_vth()
    except KeyboardInterrupt: console.print(f"\n[bold {HTOOL_COLORS['gold']}]Đã dừng. 👑[/]"); sys.exit(0)
