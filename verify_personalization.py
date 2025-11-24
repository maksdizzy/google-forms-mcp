#!/usr/bin/env python3
"""Verify personalization was applied correctly."""

from forms_api import FormsAPI


def verify_personalization():
    """Verify that NAME was replaced in all forms."""

    forms = [
        ("Sarah Johnson", "1FsyDyAqYr12F-hLQcvswbbggcWO9EFLoHX38KtvThX8"),
        ("Michael Chen", "1wtYJ4BSIYSLB9fCq3dM0-ESTyJWvQftTTjIv3vwoYB4"),
        ("Emily Rodriguez", "1-2pORK_i9lTOlrwGJX6ahkyhqz7x1BqmaWa_EqHc6CQ"),
        ("James Anderson", "1PaiqoBFWMQ7B0mT0BKQvXTZPFIoEP8OAIrRTZ83AaFo"),
        ("Priya Patel", "16FEQ0YwNOlwzxXSDPFgjkTio6hqoeptrgw1OmxXuZog")
    ]

    print("="*70)
    print("  PERSONALIZATION VERIFICATION")
    print("="*70)

    api = FormsAPI()

    for employee_name, form_id in forms:
        print(f"\n📋 Checking: {employee_name}")
        print(f"   Form ID: {form_id}")

        form = api.get_form(form_id)
        items = form.get('items', [])

        # Check form title
        form_title = form.get('info', {}).get('title', '')
        if employee_name in form_title:
            print(f"   ✅ Form title: '{form_title}'")
        else:
            print(f"   ⚠️  Form title doesn't contain name: '{form_title}'")

        # Check items for NAME placeholder
        items_with_name = []
        items_with_placeholder = []

        for i, item in enumerate(items):
            title = item.get('title', '')
            desc = item.get('description', '')

            # Check if employee name appears
            if employee_name in title or employee_name in desc:
                items_with_name.append(i)

            # Check if NAME placeholder still exists
            if 'NAME' in title or 'NAME' in desc:
                items_with_placeholder.append(i)
                print(f"   ⚠️  Item {i} still has 'NAME' placeholder:")
                if 'NAME' in title:
                    print(f"       Title: {title[:80]}")
                if 'NAME' in desc:
                    print(f"       Desc: {desc[:80]}")

        if items_with_name:
            print(f"   ✅ {len(items_with_name)} items contain employee name")
        else:
            print(f"   ⚠️  No items contain employee name")

        if not items_with_placeholder:
            print(f"   ✅ No 'NAME' placeholders found")

        # Sample a few personalized questions
        print(f"\n   📝 Sample personalized questions:")
        sample_count = 0
        for i, item in enumerate(items):
            title = item.get('title', '')
            if employee_name in title:
                print(f"      • {title[:100]}")
                sample_count += 1
                if sample_count >= 3:
                    break

    print("\n" + "="*70)
    print("  VERIFICATION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    verify_personalization()
