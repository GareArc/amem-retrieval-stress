#!/usr/bin/env python3
"""
Debug test to see if socket.getaddrinfo patch actually works with urllib.
"""

import socket
import urllib.request
import time

print("\n" + "=" * 70)
print("DNS RESOLUTION DEBUG TEST")
print("=" * 70)

# Test 1: Before patch
print("\n1️⃣  BEFORE PATCH:")
print("   Calling socket.getaddrinfo('api.deepseek.com', 443)...")
results = socket.getaddrinfo("api.deepseek.com", 443, 0, socket.SOCK_STREAM)
for family, *_, addr in results:
    family_name = "IPv4" if family == socket.AF_INET else "IPv6"
    print(f"   - {family_name}: {addr[0]}")

# Apply patch
print("\n2️⃣  APPLYING PATCH:")
_original_getaddrinfo = socket.getaddrinfo


def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    print(f"   [PATCH CALLED] host={host}, port={port}, family={family}")
    result = _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
    print(f"   [PATCH RETURNS] {len(result)} IPv4 address(es)")
    return result


socket.getaddrinfo = getaddrinfo_ipv4_only
print("   ✅ socket.getaddrinfo patched")

# Test 2: After patch - direct socket call
print("\n3️⃣  AFTER PATCH - Direct socket.getaddrinfo():")
print("   Calling socket.getaddrinfo('api.deepseek.com', 443)...")
results = socket.getaddrinfo("api.deepseek.com", 443, 0, socket.SOCK_STREAM)
print(f"   Got {len(results)} result(s)")

# Test 3: After patch - urllib usage
print("\n4️⃣  AFTER PATCH - urllib.request.urlopen():")
print("   Creating request to https://api.deepseek.com/")
print("   Watch for '[PATCH CALLED]' messages above...\n")

try:
    req = urllib.request.Request("https://api.deepseek.com/")
    req.add_header("User-Agent", "DNSDebugTest/1.0")

    start = time.time()
    with urllib.request.urlopen(req, timeout=10) as response:
        elapsed = time.time() - start
        print(f"\n   ✅ urllib connection succeeded in {elapsed:.2f}s")
        print(f"   Status: {response.status}")
except Exception as e:
    elapsed = time.time() - start
    print(f"\n   ❌ urllib failed after {elapsed:.2f}s: {e}")

print("\n" + "=" * 70)
print("ANALYSIS:")
print("=" * 70)
print("If you see '[PATCH CALLED]' during urllib test → Patch works")
print("If you DON'T see '[PATCH CALLED]' → urllib bypasses socket.getaddrinfo")
print("=" * 70)
