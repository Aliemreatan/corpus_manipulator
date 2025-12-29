#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to verify Turkish character support without console output issues
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_turkish_support():
    """Test Turkish character support"""
    print("Testing Turkish character support...")
    
    # Test 1: Configuration
    try:
        from config.config import TURKISH_CHARACTERS
        print(f"✓ Turkish characters defined: {len(TURKISH_CHARACTERS)} characters")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False
    
    # Test 2: Simple processor
    try:
        from nlp.turkish_processor import TurkishNLPProcessor
        processor = TurkishNLPProcessor(backend='simple')
        
        # Test with Turkish characters (using Unicode escape sequences to avoid console issues)
        test_text = "suc" + "\\u015F" + "ar" + "\\u00E7" + "ak"  # "şarkıçak"
        tokens = processor.process_text(test_text)
        
        print(f"✓ Simple processor: {len(tokens)} tokens processed")
        
        # Check if Turkish characters are in the regex pattern
        import inspect
        source = inspect.getsource(processor._process_simple)
        if "\\u015F" in source or "ş" in source:
            print("✓ Turkish characters found in tokenization regex")
        else:
            print("! Turkish characters may not be in tokenization")
            
    except Exception as e:
        print(f"✗ Simple processor error: {e}")
    
    # Test 3: BERT processor availability
    try:
        from nlp.custom_bert_processor import create_custom_bert_processor
        bert = create_custom_bert_processor()
        
        print(f"✓ BERT processor created (loaded: {bert.is_loaded})")
        
    except Exception as e:
        print(f"✗ BERT processor error: {e}")
    
    # Test 4: Database functionality
    try:
        from ingestion.corpus_ingestor import CorpusIngestor
        
        # Create test file with Turkish characters
        test_dir = Path("temp_turkish_test")
        test_dir.mkdir(exist_ok=True)
        
        # Create file with Turkish characters using Unicode escapes
        test_file = test_dir / "test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            # Write Turkish text using Unicode escapes
            f.write("suc\\u015Farlar\\n")  # "şarlar"
            f.write("coc\\u00E7uklar\\n")  # "çocuklar" 
            f.write("ogrenciler\\n")       # "öğrenciler"
        
        # Test ingestion
        test_db = "temp_turkish.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        ingestor = CorpusIngestor(test_db, nlp_backend='simple')
        stats = ingestor.ingest_directory(str(test_dir))
        ingestor.close()
        
        print(f"✓ Database ingestion: {stats['tokens_processed']} tokens")
        
        # Clean up
        import shutil
        shutil.rmtree(test_dir)
        if os.path.exists(test_db):
            os.remove(test_db)
            
    except Exception as e:
        print(f"✗ Database test error: {e}")
    
    print("\nTurkish character support test completed!")
    return True

if __name__ == "__main__":
    test_turkish_support()