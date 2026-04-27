#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / 'venv'
ENV_FILE = ROOT / '.env'
ENV_EXAMPLE = ROOT / '.env.example'
REQ_FILE = ROOT / 'requirements.txt'
SRC_MAIN = ROOT / 'src' / 'main.py'


def python_executable():
    if VENV_DIR.exists():
        if os.name == 'nt':
            candidate = VENV_DIR / 'Scripts' / 'python.exe'
        else:
            candidate = VENV_DIR / 'bin' / 'python'
        if candidate.exists():
            return str(candidate)
    return sys.executable


def create_venv():
    if VENV_DIR.exists():
        print('Virtual environment already exists.')
        return
    print('Creating virtual environment...')
    subprocess.check_call([sys.executable, '-m', 'venv', str(VENV_DIR)])
    print('Virtual environment created at', VENV_DIR)


def install_dependencies():
    if not REQ_FILE.exists():
        raise FileNotFoundError('requirements.txt not found')
    py = python_executable()
    print(f'Installing dependencies using {py}...')
    subprocess.check_call([py, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([py, '-m', 'pip', 'install', '-r', str(REQ_FILE)])
    print('Dependencies installed.')


def create_env_file():
    if ENV_FILE.exists():
        print('.env already exists, skipping creation.')
        return
    if not ENV_EXAMPLE.exists():
        raise FileNotFoundError('.env.example not found')
    shutil.copy(ENV_EXAMPLE, ENV_FILE)
    print('Created .env from .env.example.')


def install(args):
    create_venv()
    install_dependencies()
    create_env_file()
    print('\nInstallation complete.')
    print('Edit .env and then run:')
    if os.name == 'nt':
        print('  start.bat')
    else:
        print('  ./start.sh')


def start(args):
    if not SRC_MAIN.exists():
        raise FileNotFoundError('src/main.py not found')
    if not ENV_FILE.exists():
        print('.env not found. Creating from example...')
        create_env_file()
    py = python_executable()
    print('Starting VPN bot...')
    subprocess.check_call([py, str(SRC_MAIN)])


def main():
    parser = argparse.ArgumentParser(description='VPN bot project manager')
    parser.add_argument('command', choices=['install', 'start', 'help'], nargs='?', default='help', help='Command to run')
    args = parser.parse_args()

    if args.command == 'install':
        install(args)
    elif args.command == 'start':
        start(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
