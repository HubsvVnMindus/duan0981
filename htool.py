import urllib.request
import os
import sys
import time
import random

# Hỗ trợ ANSI trên Windows
if os.name == 'nt':
    os.system('')

# Bảng màu ANSI
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BLINK = "\033[5m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BRIGHT_RED = "\033[1;91m"
    BRIGHT_GREEN = "\033[1;92m"
    BRIGHT_YELLOW = "\033[1;93m"
    BRIGHT_CYAN = "\033[1;96m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"

def clear_screen():
    """Xóa màn hình console"""
    os.system('cls' if os.name == 'nt' else 'clear')

def type_writer(text, delay=0.03, color=Colors.WHITE):
    """Hiệu ứng gõ máy đánh chữ"""
    for char in text:
        sys.stdout.write(color + char + Colors.RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def loading_animation(message, duration=2):
    """Hiệu ứng loading với spinner"""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end_time = time.time() + duration
    while time.time() < end_time:
        for char in chars:
            sys.stdout.write(f"\r{Colors.CYAN}{char} {message}{Colors.RESET}")
            sys.stdout.flush()
            time.sleep(0.05)
    print()

def blink_text(text, color=Colors.BRIGHT_RED, duration=3):
    """Text nhấp nháy"""
    end_time = time.time() + duration
    while time.time() < end_time:
        sys.stdout.write(f"\r{color}{Colors.BOLD}{Colors.BLINK}{text}{Colors.RESET}")
        sys.stdout.flush()
        time.sleep(0.5)
        sys.stdout.write(f"\r{' ' * len(text)}")
        sys.stdout.flush()
        time.sleep(0.3)
    print(f"\r{color}{Colors.BOLD}{text}{Colors.RESET}")

def draw_warning_box():
    """Vẽ hộp cảnh báo đẹp"""
    box = f"""
{Colors.BRIGHT_RED}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║                                                                  ║
║                    {Colors.BRIGHT_YELLOW}⚠️  THÔNG BÁO QUAN TRỌNG  ⚠️{Colors.BRIGHT_RED}                    ║
║                                                                  ║
║           {Colors.WHITE}🛑 TOOL V5 ĐÃ HẾT HẠN SỬ DỤNG 🛑{Colors.BRIGHT_RED}                     ║
║                                                                  ║
║        {Colors.YELLOW}Phiên bản V5 không còn được hỗ trợ nữa{Colors.BRIGHT_RED}                   ║
║        {Colors.YELLOW}Vui lòng chờ bản cập nhật V5 mới nhất{Colors.BRIGHT_RED}                  ║
║                                                                  ║
║              {Colors.BRIGHT_GREEN}🔄 ĐANG UPDATE V5... 🔄{Colors.BRIGHT_RED}                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
    """
    print(box)

def draw_support_box():
    """Vẽ hộp thông tin hỗ trợ"""
    zalo_link = "https://zalo.me/g/e6bb2ppq4nofewqbfhrk"
    
    box = f"""
{Colors.BRIGHT_CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║                                                                  ║
║               {Colors.BRIGHT_YELLOW}💬 CẦN HỖ TRỢ TỪ ADMIN? 💬{Colors.BRIGHT_CYAN}                       ║
║                                                                  ║
║      {Colors.WHITE}Tham gia nhóm Zalo để được Admin hỗ trợ trực tiếp:{Colors.BRIGHT_CYAN}      ║
║                                                                  ║
║      {Colors.BRIGHT_GREEN}{Colors.BOLD}🔗 {zalo_link} 🔗{Colors.RESET}     {Colors.BRIGHT_CYAN}║
║                                                                  ║
║      {Colors.YELLOW}📱 Quét QR hoặc click link để tham gia ngay{Colors.BRIGHT_CYAN}            ║
║      {Colors.YELLOW}👨‍💻 Admin sẽ hỗ trợ bạn trong thời gian sớm nhất{Colors.BRIGHT_CYAN}       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
    """
    print(box)

def progress_bar_update(message="UPDATING TO V4", duration=5):
    """Thanh tiến trình cập nhật"""
    print(f"\n{Colors.CYAN}[*] {Colors.WHITE}{message}...{Colors.RESET}\n")
    
    colors = [Colors.BRIGHT_RED, Colors.BRIGHT_YELLOW, Colors.BRIGHT_GREEN, 
              Colors.BRIGHT_CYAN, Colors.MAGENTA]
    
    for i in range(101):
        bar_length = 40
        filled = i * bar_length // 100
        bar = '█' * filled + '▒' * (bar_length - filled)
        
        # Gradient color effect
        color = colors[i % len(colors)]
        
        # Thêm biểu tượng trạng thái
        if i < 30:
            status = "📥 DOWNLOADING"
        elif i < 60:
            status = "🔧 INSTALLING"
        elif i < 90:
            status = "⚙️ CONFIGURING"
        else:
            status = "✨ FINALIZING"
        
        sys.stdout.write(f"\r{color}[{Colors.BOLD}{bar}{color}] {i}% {status}{Colors.RESET}   ")
        sys.stdout.flush()
        time.sleep(duration / 100)
    
    print("\n")

def sparkle_message(text, duration=3):
    """Message lấp lánh"""
    sparkles = ["✨", "⭐", "💫", "🌟", "⚡", "🔥", "💎", "🎯", "🚀", "💡"]
    end_time = time.time() + duration
    while time.time() < end_time:
        sparkle = random.choice(sparkles)
        sys.stdout.write(f"\r{Colors.BRIGHT_YELLOW}{sparkle} {text} {sparkle}{Colors.RESET}")
        sys.stdout.flush()
        time.sleep(0.2)
    print()

def show_info_section():
    """Hiển thị thông tin chi tiết"""
    info = f"""
{Colors.CYAN}┌────────────────────────────────────────────────────────────────┐
│ {Colors.WHITE}{Colors.BOLD}THÔNG TIN CHI TIẾT:{Colors.CYAN}                                              │
│                                                                │
│ {Colors.RED}❌ {Colors.WHITE}V5 Status: {Colors.BRIGHT_RED}DEPRECATED{Colors.CYAN}                                   │
│ {Colors.YELLOW}⏳ {Colors.WHITE}V5 Status: {Colors.BRIGHT_YELLOW}DEVELOPING...{Colors.CYAN}                               │
│ {Colors.GREEN}📅 {Colors.WHITE}Release Date: {Colors.BRIGHT_GREEN}SOON{Colors.CYAN}                                       │
│                                                                │
│ {Colors.WHITE}V4 sẽ có những cải tiến vượt trội:{Colors.CYAN}                           │
│ {Colors.BRIGHT_GREEN}  🚀 {Colors.WHITE}Tốc độ nhanh hơn 200%{Colors.CYAN}                                 │
│ {Colors.BRIGHT_GREEN}  🛡️ {Colors.WHITE}Bảo mật nâng cao{Colors.CYAN}                                       │
│ {Colors.BRIGHT_GREEN}  🎨 {Colors.WHITE}Giao diện hoàn toàn mới{Colors.CYAN}                                │
│ {Colors.BRIGHT_GREEN}  🔧 {Colors.WHITE}Fix toàn bộ lỗi V3{Colors.CYAN}                                     │
│                                                                │
│ {Colors.WHITE}Theo dõi kênh để nhận thông báo sớm nhất!{Colors.CYAN}                       │
└────────────────────────────────────────────────────────────────┘{Colors.RESET}
    """
    print(info)

def animated_dots(text, duration=3):
    """Text với dấu chấm động"""
    end_time = time.time() + duration
    dots = 0
    while time.time() < end_time:
        dot_str = "." * ((dots % 3) + 1)
        sys.stdout.write(f"\r{Colors.BRIGHT_YELLOW}{text}{dot_str}{' ' * (3 - len(dot_str))}{Colors.RESET}")
        sys.stdout.flush()
        dots += 1
        time.sleep(0.5)
    print()

def animated_link(url, duration=3):
    """Hiệu ứng link nhấp nháy đặc biệt"""
    colors_link = [Colors.BRIGHT_GREEN, Colors.BRIGHT_YELLOW, Colors.BRIGHT_CYAN, Colors.BRIGHT_RED]
    end_time = time.time() + duration
    idx = 0
    while time.time() < end_time:
        color = colors_link[idx % len(colors_link)]
        sys.stdout.write(f"\r{color}{Colors.BOLD}{Colors.BLINK}🔗 {url} 🔗{Colors.RESET}     ")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.3)
    print()

def fake_update_process():
    """Mô phỏng quá trình update"""
    print(f"\n{Colors.CYAN}{'='*65}{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}[UPDATE LOG]{Colors.RESET}\n")
    
    steps = [
        (f"{Colors.GREEN}[✓]{Colors.RESET} {Colors.DIM}Kiểm tra phiên bản V3... {Colors.BRIGHT_RED}DEPRECATED{Colors.RESET}", 0.5),
        (f"{Colors.YELLOW}[→]{Colors.RESET} Đang tải metadata V5...", 1.0),
        (f"{Colors.GREEN}[✓]{Colors.RESET} {Colors.DIM}Metadata loaded (2.4MB){Colors.RESET}", 0.5),
        (f"{Colors.YELLOW}[→]{Colors.RESET} Đang kiểm tra dependencies...", 1.0),
        (f"{Colors.GREEN}[✓]{Colors.RESET} {Colors.DIM}All dependencies satisfied{Colors.RESET}", 0.5),
        (f"{Colors.YELLOW}[→]{Colors.RESET} Compiling V5 source...", 1.5),
        (f"{Colors.GREEN}[✓]{Colors.RESET} {Colors.DIM}Compilation successful{Colors.RESET}", 0.5),
        (f"{Colors.CYAN}[*]{Colors.RESET} {Colors.BRIGHT_YELLOW}V5 ready to deploy!{Colors.RESET}", 0.5),
    ]
    
    for step, delay in steps:
        sys.stdout.write(f"\r{step}")
        sys.stdout.flush()
        time.sleep(delay)
        print()
    
    print(f"\n{Colors.CYAN}{'='*65}{Colors.RESET}")

def main():
    clear_screen()
    
    # Header
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.RESET}          {Colors.WHITE}HTOOL LOADER - AUTO UPDATER{Colors.RESET}              {Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════╝{Colors.RESET}\n")
    
    time.sleep(1)
    
    # Cảnh báo V3 hết hạn
    draw_warning_box()
    
    print()
    type_writer("🔍 Đang kiểm tra trạng thái tool...", 0.03, Colors.CYAN)
    time.sleep(1)
    
    # Thông báo V3 deprecated
    blink_text("⚠️  TOOL V4 ĐÃ NGỪNG HOẠT ĐỘNG - VUI LÒNG CHỜ V5  ⚠️", Colors.BRIGHT_RED, 3)
    
    print()
    
    # Hiển thị thông tin
    show_info_section()
    
    print()
    
    # Hỗ trợ từ Admin
    draw_support_box()
    
    # Hiệu ứng link nhấp nháy
    print(f"\n{Colors.BRIGHT_YELLOW}[💡] {Colors.WHITE}Tham gia ngay nhóm Zalo để được hỗ trợ:{Colors.RESET}\n")
    animated_link("https://zalo.me/g/e6bb2ppq4nofewqbfhrk", 3)
    
    print()
    
    # Fake update process
    sparkle_message("🔄 ĐANG TIẾN HÀNH CẬP NHẬT LÊN V4 🔄", 3)
    
    fake_update_process()
    
    # Progress bar
    progress_bar_update("UPDATING TO V4", 5)
    
    # Thông báo hoàn thành
    print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗")
    print(f"║                                                          ║")
    print(f"║         ✅ UPDATE V4 ĐANG ĐƯỢC HOÀN THIỆN ✅             ║")
    print(f"║                                                          ║")
    print(f"║     Vui lòng đợi thông báo chính thức từ Admin           ║")
    print(f"║     Tool sẽ tự động cập nhật khi có phiên bản mới        ║")
    print(f"║                                                          ║")
    print(f"╚══════════════════════════════════════════════════════════╝{Colors.RESET}\n")
    
    # Nhắc lại link hỗ trợ
    print(f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗")
    print(f"║                                                          ║")
    print(f"║    📱 THAM GIA NHÓM ZALO ĐỂ ĐƯỢC HỖ TRỢ:                ║")
    print(f"║    🔗 https://zalo.me/g/e6bb2ppq4nofewqbfhrk            ║")
    print(f"║                                                          ║")
    print(f"║    👨‍💻 Admin sẽ hỗ trợ bạn cài đặt và sử dụng V4        ║")
    print(f"║    💬 Nhắn tin trực tiếp để được phản hồi nhanh nhất    ║")
    print(f"║                                                          ║")
    print(f"╚══════════════════════════════════════════════════════════╝{Colors.RESET}\n")
    
    # Countdown ảo
    print(f"{Colors.YELLOW}[*] {Colors.WHITE}Thời gian dự kiến release V4:{Colors.RESET}")
    animated_dots("⏰ Đang tính toán", 3)
    
    print(f"\n{Colors.BRIGHT_CYAN}[*] {Colors.WHITE}Dự kiến: {Colors.BRIGHT_GREEN}SOON™{Colors.RESET} {Colors.DIM}(Vui lòng kiên nhẫn chờ đợi){Colors.RESET}")
    
    # Footer
    print(f"\n{Colors.CYAN}{'='*65}{Colors.RESET}")
    print(f"{Colors.DIM}© 2024 HTOOL | Follow for updates{Colors.RESET}")
    print(f"{Colors.DIM}📧 Contact: Join Zalo group for support{Colors.RESET}")
    print(f"{Colors.DIM}🔗 https://zalo.me/g/e6bb2ppq4nofewqbfhrk{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*65}{Colors.RESET}")
    
    # Exit message
    print(f"\n{Colors.BRIGHT_YELLOW}Chương trình sẽ tự động thoát sau 5 giây...{Colors.RESET}")
    
    try:
        for i in range(5, 0, -1):
            sys.stdout.write(f"\r{Colors.DIM}Tự động thoát trong: {i} giây - Tham gia nhóm Zalo để được hỗ trợ{Colors.RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print(f"\n{Colors.BRIGHT_GREEN}👋 Tạm biệt! Hẹn gặp lại trong nhóm Zalo!{Colors.RESET}\n")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_YELLOW}👋 Thoát ngay! Nhớ tham gia nhóm Zalo nhé!{Colors.RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_YELLOW}👋 See you in V4! Join Zalo group for updates!{Colors.RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.BRIGHT_RED}[✗] Lỗi: {e}{Colors.RESET}")
        sys.exit(1)

