import os
import sys

import requests


def main() -> None:
    proxy = os.environ.get("CRAWL_PROXY")
    if not proxy:
        sys.exit("CRAWL_PROXY environment variable is not set")

    proxies = {"http": proxy, "https": proxy}

    try:
        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        response.raise_for_status()
    except Exception as exc:  # broad: we just want to print any failure reason
        sys.exit(f"Proxy failed: {exc}")

    print("Proxy reachable:", response.json())


if __name__ == "__main__":
    main()
