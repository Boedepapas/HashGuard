"""Quick MalwareBazaar API key check.
Runs a single hash lookup and prints the result/status.
"""

import os
import requests

TEST_HASH = "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"  # EICAR SHA256 (public sample)


def main():
    key = os.getenv("MALWAREBAZAAR_API_KEY") or os.getenv("MalwareBazaar_Auth_KEY")
    print(f"Key loaded? {bool(key)}")
    if not key:
        print("No API key found in environment. Set MALWAREBAZAAR_API_KEY in .env or env vars.")
        return

    try:
        resp = requests.post(
            "https://mb-api.abuse.ch/api/v1/",
            headers={"Auth-Key": key},
            data={"query": "get_info", "hash": TEST_HASH},
            timeout=10,
        )
        print(f"Status: {resp.status_code}")
        print(resp.text[:800])
    except Exception as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    main()
