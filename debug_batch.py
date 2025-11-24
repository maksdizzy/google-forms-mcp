#!/usr/bin/env python3
"""Debug batch request to find newline issues."""

from forms_api import FormsAPI
import json


def check_for_newlines(obj, path=""):
    """Recursively check for newlines in all string values."""
    issues = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            issues.extend(check_for_newlines(value, new_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]"
            issues.extend(check_for_newlines(item, new_path))
    elif isinstance(obj, str):
        if '\n' in obj or '\r' in obj:
            issues.append((path, repr(obj[:100])))

    return issues


def debug_batch_request(form_id):
    api = FormsAPI()

    print("Fetching form...")
    original = api.get_form(form_id)
    items = original.get('items', [])

    print(f"Total items: {len(items)}")

    # Build batch request like the code does
    batch_requests = []

    # Add settings
    if 'settings' in original:
        settings = original['settings'].copy()
        if 'quizSettings' not in settings:
            settings['quizSettings'] = {'isQuiz': False}
        batch_requests.append({
            "updateSettings": {
                "settings": settings,
                "updateMask": "*"
            }
        })

    # Add items
    for i, original_item in enumerate(items):
        clean_item = api._clean_item_for_duplication(original_item)
        batch_requests.append({
            "createItem": {
                "item": clean_item,
                "location": {"index": i}
            }
        })

    print(f"\nTotal batch requests: {len(batch_requests)}")

    # Check each request for newlines
    print("\nChecking for newlines in batch requests...")
    for i, request in enumerate(batch_requests):
        issues = check_for_newlines(request)
        if issues:
            print(f"\n⚠️  Request {i} has newlines:")
            for path, value in issues:
                print(f"  {path}: {value}")
        else:
            if i == 0 and 'updateSettings' in request:
                print(f"Request {i} (settings): ✓ No newlines")
            else:
                item_idx = i - (1 if 'settings' in original else 0)
                print(f"Request {i} (item {item_idx}): ✓ No newlines")


if __name__ == "__main__":
    form_id = "1WBjiy0jWvGqk21DvlBS9ejEzV4xTY2wUT4m5OioKSU4"
    debug_batch_request(form_id)
