#!/usr/bin/env python3
"""
Unit test for IPv4-only socket patching.
Tests the core IPv4 logic without requiring external dependencies.
"""

import socket
import sys


def test_ipv4_patch():
    """Test that IPv4-only patching works correctly."""

    print("=" * 80)
    print("Testing IPv4-Only Socket Patching")
    print("=" * 80)

    original_getaddrinfo = socket.getaddrinfo
    print(f"\n1. Original socket.getaddrinfo: {original_getaddrinfo}")

    def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
        """Force IPv4-only DNS resolution."""
        return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

    socket.getaddrinfo = getaddrinfo_ipv4_only
    print(f"2. After patching: {socket.getaddrinfo}")
    print(f"3. Patch applied: {socket.getaddrinfo != original_getaddrinfo}")

    print("\n" + "=" * 80)
    print("Testing DNS Resolution")
    print("=" * 80)

    try:
        results = socket.getaddrinfo(
            "api.deepseek.com", 443, socket.AF_UNSPEC, socket.SOCK_STREAM
        )

        print(f"\n✅ DNS resolution successful")
        print(f"   Addresses returned: {len(results)}")

        ipv4_count = 0
        ipv6_count = 0

        for result in results:
            family, socktype, proto, canonname, sockaddr = result
            if family == socket.AF_INET:
                ipv4_count += 1
                print(f"   IPv4: {sockaddr[0]}:{sockaddr[1]}")
            elif family == socket.AF_INET6:
                ipv6_count += 1
                print(f"   IPv6: {sockaddr[0]}:{sockaddr[1]}")

        print(f"\n📊 Results:")
        print(f"   IPv4 addresses: {ipv4_count}")
        print(f"   IPv6 addresses: {ipv6_count}")

        if ipv4_count > 0 and ipv6_count == 0:
            print("\n✅ SUCCESS: IPv4-only mode working correctly!")
            return True
        elif ipv6_count > 0:
            print(
                f"\n❌ FAILURE: IPv6 addresses returned (expected 0, got {ipv6_count})"
            )
            return False
        else:
            print("\n⚠️  WARNING: No addresses returned")
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        socket.getaddrinfo = original_getaddrinfo
        print(f"\n4. Restored original: {socket.getaddrinfo == original_getaddrinfo}")


def test_without_patch():
    """Test normal behavior without patch to show the difference."""

    print("\n" + "=" * 80)
    print("Testing WITHOUT Patch (for comparison)")
    print("=" * 80)

    try:
        results = socket.getaddrinfo(
            "api.deepseek.com", 443, socket.AF_UNSPEC, socket.SOCK_STREAM
        )

        ipv4_count = sum(1 for r in results if r[0] == socket.AF_INET)
        ipv6_count = sum(1 for r in results if r[0] == socket.AF_INET6)

        print(f"\n📊 Normal DNS resolution results:")
        print(f"   IPv4 addresses: {ipv4_count}")
        print(f"   IPv6 addresses: {ipv6_count}")

        if ipv6_count > 0:
            print(f"\n⚠️  IPv6 addresses present - this is why DeepSeek times out!")

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("\nIPv4-Only Socket Patch Unit Test\n")

    test_without_patch()

    success = test_ipv4_patch()

    print("\n" + "=" * 80)
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Tests failed!")
        sys.exit(1)
