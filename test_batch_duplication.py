#!/usr/bin/env python3
"""Test suite for optimized batch form duplication.

Tests verify:
1. Basic batch functionality with simple forms
2. All 12 question types preserve configurations
3. Performance improvements on large forms
4. Edge cases and error handling
"""

import os
import time
from forms_api import FormsAPI
from typing import Dict, Any, List


def print_test_header(test_name: str):
    """Print formatted test header."""
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)


def print_result(success: bool, message: str):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")


def verify_form_structure(api: FormsAPI, original_id: str, duplicate_id: str) -> tuple[bool, str]:
    """Verify duplicate has same structure as original."""
    try:
        original = api.get_form(original_id)
        duplicate = api.get_form(duplicate_id)

        original_items = original.get('items', [])
        duplicate_items = duplicate.get('items', [])

        # Check item count
        if len(original_items) != len(duplicate_items):
            return False, f"Item count mismatch: {len(original_items)} vs {len(duplicate_items)}"

        # Check each item type and title
        for i, (orig_item, dup_item) in enumerate(zip(original_items, duplicate_items)):
            orig_title = orig_item.get('title', '')
            dup_title = dup_item.get('title', '')

            if orig_title != dup_title:
                return False, f"Item {i} title mismatch: '{orig_title}' vs '{dup_title}'"

            # Check question type if present
            if 'questionItem' in orig_item and 'questionItem' in dup_item:
                orig_q = orig_item['questionItem']['question']
                dup_q = dup_item['questionItem']['question']

                # Check required field
                if orig_q.get('required', False) != dup_q.get('required', False):
                    return False, f"Item {i} required field mismatch"

        return True, f"All {len(original_items)} items verified successfully"

    except Exception as e:
        return False, f"Verification error: {e}"


def create_simple_test_form(api: FormsAPI) -> str:
    """Create a simple form with 5 questions for testing.

    Returns:
        Form ID of created test form
    """
    form = api.create_form(
        title="Test Form - Simple (5 Questions)",
        description="Simple test form for batch duplication validation"
    )
    form_id = form['formId']

    # Add 5 different question types
    questions = [
        {"type": "SHORT_ANSWER", "title": "What is your name?", "required": True},
        {"type": "PARAGRAPH", "title": "Tell us about yourself", "required": False},
        {"type": "MULTIPLE_CHOICE", "title": "Choose your department", "required": True,
         "options": ["Engineering", "HR", "Sales", "Marketing"]},
        {"type": "LINEAR_SCALE", "title": "Rate your satisfaction (1-5)", "required": True,
         "low": 1, "high": 5, "lowLabel": "Poor", "highLabel": "Excellent"},
        {"type": "CHECKBOXES", "title": "Select all that apply", "required": False,
         "options": ["Option A", "Option B", "Option C"]}
    ]

    for q in questions:
        api.add_question(form_id, **q)

    return form_id


def create_complex_test_form(api: FormsAPI) -> str:
    """Create a complex form with all 12 question types.

    Returns:
        Form ID of created test form
    """
    form = api.create_form(
        title="Test Form - Complex (All Question Types)",
        description="Complex test form with all 12 Google Forms question types"
    )
    form_id = form['formId']

    # All 12 question types
    questions = [
        {"type": "SHORT_ANSWER", "title": "Short answer question", "required": True},
        {"type": "PARAGRAPH", "title": "Paragraph question", "required": False},
        {"type": "MULTIPLE_CHOICE", "title": "Multiple choice question", "required": True,
         "options": ["Option 1", "Option 2", "Option 3"]},
        {"type": "CHECKBOXES", "title": "Checkboxes question", "required": False,
         "options": ["Check A", "Check B", "Check C"]},
        {"type": "DROPDOWN", "title": "Dropdown question", "required": True,
         "options": ["Choice 1", "Choice 2", "Choice 3"]},
        {"type": "LINEAR_SCALE", "title": "Linear scale question", "required": True,
         "low": 1, "high": 10, "lowLabel": "Low", "highLabel": "High"},
        {"type": "DATE", "title": "Date question", "required": False},
        {"type": "TIME", "title": "Time question", "required": False},
        {"type": "RATING", "title": "Rating question (stars)", "required": True, "high": 5},
        {"type": "MULTIPLE_CHOICE_GRID", "title": "Multiple choice grid", "required": False,
         "rows": ["Row 1", "Row 2", "Row 3"], "columns": ["Col A", "Col B", "Col C"]},
        {"type": "CHECKBOX_GRID", "title": "Checkbox grid", "required": False,
         "rows": ["Item 1", "Item 2"], "columns": ["Opt 1", "Opt 2", "Opt 3"]},
    ]

    for q in questions:
        api.add_question(form_id, **q)

    return form_id


