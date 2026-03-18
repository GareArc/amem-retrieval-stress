#!/usr/bin/env python3
"""
Standalone DeepSeek API test using only builtin packages.
Tests IPv4-only fix with a real LLM request.
"""

import socket
import json
import ssl
import urllib.request
import urllib.error
import os
import sys
import time

# ============================================================================
# IPv4-Only Patch (copied from llm_controller.py)
# ============================================================================

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
        print("🔧 IPv4-only mode enabled globally")


# ============================================================================
# Standalone DeepSeek Controller
# ============================================================================


class StandaloneDeepSeekController:
    """DeepSeek API client using only builtin packages."""

    def __init__(self, api_key=None, base_url="https://api.deepseek.com"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set OPENAI_API_KEY environment variable."
            )

        self.base_url = base_url.rstrip("/")

        # Apply IPv4-only patch
        _enable_ipv4_only()

    def chat_completion(
        self, messages, model="deepseek-chat", temperature=1.0, max_tokens=100
    ):
        """
        Send chat completion request to DeepSeek API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (default: deepseek-chat)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response dict with 'content', 'usage', and timing info
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        print(f"\n📤 Request to: {url}")
        print(f"📋 Model: {model}")
        print(f"💬 Messages: {len(messages)} message(s)")

        # Create request
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)

        try:
            start_time = time.time()

            # Send request
            with urllib.request.urlopen(req, timeout=120) as response:
                elapsed = time.time() - start_time

                # Parse response
                response_data = json.loads(response.read().decode("utf-8"))

                # Extract relevant info
                choice = response_data["choices"][0]
                content = choice["message"]["content"]
                usage = response_data.get("usage", {})

                print(f"\n✅ SUCCESS in {elapsed:.2f}s")
                print(
                    f"📊 Tokens: prompt={usage.get('prompt_tokens', 'N/A')}, "
                    f"completion={usage.get('completion_tokens', 'N/A')}, "
                    f"total={usage.get('total_tokens', 'N/A')}"
                )
                print(f"📝 Response length: {len(content)} chars")

                return {
                    "content": content,
                    "usage": usage,
                    "elapsed_seconds": elapsed,
                    "raw_response": response_data,
                }

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            print(f"\n❌ HTTP Error {e.code}: {e.reason}")
            print(f"📄 Response body: {error_body}")
            raise

        except urllib.error.URLError as e:
            elapsed = time.time() - start_time
            print(f"\n❌ URL Error after {elapsed:.2f}s: {e.reason}")
            raise

        except socket.timeout:
            elapsed = time.time() - start_time
            print(f"\n❌ TIMEOUT after {elapsed:.2f}s")
            raise


# ============================================================================
# Test Cases
# ============================================================================


def test_simple_question():
    """Test 1: Simple question-answer."""
    print("\n" + "=" * 70)
    print("TEST 1: Simple Question")
    print("=" * 70)

    controller = StandaloneDeepSeekController()

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2? Answer in one word."},
    ]

    result = controller.chat_completion(messages, max_tokens=10)

    print(f"\n💬 Response: {result['content']}")

    return True


def test_json_response():
    """Test 2: JSON structured output."""
    print("\n" + "=" * 70)
    print("TEST 2: JSON Structured Output")
    print("=" * 70)

    controller = StandaloneDeepSeekController()

    messages = [
        {"role": "system", "content": "You must respond with valid JSON only."},
        {
            "role": "user",
            "content": 'Return a JSON object with fields "color" and "number". Example: {"color": "blue", "number": 42}',
        },
    ]

    result = controller.chat_completion(messages, max_tokens=50)

    print(f"\n💬 Response: {result['content']}")

    # Validate JSON
    try:
        parsed = json.loads(result["content"])
        print(f"✅ Valid JSON: {parsed}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False


def test_connection_speed():
    """Test 3: Verify IPv4 is fast (not timing out)."""
    print("\n" + "=" * 70)
    print("TEST 3: Connection Speed (IPv4 Fix Verification)")
    print("=" * 70)

    controller = StandaloneDeepSeekController()

    messages = [{"role": "user", "content": "Say 'hello' in one word."}]

    result = controller.chat_completion(messages, max_tokens=5)

    elapsed = result["elapsed_seconds"]

    print(f"\n⏱️  Total request time: {elapsed:.2f}s")

    if elapsed < 10:
        print("✅ Fast connection - IPv4 working!")
        return True
    elif elapsed < 60:
        print("⚠️  Slow but successful - IPv4 may be working")
        return True
    else:
        print("❌ Very slow - IPv6 timeout likely occurring")
        return False


# ============================================================================
# Main
# ============================================================================


def main():
    print("\n" + "=" * 70)
    print("🧪 STANDALONE DEEPSEEK API TEST")
    print("Using only builtin packages (urllib, json, ssl, socket)")
    print("=" * 70)

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: OPENAI_API_KEY environment variable not set")
        print("   Export your DeepSeek API key:")
        print("   export OPENAI_API_KEY='sk-...'")
        sys.exit(1)

    print(f"\n🔑 API Key: {api_key[:8]}...{api_key[-4:]}")

    # Run tests
    results = []

    try:
        results.append(("Simple Question", test_simple_question()))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        results.append(("Simple Question", False))

    try:
        results.append(("JSON Output", test_json_response()))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        results.append(("JSON Output", False))

    try:
        results.append(("Connection Speed", test_connection_speed()))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        results.append(("Connection Speed", False))

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {test_name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - DeepSeek IPv4 fix verified!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
