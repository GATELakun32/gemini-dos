# -*- coding: utf-8 -*-
from google import genai
import os
import time
import sys
from datetime import datetime
from threading import Lock

# Set encoding untuk Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ANSI Color Codes untuk Windows
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    @staticmethod
    def init():
        """Enable ANSI colors on Windows"""
        if sys.platform == 'win32':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

Colors.init()

# Clear screen function
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Print dengan format yang bagus
def print_header():
    clear_screen()
    print(f"{Colors.CYAN}{Colors.BOLD}{'╔' + '═'*68 + '╗'}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.RESET} {Colors.MAGENTA}{Colors.BOLD}GEMINI API SPAM-model=gemini-2.5-flash-ULTRA HIGH PERFORMANCE MODE{Colors.RESET} {Colors.CYAN}{Colors.BOLD}║{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'╚' + '═'*68 + '╝'}{Colors.RESET}\n")

def print_statistics(stats):
    """Print real-time statistics dengan tampilan yang lebih bagus"""
    # Clear previous stats dengan carriage return
    print(f"\r{' '*80}", end="")
    print(f"\r{Colors.GRAY}{'═'*70}{Colors.RESET}")
    print(f"\r{Colors.BOLD}{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}📊 STATISTIK REAL-TIME{Colors.RESET} {' '*45} {Colors.CYAN}║{Colors.RESET}")
    print(f"\r{Colors.GRAY}{'═'*70}{Colors.RESET}")
    
    # Baris statistik dengan format yang lebih rapi
    success_bar = "█" * int((stats['success'] / max(stats['total'], 1)) * 20)
    error_bar = "█" * int((stats['error'] / max(stats['total'], 1)) * 20)
    
    print(f"\r{Colors.CYAN}║{Colors.RESET} {Colors.GREEN}✓ Berhasil:{Colors.RESET} {Colors.BOLD}{stats['success']:>4}{Colors.RESET} {success_bar:<20} {Colors.CYAN}║{Colors.RESET}")
    print(f"\r{Colors.CYAN}║{Colors.RESET} {Colors.RED}✗ Error:{Colors.RESET}     {Colors.BOLD}{stats['error']:>4}{Colors.RESET} {error_bar:<20} {Colors.CYAN}║{Colors.RESET}")
    print(f"\r{Colors.CYAN}║{Colors.RESET} {Colors.CYAN}📤 Total:{Colors.RESET}     {Colors.BOLD}{stats['total']:>4}{Colors.RESET} {'█'*20} {Colors.CYAN}║{Colors.RESET}")
    
    if stats['total'] > 0:
        success_rate = (stats['success'] / stats['total']) * 100
        rate_color = Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 50 else Colors.RED
        print(f"\r{Colors.CYAN}║{Colors.RESET} {Colors.YELLOW}📈 Success Rate:{Colors.RESET} {rate_color}{Colors.BOLD}{success_rate:>5.1f}%{Colors.RESET} {' '*35} {Colors.CYAN}║{Colors.RESET}")
    
    if stats['elapsed'] > 0:
        rps = stats['total'] / stats['elapsed']
        print(f"\r{Colors.CYAN}║{Colors.RESET} {Colors.MAGENTA}⚡ Speed:{Colors.RESET}        {Colors.BOLD}{rps:>6.2f}{Colors.RESET} requests/detik {' '*30} {Colors.CYAN}║{Colors.RESET}")
    
    if stats['avg_response_time'] > 0:
        print(f"\r{Colors.CYAN}║{Colors.RESET} {Colors.BLUE}⏱️  Avg Response:{Colors.RESET}  {Colors.BOLD}{stats['avg_response_time']:>6.3f}s{Colors.RESET} {' '*35} {Colors.CYAN}║{Colors.RESET}")
    
    print(f"\r{Colors.GRAY}{'═'*70}{Colors.RESET}\n")

