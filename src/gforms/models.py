#!/usr/bin/env python3
"""Pydantic models for Google Forms CLI.

Provides validation and serialization for form templates and API data.
"""

from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    """Supported Google Forms question types."""
    SHORT_ANSWER = "SHORT_ANSWER"
    PARAGRAPH = "PARAGRAPH"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    CHECKBOXES = "CHECKBOXES"
    DROPDOWN = "DROPDOWN"
    LINEAR_SCALE = "LINEAR_SCALE"
    DATE = "DATE"
    TIME = "TIME"
    FILE_UPLOAD = "FILE_UPLOAD"
    MULTIPLE_CHOICE_GRID = "MULTIPLE_CHOICE_GRID"
    CHECKBOX_GRID = "CHECKBOX_GRID"
    RATING = "RATING"


class BaseQuestion(BaseModel):
    """Base model for all question types."""
    type: QuestionType
    title: str
    description: Optional[str] = None
    required: bool = False


class TextQuestion(BaseQuestion):
    """Short answer or paragraph question."""
    type: QuestionType = QuestionType.SHORT_ANSWER


class ChoiceQuestion(BaseQuestion):
    """Multiple choice, checkbox, or dropdown question."""
    type: QuestionType = QuestionType.MULTIPLE_CHOICE
    options: List[str] = Field(default_factory=list)


class ScaleQuestion(BaseQuestion):
    """Linear scale or rating question."""
    type: QuestionType = QuestionType.LINEAR_SCALE
    low: int = 1
    high: int = 5
    lowLabel: Optional[str] = ""
    highLabel: Optional[str] = ""


class DateQuestion(BaseQuestion):
    """Date question."""
    type: QuestionType = QuestionType.DATE
    includeTime: bool = False
    includeYear: bool = True


class TimeQuestion(BaseQuestion):
    """Time question."""
    type: QuestionType = QuestionType.TIME
    duration: bool = False


class FileUploadQuestion(BaseQuestion):
    """File upload question."""
    type: QuestionType = QuestionType.FILE_UPLOAD
    folderId: Optional[str] = None
    maxFiles: int = 1
    maxFileSize: int = 10485760  # 10MB
    allowedTypes: List[str] = Field(default_factory=list)


class GridQuestion(BaseQuestion):
    """Grid question (multiple choice or checkbox grid)."""
    type: QuestionType = QuestionType.MULTIPLE_CHOICE_GRID
    rows: List[str] = Field(default_factory=list)
    columns: List[str] = Field(default_factory=list)


# Union of all question types
Question = Union[
    TextQuestion,
    ChoiceQuestion,
    ScaleQuestion,
    DateQuestion,
    TimeQuestion,
    FileUploadQuestion,
    GridQuestion,
]


class Section(BaseModel):
    """Section/page break in a form."""
    title: str
    description: Optional[str] = ""


class FormInfo(BaseModel):
    """Form metadata."""
    title: str
    description: Optional[str] = ""


class FormTemplate(BaseModel):
    """Complete form template for YAML serialization."""
    form: FormInfo
    questions: List[dict] = Field(default_factory=list)
    sections: Optional[List[Section]] = None

    class Config:
        extra = "allow"


class FormCreateResult(BaseModel):
    """Result of form creation."""
    formId: str
    responderUri: str
    editUri: str
    questionsAdded: int = 0


class FormListItem(BaseModel):
    """Form item in list response."""
    formId: str
    title: str
    responderUri: Optional[str] = None
    responseCount: int = 0


class FormListResult(BaseModel):
    """Result of form listing."""
    forms: List[FormListItem]
    nextPageToken: Optional[str] = None


class ResponseItem(BaseModel):
    """Individual response."""
    responseId: str
    createTime: str
    respondentEmail: Optional[str] = None


class ExportResult(BaseModel):
    """Result of CSV export."""
    csv: str
    rowCount: int


class DuplicateResult(BaseModel):
    """Result of form duplication."""
    newFormId: str
    responderUri: str
    editUri: str
    copiedItems: int
    totalItems: int
    apiCalls: int
    executionTime: str
    method: str
    chunked: bool = False