def create_large_test_form(api: FormsAPI, num_questions: int = 50) -> str:
    """Create a large form with many questions for performance testing.

    Args:
        num_questions: Number of questions to create (default 50)

    Returns:
        Form ID of created test form
    """
    form = api.create_form(
        title=f"Test Form - Large ({num_questions} Questions)",
        description=f"Large test form with {num_questions} questions for performance testing"
    )
    form_id = form['formId']

    # Create mix of question types
    question_types = [
        {"type": "SHORT_ANSWER", "title": "Question {n}: Short answer", "required": False},
        {"type": "MULTIPLE_CHOICE", "title": "Question {n}: Choose one", "required": True,
         "options": ["A", "B", "C"]},
        {"type": "LINEAR_SCALE", "title": "Question {n}: Rate 1-5", "required": False,
         "low": 1, "high": 5},
    ]

    for i in range(num_questions):
        q = question_types[i % len(question_types)].copy()
        q['title'] = q['title'].format(n=i+1)
        api.add_question(form_id, **q)

    return form_id


def test_simple_form_batch_duplication(api: FormsAPI) -> bool:
    """Test 1: Verify basic batch functionality with simple form."""
    print_test_header("Simple Form (5 Questions) - Batch Duplication")

    try:
        # Create test form
        print("Creating test form with 5 questions...")
        original_id = create_simple_test_form(api)
        print(f"✓ Created form: {original_id}")

        # Duplicate using batch method
        print("\nDuplicating with BATCH method...")
        start_time = time.time()
        result = api.duplicate_form_batch(original_id, "Copy of Simple Test Form")
        batch_time = time.time() - start_time

        duplicate_id = result['newFormId']

        print(f"✓ Duplicated form: {duplicate_id}")
        print(f"  - API Calls: {result['apiCalls']}")
        print(f"  - Items Copied: {result['copiedItems']}/{result['totalItems']}")
        print(f"  - Execution Time: {result['executionTime']}")
        print(f"  - Method: {result['method']}")

        # Verify structure
        print("\nVerifying form structure...")
        verified, message = verify_form_structure(api, original_id, duplicate_id)
        print_result(verified, message)

        # Check API call efficiency
        expected_calls = 3  # get + create + batch(settings+items)
        if result['apiCalls'] == expected_calls:
            print_result(True, f"API calls optimized: {expected_calls} calls (expected)")
        else:
            print_result(False, f"API calls: {result['apiCalls']} (expected {expected_calls})")
            verified = False

        # Cleanup
        print("\nCleaning up test forms...")
        api.delete_form(original_id)
        api.delete_form(duplicate_id)
        print("✓ Test forms deleted")

        return verified

    except Exception as e:
        print_result(False, f"Test failed with error: {e}")
        return False


def test_complex_form_all_question_types(api: FormsAPI) -> bool:
    """Test 2: Validate all 12 question types in batch duplication."""
    print_test_header("Complex Form (All Question Types) - Batch Duplication")

    try:
        # Create complex test form
        print("Creating complex form with all 12 question types...")
        original_id = create_complex_test_form(api)
        print(f"✓ Created form: {original_id}")

        # Duplicate using batch method
        print("\nDuplicating with BATCH method...")
        result = api.duplicate_form_batch(original_id, "Copy of Complex Test Form")
        duplicate_id = result['newFormId']

        print(f"✓ Duplicated form: {duplicate_id}")
        print(f"  - Items Copied: {result['copiedItems']}/{result['totalItems']}")

        # Verify all question types preserved
        print("\nVerifying all question types and configurations...")
        verified, message = verify_form_structure(api, original_id, duplicate_id)
        print_result(verified, message)

        # Cleanup
        print("\nCleaning up test forms...")
        api.delete_form(original_id)
        api.delete_form(duplicate_id)
        print("✓ Test forms deleted")

        return verified

    except Exception as e:
        print_result(False, f"Test failed with error: {e}")
        return False