def print_request(num, question, status, response_text="", response_time=0):
    """Print formatted request information"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    question_short = question[:35] + "..." if len(question) > 35 else question
    
    if status == "success":
        print(f"{Colors.GRAY}[{timestamp}]{Colors.RESET} "
              f"{Colors.CYAN}[#{num}]{Colors.RESET} "
              f"{Colors.WHITE}Q: {question_short}{Colors.RESET} "
              f"{Colors.GREEN}✓{Colors.RESET} "
              f"{Colors.GREEN}{response_text[:30]}...{Colors.RESET} "
              f"{Colors.GRAY}({response_time:.3f}s){Colors.RESET}")
    elif status == "error":
        print(f"{Colors.GRAY}[{timestamp}]{Colors.RESET} "
              f"{Colors.CYAN}[#{num}]{Colors.RESET} "
              f"{Colors.WHITE}Q: {question_short}{Colors.RESET} "
              f"{Colors.RED}✗ ERROR{Colors.RESET}")

# Function untuk input API key
def get_api_key():
    """Input API key dari user"""
    print_header()
    print(f"{Colors.BOLD}KONFIGURASI API KEY:{Colors.RESET}\n")
    print(f"{Colors.YELLOW}Masukkan API key Gemini Anda:{Colors.RESET}")
    print(f"{Colors.RED}(MASUKIN API KEY){Colors.RESET}\n")
    
    api_key = input(f"{Colors.CYAN}API Key: {Colors.RESET}").strip()
    
    if not api_key:
        # Gunakan default atau dari environment variable
        api_key = os.getenv("GEMINI_API_KEY", " ")
        print(f"{Colors.GRAY}→ Menggunakan API key default/environment variable{Colors.RESET}\n")
    else:
        print(f"{Colors.GREEN}✓ API key diterima{Colors.RESET}\n")
    
    return api_key

# Initialize Gemini Client
api_key = get_api_key()
os.environ["GEMINI_API_KEY"] = api_key
client = genai.Client()

# Baca list pertanyaan dari file
print(f"{Colors.YELLOW}Loading pertanyaan dari file...{Colors.RESET}")
try:
    with open("pertanyaan.txt", "r", encoding="utf-8") as f:
        pertanyaan_list = [line.strip() for line in f.readlines() if line.strip()]
    print(f"{Colors.GREEN}✓ Berhasil memuat {len(pertanyaan_list)} pertanyaan{Colors.RESET}\n")
except FileNotFoundError:
    print(f"{Colors.RED}✗ File pertanyaan.txt tidak ditemukan{Colors.RESET}")
    pertanyaan_list = ["1+1", "2+2", "3+3", "4+4", "5+5"]
    print(f"{Colors.YELLOW}→ Menggunakan pertanyaan default ({len(pertanyaan_list)} pertanyaan){Colors.RESET}\n")
except Exception as e:
    print(f"{Colors.RED}✗ Error membaca file: {e}{Colors.RESET}")
    pertanyaan_list = ["1+1", "2+2", "3+3", "4+4", "5+5"]
    print(f"{Colors.YELLOW}→ Menggunakan pertanyaan default ({len(pertanyaan_list)} pertanyaan){Colors.RESET}\n")

# Function untuk menampilkan menu
def show_menu():
    """Tampilkan menu pilihan jumlah request"""
    print_header()
    print(f"{Colors.BOLD}MENU PILIHAN JUMLAH REQUEST:{Colors.RESET}\n")
    print(f"  {Colors.CYAN}[1]{Colors.RESET} 10 Request")
    print(f"  {Colors.CYAN}[2]{Colors.RESET} 25 Request")
    print(f"  {Colors.CYAN}[3]{Colors.RESET} 50 Request")
    print(f"  {Colors.CYAN}[4]{Colors.RESET} 100 Request")
    print(f"  {Colors.CYAN}[5]{Colors.RESET} 200 Request")
    print(f"  {Colors.CYAN}[6]{Colors.RESET} 500 Request")
    print(f"  {Colors.CYAN}[7]{Colors.RESET} Custom (masukkan sendiri)")
    print(f"  {Colors.CYAN}[8]{Colors.RESET} {Colors.MAGENTA}Unlimited{Colors.RESET} (sampai limit habis)")
    print(f"  {Colors.CYAN}[0]{Colors.RESET} Keluar\n")
    
    while True:
        try:
            choice = input(f"{Colors.YELLOW}Pilih opsi [1-8] atau [0] untuk keluar: {Colors.RESET}").strip()
            
            if choice == "0":
                print(f"{Colors.YELLOW}Keluar dari program...{Colors.RESET}")
                sys.exit(0)
            elif choice == "1":
                return 10
            elif choice == "2":
                return 25
            elif choice == "3":
                return 50
            elif choice == "4":
                return 100
            elif choice == "5":
                return 200
            elif choice == "6":
                return 500
            elif choice == "7":
                while True:
                    try:
                        custom = input(f"{Colors.YELLOW}Masukkan jumlah request (angka): {Colors.RESET}").strip()
                        custom_num = int(custom)
                        if custom_num > 0:
                            return custom_num
                        else:
                            print(f"{Colors.RED}Masukkan angka yang lebih besar dari 0!{Colors.RESET}")
                    except ValueError:
                        print(f"{Colors.RED}Masukkan angka yang valid!{Colors.RESET}")
            elif choice == "8":
                return None  # None berarti unlimited
            else:
                print(f"{Colors.RED}Pilihan tidak valid! Silakan pilih 1-8 atau 0.{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Keluar dari program...{Colors.RESET}")
            sys.exit(0)
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")

# Variables
pertanyaan_index = 0
request_count = 0
success_count = 0
error_count = 0
start_time = time.time()
response_times = []
stats_lock = Lock()
last_error_message = ""  # Simpan error message terakhir
error_messages = []  # Simpan semua error messages untuk analisis

# Tampilkan menu dan ambil pilihan user
max_requests = show_menu()

# Print header
print_header()

if max_requests is None:
    target_text = f"{Colors.MAGENTA}Unlimited (sampai limit habis){Colors.RESET}"
else:
    target_text = f"{Colors.MAGENTA}{max_requests} request{Colors.RESET}"

print(f"{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}KONFIGURASI{Colors.RESET} {' '*50} {Colors.CYAN}║{Colors.RESET}")
print(f"{Colors.BOLD}{Colors.CYAN}╠══════════════════════════════════════════════════════════════╣{Colors.RESET}")
print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}Model:{Colors.RESET}           {Colors.CYAN}gemini-2.5-flash{Colors.RESET} {' '*38} {Colors.CYAN}║{Colors.RESET}")
print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}Total Pertanyaan:{Colors.RESET} {Colors.CYAN}{len(pertanyaan_list):>3}{Colors.RESET} {' '*44} {Colors.CYAN}║{Colors.RESET}")
print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}Mode:{Colors.RESET}            {Colors.YELLOW}ULTRA HIGH PERFORMANCE{Colors.RESET} {' '*25} {Colors.CYAN}║{Colors.RESET}")
target_display = target_text.replace(Colors.MAGENTA, "").replace(Colors.RESET, "")
spaces_needed = 68 - 15 - len(target_display)
print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.RESET} {Colors.WHITE}Target:{Colors.RESET}          {target_text}{' '*spaces_needed} {Colors.CYAN}║{Colors.RESET}")
print(f"{Colors.BOLD}{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

print(f"{Colors.YELLOW}Memulai dalam 2 detik...{Colors.RESET}")
time.sleep(2)
clear_screen()
print_header()

if max_requests is None:
    print(f"{Colors.GREEN}{Colors.BOLD}🚀 MEMULAI PENGIRIMAN REQUEST (UNLIMITED)...{Colors.RESET}\n")
else:
    print(f"{Colors.GREEN}{Colors.BOLD}🚀 MEMULAI PENGIRIMAN REQUEST ({max_requests} request)...{Colors.RESET}\n")

try:
    while True:
        # Cek apakah sudah mencapai target request
        if max_requests is not None and request_count >= max_requests:
            elapsed = time.time() - start_time
            clear_screen()
            print_header()
            
            if error_count > 0 and success_count == 0:
                print(f"{Colors.RED}{Colors.BOLD}⚠️  TARGET TERCAPAI - SEMUA REQUEST ERROR!{Colors.RESET}\n")
            elif error_count > 0:
                print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  TARGET TERCAPAI - ADA ERROR!{Colors.RESET}\n")
            else:
                print(f"{Colors.GREEN}{Colors.BOLD}✅ TARGET REQUEST TERCAPAI!{Colors.RESET}\n")
            
            avg_response = sum(response_times) / len(response_times) if response_times else 0
            rps = request_count / elapsed if elapsed > 0 else 0
            
            print(f"{Colors.BOLD}📊 STATISTIK AKHIR:{Colors.RESET}\n")
            print(f"  {Colors.CYAN}Target Request:{Colors.RESET}   {Colors.BOLD}{max_requests}{Colors.RESET}")
            print(f"  {Colors.CYAN}Total Request:{Colors.RESET}     {Colors.BOLD}{request_count}{Colors.RESET}")
            print(f"  {Colors.GREEN}Berhasil:{Colors.RESET}          {Colors.BOLD}{success_count}{Colors.RESET}")
            print(f"  {Colors.RED}Error:{Colors.RESET}             {Colors.BOLD}{error_count}{Colors.RESET}")
            
            if request_count > 0:
                success_rate = (success_count / request_count) * 100
                print(f"  {Colors.YELLOW}Success Rate:{Colors.RESET}     {Colors.BOLD}{success_rate:.1f}%{Colors.RESET}")
            
            print(f"  {Colors.MAGENTA}Waktu Total:{Colors.RESET}      {Colors.BOLD}{elapsed:.2f} detik{Colors.RESET}")
            print(f"  {Colors.MAGENTA}Kecepatan:{Colors.RESET}        {Colors.BOLD}{rps:.2f} requests/detik{Colors.RESET}")
            
            if response_times:
                print(f"  {Colors.BLUE}Avg Response Time:{Colors.RESET} {Colors.BOLD}{avg_response:.3f} detik{Colors.RESET}")
                print(f"  {Colors.BLUE}Response Tercepat:{Colors.RESET} {Colors.BOLD}{min(response_times):.3f} detik{Colors.RESET}")
                print(f"  {Colors.BLUE}Response Terlama:{Colors.RESET}  {Colors.BOLD}{max(response_times):.3f} detik{Colors.RESET}")
            
            # Tampilkan informasi error jika ada
            if error_count > 0:
                print(f"\n  {Colors.RED}{Colors.BOLD}📋 INFORMASI ERROR:{Colors.RESET}")
                if last_error_message:
                    # Ambil error type dari error message
                    error_type = "Unknown Error"
                    if "403" in last_error_message or "PERMISSION_DENIED" in last_error_message:
                        error_type = "API Key Invalid / Permission Denied"
                    elif "429" in last_error_message or "RESOURCE_EXHAUSTED" in last_error_message:
                        error_type = "Rate Limit / Quota Exceeded"
                    elif "401" in last_error_message or "UNAUTHENTICATED" in last_error_message:
                        error_type = "Authentication Error"
                    elif "400" in last_error_message or "INVALID_ARGUMENT" in last_error_message:
                        error_type = "Invalid Request"
                    elif "500" in last_error_message or "INTERNAL" in last_error_message:
                        error_type = "Server Error"
                    
                    print(f"  {Colors.RED}Error Type:{Colors.RESET}     {Colors.BOLD}{error_type}{Colors.RESET}")
                    print(f"  {Colors.RED}Error Terakhir:{Colors.RESET}")
                    # Tampilkan error message yang lebih readable
                    error_short = last_error_message[:150] + "..." if len(last_error_message) > 150 else last_error_message
                    print(f"  {Colors.GRAY}{error_short}{Colors.RESET}")
                    
                    # Jika ada banyak error, tampilkan ringkasan
                    if len(error_messages) > 1:
                        # Hitung error types
                        error_types_count = {}
                        for err in error_messages:
                            if "403" in err or "PERMISSION_DENIED" in err:
                                error_types_count["API Key Invalid"] = error_types_count.get("API Key Invalid", 0) + 1
                            elif "429" in err or "RESOURCE_EXHAUSTED" in err:
                                error_types_count["Rate Limit"] = error_types_count.get("Rate Limit", 0) + 1
                            elif "401" in err or "UNAUTHENTICATED" in err:
                                error_types_count["Auth Error"] = error_types_count.get("Auth Error", 0) + 1
                            elif "400" in err or "INVALID_ARGUMENT" in err:
                                error_types_count["Invalid Request"] = error_types_count.get("Invalid Request", 0) + 1
                            else:
                                error_types_count["Other"] = error_types_count.get("Other", 0) + 1
                        
                        if len(error_types_count) > 1:
                            print(f"\n  {Colors.YELLOW}Ringkasan Error:{Colors.RESET}")
                            for err_type, count in error_types_count.items():
                                print(f"    - {err_type}: {count}x")
            break
        
        request_count += 1
        request_start = time.time()
        
        try:
            # Ambil pertanyaan dari list (rotasi dengan modulo untuk efisiensi)
            pertanyaan = pertanyaan_list[pertanyaan_index % len(pertanyaan_list)]
            pertanyaan_index = (pertanyaan_index + 1) % len(pertanyaan_list)
            
            # Tampilkan progress jika ada target dengan animasi
            progress_info = ""
            if max_requests is not None:
                progress = (request_count / max_requests) * 100
                filled = int(progress / 2)
                empty = 50 - filled
                # Animasi progress bar dengan gradient
                progress_bar = f"{Colors.GREEN}{'█' * filled}{Colors.RESET}{Colors.GRAY}{'░' * empty}{Colors.RESET}"
                # Tambahkan spinner untuk efek visual
                spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"][request_count % 10]
                progress_info = f"{Colors.CYAN}[{request_count:>{len(str(max_requests))}}/{max_requests}]{Colors.RESET} {spinner} {progress_bar} {Colors.YELLOW}{progress:>5.1f}%{Colors.RESET} "
            
            # Kirim request
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=pertanyaan
            )
            
            # Hitung response time
            response_time = time.time() - request_start
            response_times.append(response_time)
            
            success_count += 1
            response_text = response.text.strip() if hasattr(response, 'text') else "OK"
            
            if max_requests is None:
                print_request(request_count, pertanyaan, "success", response_text, response_time)
            else:
                # Format yang lebih compact dan bagus jika ada target
                timestamp = datetime.now().strftime("%H:%M:%S")
                question_short = pertanyaan[:30] + "..." if len(pertanyaan) > 30 else pertanyaan
                # Warna response time berdasarkan kecepatan
                time_color = Colors.GREEN if response_time < 0.5 else Colors.YELLOW if response_time < 1.0 else Colors.RED
                print(f"{progress_info} {Colors.GRAY}│{Colors.RESET} {Colors.GRAY}[{timestamp}]{Colors.RESET} "
                      f"{Colors.WHITE}{question_short:<33}{Colors.RESET} "
                      f"{Colors.GREEN}✓{Colors.RESET} "
                      f"{Colors.GREEN}{response_text[:20]:<20}{Colors.RESET} "
                      f"{time_color}({response_time:.3f}s){Colors.RESET}")
            
            # Delay sangat minimal untuk performa maksimal (0.01 detik = ultra fast)
            time.sleep(0.01)
            
        except Exception as e:
            error_count += 1
            error_message = str(e)
            last_error_message = error_message  # Simpan error terakhir
            error_messages.append(error_message)  # Simpan ke list untuk analisis
            response_time = time.time() - request_start
            
            # Tampilkan progress jika ada target (hanya sekali) dengan animasi
            progress_info = ""
            if max_requests is not None:
                progress = (request_count / max_requests) * 100
                filled = int(progress / 2)
                empty = 50 - filled
                progress_bar = f"{Colors.RED}{'█' * filled}{Colors.RESET}{Colors.GRAY}{'░' * empty}{Colors.RESET}"
                spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"][request_count % 10]
                progress_info = f"{Colors.CYAN}[{request_count:>{len(str(max_requests))}}/{max_requests}]{Colors.RESET} {spinner} {progress_bar} {Colors.YELLOW}{progress:>5.1f}%{Colors.RESET} "
            
            if max_requests is None:
                print_request(request_count, pertanyaan, "error")
            else:
                timestamp = datetime.now().strftime("%H:%M:%S")
                question_short = pertanyaan[:30] + "..." if len(pertanyaan) > 30 else pertanyaan
                print(f"{progress_info} {Colors.GRAY}│{Colors.RESET} {Colors.GRAY}[{timestamp}]{Colors.RESET} "
                      f"{Colors.WHITE}{question_short:<33}{Colors.RESET} "
                      f"{Colors.RED}✗ ERROR{Colors.RESET}")
            
            print(f"{Colors.RED}   Error: {error_message[:80]}...{Colors.RESET}")
            
            # Cek apakah error karena API key tidak valid (403 PERMISSION_DENIED)
            if any(keyword in error_message.lower() for keyword in [
                "403", "permission denied", "api key", "revoked", "invalid api key",
                "unauthorized", "forbidden", "api key was"
            ]):
                elapsed = time.time() - start_time
                
                # Print final statistics
                clear_screen()
                print_header()
                print(f"{Colors.RED}{Colors.BOLD}❌ API KEY TIDAK VALID ATAU TIDAK MEMILIKI IZIN!{Colors.RESET}\n")
                
                print(f"{Colors.YELLOW}Kemungkinan penyebab:{Colors.RESET}")
                print(f"  • API key tidak valid atau sudah expired")
                print(f"  • API key sudah dicabut (revoked)")
                print(f"  • API key tidak memiliki permission untuk mengakses Gemini API")
                print(f"  • API key belum diaktifkan atau belum dikonfigurasi dengan benar\n")
                
                print(f"{Colors.CYAN}Solusi:{Colors.RESET}")
                print(f"  1. Periksa API key di Google AI Studio: https://aistudio.google.com/apikey")
                print(f"  2. Pastikan API key sudah diaktifkan dan memiliki akses ke Gemini API")
                print(f"  3. Buat API key baru jika yang lama sudah tidak valid")
                print(f"  4. Update API key di script (baris 88)\n")
                
                avg_response = sum(response_times) / len(response_times) if response_times else 0
                rps = request_count / elapsed if elapsed > 0 else 0
                
                print(f"{Colors.BOLD}📊 STATISTIK AKHIR:{Colors.RESET}\n")
                print(f"  {Colors.CYAN}Total Request:{Colors.RESET}     {Colors.BOLD}{request_count}{Colors.RESET}")
                print(f"  {Colors.GREEN}Berhasil:{Colors.RESET}          {Colors.BOLD}{success_count}{Colors.RESET}")
                print(f"  {Colors.RED}Error:{Colors.RESET}             {Colors.BOLD}{error_count}{Colors.RESET}")
                
                if request_count > 0:
                    success_rate = (success_count / request_count) * 100
                    print(f"  {Colors.YELLOW}Success Rate:{Colors.RESET}     {Colors.BOLD}{success_rate:.1f}%{Colors.RESET}")
                
                print(f"  {Colors.MAGENTA}Waktu Total:{Colors.RESET}      {Colors.BOLD}{elapsed:.2f} detik{Colors.RESET}")
                print(f"  {Colors.MAGENTA}Kecepatan:{Colors.RESET}        {Colors.BOLD}{rps:.2f} requests/detik{Colors.RESET}")
                
                if response_times:
                    print(f"  {Colors.BLUE}Avg Response Time:{Colors.RESET} {Colors.BOLD}{avg_response:.3f} detik{Colors.RESET}")
                    print(f"  {Colors.BLUE}Response Tercepat:{Colors.RESET} {Colors.BOLD}{min(response_times):.3f} detik{Colors.RESET}")
                    print(f"  {Colors.BLUE}Response Terlama:{Colors.RESET}  {Colors.BOLD}{max(response_times):.3f} detik{Colors.RESET}")
                
                print(f"\n  {Colors.RED}Error Detail:{Colors.RESET}")
                error_short = error_message[:200] + "..." if len(error_message) > 200 else error_message
                print(f"  {Colors.GRAY}{error_short}{Colors.RESET}")
                break
            
            # Cek apakah error karena limit/quota habis
            if any(keyword in error_message.lower() for keyword in [
                "quota", "limit", "rate limit", "429", 
                "resource exhausted", "exceeded", "insufficient"
            ]):
                elapsed = time.time() - start_time
                
                # Print final statistics
                clear_screen()
                print_header()
                print(f"{Colors.RED}{Colors.BOLD}⚠️  LIMIT API KEY HABIS!{Colors.RESET}\n")
                
                avg_response = sum(response_times) / len(response_times) if response_times else 0
                rps = request_count / elapsed if elapsed > 0 else 0
                
                print(f"{Colors.BOLD}📊 STATISTIK AKHIR:{Colors.RESET}\n")
                print(f"  {Colors.CYAN}Total Request:{Colors.RESET}     {Colors.BOLD}{request_count}{Colors.RESET}")
                print(f"  {Colors.GREEN}Berhasil:{Colors.RESET}          {Colors.BOLD}{success_count}{Colors.RESET}")
                print(f"  {Colors.RED}Error:{Colors.RESET}             {Colors.BOLD}{error_count}{Colors.RESET}")
                
                if request_count > 0:
                    success_rate = (success_count / request_count) * 100
                    print(f"  {Colors.YELLOW}Success Rate:{Colors.RESET}     {Colors.BOLD}{success_rate:.1f}%{Colors.RESET}")
                
                print(f"  {Colors.MAGENTA}Waktu Total:{Colors.RESET}      {Colors.BOLD}{elapsed:.2f} detik{Colors.RESET}")
                print(f"  {Colors.MAGENTA}Kecepatan:{Colors.RESET}        {Colors.BOLD}{rps:.2f} requests/detik{Colors.RESET}")
                
                if response_times:
                    print(f"  {Colors.BLUE}Avg Response Time:{Colors.RESET} {Colors.BOLD}{avg_response:.3f} detik{Colors.RESET}")
                    print(f"  {Colors.BLUE}Response Tercepat:{Colors.RESET} {Colors.BOLD}{min(response_times):.3f} detik{Colors.RESET}")
                    print(f"  {Colors.BLUE}Response Terlama:{Colors.RESET}  {Colors.BOLD}{max(response_times):.3f} detik{Colors.RESET}")
                
                print(f"\n  {Colors.GRAY}Error terakhir:{Colors.RESET}")
                print(f"  {Colors.GRAY}{error_message[:100]}...{Colors.RESET}")
                break
            
            # Jika error lain, tunggu sebentar lalu coba lagi
            time.sleep(1)
            
        # Update statistics setiap 5 request atau setiap request jika ada target
        if max_requests is not None or request_count % 5 == 0:
            elapsed = time.time() - start_time
            avg_response = sum(response_times[-10:]) / len(response_times[-10:]) if len(response_times) >= 10 else (sum(response_times) / len(response_times) if response_times else 0)
            
            stats = {
                'total': request_count,
                'success': success_count,
                'error': error_count,
                'elapsed': elapsed,
                'avg_response_time': avg_response
            }
            print_statistics(stats)
            
except KeyboardInterrupt:
    elapsed = time.time() - start_time
    clear_screen()
    print_header()
    print(f"{Colors.YELLOW}{Colors.BOLD}⏹️  DIHENTIKAN OLEH USER (Ctrl+C){Colors.RESET}\n")
    
    avg_response = sum(response_times) / len(response_times) if response_times else 0
    rps = request_count / elapsed if elapsed > 0 else 0
    
    print(f"{Colors.BOLD}📊 STATISTIK AKHIR:{Colors.RESET}\n")
    print(f"  {Colors.CYAN}Total Request:{Colors.RESET}     {Colors.BOLD}{request_count}{Colors.RESET}")
    print(f"  {Colors.GREEN}Berhasil:{Colors.RESET}          {Colors.BOLD}{success_count}{Colors.RESET}")
    print(f"  {Colors.RED}Error:{Colors.RESET}             {Colors.BOLD}{error_count}{Colors.RESET}")
    
    if request_count > 0:
        success_rate = (success_count / request_count) * 100
        print(f"  {Colors.YELLOW}Success Rate:{Colors.RESET}     {Colors.BOLD}{success_rate:.1f}%{Colors.RESET}")
    
    print(f"  {Colors.MAGENTA}Waktu Total:{Colors.RESET}      {Colors.BOLD}{elapsed:.2f} detik{Colors.RESET}")
    print(f"  {Colors.MAGENTA}Kecepatan:{Colors.RESET}        {Colors.BOLD}{rps:.2f} requests/detik{Colors.RESET}")
    
    if response_times:
        print(f"  {Colors.BLUE}Avg Response Time:{Colors.RESET} {Colors.BOLD}{avg_response:.3f} detik{Colors.RESET}")
    
    # Tampilkan informasi error jika ada
    if error_count > 0 and last_error_message:
        print(f"\n  {Colors.RED}{Colors.BOLD}📋 ERROR TERAKHIR:{Colors.RESET}")
        error_short = last_error_message[:150] + "..." if len(last_error_message) > 150 else last_error_message
        print(f"  {Colors.GRAY}{error_short}{Colors.RESET}")

except Exception as e:
    elapsed = time.time() - start_time
    clear_screen()
    print_header()
    print(f"{Colors.RED}{Colors.BOLD}❌ ERROR TIDAK TERDUGA:{Colors.RESET} {e}\n")
    print(f"{Colors.BOLD}📊 STATISTIK:{Colors.RESET}")
    print(f"  Total Request: {request_count}")
    print(f"  Berhasil: {success_count}")
    print(f"  Error: {error_count}")
    
    # Tampilkan informasi error jika ada
    if error_count > 0 and last_error_message:
        print(f"\n  {Colors.RED}{Colors.BOLD}📋 ERROR TERAKHIR:{Colors.RESET}")
        error_short = last_error_message[:150] + "..." if len(last_error_message) > 150 else last_error_message
        print(f"  {Colors.GRAY}{error_short}{Colors.RESET}")

finally:
    print(f"\n{Colors.CYAN}{Colors.BOLD}✅ Script selesai!{Colors.RESET}\n")
