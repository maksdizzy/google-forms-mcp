"""Google Sheets API wrapper.

Provides high-level interface to Google Sheets API for reading spreadsheet data.
"""

import re
import logging
from typing import Dict, List, Optional, Any

from googleapiclient.errors import HttpError

from ..core.base import BaseAPI

logger = logging.getLogger("gtools")


class SheetsAPI(BaseAPI):
    """Google Sheets API client for reading spreadsheet data."""

    API_NAME = "sheets"
    API_VERSION = "v4"

    def _extract_spreadsheet_id(self, spreadsheet_id_or_url: str) -> str:
        """Extract spreadsheet ID from URL or return as-is if already an ID.

        Args:
            spreadsheet_id_or_url: Either a spreadsheet ID or a full Google Sheets URL

        Returns:
            Extracted spreadsheet ID

        Raises:
            ValueError: If URL format is invalid
        """
        if "docs.google.com" in spreadsheet_id_or_url or "sheets.google.com" in spreadsheet_id_or_url:
            match = re.search(r'/d/([a-zA-Z0-9-_]+)', spreadsheet_id_or_url)
            if match:
                return match.group(1)
            raise ValueError(f"Invalid spreadsheet URL: {spreadsheet_id_or_url}")
        return spreadsheet_id_or_url

    def _build_range(
        self,
        sheet_name: Optional[str] = None,
        range_notation: Optional[str] = None
    ) -> str:
        """Build A1 notation range string.

        Args:
            sheet_name: Name of the sheet (optional)
            range_notation: A1 notation range like "A1:D10" (optional)

        Returns:
            Properly formatted A1 notation string
        """
        if sheet_name and range_notation:
            escaped_name = sheet_name.replace("'", "''")
            return f"'{escaped_name}'!{range_notation}"
        elif sheet_name:
            escaped_name = sheet_name.replace("'", "''")
            return f"'{escaped_name}'"
        elif range_notation:
            return range_notation
        return "A:ZZ"

    def _normalize_values(
        self,
        values: List[List[Any]],
        fill_value: str = ""
    ) -> List[List[str]]:
        """Normalize jagged array to rectangular matrix.

        Args:
            values: Jagged array from Sheets API
            fill_value: Value to use for missing cells

        Returns:
            Rectangular matrix with all rows having the same length
        """
        if not values:
            return []
        max_cols = max(len(row) for row in values)
        return [
            [str(cell) if cell is not None else fill_value for cell in row] +
            [fill_value] * (max_cols - len(row))
            for row in values
        ]

    def get_spreadsheet(self, spreadsheet_id: str) -> Dict[str, Any]:
        """Get spreadsheet metadata including all sheets.

        Args:
            spreadsheet_id: Spreadsheet ID or URL

        Returns:
            Dictionary with spreadsheet metadata

        Raises:
            HttpError: If spreadsheet not found or access denied
        """
        sid = self._extract_spreadsheet_id(spreadsheet_id)

        try:
            result = self.service.spreadsheets().get(
                spreadsheetId=sid,
                includeGridData=False
            ).execute()

            return {
                "spreadsheetId": result["spreadsheetId"],
                "title": result["properties"]["title"],
                "locale": result["properties"].get("locale"),
                "timeZone": result["properties"].get("timeZone"),
                "sheets": [
                    {
                        "sheetId": sheet["properties"]["sheetId"],
                        "title": sheet["properties"]["title"],
                        "index": sheet["properties"]["index"],
                        "rowCount": sheet["properties"]["gridProperties"]["rowCount"],
                        "columnCount": sheet["properties"]["gridProperties"]["columnCount"],
                    }
                    for sheet in result.get("sheets", [])
                ]
            }
        except HttpError as e:
            if e.resp.status == 404:
                raise ValueError(f"Spreadsheet not found: {sid}")
            elif e.resp.status == 403:
                raise ValueError(
                    f"Access denied to spreadsheet: {sid}. "
                    "Make sure you have view access and have re-authenticated with 'gtools auth setup'."
                )
            raise

    def list_sheets(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """List all sheets in a spreadsheet.

        Args:
            spreadsheet_id: Spreadsheet ID or URL

        Returns:
            List of sheet metadata dictionaries
        """
        info = self.get_spreadsheet(spreadsheet_id)
        return info["sheets"]

    def read_values(
        self,
        spreadsheet_id: str,
        range_notation: Optional[str] = None,
        sheet_name: Optional[str] = None,
        normalize: bool = True
    ) -> Dict[str, Any]:
        """Read values from a spreadsheet range.

        Args:
            spreadsheet_id: Spreadsheet ID or URL
            range_notation: A1 notation range (e.g., "A1:D10")
            sheet_name: Name of sheet to read from
            normalize: Whether to normalize jagged arrays

        Returns:
            Dictionary with range, values, rowCount, columnCount

        Raises:
            HttpError: If spreadsheet not found or access denied
        """
        sid = self._extract_spreadsheet_id(spreadsheet_id)
        range_str = self._build_range(sheet_name, range_notation)

        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sid,
                range=range_str,
                valueRenderOption="FORMATTED_VALUE",
                dateTimeRenderOption="FORMATTED_STRING"
            ).execute()

            values = result.get("values", [])

            if normalize:
                values = self._normalize_values(values)

            return {
                "range": result.get("range", range_str),
                "values": values,
                "rowCount": len(values),
                "columnCount": max(len(row) for row in values) if values else 0
            }
        except HttpError as e:
            if e.resp.status == 404:
                raise ValueError(f"Spreadsheet not found: {sid}")
            elif e.resp.status == 403:
                raise ValueError(
                    f"Access denied to spreadsheet: {sid}. "
                    "Make sure you have view access and have re-authenticated with 'gtools auth setup'."
                )
            elif e.resp.status == 400:
                raise ValueError(f"Invalid range: {range_str}")
            raise

    def read_batch(
        self,
        spreadsheet_id: str,
        ranges: List[str]
    ) -> List[Dict[str, Any]]:
        """Read multiple ranges in a single API call.

        Args:
            spreadsheet_id: Spreadsheet ID or URL
            ranges: List of A1 notation ranges

        Returns:
            List of dictionaries with range, values, rowCount, columnCount
        """
        sid = self._extract_spreadsheet_id(spreadsheet_id)

        try:
            result = self.service.spreadsheets().values().batchGet(
                spreadsheetId=sid,
                ranges=ranges,
                valueRenderOption="FORMATTED_VALUE",
                dateTimeRenderOption="FORMATTED_STRING"
            ).execute()

            return [
                {
                    "range": vr.get("range", ""),
                    "values": self._normalize_values(vr.get("values", [])),
                    "rowCount": len(vr.get("values", [])),
                    "columnCount": max(len(row) for row in vr.get("values", [])) if vr.get("values") else 0
                }
                for vr in result.get("valueRanges", [])
            ]
        except HttpError as e:
            if e.resp.status == 404:
                raise ValueError(f"Spreadsheet not found: {sid}")
            elif e.resp.status == 403:
                raise ValueError(
                    f"Access denied to spreadsheet: {sid}. "
                    "Make sure you have view access and have re-authenticated with 'gtools auth setup'."
                )
            raise

    def export_to_csv(
        self,
        spreadsheet_id: str,
        range_notation: Optional[str] = None,
        sheet_name: Optional[str] = None,
        include_header: bool = True
    ) -> str:
        """Export spreadsheet data to CSV format.

        Args:
            spreadsheet_id: Spreadsheet ID or URL
            range_notation: A1 notation range (optional)
            sheet_name: Sheet name (optional)
            include_header: Whether first row is a header

        Returns:
            CSV formatted string
        """
        import csv
        import io

        data = self.read_values(spreadsheet_id, range_notation, sheet_name)
        values = data["values"]

        if not values:
            return ""

        output = io.StringIO()
        writer = csv.writer(output)
        for row in values:
            writer.writerow(row)

        return output.getvalue()
