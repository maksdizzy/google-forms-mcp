#!/usr/bin/env python3
"""Debug script to find which item has newlines."""

from forms_api import FormsAPI
import json

def debug_form(form_id):
    api = FormsAPI()

    print("Fetching form...")
    form = api.get_form(form_id)

    items = form.get('items', [])
    print(f"\nTotal items: {len(items)}")

    for i, item in enumerate(items):
        print(f"\n--- Item {i} ---")
        print(f"Title: {item.get('title', 'No title')[:50]}")

        if 'questionItem' in item:
            question = item['questionItem']['question']

            # Check scale question
            if 'scaleQuestion' in question:
                scale = question['scaleQuestion']
                low_label = scale.get('lowLabel', '')
                high_label = scale.get('highLabel', '')

                if '\n' in low_label or '\r' in low_label:
                    print(f"  ⚠️  LOW LABEL has newlines: {repr(low_label)}")
                if '\n' in high_label or '\r' in high_label:
                    print(f"  ⚠️  HIGH LABEL has newlines: {repr(high_label)}")

            # Check choice question
            if 'choiceQuestion' in question:
                if 'options' in question['choiceQuestion']:
                    for j, option in enumerate(question['choiceQuestion']['options']):
                        value = option.get('value', '')
                        if '\n' in value or '\r' in value:
                            print(f"  ⚠️  OPTION {j} has newlines: {repr(value)}")

        elif 'questionGroupItem' in item:
            group = item['questionGroupItem']

            # Check grid columns
            if 'grid' in group and 'columns' in group['grid']:
                if 'options' in group['grid']['columns']:
                    for j, option in enumerate(group['grid']['columns']['options']):
                        value = option.get('value', '')
                        if '\n' in value or '\r' in value:
                            print(f"  ⚠️  GRID COLUMN {j} has newlines: {repr(value)}")

    # Try cleaning and show result
    print("\n\n=== Testing cleaned items ===")
    for i, item in enumerate(items):
        try:
            cleaned = api._clean_item_for_duplication(item)
            print(f"Item {i}: ✓ Cleaned successfully")

            # Verify no newlines in cleaned version
            if 'questionItem' in cleaned:
                question = cleaned['questionItem']['question']

                if 'scaleQuestion' in question:
                    scale = question['scaleQuestion']
                    if '\n' in scale.get('lowLabel', '') or '\n' in scale.get('highLabel', ''):
                        print(f"  ⚠️  Still has newlines after cleaning!")

                if 'choiceQuestion' in question:
                    if 'options' in question['choiceQuestion']:
                        for option in question['choiceQuestion']['options']:
                            if '\n' in option.get('value', ''):
                                print(f"  ⚠️  Still has newlines in options after cleaning!")

        except Exception as e:
            print(f"Item {i}: ❌ Error cleaning: {e}")


if __name__ == "__main__":
    form_id = "1WBjiy0jWvGqk21DvlBS9ejEzV4xTY2wUT4m5OioKSU4"
    debug_form(form_id)
