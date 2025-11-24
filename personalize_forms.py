#!/usr/bin/env python3
"""Personalize all 5 employee forms by replacing NAME placeholder."""

import time
from forms_api import FormsAPI


def personalize_form(api, form_id, employee_name):
    """
    Personalize a form by replacing NAME with actual employee name.

    Args:
        api: FormsAPI instance
        form_id: Form ID to personalize
        employee_name: Actual employee name to use

    Returns:
        dict with results
    """
    print(f"\n🔄 Personalizing form for {employee_name}...")

    start = time.time()

    # Get the form
    form = api.get_form(form_id)
    items = form.get('items', [])

    # Build batch update requests
    batch_requests = []
    items_updated = 0

    for item in items:
        item_id = item.get('itemId')
        if not item_id:
            continue

        update_needed = False
        updated_item = {}

        # Check title
        title = item.get('title', '')
        if 'NAME' in title:
            updated_item['title'] = title.replace('NAME', employee_name)
            update_needed = True

        # Check description
        description = item.get('description', '')
        if 'NAME' in description:
            updated_item['description'] = description.replace('NAME', employee_name)
            update_needed = True

        # If updates needed, add to batch
        if update_needed:
            # Build proper update request with updateMask
            update_mask_fields = []
            if 'title' in updated_item:
                update_mask_fields.append('title')
            if 'description' in updated_item:
                update_mask_fields.append('description')

            # Get full item structure
            full_item = item.copy()
            full_item.update(updated_item)

            batch_requests.append({
                "updateItem": {
                    "item": full_item,
                    "location": {"index": items.index(item)},
                    "updateMask": ','.join(update_mask_fields)
                }
            })
            items_updated += 1

    # Execute batch update
    if batch_requests:
        try:
            api.service.forms().batchUpdate(
                formId=form_id,
                body={"requests": batch_requests}
            ).execute()

            elapsed = time.time() - start
            print(f"   ✅ Updated {items_updated} items in {elapsed:.2f}s")

            return {
                "success": True,
                "items_updated": items_updated,
                "time": elapsed,
                "api_calls": 2  # get_form + batchUpdate
            }
        except Exception as e:
            elapsed = time.time() - start
            print(f"   ❌ Failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "time": elapsed
            }
    else:
        elapsed = time.time() - start
        print(f"   ℹ️  No NAME placeholders found")
        return {
            "success": True,
            "items_updated": 0,
            "time": elapsed,
            "api_calls": 1  # only get_form
        }


def personalize_all_forms():
    """Personalize all 5 employee forms."""

    # Employee forms created in battle test
    forms = [
        {
            "name": "Sarah Johnson",
            "form_id": "1FsyDyAqYr12F-hLQcvswbbggcWO9EFLoHX38KtvThX8"
        },
        {
            "name": "Michael Chen",
            "form_id": "1wtYJ4BSIYSLB9fCq3dM0-ESTyJWvQftTTjIv3vwoYB4"
        },
        {
            "name": "Emily Rodriguez",
            "form_id": "1-2pORK_i9lTOlrwGJX6ahkyhqz7x1BqmaWa_EqHc6CQ"
        },
        {
            "name": "James Anderson",
            "form_id": "1PaiqoBFWMQ7B0mT0BKQvXTZPFIoEP8OAIrRTZ83AaFo"
        },
        {
            "name": "Priya Patel",
            "form_id": "16FEQ0YwNOlwzxXSDPFgjkTio6hqoeptrgw1OmxXuZog"
        }
    ]

    print("="*70)
    print("  PERSONALIZING 5 EMPLOYEE FORMS")
    print("="*70)
    print("\nReplacing 'NAME' placeholder with actual employee names...\n")

    api = FormsAPI()
    results = []
    total_start = time.time()

    for i, form_info in enumerate(forms, 1):
        print(f"[{i}/{len(forms)}] {form_info['name']}")
        result = personalize_form(api, form_info['form_id'], form_info['name'])
        result['employee'] = form_info['name']
        result['form_id'] = form_info['form_id']
        results.append(result)

    total_time = time.time() - total_start

    # Summary
    print("\n" + "="*70)
    print("  PERSONALIZATION RESULTS")
    print("="*70)

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    print(f"\n📊 Summary:")
    print(f"  • Total forms: {len(forms)}")
    print(f"  • Successful: {len(successful)}")
    print(f"  • Failed: {len(failed)}")
    print(f"  • Total time: {total_time:.2f}s")

    if successful:
        total_items = sum(r['items_updated'] for r in successful)
        total_api_calls = sum(r['api_calls'] for r in successful)
        avg_time = sum(r['time'] for r in successful) / len(successful)

        print(f"  • Total items updated: {total_items}")
        print(f"  • Total API calls: {total_api_calls}")
        print(f"  • Average time per form: {avg_time:.2f}s")

    # Individual results
    print(f"\n📋 Individual Results:")
    for result in results:
        if result['success']:
            print(f"\n  ✅ {result['employee']}")
            print(f"     Items updated: {result['items_updated']}")
            print(f"     Time: {result['time']:.2f}s")
            print(f"     Edit: https://docs.google.com/forms/d/{result['form_id']}/edit")
        else:
            print(f"\n  ❌ {result['employee']}")
            print(f"     Error: {result['error']}")

    print("\n" + "="*70)

    return results


if __name__ == "__main__":
    personalize_all_forms()
