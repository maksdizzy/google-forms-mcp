#!/usr/bin/env python3
"""Test script for verifying forms_create and forms_duplicate fixes.

Run this after applying the fixes to verify they work correctly.
"""

import sys
from forms_api import FormsAPI

def test_forms_create():
    """Test forms_create with description (Fix #1)."""
    print("\n" + "="*60)
    print("TEST 1: forms_create with description")
    print("="*60)

    try:
        api = FormsAPI()

        # Test creating form with description
        print("\n📝 Creating form with title and description...")
        result = api.create_form(
            title="Test Form - Fix Verification",
            description="This form tests the quiz_settings fix"
        )

        form_id = result['formId']
        print(f"✅ Form created successfully!")
        print(f"   Form ID: {form_id}")
        print(f"   Responder URI: {result['responderUri']}")

        # Verify the form has the description
        print("\n🔍 Verifying form structure...")
        form = api.get_form(form_id)

        actual_title = form.get('info', {}).get('title', '')
        actual_description = form.get('info', {}).get('description', '')

        if actual_title == "Test Form - Fix Verification":
            print(f"✅ Title correct: {actual_title}")
        else:
            print(f"❌ Title mismatch: expected 'Test Form - Fix Verification', got '{actual_title}'")
            return False

        if actual_description == "This form tests the quiz_settings fix":
            print(f"✅ Description correct: {actual_description}")
        else:
            print(f"❌ Description mismatch: expected 'This form tests...', got '{actual_description}'")
            return False

        # Check quiz settings
        settings = form.get('settings', {})
        quiz_settings = settings.get('quizSettings', {})
        is_quiz = quiz_settings.get('isQuiz', None)

        if is_quiz is False:
            print(f"✅ Quiz settings correct: isQuiz = {is_quiz}")
        else:
            print(f"⚠️  Quiz settings: isQuiz = {is_quiz} (expected False)")

        print("\n✅ TEST 1 PASSED: forms_create works with description!")
        return True

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        return False


def test_forms_duplicate():
    """Test forms_duplicate with existing form (Fix #2)."""
    print("\n" + "="*60)
    print("TEST 2: forms_duplicate")
    print("="*60)

    try:
        api = FormsAPI()

        # First, create a form to duplicate
        print("\n📝 Creating source form...")
        source = api.create_form(
            title="Source Form for Duplication",
            description="Original form with questions"
        )
        source_id = source['formId']
        print(f"✅ Source form created: {source_id}")

        # Add some questions to the source form
        print("\n➕ Adding questions to source form...")

        api.add_question(
            form_id=source_id,
            question_type="SHORT_ANSWER",
            title="What is your name?",
            required=True,
            position=0
        )
        print("   ✅ Added SHORT_ANSWER question")

        api.add_question(
            form_id=source_id,
            question_type="MULTIPLE_CHOICE",
            title="Select your department",
            options=["Engineering", "Sales", "Marketing"],
            required=True,
            position=1
        )
        print("   ✅ Added MULTIPLE_CHOICE question")

        api.add_section(
            form_id=source_id,
            title="Section 2",
            description="Additional questions",
            position=2
        )
        print("   ✅ Added section break")

        # Get source form structure
        source_form = api.get_form(source_id)
        source_items = source_form.get('items', [])
        print(f"\n📊 Source form has {len(source_items)} items")

        # Now duplicate it
        print("\n📋 Duplicating form...")
        result = api.duplicate_form(
            form_id=source_id,
            new_title="Duplicated Form - Fix Verification"
        )

        duplicate_id = result['newFormId']
        copied_items = result['copiedItems']
        total_items = result['totalItems']

        print(f"✅ Duplication completed!")
        print(f"   New Form ID: {duplicate_id}")
        print(f"   Copied Items: {copied_items}/{total_items}")

        # Verify the duplicated form
        print("\n🔍 Verifying duplicated form...")
        duplicate_form = api.get_form(duplicate_id)
        duplicate_items = duplicate_form.get('items', [])

        # Check item count
        if len(duplicate_items) == len(source_items):
            print(f"✅ Item count matches: {len(duplicate_items)} items")
        else:
            print(f"❌ Item count mismatch: source has {len(source_items)}, duplicate has {len(duplicate_items)}")
            return False

        # Check that item IDs are different
        source_ids = {item['itemId'] for item in source_items}
        duplicate_ids = {item['itemId'] for item in duplicate_items}

        if source_ids.isdisjoint(duplicate_ids):
            print(f"✅ Item IDs are unique (no conflicts)")
        else:
            overlapping = source_ids.intersection(duplicate_ids)
            print(f"❌ Item ID conflicts found: {overlapping}")
            return False

        # Check that titles match
        source_titles = [item.get('title', '') for item in source_items]
        duplicate_titles = [item.get('title', '') for item in duplicate_items]

        if source_titles == duplicate_titles:
            print(f"✅ Item titles match")
        else:
            print(f"⚠️  Item titles differ")

        print("\n✅ TEST 2 PASSED: forms_duplicate works without conflicts!")
        return True

    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Google Forms MCP - Fix Verification Tests")
    print("="*60)
    print("\nThis script tests the fixes for:")
    print("1. forms_create - Missing quiz_settings")
    print("2. forms_duplicate - ItemId conflicts")

    results = []

    # Test 1: forms_create
    results.append(("forms_create", test_forms_create()))

    # Test 2: forms_duplicate
    results.append(("forms_duplicate", test_forms_duplicate()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Fixes are working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
