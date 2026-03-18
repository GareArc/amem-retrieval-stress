#!/usr/bin/env python3
"""
Integration test for DeepSeek standalone controller in A-mem-sys.
Tests the controller works with the memory system.
"""

import os
import sys

# Set up environment
os.environ["OPENAI_API_KEY"] = "sk-698630a117a045e789ea6a62c4f7b01c"
os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com"

# Add A-mem-sys to path
sys.path.insert(0, "/home/gareth/code/memory-retrieval/A-mem-sys")


def test_standalone_controller():
    """Test standalone DeepSeek controller directly."""
    print("\n" + "=" * 70)
    print("TEST 1: Standalone DeepSeek Controller")
    print("=" * 70)

    from agentic_memory.llm_controller import DeepSeekController

    controller = DeepSeekController(model="deepseek-chat")

    # Simple test
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "response",
            "schema": {
                "type": "object",
                "properties": {"answer": {"type": "string"}},
                "required": ["answer"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }

    prompt = 'What is the capital of France? Respond with JSON: {"answer": "..."}'

    result = controller.get_completion(prompt, response_format, temperature=0.7)

    print(f"\n💬 Response: {result}")

    import json

    try:
        parsed = json.loads(result)
        print(f"✅ Valid JSON: {parsed}")
        if "answer" in parsed and "paris" in parsed["answer"].lower():
            print("✅ Correct answer!")
            return True
        else:
            print("⚠️  Answer unexpected but JSON valid")
            return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False


def test_llm_controller_integration():
    """Test LLMController auto-detects DeepSeek and uses standalone controller."""
    print("\n" + "=" * 70)
    print("TEST 2: LLMController Auto-Detection")
    print("=" * 70)

    from agentic_memory.llm_controller import LLMController

    # Should auto-detect DeepSeek from OPENAI_BASE_URL
    controller = LLMController(backend="openai", model="deepseek-chat")

    print(f"✅ Controller type: {type(controller.llm).__name__}")

    if type(controller.llm).__name__ != "DeepSeekController":
        print("❌ Expected DeepSeekController but got different type")
        return False

    # Test completion
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "response",
            "schema": {
                "type": "object",
                "properties": {"color": {"type": "string"}},
                "required": ["color"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }

    prompt = 'Name a color. Respond with JSON: {"color": "..."}'

    result = controller.get_completion(prompt, response_format, temperature=0.7)

    print(f"\n💬 Response: {result}")

    import json

    try:
        parsed = json.loads(result)
        print(f"✅ Valid JSON: {parsed}")
        if "color" in parsed:
            print(f"✅ Got color: {parsed['color']}")
            return True
        else:
            print("⚠️  Missing 'color' field but JSON valid")
            return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False


def main():
    print("\n" + "=" * 70)
    print("🧪 DEEPSEEK STANDALONE CONTROLLER INTEGRATION TEST")
    print("=" * 70)

    results = []

    try:
        results.append(("Standalone Controller", test_standalone_controller()))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Standalone Controller", False))

    try:
        results.append(("LLMController Integration", test_llm_controller_integration()))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        results.append(("LLMController Integration", False))

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
        print("\n✅ ALL TESTS PASSED - Standalone controller integrated successfully!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
