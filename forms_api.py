#!/usr/bin/env python3
"""Google Forms API wrapper for MCP server.

Provides high-level interface to Google Forms and Drive APIs with error handling.
"""

import csv
import io
from typing import Dict, List, Optional, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials


class FormsAPI:
    """Google Forms API client with comprehensive form management capabilities."""

    def __init__(self):
        """Initialize API clients with OAuth credentials."""
        self.creds = get_credentials()
        self.service = build('forms', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    def create_form(self, title: str, description: str = "") -> Dict[str, Any]:
        """Create and publish a new form.

        Args:
            title: Form title
            description: Form description (optional)

        Returns:
            Dict with formId, responderUri, and editUri

        Raises:
            HttpError: If form creation fails
        """
        try:
            # Create form with ONLY title (API requirement)
            form = {
                "info": {
                    "title": title
                }
            }

            result = self.service.forms().create(body=form).execute()
            form_id = result['formId']

            # Add description and settings via batchUpdate if provided
            if description:
                requests = []

                # Add description update
                requests.append({
                    "updateFormInfo": {
                        "info": {
                            "description": description
                        },
                        "updateMask": "description"
                    }
                })

                # Add default quiz settings (required by API)
                requests.append({
                    "updateSettings": {
                        "settings": {
                            "quizSettings": {
                                "isQuiz": False  # Default to non-quiz form
                            }
                        },
                        "updateMask": "quizSettings.isQuiz"
                    }
                })

                update = {"requests": requests}
                self.service.forms().batchUpdate(formId=form_id, body=update).execute()

            return {
                "formId": form_id,
                "responderUri": result.get('responderUri'),
                "editUri": f"https://docs.google.com/forms/d/{form_id}/edit"
            }

        except HttpError as e:
            raise Exception(f"Failed to create form: {e}")

    def list_forms(self, page_size: int = 50, page_token: Optional[str] = None) -> Dict[str, Any]:
        """List all forms owned by the user via Drive API.

        Args:
            page_size: Maximum number of forms to return
            page_token: Token for pagination (optional)

        Returns:
            Dict with 'forms' list and optional 'nextPageToken'

        Raises:
            HttpError: If listing fails
        """
        try:
            query = "mimeType='application/vnd.google-apps.form'"
            params = {
                'q': query,
                'pageSize': page_size,
                'fields': 'files(id,name,webViewLink),nextPageToken'
            }

            if page_token:
                params['pageToken'] = page_token

            results = self.drive_service.files().list(**params).execute()
            files = results.get('files', [])

            # Get response counts for each form
            forms = []
            for file in files:
                form_id = file['id']
                try:
                    form = self.service.forms().get(formId=form_id).execute()
                    responses = self.service.forms().responses().list(formId=form_id).execute()
                    response_count = len(responses.get('responses', []))
                except:
                    response_count = 0

                forms.append({
                    "formId": form_id,
                    "title": file['name'],
                    "responderUri": form.get('responderUri', ''),
                    "responseCount": response_count
                })

            result = {"forms": forms}
            if 'nextPageToken' in results:
                result['nextPageToken'] = results['nextPageToken']

            return result

        except HttpError as e:
            raise Exception(f"Failed to list forms: {e}")

    def get_form(self, form_id: str) -> Dict[str, Any]:
        """Get complete form details.

        Args:
            form_id: The form ID

        Returns:
            Complete Form object

        Raises:
            HttpError: If form retrieval fails
        """
        try:
            return self.service.forms().get(formId=form_id).execute()
        except HttpError as e:
            raise Exception(f"Failed to get form: {e}")

    def update_form(self, form_id: str, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Update form title and/or description.

        Args:
            form_id: The form ID
            title: New title (optional)
            description: New description (optional)

        Returns:
            Updated Form object

        Raises:
            HttpError: If update fails
        """
        try:
            requests = []
            update_mask = []

            if title is not None:
                requests.append({
                    "updateFormInfo": {
                        "info": {
                            "title": title
                        },
                        "updateMask": "title"
                    }
                })

            if description is not None:
                requests.append({
                    "updateFormInfo": {
                        "info": {
                            "description": description
                        },
                        "updateMask": "description"
                    }
                })

            if not requests:
                raise ValueError("Must provide either title or description to update")

            body = {"requests": requests}
            self.service.forms().batchUpdate(formId=form_id, body=body).execute()

            return self.get_form(form_id)

        except HttpError as e:
            raise Exception(f"Failed to update form: {e}")

    def delete_form(self, form_id: str) -> Dict[str, bool]:
        """Delete a form via Drive API.

        Args:
            form_id: The form ID

        Returns:
            Dict with 'deleted': True

        Raises:
            HttpError: If deletion fails
        """
        try:
            self.drive_service.files().delete(fileId=form_id).execute()
            return {"deleted": True}
        except HttpError as e:
            raise Exception(f"Failed to delete form: {e}")

    def _get_item_index(self, form_id: str, item_id: str) -> int:
        """Helper method to get an item's index by its itemId.

        Args:
            form_id: The form ID
            item_id: The item ID to find

        Returns:
            The index of the item

        Raises:
            ValueError: If item not found
        """
        form = self.get_form(form_id)
        items = form.get('items', [])

        for index, item in enumerate(items):
            if item.get('itemId') == item_id:
                return index

        raise ValueError(f"Item with ID '{item_id}' not found in form")

    def add_question(self, form_id: str, question_type: str, title: str, **kwargs) -> Dict[str, Any]:
        """Add a question to a form.

        Supports all 12 Google Forms question types with appropriate parameters.

        Args:
            form_id: The form ID
            question_type: Type of question (SHORT_ANSWER, PARAGRAPH, MULTIPLE_CHOICE, etc.)
            title: Question text
            **kwargs: Additional parameters based on question type

        Returns:
            Dict with created item details

        Raises:
            HttpError: If question creation fails
        """
        try:
            location = {"index": kwargs.get('position', 0)}

            # Build question object with correct structure
            question = {
                "required": kwargs.get('required', False)
            }

            # Build question type-specific fields
            if question_type == "SHORT_ANSWER":
                question["textQuestion"] = {"paragraph": False}

            elif question_type == "PARAGRAPH":
                question["textQuestion"] = {"paragraph": True}

            elif question_type == "MULTIPLE_CHOICE":
                options = kwargs.get('options', [])
                question["choiceQuestion"] = {
                    "type": "RADIO",
                    "options": [{"value": opt} for opt in options]
                }

            elif question_type == "CHECKBOXES":
                options = kwargs.get('options', [])
                question["choiceQuestion"] = {
                    "type": "CHECKBOX",
                    "options": [{"value": opt} for opt in options]
                }

            elif question_type == "DROPDOWN":
                options = kwargs.get('options', [])
                question["choiceQuestion"] = {
                    "type": "DROP_DOWN",
                    "options": [{"value": opt} for opt in options]
                }

            elif question_type == "LINEAR_SCALE":
                question["scaleQuestion"] = {
                    "low": kwargs.get('low', 1),
                    "high": kwargs.get('high', 5),
                    "lowLabel": kwargs.get('lowLabel', ''),
                    "highLabel": kwargs.get('highLabel', '')
                }

            elif question_type == "DATE":
                question["dateQuestion"] = {
                    "includeTime": False,
                    "includeYear": True
                }

            elif question_type == "TIME":
                question["timeQuestion"] = {"duration": False}

            elif question_type == "FILE_UPLOAD":
                question["fileUploadQuestion"] = {
                    "folderId": kwargs.get('folderId', ''),
                    "maxFiles": kwargs.get('maxFiles', 1),
                    "maxFileSize": kwargs.get('maxFileSize', 10485760),
                    "types": kwargs.get('allowedTypes', [])
                }

            elif question_type == "MULTIPLE_CHOICE_GRID":
                rows = kwargs.get('rows', [])
                columns = kwargs.get('columns', [])
                question["questionGroupItem"] = {
                    "questions": [{"rowQuestion": {"title": row}} for row in rows],
                    "grid": {
                        "columns": {
                            "type": "RADIO",
                            "options": [{"value": col} for col in columns]
                        }
                    }
                }

            elif question_type == "CHECKBOX_GRID":
                rows = kwargs.get('rows', [])
                columns = kwargs.get('columns', [])
                question["questionGroupItem"] = {
                    "questions": [{"rowQuestion": {"title": row}} for row in rows],
                    "grid": {
                        "columns": {
                            "type": "CHECKBOX",
                            "options": [{"value": col} for col in columns]
                        }
                    }
                }

            elif question_type == "RATING":
                question["scaleQuestion"] = {
                    "low": 1,
                    "high": kwargs.get('high', 5),
                    "lowLabel": '',
                    "highLabel": ''
                }

            else:
                raise ValueError(f"Unsupported question type: {question_type}")

            # Correct API structure: title at item level, question details nested
            request = {
                "requests": [{
                    "createItem": {
                        "item": {
                            "title": title,
                            "questionItem": {
                                "question": question
                            }
                        },
                        "location": location
                    }
                }]
            }

            result = self.service.forms().batchUpdate(formId=form_id, body=request).execute()
            return result

        except HttpError as e:
            raise Exception(f"Failed to add question: {e}")

    def update_question(self, form_id: str, item_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing question.

        Args:
            form_id: The form ID
            item_id: The item ID to update
            **kwargs: Fields to update (title, required, etc.)

        Returns:
            Result of batch update

        Raises:
            HttpError: If update fails
        """
        try:
            # Convert itemId to index
            item_index = self._get_item_index(form_id, item_id)

            updates = {}
            update_mask = []

            if 'title' in kwargs:
                updates['title'] = kwargs['title']
                update_mask.append('title')

            if 'required' in kwargs:
                if 'questionItem' not in updates:
                    updates['questionItem'] = {}
                if 'question' not in updates['questionItem']:
                    updates['questionItem']['question'] = {}
                updates['questionItem']['question']['required'] = kwargs['required']
                update_mask.append('questionItem.question.required')

            request = {
                "requests": [{
                    "updateItem": {
                        "item": updates,
                        "location": {"index": item_index},
                        "updateMask": ','.join(update_mask)
                    }
                }]
            }

            return self.service.forms().batchUpdate(formId=form_id, body=request).execute()

        except HttpError as e:
            raise Exception(f"Failed to update question: {e}")

    def delete_question(self, form_id: str, item_id: str) -> Dict[str, Any]:
        """Delete a question from a form.

        Args:
            form_id: The form ID
            item_id: The item ID to delete

        Returns:
            Result of batch update

        Raises:
            HttpError: If deletion fails
        """
        try:
            # Convert itemId to index
            item_index = self._get_item_index(form_id, item_id)

            request = {
                "requests": [{
                    "deleteItem": {
                        "location": {"index": item_index}
                    }
                }]
            }

            return self.service.forms().batchUpdate(formId=form_id, body=request).execute()

        except HttpError as e:
            raise Exception(f"Failed to delete question: {e}")

    def move_question(self, form_id: str, item_id: str, new_position: int) -> Dict[str, Any]:
        """Move a question to a new position.

        Args:
            form_id: The form ID
            item_id: The item ID to move
            new_position: New position index

        Returns:
            Result of batch update

        Raises:
            HttpError: If move fails
        """
        try:
            # Convert itemId to index
            item_index = self._get_item_index(form_id, item_id)

            request = {
                "requests": [{
                    "moveItem": {
                        "originalLocation": {"index": item_index},
                        "newLocation": {"index": new_position}
                    }
                }]
            }

            return self.service.forms().batchUpdate(formId=form_id, body=request).execute()

        except HttpError as e:
            raise Exception(f"Failed to move question: {e}")

    def add_section(self, form_id: str, title: str, description: str = "", position: Optional[int] = None) -> Dict[str, Any]:
        """Add a section break (page break) to the form.

        Args:
            form_id: The form ID
            title: Section title
            description: Section description (optional)
            position: Position index (optional, defaults to end of form)

        Returns:
            Result of batch update

        Raises:
            HttpError: If section creation fails
        """
        try:
            # If position not specified, add to end of form
            if position is None:
                form = self.get_form(form_id)
                position = len(form.get('items', []))

            request = {
                "requests": [{
                    "createItem": {
                        "item": {
                            "title": title,
                            "description": description,
                            "pageBreakItem": {}
                        },
                        "location": {"index": position}
                    }
                }]
            }

            return self.service.forms().batchUpdate(formId=form_id, body=request).execute()

        except HttpError as e:
            raise Exception(f"Failed to add section: {e}")

    def list_responses(self, form_id: str, page_size: int = 100, page_token: Optional[str] = None) -> Dict[str, Any]:
        """List all responses for a form.

        Args:
            form_id: The form ID
            page_size: Maximum responses to return
            page_token: Pagination token (optional)

        Returns:
            Dict with 'responses' list and optional 'nextPageToken'

        Raises:
            HttpError: If listing fails
        """
        try:
            params = {'pageSize': page_size}
            if page_token:
                params['pageToken'] = page_token

            result = self.service.forms().responses().list(formId=form_id, **params).execute()
            return result

        except HttpError as e:
            raise Exception(f"Failed to list responses: {e}")

    def get_response(self, form_id: str, response_id: str) -> Dict[str, Any]:
        """Get a specific response.

        Args:
            form_id: The form ID
            response_id: The response ID

        Returns:
            Complete FormResponse object

        Raises:
            HttpError: If retrieval fails
        """
        try:
            return self.service.forms().responses().get(formId=form_id, responseId=response_id).execute()
        except HttpError as e:
            raise Exception(f"Failed to get response: {e}")

    def export_responses_csv(self, form_id: str, include_timestamps: bool = True, include_email: bool = True) -> Dict[str, Any]:
        """Export responses to CSV format.

        Args:
            form_id: The form ID
            include_timestamps: Include submission timestamps
            include_email: Include respondent emails

        Returns:
            Dict with 'csv' string and 'rowCount'

        Raises:
            HttpError: If export fails
        """
        try:
            # Get form structure
            form = self.get_form(form_id)
            responses_data = self.list_responses(form_id, page_size=1000)
            responses = responses_data.get('responses', [])

            if not responses:
                return {"csv": "", "rowCount": 0}

            # Build CSV
            output = io.StringIO()
            writer = csv.writer(output)

            # Build header
            header = []
            if include_timestamps:
                header.append('Timestamp')
            if include_email:
                header.append('Email')

            # Extract question titles
            items = form.get('items', [])
            question_map = {}
            for item in items:
                if 'questionItem' in item:
                    question_id = item['itemId']
                    question_map[question_id] = item.get('title', f'Question {question_id}')
                    header.append(question_map[question_id])

            writer.writerow(header)

            # Write responses
            for response in responses:
                row = []
                if include_timestamps:
                    row.append(response.get('createTime', ''))
                if include_email:
                    row.append(response.get('respondentEmail', ''))

                answers = response.get('answers', {})
                for question_id in question_map.keys():
                    if question_id in answers:
                        answer = answers[question_id]
                        if 'textAnswers' in answer:
                            text_values = [a.get('value', '') for a in answer['textAnswers'].get('answers', [])]
                            row.append('; '.join(text_values))
                        else:
                            row.append('')
                    else:
                        row.append('')

                writer.writerow(row)

            csv_content = output.getvalue()
            output.close()

            return {
                "csv": csv_content,
                "rowCount": len(responses)
            }

        except HttpError as e:
            raise Exception(f"Failed to export responses: {e}")

    def duplicate_form(self, form_id: str, new_title: str) -> Dict[str, Any]:
        """Duplicate an existing form.

        Args:
            form_id: The form ID to copy
            new_title: Title for the new form

        Returns:
            Dict with newFormId, responderUri, and copiedItems count

        Raises:
            HttpError: If duplication fails
        """
        try:
            # Step 1: Get original form structure
            original = self.get_form(form_id)

            # Step 2: Create new empty form
            description = original.get('info', {}).get('description', '')
            new_form = self.create_form(new_title, description)
            new_form_id = new_form['formId']

            # Step 3: Copy settings (if quiz settings exist)
            if 'settings' in original:
                settings_request = {
                    "requests": [{
                        "updateSettings": {
                            "settings": original['settings'],
                            "updateMask": "*"  # Copy all settings
                        }
                    }]
                }
                self.service.forms().batchUpdate(
                    formId=new_form_id,
                    body=settings_request
                ).execute()

            # Step 4: Copy all items WITHOUT itemId (let API assign new IDs)
            items = original.get('items', [])
            copied_count = 0

            for i, original_item in enumerate(items):
                # Create clean copy without itemId and questionId
                clean_item = self._clean_item_for_duplication(original_item)

                # Create item without IDs (API will assign new ones)
                request = {
                    "requests": [{
                        "createItem": {
                            "item": clean_item,
                            "location": {"index": i}
                        }
                    }]
                }

                try:
                    self.service.forms().batchUpdate(
                        formId=new_form_id,
                        body=request
                    ).execute()
                    copied_count += 1
                except HttpError as item_error:
                    # Log but continue with next item
                    print(f"Warning: Failed to copy item {i}: {item_error}")
                    continue

            return {
                "newFormId": new_form_id,
                "responderUri": new_form['responderUri'],
                "copiedItems": copied_count,
                "totalItems": len(items)
            }

        except HttpError as e:
            raise Exception(f"Failed to duplicate form: {e}")

    def _clean_item_for_duplication(self, original_item: Dict[str, Any]) -> Dict[str, Any]:
        """Remove IDs from item for safe duplication.

        Args:
            original_item: Original item from form

        Returns:
            Clean item without itemId or questionId fields
        """
        clean_item = {}

        # Copy basic fields
        if 'title' in original_item:
            clean_item['title'] = original_item['title']
        if 'description' in original_item:
            clean_item['description'] = original_item['description']

        # Copy item type (questionItem, pageBreakItem, textItem, etc.)
        if 'questionItem' in original_item:
            question = original_item['questionItem']['question'].copy()
            # Remove questionId if present
            question.pop('questionId', None)
            clean_item['questionItem'] = {
                'question': question
            }
            if 'image' in original_item['questionItem']:
                clean_item['questionItem']['image'] = original_item['questionItem']['image']

        elif 'questionGroupItem' in original_item:
            import copy
            group = copy.deepcopy(original_item['questionGroupItem'])
            # Remove questionIds from all questions in group
            if 'questions' in group:
                for q in group['questions']:
                    q.pop('questionId', None)
            clean_item['questionGroupItem'] = group

        elif 'pageBreakItem' in original_item:
            clean_item['pageBreakItem'] = original_item['pageBreakItem']

        elif 'textItem' in original_item:
            clean_item['textItem'] = original_item['textItem']

        elif 'imageItem' in original_item:
            clean_item['imageItem'] = original_item['imageItem']

        elif 'videoItem' in original_item:
            clean_item['videoItem'] = original_item['videoItem']

        return clean_item
