import textwrap

def wrap_text(s: str, width: int = 20) -> str:
    return textwrap.fill(str(s), width=width)
