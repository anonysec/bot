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
ENV_FILE = ROOT / '.env'
ENV_EXAMPLE = ROOT / '.env.example'
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

def create_env_file():
    if ENV_FILE.exists():
        print('✓ .env already exists.')
        return
    if not ENV_EXAMPLE.exists():
        raise FileNotFoundError('.env.example not found')
    shutil.copy(ENV_EXAMPLE, ENV_FILE)
    print('✓ Created .env from .env.example.')

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

    if not ENV_FILE.exists():
        print('⚠️  .env not found. Creating from example...')
        create_env_file()

    py = python_executable()
    print('🚀 Starting VPN Bot...')

    if args.daemon or not is_windows():
        # Daemon mode for Linux/macOS
        with open(ROOT / 'bot.log', 'a') as log_file:
            process = subprocess.Popen(
                [py, str(SRC_MAIN)],
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
            subprocess.run([py, str(SRC_MAIN)])
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
    """Text-based User Interface"""
    try:
        import curses
    except ImportError:
        print("❌ curses not available. Install with: pip install windows-curses (Windows) or use Linux")
        return

    def main_tui(stdscr):
        curses.curs_set(0)
        stdscr.clear()
        stdscr.refresh()

        menu = ['Install', 'Start', 'Stop', 'Restart', 'Status', 'Exit']
        current_row = 0

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Title
            title = "🚀 VPN Bot Manager"
            stdscr.addstr(1, (width - len(title)) // 2, title, curses.A_BOLD)

            # Menu
            for idx, item in enumerate(menu):
                x = (width - len(item)) // 2
                y = height // 2 - len(menu) // 2 + idx
                if idx == current_row:
                    stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(y, x, item)
                    stdscr.attroff(curses.A_REVERSE)
                else:
                    stdscr.addstr(y, x, item)

            # Status
            status_text = "Use arrow keys to navigate, Enter to select, Q to quit"
            stdscr.addstr(height - 2, (width - len(status_text)) // 2, status_text)

            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if menu[current_row] == 'Install':
                    stdscr.clear()
                    stdscr.addstr(height // 2, width // 2 - 10, "Installing...")
                    stdscr.refresh()
                    install(None)
                    stdscr.addstr(height // 2 + 1, width // 2 - 15, "Press any key to continue...")
                    stdscr.getch()
                elif menu[current_row] == 'Start':
                    stdscr.clear()
                    stdscr.addstr(height // 2, width // 2 - 10, "Starting...")
                    stdscr.refresh()
                    start(argparse.Namespace(daemon=True))
                    stdscr.addstr(height // 2 + 1, width // 2 - 15, "Press any key to continue...")
                    stdscr.getch()
                elif menu[current_row] == 'Stop':
                    stdscr.clear()
                    stdscr.addstr(height // 2, width // 2 - 10, "Stopping...")
                    stdscr.refresh()
                    stop(None)
                    stdscr.addstr(height // 2 + 1, width // 2 - 15, "Press any key to continue...")
                    stdscr.getch()
                elif menu[current_row] == 'Restart':
                    stdscr.clear()
                    stdscr.addstr(height // 2, width // 2 - 10, "Restarting...")
                    stdscr.refresh()
                    restart(None)
                    stdscr.addstr(height // 2 + 1, width // 2 - 15, "Press any key to continue...")
                    stdscr.getch()
                elif menu[current_row] == 'Status':
                    stdscr.clear()
                    stdscr.addstr(height // 2, width // 2 - 10, "Checking status...")
                    stdscr.refresh()
                    status(None)
                    stdscr.addstr(height // 2 + 1, width // 2 - 15, "Press any key to continue...")
                    stdscr.getch()
                elif menu[current_row] == 'Exit':
                    break
            elif key == ord('q') or key == ord('Q'):
                break

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

    args = parser.parse_args()

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