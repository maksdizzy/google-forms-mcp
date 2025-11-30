"""YAML template engine for Google Forms.

Supports creating forms from YAML templates and exporting forms to YAML.
"""

from pathlib import Path
from typing import Dict, Any

import yaml
from rich.console import Console

from .forms.api import FormsAPI
from .forms.models import QuestionType

console = Console()


def create_from_template(template_path: str) -> Dict[str, Any]:
    """Create a Google Form from a YAML template.

    Args:
        template_path: Path to the YAML template file

    Returns:
        Dict with formId, responderUri, and questionsAdded count

    Raises:
        FileNotFoundError: If template file not found
        ValueError: If template is invalid
    """
    path = Path(template_path)
    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    # Load and parse YAML
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Validate basic structure
    if 'form' not in data:
        raise ValueError("Template must have 'form' section with title")

    form_info = data['form']
    if 'title' not in form_info:
        raise ValueError("Form must have a title")

    # Initialize API
    api = FormsAPI()

    # Create form
    result = api.create_form(
        title=form_info['title'],
        description=form_info.get('description', '')
    )
    form_id = result['formId']

    questions_added = 0
    actual_position = 0  # Track actual position accounting for failed items

    # Add questions
    questions = data.get('questions', [])
    for i, q in enumerate(questions):
        try:
            question_type = q.get('type', 'SHORT_ANSWER').upper()

            # Clean title - Google Forms API doesn't allow newlines in displayed text
            title = q['title'].replace('\n', ' ').replace('\r', '').strip()

            # Prepare kwargs based on question type
            kwargs = {
                'required': q.get('required', False),
                'position': actual_position,  # Use actual position, not loop index
            }

            # Add type-specific parameters
            if question_type in ['MULTIPLE_CHOICE', 'CHECKBOXES', 'DROPDOWN']:
                kwargs['options'] = q.get('options', [])

            elif question_type in ['LINEAR_SCALE', 'RATING']:
                kwargs['low'] = q.get('low', 1)
                kwargs['high'] = q.get('high', 5)
                kwargs['lowLabel'] = q.get('lowLabel', '')
                kwargs['highLabel'] = q.get('highLabel', '')

            elif question_type in ['MULTIPLE_CHOICE_GRID', 'CHECKBOX_GRID']:
                kwargs['rows'] = q.get('rows', [])
                kwargs['columns'] = q.get('columns', [])

            elif question_type == 'FILE_UPLOAD':
                kwargs['folderId'] = q.get('folderId', '')
                kwargs['maxFiles'] = q.get('maxFiles', 1)
                kwargs['maxFileSize'] = q.get('maxFileSize', 10485760)
                kwargs['allowedTypes'] = q.get('allowedTypes', [])

            api.add_question(
                form_id=form_id,
                question_type=question_type,
                title=title,  # Use cleaned title
                **kwargs
            )
            questions_added += 1
            actual_position += 1  # Only increment on success

        except Exception as e:
            console.print(f"[yellow]Warning: Failed to add question '{q.get('title', 'unknown')[:50]}...': {e}[/yellow]")

    return {
        "formId": form_id,
        "responderUri": result['responderUri'],
        "editUri": result['editUri'],
        "questionsAdded": questions_added
    }


def export_to_template(form_id: str) -> str:
    """Export a Google Form to YAML template format.

    Args:
        form_id: The form ID to export

    Returns:
        YAML string representation of the form

    Raises:
        Exception: If form retrieval fails
    """
    api = FormsAPI()
    form = api.get_form(form_id)

    # Build template structure
    template = {
        'form': {
            'title': form.get('info', {}).get('title', 'Untitled'),
            'description': form.get('info', {}).get('description', ''),
        },
        'questions': []
    }

    items = form.get('items', [])
    for item in items:
        if 'questionItem' not in item:
            continue

        question_item = item['questionItem']
        question = question_item.get('question', {})

        q = {
            'title': item.get('title', 'Untitled'),
            'required': question.get('required', False),
        }

        # Determine question type and add specific fields
        if 'textQuestion' in question:
            if question['textQuestion'].get('paragraph', False):
                q['type'] = 'PARAGRAPH'
            else:
                q['type'] = 'SHORT_ANSWER'

        elif 'choiceQuestion' in question:
            choice_type = question['choiceQuestion'].get('type', 'RADIO')
            options = [opt.get('value', '') for opt in question['choiceQuestion'].get('options', [])]

            if choice_type == 'RADIO':
                q['type'] = 'MULTIPLE_CHOICE'
            elif choice_type == 'CHECKBOX':
                q['type'] = 'CHECKBOXES'
            elif choice_type == 'DROP_DOWN':
                q['type'] = 'DROPDOWN'

            q['options'] = options

        elif 'scaleQuestion' in question:
            scale = question['scaleQuestion']
            q['type'] = 'LINEAR_SCALE'
            q['low'] = scale.get('low', 1)
            q['high'] = scale.get('high', 5)
            if scale.get('lowLabel'):
                q['lowLabel'] = scale['lowLabel']
            if scale.get('highLabel'):
                q['highLabel'] = scale['highLabel']

        elif 'dateQuestion' in question:
            q['type'] = 'DATE'

        elif 'timeQuestion' in question:
            q['type'] = 'TIME'

        elif 'fileUploadQuestion' in question:
            q['type'] = 'FILE_UPLOAD'
            fu = question['fileUploadQuestion']
            if fu.get('folderId'):
                q['folderId'] = fu['folderId']
            q['maxFiles'] = fu.get('maxFiles', 1)

        else:
            q['type'] = 'SHORT_ANSWER'  # Default

        template['questions'].append(q)

    # Convert to YAML with nice formatting
    yaml_str = yaml.dump(
        template,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120
    )

    # Add header comment
    header = """# Google Forms Template
# Created by: gtools forms export-template
#
# Usage: gtools forms apply this_file.yaml
#
# Supported question types:
#   - SHORT_ANSWER
#   - PARAGRAPH
#   - MULTIPLE_CHOICE (with options)
#   - CHECKBOXES (with options)
#   - DROPDOWN (with options)
#   - LINEAR_SCALE (with low, high, lowLabel, highLabel)
#   - DATE
#   - TIME
#   - RATING
#   - MULTIPLE_CHOICE_GRID (with rows, columns)
#   - CHECKBOX_GRID (with rows, columns)
#   - FILE_UPLOAD (with folderId, maxFiles)
#
"""

    return header + yaml_str
