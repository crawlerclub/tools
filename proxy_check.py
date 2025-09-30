import os
import sys
import time
from collections import Counter

import requests


def main() -> None:
    proxy = os.environ.get("CRAWL_PROXY")
    if not proxy:
        sys.exit("CRAWL_PROXY environment variable is not set")

    # Get number of requests from command line arg, default to 100
    num_requests = 100
    if len(sys.argv) > 1:
        try:
            num_requests = int(sys.argv[1])
            if num_requests <= 0:
                raise ValueError("Number must be positive")
        except ValueError:
            sys.exit("Invalid number of requests. Please provide a positive integer.")

    proxies = {"http": proxy, "https": proxy}

    print(f"Testing proxy with {num_requests} consecutive requests...")
    print(f"Proxy: {proxy}")
    print("-" * 50)

    ips = []
    success_count = 0
    failure_count = 0
    start_time = time.time()

    for i in range(num_requests):
        try:
            response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
            response.raise_for_status()

            ip_data = response.json()
            origin_ip = ip_data.get("origin", "unknown")
            ips.append(origin_ip)
            success_count += 1

            if i < 5 or i % 20 == 19:  # Show first 5 and every 20th request
                print(f"Request {i+1:3d}: {origin_ip}")

        except Exception as exc:
            failure_count += 1
            print(f"Request {i+1:3d}: FAILED - {exc}")

    end_time = time.time()
    duration = end_time - start_time

    # Analysis
    print("-" * 50)
    print("PROXY ANALYSIS RESULTS:")
    print(f"Total requests: {num_requests}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"Success rate: {success_count/num_requests*100:.1f}%")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Average time per request: {duration/num_requests:.3f} seconds")

    if ips:
        ip_counts = Counter(ips)
        unique_ips = len(ip_counts)

        print(f"\nUnique IPs detected: {unique_ips}")

        if unique_ips == 1:
            print("✅ Proxy uses consistent IP address")
        else:
            print("🔄 Proxy rotates IP addresses")
            print("IP distribution:")
            for ip, count in ip_counts.most_common():
                percentage = count / len(ips) * 100
                print(f"  {ip}: {count} times ({percentage:.1f}%)")

    if failure_count > 0:
        print(f"\n⚠️  {failure_count} requests failed - proxy may be unstable")


if __name__ == "__main__":
    main()
