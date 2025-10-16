"""
Test validation edge cases to ensure robustness
"""
import sys
sys.path.insert(0, '/home/gir/Desktop/programming/project1-tds-t3-2025')

from utils.validation import validate_request

# Test cases
test_cases = [
    {
        "name": "Valid request",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": "calculator-app",
            "round": 1,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
            "checks": ["Has MIT license"],
        },
        "expected": True
    },
    {
        "name": "Empty task name",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": "",
            "round": 1,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": False
    },
    {
        "name": "Task with spaces (invalid)",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": "calculator app",
            "round": 1,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": False
    },
    {
        "name": "Task with special chars (invalid)",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": "calculator@app!",
            "round": 1,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": False
    },
    {
        "name": "Task starts with period (invalid)",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": ".calculator",
            "round": 1,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": False
    },
    {
        "name": "Task is just '.' (invalid)",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": ".",
            "round": 1,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": False
    },
    {
        "name": "Valid task with hyphen, underscore, period",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": "calculator_app-v1.0",
            "round": 1,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": True
    },
    {
        "name": "Task too long (invalid)",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": "a" * 101,
            "round": 1,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": False
    },
    {
        "name": "Missing task field",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "round": 1,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": False
    },
    {
        "name": "Round is 0 (invalid)",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": "calculator",
            "round": 0,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": False
    },
    {
        "name": "Round is negative (invalid)",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": "calculator",
            "round": -1,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": False
    },
    {
        "name": "Round is string (invalid)",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": "calculator",
            "round": "1",
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": False
    },
    {
        "name": "Missing checks (should pass with warning)",
        "data": {
            "email": "test@example.com",
            "secret": "test-secret",
            "task": "calculator",
            "round": 1,
            "nonce": "abc123",
            "brief": "Create a calculator",
            "evaluation_url": "https://example.com/eval",
        },
        "expected": True
    },
]

# Note: This test won't actually verify secrets since we don't have the .env loaded
# It will test the validation logic structure

print("=" * 80)
print("VALIDATION TEST SUITE")
print("=" * 80)

passed = 0
failed = 0

for test in test_cases:
    is_valid, message = validate_request(test["data"])
    
    if is_valid == test["expected"]:
        print(f"✅ PASS: {test['name']}")
        passed += 1
    else:
        print(f"❌ FAIL: {test['name']}")
        print(f"   Expected: {test['expected']}, Got: {is_valid}")
        print(f"   Message: {message}")
        failed += 1

print("=" * 80)
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 80)

if failed == 0:
    print("🎉 ALL TESTS PASSED!")
else:
    print(f"⚠️  {failed} test(s) failed")
