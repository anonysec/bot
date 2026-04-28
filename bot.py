#!/usr/bin/env python3
"""
VPN Bot Manager - Single unified script for all operations
Supports: install, start, stop, restart, status, tui
Works on both Windows and Linux from root folder
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import signal
import psutil
import json

# Configuration
ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / 'venv'
REQ_FILE = ROOT / 'requirements.txt'
SRC_MAIN = ROOT / 'src' / 'main.py'
PID_FILE = ROOT / 'bot.pid'
CONFIG_FILE = ROOT / 'config.json'

def is_windows():
    return os.name == 'nt'

def python_executable():
    if VENV_DIR.exists():
        if is_windows():
            candidate = VENV_DIR / 'Scripts' / 'python.exe'
        else:
            candidate = VENV_DIR / 'bin' / 'python'
        if candidate.exists():
            return str(candidate)
    return sys.executable

def create_venv():
    if VENV_DIR.exists():
        print('✓ Virtual environment already exists.')
        return
    print('📦 Creating virtual environment...')
    subprocess.check_call([sys.executable, '-m', 'venv', str(VENV_DIR)])
    print('✓ Virtual environment created.')

def install_dependencies():
    if not REQ_FILE.exists():
        raise FileNotFoundError('requirements.txt not found')
    py = python_executable()
    print(f'📥 Installing dependencies using {py}...')
    subprocess.check_call([py, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([py, '-m', 'pip', 'install', '-r', str(REQ_FILE)])
    print('✓ Dependencies installed.')

def save_pid(pid):
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))

def load_pid():
    if not PID_FILE.exists():
        return None
    try:
        with open(PID_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return None

def remove_pid():
    if PID_FILE.exists():
        PID_FILE.unlink()

def is_process_running(pid):
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except:
        return False

def get_bot_process():
    """Find running bot process"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) > 1 and 'main.py' in cmdline[-1]:
                    return proc
        except:
            continue
    return None

def install(args):
    print('🚀 Installing VPN Bot...')
    create_venv()
    install_dependencies()
    create_env_file()
    print('\n✅ Installation complete!')
    print('Next steps:')
    print('1. Run: python bot.py setup')
    print('2. Open http://localhost:5000/setup and configure your bot')
    print('3. Run: python bot.py start')

def start(args):
    if not SRC_MAIN.exists():
        print('❌ Error: src/main.py not found')
        return

    # Check if already running
    existing_proc = get_bot_process()
    if existing_proc:
        print(f'⚠️  Bot is already running (PID: {existing_proc.pid})')
        return

    if not CONFIG_FILE.exists():
        print('⚠️  config.json not found. Please run: python bot.py setup')
        return

    py = python_executable()
    print('🚀 Starting VPN Bot...')

    if args.daemon or not is_windows():
        # Daemon mode for Linux/macOS
        config_arg = str(CONFIG_FILE.relative_to(ROOT)) if CONFIG_FILE != ROOT / 'config.json' else 'config.json'
        with open(ROOT / 'bot.log', 'a') as log_file:
            process = subprocess.Popen(
                [py, str(SRC_MAIN), config_arg],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                close_fds=True
            )
        save_pid(process.pid)
        print(f'✅ Bot started in background (PID: {process.pid})')
        print('Logs are being written to bot.log')
    else:
        # Foreground mode for Windows
        try:
            config_arg = str(CONFIG_FILE.relative_to(ROOT)) if CONFIG_FILE != ROOT / 'config.json' else 'config.json'
            subprocess.run([py, str(SRC_MAIN), config_arg])
        except KeyboardInterrupt:
            print('\n🛑 Bot stopped by user')

