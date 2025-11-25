#!/usr/bin/env python3
"""Google Forms API wrapper for CLI.

Provides high-level interface to Google Forms and Drive APIs with error handling.
"""

import csv
import io
import copy
import time
import logging
from typing import Dict, List, Optional, Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .auth import get_credentials

logger = logging.getLogger("gforms")


class FormsAPI:
    """Google Forms API client with comprehensive form management capabilities."""

    def __init__(self):
        """Initialize API clients with OAuth credentials."""
        self.creds = get_credentials()
        self.service = build('forms', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    def _sync_drive_name(self, form_id: str, title: str) -> None:
        """Sync Drive document name with form title.

        Google Forms API sets info.title but NOT the Drive document name.
        This method ensures both are synchronized.
        """
        try:
            self.drive_service.files().update(
                fileId=form_id,
                body={'name': title}
            ).execute()
        except HttpError as e:
            logger.warning(f"Failed to sync Drive name: {e}")

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

            # Sync Drive document name with form title
            self._sync_drive_name(form_id, title)

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
                except Exception:
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

            # Sync Drive document name when title changes
            if title is not None:
                self._sync_drive_name(form_id, title)

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

    def update_item(self, form_id: str, item_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing item (question, section, etc.).

        The Google Forms API requires the item type structure to be included
        in update requests, even when only updating the title.

        Args:
            form_id: The form ID
            item_id: The item ID to update
            **kwargs: Fields to update (title, description, required, etc.)

        Returns:
            Result of batch update

        Raises:
            HttpError: If update fails
        """
        try:
            # Get current form to find item structure
            form = self.get_form(form_id)
            items = form.get('items', [])

            # Find item by ID
            item_index = None
            original_item = None
            for idx, item in enumerate(items):
                if item.get('itemId') == item_id:
                    item_index = idx
                    original_item = item
                    break

            if item_index is None:
                raise ValueError(f"Item with ID '{item_id}' not found in form")

            # Build update item - must include item type structure
            update_item = copy.deepcopy(original_item)
            update_item.pop('itemId', None)  # Remove read-only field

            # Remove questionId from nested structures
            if 'questionItem' in update_item:
                if 'question' in update_item['questionItem']:
                    update_item['questionItem']['question'].pop('questionId', None)
            if 'questionGroupItem' in update_item:
                if 'questions' in update_item['questionGroupItem']:
                    for q in update_item['questionGroupItem']['questions']:
                        q.pop('questionId', None)

            update_mask = []

            if 'title' in kwargs:
                update_item['title'] = kwargs['title']
                update_mask.append('title')

            if 'description' in kwargs:
                update_item['description'] = kwargs['description']
                update_mask.append('description')

            if 'required' in kwargs and 'questionItem' in update_item:
                update_item['questionItem']['question']['required'] = kwargs['required']
                update_mask.append('questionItem.question.required')

            if not update_mask:
                raise ValueError("No fields to update")

            request = {
                "requests": [{
                    "updateItem": {
                        "item": update_item,
                        "location": {"index": item_index},
                        "updateMask": ','.join(update_mask)
                    }
                }]
            }

            return self.service.forms().batchUpdate(formId=form_id, body=request).execute()

        except HttpError as e:
            raise Exception(f"Failed to update item: {e}")

    def update_question(self, form_id: str, item_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing question. Alias for update_item for backwards compatibility."""
        return self.update_item(form_id, item_id, **kwargs)

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

            # Extract question titles using questionId (NOT itemId)
            # Response answers use questionId, not itemId
            items = form.get('items', [])
            question_map = {}
            for item in items:
                if 'questionItem' in item:
                    # Regular question
                    question_id = item['questionItem'].get('question', {}).get('questionId')
                    if question_id:
                        question_map[question_id] = item.get('title', f'Question {question_id}')
                        header.append(question_map[question_id])
                elif 'questionGroupItem' in item:
                    # Grid question - has multiple sub-questions
                    grid_title = item.get('title', 'Grid')
                    for q in item['questionGroupItem'].get('questions', []):
                        question_id = q.get('questionId')
                        row_title = q.get('rowQuestion', {}).get('title', '')
                        if question_id:
                            full_title = f"{grid_title} - {row_title}" if row_title else grid_title
                            question_map[question_id] = full_title
                            header.append(full_title)

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

    def duplicate_form(self, form_id: str, new_title: str, use_batch: bool = True, chunk_size: int = 100) -> Dict[str, Any]:
        """Duplicate an existing form with optional batch optimization.

        Args:
            form_id: The form ID to copy
            new_title: Title for the new form
            use_batch: Use optimized batch API (default True, 87-94% faster)
            chunk_size: Items per batch for large forms (default 100)

        Returns:
            Dict with newFormId, responderUri, copiedItems count, and method used

        Raises:
            HttpError: If duplication fails
        """
        if use_batch:
            return self._duplicate_form_batch(form_id, new_title, chunk_size)
        else:
            return self._duplicate_form_legacy(form_id, new_title)

    def _duplicate_form_batch(self, form_id: str, new_title: str, chunk_size: int = 100) -> Dict[str, Any]:
        """Duplicate a form using optimized batch API (87-94% faster)."""
        start_time = time.time()

        try:
            # Step 1: Get original form structure (1 API call)
            original = self.get_form(form_id)
            items = original.get('items', [])

            # Step 2: Create new empty form (1 API call)
            description = original.get('info', {}).get('description', '')
            new_form = self.create_form(new_title, description)
            new_form_id = new_form['formId']

            # Step 3: Build batch request with settings + all items
            batch_requests = []

            # Add settings update if exists
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

            # Add all item creation requests
            for i, original_item in enumerate(items):
                clean_item = self._clean_item_for_duplication(original_item)
                batch_requests.append({
                    "createItem": {
                        "item": clean_item,
                        "location": {"index": i}
                    }
                })

            # Step 4: Execute batch operations
            api_calls = 2  # get_form + create_form
            total_copied = 0

            if batch_requests:
                if len(batch_requests) <= chunk_size:
                    # Single batch execution
                    try:
                        self.service.forms().batchUpdate(
                            formId=new_form_id,
                            body={"requests": batch_requests}
                        ).execute()
                        api_calls += 1
                        total_copied = len(items)
                    except HttpError as e:
                        raise Exception(f"Failed to batch duplicate form: {e}")
                else:
                    # Chunked batch execution
                    chunks = []
                    settings_chunk = []

                    if 'settings' in original:
                        settings_chunk = [batch_requests[0]]
                        item_requests = batch_requests[1:]
                    else:
                        item_requests = batch_requests

                    for i in range(0, len(item_requests), chunk_size):
                        chunk = item_requests[i:i + chunk_size]
                        if i == 0 and settings_chunk:
                            chunk = settings_chunk + chunk
                        chunks.append(chunk)

                    for chunk_idx, chunk in enumerate(chunks):
                        try:
                            self.service.forms().batchUpdate(
                                formId=new_form_id,
                                body={"requests": chunk}
                            ).execute()
                            api_calls += 1
                            items_in_chunk = len([r for r in chunk if 'createItem' in r])
                            total_copied += items_in_chunk
                        except HttpError as e:
                            raise Exception(f"Failed to duplicate chunk {chunk_idx + 1}: {e}")

            elapsed_time = time.time() - start_time

            return {
                "newFormId": new_form_id,
                "responderUri": new_form['responderUri'],
                "editUri": f"https://docs.google.com/forms/d/{new_form_id}/edit",
                "copiedItems": total_copied,
                "totalItems": len(items),
                "apiCalls": api_calls,
                "executionTime": f"{elapsed_time:.2f}s",
                "method": "batch",
                "chunked": len(batch_requests) > chunk_size
            }

        except HttpError as e:
            raise Exception(f"Failed to duplicate form (batch method): {e}")

    def _duplicate_form_legacy(self, form_id: str, new_title: str) -> Dict[str, Any]:
        """Duplicate a form using legacy item-by-item method."""
        start_time = time.time()

        try:
            # Step 1: Get original form structure
            original = self.get_form(form_id)

            # Step 2: Create new empty form
            description = original.get('info', {}).get('description', '')
            new_form = self.create_form(new_title, description)
            new_form_id = new_form['formId']

            api_calls = 2

            # Step 3: Copy settings
            if 'settings' in original:
                settings = original['settings'].copy()
                if 'quizSettings' not in settings:
                    settings['quizSettings'] = {'isQuiz': False}

                settings_request = {
                    "requests": [{
                        "updateSettings": {
                            "settings": settings,
                            "updateMask": "*"
                        }
                    }]
                }
                self.service.forms().batchUpdate(
                    formId=new_form_id,
                    body=settings_request
                ).execute()
                api_calls += 1

            # Step 4: Copy all items
            items = original.get('items', [])
            copied_count = 0

            for i, original_item in enumerate(items):
                clean_item = self._clean_item_for_duplication(original_item)

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
                    api_calls += 1
                    copied_count += 1
                except HttpError as item_error:
                    logger.warning(f"Failed to copy item {i}: {item_error}")
                    continue

            elapsed_time = time.time() - start_time

            return {
                "newFormId": new_form_id,
                "responderUri": new_form['responderUri'],
                "editUri": f"https://docs.google.com/forms/d/{new_form_id}/edit",
                "copiedItems": copied_count,
                "totalItems": len(items),
                "apiCalls": api_calls,
                "executionTime": f"{elapsed_time:.2f}s",
                "method": "legacy"
            }

        except HttpError as e:
            raise Exception(f"Failed to duplicate form: {e}")

    def _clean_item_for_duplication(self, original_item: Dict[str, Any]) -> Dict[str, Any]:
        """Remove IDs and clean invalid characters from item for safe duplication."""
        clean_item = {}

        # Copy basic fields and clean newlines
        if 'title' in original_item:
            clean_item['title'] = original_item['title'].replace('\n', ' ').replace('\r', '')
        if 'description' in original_item:
            clean_item['description'] = original_item['description'].replace('\n', ' ').replace('\r', '')

        # Copy item type
        if 'questionItem' in original_item:
            question = copy.deepcopy(original_item['questionItem']['question'])
            question.pop('questionId', None)

            # Clean newlines from scale labels
            if 'scaleQuestion' in question:
                scale = question['scaleQuestion']
                if 'lowLabel' in scale:
                    scale['lowLabel'] = scale['lowLabel'].replace('\n', ' ').replace('\r', '')
                if 'highLabel' in scale:
                    scale['highLabel'] = scale['highLabel'].replace('\n', ' ').replace('\r', '')

            # Clean newlines from choice options
            if 'choiceQuestion' in question:
                if 'options' in question['choiceQuestion']:
                    for option in question['choiceQuestion']['options']:
                        if 'value' in option:
                            option['value'] = option['value'].replace('\n', ' ').replace('\r', '')

            clean_item['questionItem'] = {
                'question': question
            }
            if 'image' in original_item['questionItem']:
                clean_item['questionItem']['image'] = original_item['questionItem']['image']

        elif 'questionGroupItem' in original_item:
            group = copy.deepcopy(original_item['questionGroupItem'])

            if 'questions' in group:
                for q in group['questions']:
                    q.pop('questionId', None)

            if 'grid' in group and 'columns' in group['grid']:
                if 'options' in group['grid']['columns']:
                    for option in group['grid']['columns']['options']:
                        if 'value' in option:
                            option['value'] = option['value'].replace('\n', ' ').replace('\r', '')

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

    def personalize_form(self, form_id: str, replacements: Dict[str, str]) -> Dict[str, Any]:
        """Personalize a form by replacing placeholders in titles and descriptions.

        Replaces placeholder text in form title, description, and all item titles/descriptions.

        Args:
            form_id: The form ID to personalize
            replacements: Dict of placeholder -> replacement text (e.g. {"NAME": "John"})

        Returns:
            Dict with form_id, items_updated count, and details

        Raises:
            HttpError: If personalization fails
        """
        try:
            # Get current form
            form = self.get_form(form_id)
            items_updated = 0
            updates_made = []

            # Update form title and description
            form_title = form.get('info', {}).get('title', '')
            form_desc = form.get('info', {}).get('description', '')

            new_title = form_title
            new_desc = form_desc
            for placeholder, replacement in replacements.items():
                new_title = new_title.replace(placeholder, replacement)
                new_desc = new_desc.replace(placeholder, replacement)

            if new_title != form_title or new_desc != form_desc:
                self.update_form(form_id, title=new_title, description=new_desc)
                updates_made.append(f"Form title/description updated")

            # Update all items
            for item in form.get('items', []):
                item_id = item.get('itemId')
                title = item.get('title', '')
                description = item.get('description', '')

                new_item_title = title
                new_item_desc = description
                for placeholder, replacement in replacements.items():
                    new_item_title = new_item_title.replace(placeholder, replacement)
                    new_item_desc = new_item_desc.replace(placeholder, replacement)

                # Clean newlines (Google API limitation)
                new_item_title = new_item_title.replace('\n', ' ').replace('\r', '').strip()
                new_item_desc = new_item_desc.replace('\n', ' ').replace('\r', '').strip()

                if new_item_title != title.replace('\n', ' ').replace('\r', '').strip() or \
                   new_item_desc != description.replace('\n', ' ').replace('\r', '').strip():
                    try:
                        update_kwargs = {'title': new_item_title}
                        if description:
                            update_kwargs['description'] = new_item_desc
                        self.update_item(form_id, item_id, **update_kwargs)
                        items_updated += 1
                        updates_made.append(f"Updated: {new_item_title[:40]}...")
                    except Exception as e:
                        logger.warning(f"Failed to update item {item_id}: {e}")

            return {
                "formId": form_id,
                "itemsUpdated": items_updated,
                "totalItems": len(form.get('items', [])),
                "updates": updates_made
            }

        except HttpError as e:
            raise Exception(f"Failed to personalize form: {e}")
