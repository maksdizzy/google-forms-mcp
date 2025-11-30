"""Pydantic models for Google Sheets.

Provides validation and serialization for spreadsheet data.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class SheetMetadata(BaseModel):
    """Metadata for a single sheet within a spreadsheet."""
    sheetId: int
    title: str
    index: int = 0
    rowCount: int = 0
    columnCount: int = 0


class SpreadsheetInfo(BaseModel):
    """Spreadsheet metadata including all sheets."""
    spreadsheetId: str
    title: str
    locale: Optional[str] = None
    timeZone: Optional[str] = None
    sheets: List[SheetMetadata] = Field(default_factory=list)


class SheetData(BaseModel):
    """Data read from a spreadsheet range."""
    range: str
    values: List[List[str]] = Field(default_factory=list)
    rowCount: int = 0
    columnCount: int = 0