def test_performance_comparison(api: FormsAPI, num_questions: int = 20) -> bool:
    """Test 3: Compare batch vs legacy performance."""
    print_test_header(f"Performance Comparison ({num_questions} Questions)")

    try:
        # Create test form
        print(f"Creating test form with {num_questions} questions...")
        original_id = create_large_test_form(api, num_questions)
        print(f"✓ Created form: {original_id}")

        # Test BATCH method
        print("\n--- BATCH Method ---")
        start_time = time.time()
        batch_result = api.duplicate_form_batch(original_id, f"Batch Copy ({num_questions}q)")
        batch_time = time.time() - start_time

        print(f"✓ Duplicated: {batch_result['newFormId']}")
        print(f"  - API Calls: {batch_result['apiCalls']}")
        print(f"  - Execution Time: {batch_time:.2f}s")
        print(f"  - Items: {batch_result['copiedItems']}/{batch_result['totalItems']}")

        # Test LEGACY method
        print("\n--- LEGACY Method ---")
        start_time = time.time()
        legacy_result = api.duplicate_form_legacy(original_id, f"Legacy Copy ({num_questions}q)")
        legacy_time = time.time() - start_time

        print(f"✓ Duplicated: {legacy_result['newFormId']}")
        print(f"  - API Calls: {legacy_result['apiCalls']}")
        print(f"  - Execution Time: {legacy_time:.2f}s")
        print(f"  - Items: {legacy_result['copiedItems']}/{legacy_result['totalItems']}")

        # Calculate improvement
        print("\n--- Performance Analysis ---")
        api_improvement = ((legacy_result['apiCalls'] - batch_result['apiCalls']) /
                          legacy_result['apiCalls'] * 100)
        time_improvement = ((legacy_time - batch_time) / legacy_time * 100) if legacy_time > 0 else 0

        print(f"API Call Reduction: {api_improvement:.1f}% ({legacy_result['apiCalls']} → {batch_result['apiCalls']} calls)")
        print(f"Time Improvement: {time_improvement:.1f}% ({legacy_time:.2f}s → {batch_time:.2f}s)")

        success = (batch_result['apiCalls'] <= 3 and
                  batch_result['copiedItems'] == batch_result['totalItems'])

        print_result(success, f"Batch method {'passed' if success else 'failed'} performance requirements")

        # Cleanup
        print("\nCleaning up test forms...")
        api.delete_form(original_id)
        api.delete_form(batch_result['newFormId'])
        api.delete_form(legacy_result['newFormId'])
        print("✓ Test forms deleted")

        return success

    except Exception as e:
        print_result(False, f"Test failed with error: {e}")
        return False


def test_edge_cases(api: FormsAPI) -> bool:
    """Test 4: Validate edge cases and error handling."""
    print_test_header("Edge Cases and Error Handling")

    all_passed = True

    try:
        # Test 4a: Empty form (no questions)
        print("\n--- Test 4a: Empty Form ---")
        empty_form = api.create_form("Empty Test Form", "Form with no questions")
        empty_id = empty_form['formId']

        result = api.duplicate_form_batch(empty_id, "Copy of Empty Form")
        success = (result['copiedItems'] == 0 and
                  result['totalItems'] == 0 and
                  result['apiCalls'] == 2)  # Just get + create, no batch needed

        print_result(success, f"Empty form handling: {result['copiedItems']} items, {result['apiCalls']} API calls")
        all_passed = all_passed and success

        api.delete_form(empty_id)
        api.delete_form(result['newFormId'])

        # Test 4b: Form with sections
        print("\n--- Test 4b: Form with Sections ---")
        section_form = api.create_form("Sectioned Test Form", "Form with page breaks")
        section_id = section_form['formId']

        api.add_question(section_id, "SHORT_ANSWER", "Question 1")
        api.add_section(section_id, "Section 2", "Second page")
        api.add_question(section_id, "SHORT_ANSWER", "Question 2")

        result = api.duplicate_form_batch(section_id, "Copy of Sectioned Form")
        success = result['copiedItems'] == 3  # 2 questions + 1 section

        print_result(success, f"Sectioned form handling: {result['copiedItems']} items copied")
        all_passed = all_passed and success

        api.delete_form(section_id)
        api.delete_form(result['newFormId'])

        return all_passed

    except Exception as e:
        print_result(False, f"Edge case testing failed: {e}")
        return False


def run_all_tests():
    """Run complete test suite for batch duplication."""
    print("\n" + "="*70)
    print("GOOGLE FORMS BATCH DUPLICATION TEST SUITE")
    print("="*70)
    print("\nInitializing Forms API...")

    try:
        api = FormsAPI()
        print("✓ Forms API initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Forms API: {e}")
        print("\nPlease ensure:")
        print("1. .env file exists with valid credentials")
        print("2. Google Forms API is enabled")
        print("3. OAuth tokens are valid")
        return

    # Run test suite
    results = {
        "Test 1: Simple Form (5 questions)": test_simple_form_batch_duplication(api),
        "Test 2: Complex Form (all types)": test_complex_form_all_question_types(api),
        "Test 3: Performance Comparison": test_performance_comparison(api, 20),
        "Test 4: Edge Cases": test_edge_cases(api)
    }

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "-"*70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*70)

    if passed == total:
        print("\n🎉 All tests passed! Batch duplication is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")


if __name__ == "__main__":
    run_all_tests()
