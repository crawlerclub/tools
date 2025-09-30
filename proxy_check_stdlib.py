import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from collections import Counter


def get_ip_through_proxy(proxy_url: str, timeout: int = 10) -> str:
    """Get IP address through proxy using standard library."""
    # Parse proxy URL to extract credentials
    parsed = urllib.parse.urlparse(proxy_url)

    # Create proxy handler
    proxy_handler = urllib.request.ProxyHandler({
        'http': proxy_url,
        'https': proxy_url
    })

    # Create opener with proxy handler
    opener = urllib.request.build_opener(proxy_handler)

    # Create request
    req = urllib.request.Request('https://httpbin.org/ip')
    req.add_header('User-Agent', 'Mozilla/5.0 (compatible; proxy-check/1.0)')

    try:
        # Make request through proxy
        with opener.open(req, timeout=timeout) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                ip_data = json.loads(data)
                return ip_data.get("origin", "unknown")
            else:
                raise Exception(f"HTTP {response.status}")
    except Exception as e:
        raise Exception(f"Proxy request failed: {e}")


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

    print(f"Testing proxy with {num_requests} consecutive requests...")
    print(f"Proxy: {proxy}")
    print("-" * 50)

    ips = []
    success_count = 0
    failure_count = 0
    start_time = time.time()

    for i in range(num_requests):
        try:
            origin_ip = get_ip_through_proxy(proxy, timeout=10)
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