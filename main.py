def load_emails():
    try:
        with open('email.txt', 'r') as f:
            emails = [line.strip() for line in f if line.strip()]
        if emails:
            print(f"{Fore.GREEN}Loaded {len(emails)} emails from email.txt\n{Fore.RESET}")
        return emails
    except FileNotFoundError:
        print(f"{Fore.YELLOW}email.txt not found, please provide an email list\n{Fore.RESET}")
        return []

class TeneoAutoref:
    def __init__(self, ref_code, proxy=None):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.ref_code = ref_code
        self.proxy = proxy
        if proxy:
            self.proxies = {
                'http': proxy,
                'https': proxy
            }
        else:
            self.proxies = None

    def get_next_email(self, emails, used_emails):
        for email in emails:
            if email not in used_emails:
                return email
        return None

    def generate_password(self):
        log_message(self.current_num, self.total, "Generating password...", "process")
        first_letter = random.choice(string.ascii_uppercase)
        lower_letters = ''.join(random.choices(string.ascii_lowercase, k=4))
        numbers = ''.join(random.choices(string.digits, k=3))
        password = f"{first_letter}{lower_letters}@{numbers}"
        log_message(self.current_num, self.total, "Password created successfully", "success")
        return password

    def check_user_exists(self, email):
        log_message(self.current_num, self.total, "Checking email availability...", "process")
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "x-api-key": "OwAG3kib1ivOJG4Y0OCZ8lJETa6ypvsDtGmdhcjA",
            "user-agent": self.ua.random,
            'Origin': 'https://dashboard.teneo.pro',
            'Referer': 'https://dashboard.teneo.pro/'
        }
        check_url = "https://auth.teneo.pro/api/check-user-exists"
        response = self.make_request('POST', check_url, headers=headers, json={"email": email}, timeout=60)
        
        if not response:
            return True
            
        exists = response.json().get("exists", True)
        
        if exists:
            log_message(self.current_num, self.total, "Email already registered", "error")
        else:
            log_message(self.current_num, self.total, "Email is available", "success")
        return exists

    def create_account(self, current_num, total, email):
        self.current_num = current_num
        self.total = total
        
        if self.check_user_exists(email):
            return None, f"Email {email} already registered"

        password = self.generate_password()
        register_response = self.register_account(email, password)
        if register_response.get("role") != "authenticated":
            return None, "Registration failed"

        verification_url = self.get_verification_link(email, email.split("@")[1])
        if not verification_url:
            return None, "Could not get verification link"

        if not self.verify_email(verification_url):
            return None, "Email verification failed"

        login_response = self.login(email, password)
        if "access_token" not in login_response:
            return None, "Login failed"
            
        wallet = self.link_wallet(login_response["access_token"], email) 
        if not wallet:
            return None, "Wallet linking failed"
        
        if not self.check_user_onboarded(login_response["access_token"]):
            return None, "Account active validation failed"

        return {
            "email": email,
            "password": password,
            "access_token": login_response["access_token"],
            "wallet_private_key": wallet['private_key'],
            "wallet_address": wallet['address']
        }, "Success"

def main():
    banner = f"""
{Fore.LIGHTCYAN_EX}╔═══════════════════════════════════════════╗
║            Teneo Autoreferral             ║
║       https://github.com/im-hanzou        ║
╚═══════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)    
    
    ref_code = input(f"{Fore.LIGHTYELLOW_EX}Enter referral code: {Fore.RESET}")
    emails = load_emails()
    proxies = load_proxies()
    
    if not emails:
        print(f"{Fore.RED}No emails found. Exiting.{Fore.RESET}")
        return

    used_emails = set()
    successful = 0
    
    with open("accounts.txt", "a") as f:
        for i, email in enumerate(emails, 1):
            print(f"{Fore.LIGHTWHITE_EX}{'-'*85}")
            log_message(i, len(emails), "Starting new referral process", "debug")

            current_proxy = get_random_proxy(proxies) if proxies else None
            generator = TeneoAutoref(ref_code, proxy=current_proxy)
            account, message = generator.create_account(i, len(emails), email)
            
            if account:
                f.write(f"Email: {account['email']}\n")
                f.write(f"Password: {account['password']}\n")
                f.write(f"Token: {account['access_token']}\n")
                f.write(f"Wallet Private Key: {account['wallet_private_key']}\n")
                f.write(f"Wallet Address: {account['wallet_address']}\n")
                f.write(f"Points: 51000\n")
                f.write("-" * 85 + "\n")
                f.flush()
                used_emails.add(email)
                successful += 1
                log_message(i, len(emails), "Account created successfully!", "debug")
            else:
                log_message(i, len(emails), f"Failed: {message}", "error")
    
    print(f"{Fore.GREEN}{successful}/{len(emails)} accounts created successfully!{Fore.RESET}")

if __name__ == "__main__":
    main()
        
