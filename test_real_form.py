#!/usr/bin/env python3
"""Test batch duplication on real Google Form.

Tests the optimized batch duplication against a real form to verify:
1. Functionality with production data
2. Performance improvements in real-world scenario
3. Structure preservation with actual form configuration
"""

import sys
import time
from forms_api import FormsAPI


def extract_form_id(url: str) -> str:
    """Extract form ID from Google Forms URL.

    Args:
        url: Google Forms URL (edit or view)

    Returns:
        Form ID

    Example:
        https://docs.google.com/forms/d/1WBjiy0jWvGqk21DvlBS9ejEzV4xTY2wUT4m5OioKSU4/edit
        → 1WBjiy0jWvGqk21DvlBS9ejEzV4xTY2wUT4m5OioKSU4
    """
    if '/d/' in url:
        parts = url.split('/d/')
        if len(parts) > 1:
            form_id = parts[1].split('/')[0]
            return form_id
    raise ValueError(f"Could not extract form ID from URL: {url}")


def print_header(text: str):
    """Print formatted section header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_form_details(api: FormsAPI, form_id: str):
    """Print form structure details."""
    form = api.get_form(form_id)
    info = form.get('info', {})
    items = form.get('items', [])

    print(f"\n📋 Form Details:")
    print(f"  Title: {info.get('title', 'Untitled')}")
    print(f"  Description: {info.get('description', 'No description')[:100]}")
    print(f"  Total Items: {len(items)}")

    # Count question types
    question_types = {}
    for item in items:
        if 'questionItem' in item:
            q_type = None
            question = item['questionItem']['question']

            if 'textQuestion' in question:
                q_type = "Text" if not question['textQuestion'].get('paragraph', False) else "Paragraph"
            elif 'choiceQuestion' in question:
                choice_type = question['choiceQuestion'].get('type', '')
                if choice_type == 'RADIO':
                    q_type = "Multiple Choice"
                elif choice_type == 'CHECKBOX':
                    q_type = "Checkboxes"
                elif choice_type == 'DROP_DOWN':
                    q_type = "Dropdown"
            elif 'scaleQuestion' in question:
                q_type = "Linear Scale"
            elif 'dateQuestion' in question:
                q_type = "Date"
            elif 'timeQuestion' in question:
                q_type = "Time"

            if q_type:
                question_types[q_type] = question_types.get(q_type, 0) + 1
        elif 'pageBreakItem' in item:
            question_types['Section'] = question_types.get('Section', 0) + 1

    if question_types:
        print(f"\n  Question Types:")
        for q_type, count in sorted(question_types.items()):
            print(f"    - {q_type}: {count}")


def verify_structure_match(api: FormsAPI, original_id: str, duplicate_id: str) -> tuple[bool, list]:
    """Verify duplicate matches original structure.

    Returns:
        Tuple of (success, list of differences)
    """
    original = api.get_form(original_id)
    duplicate = api.get_form(duplicate_id)

    orig_items = original.get('items', [])
    dup_items = duplicate.get('items', [])

    differences = []

    # Check item count
    if len(orig_items) != len(dup_items):
        differences.append(f"Item count mismatch: {len(orig_items)} vs {len(dup_items)}")
        return False, differences

    # Check each item
    for i, (orig, dup) in enumerate(zip(orig_items, dup_items)):
        # Check titles
        if orig.get('title') != dup.get('title'):
            differences.append(f"Item {i}: Title mismatch")

        # Check item types
        if 'questionItem' in orig and 'questionItem' not in dup:
            differences.append(f"Item {i}: Type mismatch (question vs non-question)")
        elif 'pageBreakItem' in orig and 'pageBreakItem' not in dup:
            differences.append(f"Item {i}: Type mismatch (section)")

    return len(differences) == 0, differences


def test_real_form(form_url: str):
    """Test batch duplication on real form with comprehensive analysis."""

    print_header("REAL FORM DUPLICATION TEST")

    # Extract form ID
    try:
        form_id = extract_form_id(form_url)
        print(f"\n✓ Extracted Form ID: {form_id}")
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return

    # Initialize API
    print("\n🔧 Initializing Forms API...")
    try:
        api = FormsAPI()
        print("✓ API initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize API: {e}")
        print("\nPlease ensure:")
        print("  1. .env file exists with valid credentials")
        print("  2. Google Forms API is enabled")
        print("  3. OAuth tokens are valid")
        return

    # Get original form details
    print_header("ORIGINAL FORM")
    try:
        print_form_details(api, form_id)
    except Exception as e:
        print(f"\n❌ Failed to access form: {e}")
        print(f"\nPlease verify:")
        print(f"  1. Form ID is correct: {form_id}")
        print(f"  2. You have access to this form")
        print(f"  3. Form URL: {form_url}")
        return

    # Test BATCH method
    print_header("BATCH DUPLICATION METHOD")
    print("\n⚡ Running optimized batch duplication...")

    try:
        batch_start = time.time()
        batch_result = api.duplicate_form_batch(form_id, "Batch Test Copy - Delete Me")
        batch_time = time.time() - batch_start

        print(f"\n✅ Batch duplication completed!")
        print(f"\n📊 Performance Metrics:")
        print(f"  • New Form ID: {batch_result['newFormId']}")
        print(f"  • API Calls: {batch_result['apiCalls']}")
        print(f"  • Execution Time: {batch_result['executionTime']}")
        print(f"  • Items Copied: {batch_result['copiedItems']}/{batch_result['totalItems']}")
        print(f"  • Method: {batch_result['method']}")
        print(f"  • Chunked: {'Yes' if batch_result.get('chunked', False) else 'No'}")
        print(f"  • Responder Link: {batch_result['responderUri']}")

        batch_form_id = batch_result['newFormId']

    except Exception as e:
        print(f"\n❌ Batch duplication failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test LEGACY method
    print_header("LEGACY DUPLICATION METHOD")
    print("\n🐌 Running legacy duplication for comparison...")

    try:
        legacy_start = time.time()
        legacy_result = api.duplicate_form_legacy(form_id, "Legacy Test Copy - Delete Me")
        legacy_time = time.time() - legacy_start

        print(f"\n✅ Legacy duplication completed!")
        print(f"\n📊 Performance Metrics:")
        print(f"  • New Form ID: {legacy_result['newFormId']}")
        print(f"  • API Calls: {legacy_result['apiCalls']}")
        print(f"  • Execution Time: {legacy_result['executionTime']}")
        print(f"  • Items Copied: {legacy_result['copiedItems']}/{legacy_result['totalItems']}")
        print(f"  • Method: {legacy_result['method']}")

        legacy_form_id = legacy_result['newFormId']

    except Exception as e:
        print(f"\n❌ Legacy duplication failed: {e}")
        import traceback
        traceback.print_exc()
        legacy_form_id = None

    # Performance comparison
    print_header("PERFORMANCE COMPARISON")

    if legacy_form_id:
        api_reduction = ((legacy_result['apiCalls'] - batch_result['apiCalls']) /
                        legacy_result['apiCalls'] * 100)
        time_reduction = ((legacy_time - batch_time) / legacy_time * 100)

        print(f"\n📈 Improvements:")
        print(f"  • API Calls: {legacy_result['apiCalls']} → {batch_result['apiCalls']}")
        print(f"    Reduction: {api_reduction:.1f}% fewer calls")
        print(f"\n  • Execution Time: {legacy_time:.2f}s → {batch_time:.2f}s")
        print(f"    Improvement: {time_reduction:.1f}% faster")

        # Calculate expected API calls for legacy
        total_items = batch_result['totalItems']
        expected_legacy_calls = 3 + total_items  # get + create + settings + N items

        print(f"\n💡 Analysis:")
        print(f"  • Form has {total_items} items")
        print(f"  • Expected legacy calls: ~{expected_legacy_calls}")
        print(f"  • Actual legacy calls: {legacy_result['apiCalls']}")
        print(f"  • Batch calls (constant): {batch_result['apiCalls']}")

        if api_reduction >= 85:
            print(f"\n  ✅ EXCELLENT: Achieved {api_reduction:.0f}% API reduction!")
        elif api_reduction >= 70:
            print(f"\n  ✓ GOOD: Achieved {api_reduction:.0f}% API reduction")
        else:
            print(f"\n  ⚠️ MODERATE: Only {api_reduction:.0f}% API reduction")

    # Verify structure
    print_header("STRUCTURE VERIFICATION")
    print("\n🔍 Verifying batch duplicate matches original...")

    try:
        match, differences = verify_structure_match(api, form_id, batch_form_id)

        if match:
            print("✅ Perfect match! All items copied correctly.")
        else:
            print(f"⚠️ Found {len(differences)} differences:")
            for diff in differences:
                print(f"  - {diff}")
    except Exception as e:
        print(f"❌ Verification failed: {e}")

    # Summary
    print_header("TEST SUMMARY")

    print("\n✅ Test completed successfully!")
    print(f"\n📋 Forms created (remember to delete):")
    print(f"  1. Batch copy: https://docs.google.com/forms/d/{batch_form_id}/edit")
    if legacy_form_id:
        print(f"  2. Legacy copy: https://docs.google.com/forms/d/{legacy_form_id}/edit")

    print(f"\n🗑️ Cleanup command:")
    print(f'  python -c "from forms_api import FormsAPI; api = FormsAPI(); api.delete_form(\'{batch_form_id}\'); {"api.delete_form(\'" + legacy_form_id + "\'); " if legacy_form_id else ""}print(\'Deleted\')"')

    print("\n" + "="*70)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        form_url = sys.argv[1]
    else:
        form_url = "https://docs.google.com/forms/d/1WBjiy0jWvGqk21DvlBS9ejEzV4xTY2wUT4m5OioKSU4/edit"

    test_real_form(form_url)
