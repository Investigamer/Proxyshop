"""
Utility Helpers Module
"""
import unicodedata
import string


def normalize_str(st: str) -> str:
    # Ignore accents and unusual characters, all lowercase
    st = unicodedata.normalize("NFD", st).encode("ascii", "ignore").decode("utf8").lower()

    # Remove punctuation
    return st.translate(str.maketrans("", "", string.punctuation))
