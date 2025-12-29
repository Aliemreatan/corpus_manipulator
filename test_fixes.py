#!/usr/bin/env python3
"""
Simple test without Unicode - Test all fixes
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic functionality step by step"""
    print("TESTING BASIC FUNCTIONALITY")
    print("=" * 40)
    
    # Test 1: Database
    print("\n1. Testing Database...")
    try:
        from database.schema import CorpusDatabase
        
        db_path = "test_basic.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            
        db = CorpusDatabase(db_path)
        db.connect()
        db.create_schema()
        db.close()
        
        print("   SUCCESS: Database created")
        
    except Exception as e:
        print(f"   ERROR: Database - {e}")
        return False
    
    # Test 2: BERT Model
    print("\n2. Testing BERT Model...")
    try:
        from nlp.custom_bert_processor import create_custom_bert_processor
        
        bert = create_custom_bert_processor()
        info = bert.get_model_info()
        
        print(f"   Model: {info['model_path']}")
        print(f"   Loaded: {info['is_loaded']}")
        
        if info['is_loaded']:
            test_text = "Merhaba dunya"
            tokens = bert.process_text(test_text)
            print(f"   SUCCESS: Processed {len(tokens)} tokens")
        else:
            print("   WARNING: BERT not loaded")
            
    except Exception as e:
        print(f"   ERROR: BERT - {e}")
        return False
    
    # Test 3: File Ingestion
    print("\n3. Testing File Ingestion...")
    try:
        from ingestion.corpus_ingestor import CorpusIngestor
        
        ingest_db = "test_ingest.db"
        if os.path.exists(ingest_db):
            os.remove(ingest_db)
        
        # Create sample file
        sample_dir = Path("test_samples")
        sample_dir.mkdir(exist_ok=True)
        
        with open(sample_dir / "test1.txt", 'w', encoding='utf-8') as f:
            f.write("Ben okula gidiyorum. Annem eve geldi.")
        
        # Test ingestion
        ingestor = CorpusIngestor(ingest_db, nlp_backend='simple')
        stats = ingestor.ingest_directory(str(sample_dir))
        ingestor.close()
        
        print(f"   Documents: {stats['documents_processed']}")
        print(f"   Tokens: {stats['tokens_processed']}")
        print(f"   Errors: {stats['errors']}")
        
        if stats['errors'] == 0:
            print("   SUCCESS: Ingestion completed")
        else:
            print("   WARNING: Some errors during ingestion")
            
    except Exception as e:
        print(f"   ERROR: Ingestion - {e}")
        return False
    
    # Test 4: Search
    print("\n4. Testing Search...")
    try:
        from query.corpus_query import CorpusQuery
        
        query = CorpusQuery("test_ingest.db")
        
        # Test frequency
        freq = query.frequency_list(limit=10)
        print(f"   Frequency results: {len(freq)} words")
        
        # Test KWIC
        if freq:
            test_word = freq[0]['word']
            kwic = query.kwic_concordance(test_word, limit=3)
            print(f"   KWIC results for '{test_word}': {len(kwic)} matches")
        
        query.close()
        print("   SUCCESS: Search working")
        
    except Exception as e:
        print(f"   ERROR: Search - {e}")
        return False
    
    print("\n" + "=" * 40)
    print("BASIC TESTS COMPLETED")
    return True

def test_gui_compatibility():
    """Test GUI compatibility"""
    print("\nTESTING GUI COMPATIBILITY")
    print("=" * 40)
    
    try:
        # Test if GUI can be imported
        from gui.corpus_gui import CorpusGUI
        print("SUCCESS: GUI module imports correctly")
        
        # Test if required modules are available
        required_modules = [
            'database.schema',
            'nlp.turkish_processor', 
            'ingestion.corpus_ingestor',
            'query.corpus_query'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"SUCCESS: {module} available")
            except Exception as e:
                print(f"ERROR: {module} - {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: GUI compatibility - {e}")
        return False

def create_working_example():
    """Create a working example"""
    print("\nCREATING WORKING EXAMPLE")
    print("=" * 40)
    
    try:
        # Create sample data
        sample_dir = Path("working_example")
        sample_dir.mkdir(exist_ok=True)
        
        # Create Turkish text files
        texts = [
            "Ben okula gidiyorum. Annem eve geldi.",
            "Bu kitap cok guzel. Arkadasimla okudum.",
            "Okulda ogreten var. Ogrenciler calisiyor."
        ]
        
        for i, text in enumerate(texts, 1):
            with open(sample_dir / f"example_{i}.txt", 'w', encoding='utf-8') as f:
                f.write(text)
        
        print(f"Created {len(texts)} example files")
        
        # Ingest with simple backend for reliability
        from ingestion.corpus_ingestor import CorpusIngestor
        
        db_path = "working_example.db"
        if os.path.exists(db_path):
            os.remove(db_path)
        
        ingestor = CorpusIngestor(db_path, nlp_backend='simple')
        stats = ingestor.ingest_directory(str(sample_dir))
        ingestor.close()
        
        print(f"Ingestion complete:")
        print(f"  Documents: {stats['documents_processed']}")
        print(f"  Tokens: {stats['tokens_processed']}")
        
        # Test the database
        from query.corpus_query import CorpusQuery
        query = CorpusQuery(db_path)
        
        freq = query.frequency_list(limit=5)
        print(f"Search test: {len(freq)} unique words")
        
        if freq:
            print(f"Top words: {[item['word'] for item in freq[:3]]}")
        
        query.close()
        
        print("SUCCESS: Working example created")
        return True
        
    except Exception as e:
        print(f"ERROR: Working example - {e}")
        return False

def main():
    """Main test function"""
    print("CORPUS MANIPULATOR FUNCTIONALITY TEST")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("GUI Compatibility", test_gui_compatibility),
        ("Working Example", create_working_example)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'-'*20} {test_name} {'-'*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"ERROR: {test_name} failed - {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    for test_name, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"{test_name:20} {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSUCCESS: All functionality working!")
        print("\nGUI Usage:")
        print("1. python run_gui.py")
        print("2. Create database: working_example.db")
        print("3. Import corpus: working_example folder")
        print("4. Try search functions")
    else:
        print(f"\nFAILURE: {total-passed} tests failed")

if __name__ == "__main__":
    main()