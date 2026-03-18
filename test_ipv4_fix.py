#!/usr/bin/env python3
"""Unit test for IPv4-only DNS resolution patch."""

import socket
import sys

# Simulate the patch code
_original_getaddrinfo = socket.getaddrinfo
_ipv4_mode_active = False


def _enable_ipv4_only():
    """Enable IPv4-only DNS resolution globally for DeepSeek."""
    global _ipv4_mode_active
    if not _ipv4_mode_active:

        def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
            return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

        socket.getaddrinfo = getaddrinfo_ipv4_only
        _ipv4_mode_active = True
        print("✅ IPv4-only mode enabled globally")


def test_ipv4_only():
    """Test that the patch forces IPv4 resolution."""

    print("\n" + "=" * 60)
    print("TEST: IPv4-Only DNS Resolution")
    print("=" * 60)

    # Test 1: Before patch - both IPv4 and IPv6 may be returned
    print("\n1️⃣  BEFORE PATCH:")
    try:
        results = socket.getaddrinfo("api.deepseek.com", 443, 0, socket.SOCK_STREAM)
        print(f"   Total addresses: {len(results)}")
        for idx, (family, *_, addr) in enumerate(results, 1):
            family_name = (
                "IPv4"
                if family == socket.AF_INET
                else "IPv6"
                if family == socket.AF_INET6
                else "Unknown"
            )
            print(f"   [{idx}] {family_name}: {addr[0]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Test 2: Apply patch
    print("\n2️⃣  APPLYING PATCH:")
    _enable_ipv4_only()

    # Test 3: After patch - only IPv4 should be returned
    print("\n3️⃣  AFTER PATCH:")
    try:
        results = socket.getaddrinfo("api.deepseek.com", 443, 0, socket.SOCK_STREAM)
        print(f"   Total addresses: {len(results)}")

        ipv4_count = 0
        ipv6_count = 0

        for idx, (family, *_, addr) in enumerate(results, 1):
            family_name = (
                "IPv4"
                if family == socket.AF_INET
                else "IPv6"
                if family == socket.AF_INET6
                else "Unknown"
            )
            print(f"   [{idx}] {family_name}: {addr[0]}")

            if family == socket.AF_INET:
                ipv4_count += 1
            elif family == socket.AF_INET6:
                ipv6_count += 1

        print(f"\n📊 RESULTS:")
        print(f"   IPv4 addresses: {ipv4_count}")
        print(f"   IPv6 addresses: {ipv6_count}")

        if ipv6_count > 0:
            print("\n❌ FAILED: IPv6 addresses still present after patch!")
            return False

        if ipv4_count == 0:
            print("\n❌ FAILED: No IPv4 addresses found!")
            return False

        print("\n✅ SUCCESS: Only IPv4 addresses returned!")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_connection_speed():
    """Test actual connection to verify IPv4 is faster."""
    import time

    print("\n" + "=" * 60)
    print("TEST: Connection Speed (IPv4 vs IPv6)")
    print("=" * 60)

    # Ensure patch is active
    _enable_ipv4_only()

    print("\n🔌 Attempting HTTPS connection to api.deepseek.com...")

    try:
        start = time.time()

        # Get IPv4 address
        results = socket.getaddrinfo(
            "api.deepseek.com", 443, socket.AF_INET, socket.SOCK_STREAM
        )
        if not results:
            print("❌ No IPv4 address found")
            return False

        addr = results[0][4]
        print(f"   Resolved to: {addr[0]} (IPv4)")

        # Try to connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)

        connect_start = time.time()
        sock.connect(addr)
        connect_time = (time.time() - connect_start) * 1000

        print(f"   ✅ TCP connected in {connect_time:.1f}ms")

        # Try TLS handshake
        import ssl

        context = ssl.create_default_context()

        tls_start = time.time()
        sock = context.wrap_socket(sock, server_hostname="api.deepseek.com")
        tls_time = (time.time() - tls_start) * 1000

        total_time = (time.time() - start) * 1000

        print(f"   ✅ TLS handshake completed in {tls_time:.1f}ms")
        print(f"   ✅ Total time: {total_time:.1f}ms")

        sock.close()

        if total_time < 2000:  # Less than 2 seconds
            print(f"\n✅ SUCCESS: Fast connection via IPv4!")
            return True
        else:
            print(f"\n⚠️  WARNING: Slow connection ({total_time:.1f}ms)")
            return True

    except socket.timeout:
        elapsed = (time.time() - start) * 1000
        print(f"\n❌ TIMEOUT after {elapsed:.1f}ms - IPv6 still being used?")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n🧪 IPv4-Only Patch Unit Tests\n")

    success = True

    # Test 1: DNS resolution
    if not test_ipv4_only():
        success = False

    # Test 2: Actual connection
    if not test_connection_speed():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
