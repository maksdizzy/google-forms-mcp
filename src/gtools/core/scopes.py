"""OAuth scopes for Google APIs.

Centralized scope management for all Google services.
"""

# Google Forms scopes
SCOPES_FORMS = [
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/forms.responses.readonly',
]

# Google Sheets scopes
SCOPES_SHEETS = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
]

# Google Drive scopes (commonly needed by other services)
SCOPES_DRIVE = [
    'https://www.googleapis.com/auth/drive.file',
]

# All scopes combined
SCOPES = SCOPES_FORMS + SCOPES_SHEETS + SCOPES_DRIVE


def get_scopes_for_products(products: list[str] | None = None) -> list[str]:
    """Get OAuth scopes for specified products.

    Args:
        products: List of product names ('forms', 'sheets', 'drive').
                  If None, returns all scopes.

    Returns:
        List of OAuth scope URLs.
    """
    if products is None:
        return SCOPES

    scopes = set(SCOPES_DRIVE)  # Drive is always needed

    if 'forms' in products:
        scopes.update(SCOPES_FORMS)
    if 'sheets' in products:
        scopes.update(SCOPES_SHEETS)

    return list(scopes)
