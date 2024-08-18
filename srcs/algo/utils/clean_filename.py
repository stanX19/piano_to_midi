import re


def clean_filename(filename: str, replacement: str = "_") -> str:
    """
    Cleans the given filename by replacing invalid characters with a specified replacement character.

    Args:
        filename (str): The original filename to be cleaned.
        replacement (str): The character to replace invalid characters with (default is '_').

    Returns:
        str: The cleaned filename.
    """
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned_filename = re.sub(invalid_chars, replacement, filename)
    cleaned_filename = cleaned_filename.strip()
    max_length = 255
    if len(cleaned_filename) > max_length:
        cleaned_filename = cleaned_filename[:max_length]
    return cleaned_filename


def test():
    # Example usage
    filename = 'https://www.youtube.com/watch?v=0gsKxV3dmkU.dpf.json'
    cleaned_filename = clean_filename(filename)
    print(cleaned_filename)  # Output: https__www.youtube.com_watch?v=0gsKxV3dmkU.dpf.json


if __name__ == '__main__':
    test()
