import platform;

def get_python_info() -> str:
    python_info = f"Python {platform.python_version()} {platform.architecture()}"
    return python_info