"""Collection of helper functions to colorize print output."""

def color_red(text: str) -> str:
    """Print text in red color."""

    return f"\033[91m{text}\033[0m"

def color_green(text: str) -> str:
    """Print text in green color."""

    return f"\033[92m{text}\033[0m"

def color_yellow(text: str) -> str:
    """Print text in yellow color."""

    return f"\033[93m{text}\033[0m"

def color_cyan(text: str) -> str:
    """Print text in cyan color."""

    return f"\033[96m{text}\033[0m"
