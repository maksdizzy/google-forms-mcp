#!/usr/bin/env python3
"""Battle test: Create 5 personalized form copies for mock employees."""

import time
from forms_api import FormsAPI


def battle_test_personalized_copies():
    """Create 5 personalized 360 Feedback forms for mock employees."""

    # Mock employee names
    employees = [
        "Sarah Johnson",
        "Michael Chen",
        "Emily Rodriguez",
        "James Anderson",
        "Priya Patel"
    ]

    # Template form ID (360 Feedback form)
    template_form_id = "1WBjiy0jWvGqk21DvlBS9ejEzV4xTY2wUT4m5OioKSU4"

    print("="*70)
    print("  BATTLE TEST: 5 PERSONALIZED FORM COPIES")
    print("="*70)
    print(f"\n📋 Template: 360 Feedback Form")
    print(f"👥 Creating forms for {len(employees)} employees")
    print(f"⚡ Using optimized batch duplication\n")

    # Initialize API
    api = FormsAPI()

    results = []
    total_start = time.time()

    # Create personalized copy for each employee
    for i, employee_name in enumerate(employees, 1):
        print(f"[{i}/{len(employees)}] Creating form for {employee_name}...")

        try:
            start = time.time()
            result = api.duplicate_form_batch(
                form_id=template_form_id,
                new_title=f"🔁 360 Feedback - {employee_name}"
            )
            elapsed = time.time() - start

            results.append({
                "employee": employee_name,
                "success": True,
                "form_id": result['newFormId'],
                "edit_url": f"https://docs.google.com/forms/d/{result['newFormId']}/edit",
                "responder_url": result['responderUri'],
                "time": elapsed,
                "api_calls": result['apiCalls'],
                "items": result['copiedItems']
            })

            print(f"   ✅ Success in {elapsed:.2f}s - {result['copiedItems']} items")

        except Exception as e:
            results.append({
                "employee": employee_name,
                "success": False,
                "error": str(e)
            })
            print(f"   ❌ Failed: {e}")

    total_time = time.time() - total_start

    # Summary report
    print("\n" + "="*70)
    print("  BATTLE TEST RESULTS")
    print("="*70)

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    print(f"\n📊 Summary:")
    print(f"  • Total forms: {len(employees)}")
    print(f"  • Successful: {len(successful)}")
    print(f"  • Failed: {len(failed)}")
    print(f"  • Total time: {total_time:.2f}s")

    if successful:
        avg_time = sum(r['time'] for r in successful) / len(successful)
        total_api_calls = sum(r['api_calls'] for r in successful)
        print(f"  • Average time per form: {avg_time:.2f}s")
        print(f"  • Total API calls: {total_api_calls}")
        print(f"  • Average API calls per form: {total_api_calls / len(successful):.1f}")

    # Individual results
    print(f"\n📋 Individual Results:")
    for i, result in enumerate(results, 1):
        if result['success']:
            print(f"\n  {i}. {result['employee']} ✅")
            print(f"     Time: {result['time']:.2f}s | API Calls: {result['api_calls']} | Items: {result['items']}")
            print(f"     Edit: {result['edit_url']}")
            print(f"     Share: {result['responder_url']}")
        else:
            print(f"\n  {i}. {result['employee']} ❌")
            print(f"     Error: {result['error']}")

    # Cleanup command
    if successful:
        print(f"\n🗑️ Cleanup command:")
        form_ids = [r['form_id'] for r in successful]
        delete_commands = '; '.join([f"api.delete_form('{fid}')" for fid in form_ids])
        print(f'  python -c "from forms_api import FormsAPI; api = FormsAPI(); {delete_commands}; print(\'Deleted {len(form_ids)} forms\')"')

    print("\n" + "="*70)

    return results


if __name__ == "__main__":
    battle_test_personalized_copies()
