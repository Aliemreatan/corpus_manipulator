"""
Configuration settings for Corpus Data Manipulator
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for dir_path in [DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# Database settings
DATABASE_PATH = BASE_DIR / "corpus.db"

# NLP Settings
DEFAULT_WINDOW_SIZE = 5  # For collocation analysis
MAX_TOKEN_LENGTH = 100
MIN_TOKEN_LENGTH = 1

# Turkish language specific settings
TURKISH_STOPWORDS = {
    've', 'bir', 'bu', 'da', 'de', 'ile', 'için', 'var', 'yok', 'çok', 'daha',
    'ama', 'ancak', 'fakat', 'lakin', 'halbuki', 'oysa', 'şu', 'o', 'onun',
    'bunun', 'şunun', 'o', 'hepsi', 'tümü', 'bütün', 'hiç', 'bazı', 'kimse',
    'herkes', 'her', 'hiçbir', 'biri', 'bazıları', 'bazılarına', 'bazılarından'
}

# Turkish character preservation (NO normalization to ASCII)
# Turkish characters are PRESERVED throughout the system
TURKISH_CHARACTERS = {
    'ç', 'ğ', 'ı', 'İ', 'ö', 'ş', 'ü', 'Ç', 'Ğ', 'İ', 'Ö', 'Ş', 'Ü'
}

# Legacy normalization (deprecated - kept for backward compatibility only)
# NOTE: This is NO LONGER USED in the system - Turkish characters are preserved
TURKISH_NORMALIZATION = {}

# Dependency relations commonly used in Turkish
TURKISH_DEPREL_SET = {
    'nsubj', 'obj', 'iobj', 'obl', 'advcl', 'advmod', 'amod', 'det', 'case',
    'conj', 'cc', 'discourse', 'expl', 'aux', 'cop', 'mark', 'punct', 'root',
    'compound', 'list', 'parataxis', 'appos', 'num', 'acl', 'csubj', 'xcomp'
}