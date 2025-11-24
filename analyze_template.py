#!/usr/bin/env python3
"""Analyze template form to see what questions need personalization."""

from forms_api import FormsAPI
import json


def analyze_template():
    """Analyze the template form structure."""

    template_form_id = "1WBjiy0jWvGqk21DvlBS9ejEzV4xTY2wUT4m5OioKSU4"

    api = FormsAPI()
    form = api.get_form(template_form_id)

    print("="*70)
    print("  TEMPLATE FORM ANALYSIS")
    print("="*70)

    info = form.get('info', {})
    print(f"\nForm Title: {info.get('title', 'N/A')}")
    print(f"Description: {info.get('description', 'N/A')[:100]}...")

    items = form.get('items', [])
    print(f"\nTotal Items: {len(items)}")

    print("\n" + "="*70)
    print("  ITEM DETAILS")
    print("="*70)

    for i, item in enumerate(items):
        print(f"\n--- Item {i} ---")
        print(f"Item ID: {item.get('itemId', 'N/A')}")
        print(f"Title: {item.get('title', 'N/A')}")

        if item.get('description'):
            print(f"Description: {item['description'][:100]}")

        # Check item type
        if 'questionItem' in item:
            question = item['questionItem']['question']
            question_id = question.get('questionId', 'N/A')
            print(f"Question ID: {question_id}")

            # Check question type
            if 'choiceQuestion' in question:
                choice_type = question['choiceQuestion'].get('type', 'UNKNOWN')
                print(f"Type: Choice Question ({choice_type})")

                options = question['choiceQuestion'].get('options', [])
                print(f"Options ({len(options)}):")
                for j, opt in enumerate(options):
                    print(f"  {j+1}. {opt.get('value', 'N/A')}")

            elif 'textQuestion' in question:
                is_paragraph = question['textQuestion'].get('paragraph', False)
                print(f"Type: Text Question ({'Paragraph' if is_paragraph else 'Short Answer'})")

            elif 'scaleQuestion' in question:
                scale = question['scaleQuestion']
                print(f"Type: Linear Scale")
                print(f"  Low: {scale.get('low', 'N/A')} - {scale.get('lowLabel', '')}")
                print(f"  High: {scale.get('high', 'N/A')} - {scale.get('highLabel', '')}")

        elif 'pageBreakItem' in item:
            print("Type: Page Break / Section")

        elif 'textItem' in item:
            print("Type: Text (Description)")

    print("\n" + "="*70)
    print("  PERSONALIZATION NEEDS")
    print("="*70)

    print("\nPlaceholders to replace:")
    print("  • Form title: '360 Feedback - Employee Name' → '360 Feedback - [Actual Name]'")
    print("  • Question text containing 'Employee Name' → [Actual Name]")
    print("  • Description text containing 'Employee Name' → [Actual Name]")

    # Search for "Employee Name" in items
    print("\nItems containing 'Employee Name':")
    for i, item in enumerate(items):
        title = item.get('title', '')
        desc = item.get('description', '')

        if 'Employee Name' in title or 'employee name' in title.lower():
            print(f"  - Item {i}: Title contains placeholder")
        if 'Employee Name' in desc or 'employee name' in desc.lower():
            print(f"  - Item {i}: Description contains placeholder")

    print("\n" + "="*70)


if __name__ == "__main__":
    analyze_template()