def stop(args):
    # Try PID file first
    pid = load_pid()
    if pid and is_process_running(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
            if is_process_running(pid):
                os.kill(pid, signal.SIGKILL)
            print('✅ Bot stopped via PID file')
            remove_pid()
            return
        except:
            pass

    # Try to find process
    proc = get_bot_process()
    if proc:
        try:
            proc.terminate()
            time.sleep(2)
            if proc.is_running():
                proc.kill()
            print('✅ Bot stopped')
            remove_pid()
            return
        except:
            pass

    print('❌ No running bot found')

def restart(args):
    print('🔄 Restarting bot...')
    stop(args)
    time.sleep(2)
    start(args)

def status(args):
    # Check PID file
    pid = load_pid()
    if pid and is_process_running(pid):
        print(f'✅ Bot is running (PID: {pid})')
        return

    # Check process list
    proc = get_bot_process()
    if proc:
        print(f'✅ Bot is running (PID: {proc.pid})')
        return

    print('❌ Bot is not running')

def tui(args):
    """Advanced Text-based User Interface (like x-ui)"""
    try:
        import curses
    except ImportError:
        print("❌ curses not available. Install with: pip install windows-curses (Windows) or use Linux")
        return

    def draw_menu(stdscr, menu_items, current_row, title):
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Title
        title_str = f"🚀 {title}"
        stdscr.addstr(1, (width - len(title_str)) // 2, title_str, curses.A_BOLD)

        # Menu items
        for idx, item in enumerate(menu_items):
            x = (width - len(item)) // 2
            y = height // 2 - len(menu_items) // 2 + idx
            if idx == current_row:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, item)

        # Footer
        footer = "↑↓ Navigate | Enter Select | Q Quit"
        stdscr.addstr(height - 2, (width - len(footer)) // 2, footer)

    def show_status(stdscr):
        height, width = stdscr.getmaxyx()
        stdscr.clear()

        title = "📊 System Status"
        stdscr.addstr(1, (width - len(title)) // 2, title, curses.A_BOLD)

        # Check bot status
        running = get_bot_process() is not None
        status = "🟢 Running" if running else "🔴 Stopped"
        stdscr.addstr(4, 4, f"Bot Status: {status}")

        # Check config
        config_exists = CONFIG_FILE.exists()
        config_status = "✅ Configured" if config_exists else "❌ Not Configured"
        stdscr.addstr(6, 4, f"Configuration: {config_status}")

        # Check database
        db_exists = (ROOT / 'vpn_bot.db').exists()
        db_status = "✅ Database OK" if db_exists else "❌ Database Missing"
        stdscr.addstr(8, 4, f"Database: {db_status}")

        # Show panels count
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                panels = config.get('panels', [])
                resellers = config.get('resellers', [])
                stdscr.addstr(10, 4, f"Panels: {len(panels)}")
                stdscr.addstr(12, 4, f"Resellers: {len(resellers)}")
        except:
            stdscr.addstr(10, 4, "Panels: Unable to read config")
            stdscr.addstr(12, 4, "Resellers: Unable to read config")

        stdscr.addstr(height - 2, (width - 20) // 2, "Press any key to return...")
        stdscr.getch()

    def main_tui(stdscr):
        curses.curs_set(0)
        stdscr.clear()
        stdscr.refresh()

        current_menu = "main"
        current_row = 0

        while True:
            if current_menu == "main":
                menu_items = [
                    "📊 System Status",
                    "⚙️  Configuration",
                    "🔧 Panel Management",
                    "👥 User Management",
                    "🚀 Start Bot",
                    "🛑 Stop Bot",
                    "🔄 Restart Bot",
                    "❌ Exit"
                ]
                draw_menu(stdscr, menu_items, current_row, "VPN Bot Manager (x-ui style)")

            elif current_menu == "config":
                menu_items = [
                    "🌐 Web Setup Wizard",
                    "📝 Edit Config File",
                    "🔍 View Current Config",
                    "⬅️  Back to Main Menu"
                ]
                draw_menu(stdscr, menu_items, current_row, "Configuration")

            elif current_menu == "panels":
                menu_items = [
                    "📋 List Panels",
                    "➕ Add Panel",
                    "✏️  Edit Panel",
                    "🗑️  Delete Panel",
                    "⬅️  Back to Main Menu"
                ]
                draw_menu(stdscr, menu_items, current_row, "Panel Management")

            elif current_menu == "users":
                menu_items = [
                    "📋 List Users",
                    "👤 Add Admin User",
                    "📊 User Statistics",
                    "⬅️  Back to Main Menu"
                ]
                draw_menu(stdscr, menu_items, current_row, "User Management")

            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                # Main menu actions
                if current_menu == "main":
                    if current_row == 0:  # System Status
                        show_status(stdscr)
                    elif current_row == 1:  # Configuration
                        current_menu = "config"
                        current_row = 0
                    elif current_row == 2:  # Panel Management
                        current_menu = "panels"
                        current_row = 0
                    elif current_row == 3:  # User Management
                        current_menu = "users"
                        current_row = 0
                    elif current_row == 4:  # Start Bot
                        stdscr.clear()
                        height, width = stdscr.getmaxyx()
                        stdscr.addstr(height // 2, width // 2 - 10, "Starting bot...")
                        stdscr.refresh()
                        start(argparse.Namespace(daemon=True))
                        stdscr.addstr(height // 2 + 1, width // 2 - 15, "Bot started! Press any key...")
                        stdscr.getch()
                    elif current_row == 5:  # Stop Bot
                        stdscr.clear()
                        height, width = stdscr.getmaxyx()
                        stdscr.addstr(height // 2, width // 2 - 10, "Stopping bot...")
                        stdscr.refresh()
                        stop(None)
                        stdscr.addstr(height // 2 + 1, width // 2 - 15, "Bot stopped! Press any key...")
                        stdscr.getch()
                    elif current_row == 6:  # Restart Bot
                        stdscr.clear()
                        height, width = stdscr.getmaxyx()
                        stdscr.addstr(height // 2, width // 2 - 10, "Restarting bot...")
                        stdscr.refresh()
                        restart(None)
                        stdscr.addstr(height // 2 + 1, width // 2 - 15, "Bot restarted! Press any key...")
                        stdscr.getch()
                    elif current_row == 7:  # Exit
                        break

                # Config menu actions
                elif current_menu == "config":
                    if current_row == 0:  # Web Setup
                        setup(None)
                        stdscr.clear()
                        height, width = stdscr.getmaxyx()
                        stdscr.addstr(height // 2, width // 2 - 20, "Web setup started! Check your browser.")
                        stdscr.addstr(height // 2 + 1, width // 2 - 15, "Press any key to continue...")
                        stdscr.getch()
                    elif current_row == 1:  # Edit Config
                        stdscr.clear()
                        height, width = stdscr.getmaxyx()
                        msg = "Use your preferred editor to edit config.json"
                        stdscr.addstr(height // 2, (width - len(msg)) // 2, msg)
                        stdscr.addstr(height // 2 + 1, (width - 30) // 2, "Press any key to continue...")
                        stdscr.getch()
                    elif current_row == 2:  # View Config
                        stdscr.clear()
                        try:
                            with open(CONFIG_FILE, 'r') as f:
                                config_content = f.read()
                            stdscr.addstr(1, 1, "Current Configuration (press any key to scroll):")
                            lines = config_content.split('\n')
                            max_lines = height - 3
                            for i, line in enumerate(lines[:max_lines]):
                                if i < height - 3:
                                    stdscr.addstr(i + 2, 1, line[:width-2])
                        except:
                            stdscr.addstr(height // 2, width // 2 - 15, "Unable to read config file")
                        stdscr.getch()
                    elif current_row == 3:  # Back
                        current_menu = "main"
                        current_row = 0

                # Panels menu actions
                elif current_menu == "panels":
                    if current_row == 0:  # List Panels
                        stdscr.clear()
                        height, width = stdscr.getmaxyx()
                        stdscr.addstr(1, 1, "Configured Panels:")
                        try:
                            with open(CONFIG_FILE, 'r') as f:
                                config = json.load(f)
                                panels = config.get('panels', [])
                                for i, panel in enumerate(panels):
                                    status = "🟢" if panel.get('enabled', True) else "🔴"
                                    info = f"{status} {panel.get('id', 'unknown')}: {panel.get('url', 'no url')}"
                                    stdscr.addstr(3 + i, 1, info[:width-2])
                        except:
                            stdscr.addstr(3, 1, "Unable to read panel configuration")
                        stdscr.addstr(height - 2, 1, "Press any key to return...")
                        stdscr.getch()
                    elif current_row == 4:  # Back
                        current_menu = "main"
                        current_row = 0

                # Users menu actions
                elif current_menu == "users":
                    if current_row == 3:  # Back
                        current_menu = "main"
                        current_row = 0

            elif key == ord('q') or key == ord('Q'):
                if current_menu == "main":
                    break
                else:
                    current_menu = "main"
                    current_row = 0

    curses.wrapper(main_tui)

def setup(args):
    """Web-based setup"""
    if not SRC_MAIN.exists():
        print('❌ Error: src/main.py not found')
        return

    py = python_executable()
    print('🌐 Starting web setup...')
    print('Open http://localhost:5000/setup in your browser')
    print('Press Ctrl+C to stop when finished.')
    try:
        subprocess.run([py, '-m', 'src.web.web'])
    except KeyboardInterrupt:
        print('\n🛑 Web setup stopped by user')

def main():
    parser = argparse.ArgumentParser(description='VPN Bot Manager - Single unified script')
    parser.add_argument('command', choices=['install', 'start', 'stop', 'restart', 'status', 'tui', 'setup'],
                       nargs='?', default='tui', help='Command to run')
    parser.add_argument('--daemon', action='store_true', help='Run in daemon mode (background)')
    parser.add_argument('--config', default='config.json', help='Configuration file path (default: config.json)')

    args = parser.parse_args()

    # Set global config file path
    global CONFIG_FILE
    CONFIG_FILE = ROOT / args.config

    if args.command == 'install':
        install(args)
    elif args.command == 'start':
        start(args)
    elif args.command == 'stop':
        stop(args)
    elif args.command == 'restart':
        restart(args)
    elif args.command == 'status':
        status(args)
    elif args.command == 'tui':
        tui(args)
    elif args.command == 'setup':
        setup(args)

if __name__ == '__main__':
    main()