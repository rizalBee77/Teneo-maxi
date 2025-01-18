import requests
import json
import random
import string
import names
import time
import secrets
from datetime import datetime
from eth_account import Account
from eth_account.messages import encode_defunct
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
from websocket import create_connection

init(autoreset=True)


# Fungsi untuk memuat email dari file
def load_emails():
    try:
        with open('email.txt', 'r') as f:
            emails = [line.strip() for line in f if line.strip()]
        return emails
    except FileNotFoundError:
        print(f"{Fore.RED}File email.txt tidak ditemukan. Harap buat file tersebut dengan daftar email.{Fore.RESET}")
        return []


# Fungsi untuk memuat proxy
def load_proxies():
    try:
        with open('proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies
    except FileNotFoundError:
        print(f"{Fore.YELLOW}File proxies.txt tidak ditemukan. Proses tanpa proxy.{Fore.RESET}")
        return []


# Fungsi untuk mengambil proxy acak
def get_random_proxy(proxies):
    return random.choice(proxies) if proxies else None


# Fungsi untuk mencetak log
def log_message(account_num=None, total=None, message="", message_type="info"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    account_status = f"{account_num}/{total}" if account_num and total else ""
    colors = {
        "info": Fore.LIGHTWHITE_EX,
        "success": Fore.LIGHTGREEN_EX,
        "error": Fore.LIGHTRED_EX,
        "warning": Fore.LIGHTYELLOW_EX,
        "process": Fore.LIGHTCYAN_EX,
        "debug": Fore.LIGHTMAGENTA_EX
    }
    log_color = colors.get(message_type, Fore.LIGHTWHITE_EX)
    print(f"{Fore.WHITE}[{Style.DIM}{timestamp}{Style.RESET_ALL}{Fore.WHITE}] "
          f"[{Fore.LIGHTYELLOW_EX}{account_status}{Fore.WHITE}] "
          f"{log_color}{message}")


# Fungsi untuk membuat dompet Ethereum
def generate_ethereum_wallet():
    private_key = '0x' + secrets.token_hex(32)
    account = Account.from_key(private_key)
    return {'address': account.address, 'private_key': private_key}


# Fungsi untuk membuat tanda tangan dompet
def create_wallet_signature(wallet, message):
    account = Account.from_key(wallet['private_key'])
    signable_message = encode_defunct(text=message)
    signed_message = account.sign_message(signable_message)
    return signed_message.signature.hex()


class TeneoAutoref:
    def __init__(self, ref_code, email_list, proxy=None):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.ref_code = ref_code
        self.emails = email_list
        self.proxies = {'http': proxy, 'https': proxy} if proxy else None

    def make_request(self, method, url, **kwargs):
        try:
            kwargs['proxies'] = self.proxies
            kwargs['timeout'] = 60
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            log_message(None, None, f"Request failed: {str(e)}", "error")
            return None

    def generate_password(self):
        return f"{random.choice(string.ascii_uppercase)}{''.join(random.choices(string.ascii_lowercase, k=6))}@{''.join(random.choices(string.digits, k=4))}"

    def register_account(self, email, password):
        log_message(None, None, f"Registering account: {email}", "process")
        headers = {'User-Agent': self.ua.random}
        data = {
            "email": email,
            "password": password,
            "data": {"invited_by": self.ref_code}
        }
        response = self.make_request('POST', 'https://node-b.teneo.pro/auth/v1/signup', headers=headers, json=data)
        if response:
            log_message(None, None, f"Account registered successfully: {email}", "success")
        else:
            log_message(None, None, f"Account registration failed: {email}", "error")
        return response

    def main_process(self):
        for i, email in enumerate(self.emails):
            log_message(i + 1, len(self.emails), "Starting referral process", "debug")
            password = self.generate_password()
            self.register_account(email, password)


def main():
    print(f"{Fore.LIGHTCYAN_EX}Teneo Autoreferral Script{Fore.RESET}")
    ref_code = input("Enter referral code: ")
    emails = load_emails()

    if not emails:
        print(f"{Fore.RED}Email list is empty. Please add emails to email.txt.{Fore.RESET}")
        return

    proxies = load_proxies()

    teneo = TeneoAutoref(ref_code, email_list=emails, proxy=get_random_proxy(proxies))
    teneo.main_process()


if __name__ == "__main__":
    main()
    
