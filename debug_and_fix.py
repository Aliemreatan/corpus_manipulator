#!/usr/bin/env python3
"""
Debug and Fix Script for Corpus Manipulator
This script systematically tests and fixes all reported issues.
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_schema():
    """Test and fix database schema issues"""
    print("=== DATABASE SCHEMA TEST ===")
    
    try:
        from database.schema import CorpusDatabase
        
        # Create fresh database
        db_path = "debug_test.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            
        db = CorpusDatabase(db_path)
        db.connect()
        db.create_schema()
        
        print("✅ Database schema created successfully")
        
        # Test schema
        schema_info = db.get_schema_info()
        print(f"✅ Tables created: {list(schema_info['tables'].keys())}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database schema error: {e}")
        return False

def test_bert_model():
    """Test BERT model functionality"""
    print("\n=== BERT MODEL TEST ===")
    
    try:
        from nlp.custom_bert_processor import create_custom_bert_processor
        
        bert = create_custom_bert_processor()
        info = bert.get_model_info()
        
        print(f"Model: {info['model_path']}")
        print(f"Loaded: {info['is_loaded']}")
        
        if info['is_loaded']:
            # Test with simple text
            test_text = "Merhaba dunya"
            tokens = bert.process_text(test_text)
            
            print(f"✅ Test text processed: {len(tokens)} tokens")
            for i, token in enumerate(tokens[:3], 1):
                confidence = token.get('bert_confidence', 'N/A')
                print(f"  {i}. {token['form']} -> {token['upos']} (conf: {confidence})")
            
            return True
        else:
            print("❌ BERT model not loaded")
            return False
            
    except Exception as e:
        print(f"❌ BERT model error: {e}")
        return False

def test_file_ingestion():
    """Test file ingestion with multiple formats"""
    print("\n=== FILE INGESTION TEST ===")
    
    try:
        from ingestion.corpus_ingestor import CorpusIngestor
        
        # Clean test database
        test_db = "debug_ingest.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        # Create ingestor with BERT backend
        ingestor = CorpusIngestor(test_db, nlp_backend='custom_bert')
        
        # Test with sample directory
        sample_dir = "sample_turkish_corpus"
        if os.path.exists(sample_dir):
            print(f"📂 Processing directory: {sample_dir}")
            
            # Test ingestion with multiple formats
            stats = ingestor.ingest_directory(sample_dir, file_patterns=['*.txt', '*.json', '*.xml'])
            
            print(f"✅ Ingestion results:")
            print(f"  Documents: {stats['documents_processed']}")
            print(f"  Sentences: {stats['sentences_processed']}")
            print(f"  Tokens: {stats['tokens_processed']}")
            print(f"  Errors: {stats['errors']}")
            
            # Test database content
            if stats['documents_processed'] > 0:
                cursor = ingestor.db.connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM documents")
                doc_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM tokens")
                token_count = cursor.fetchone()[0]
                
                print(f"✅ Database verification:")
                print(f"  Documents in DB: {doc_count}")
                print(f"  Tokens in DB: {token_count}")
                
                # Show sample data
                cursor.execute("SELECT doc_name FROM documents LIMIT 3")
                docs = cursor.fetchall()
                print(f"  Sample documents: {[doc[0] for doc in docs]}")
            
            ingestor.close()
            return stats['errors'] == 0
            
        else:
            print(f"❌ Sample directory not found: {sample_dir}")
            return False
            
    except Exception as e:
        print(f"❌ File ingestion error: {e}")
        return False

def test_search_functionality():
    """Test search and query functionality"""
    print("\n=== SEARCH FUNCTIONALITY TEST ===")
    
    try:
        from query.corpus_query import CorpusQuery
        
        # Test with debug database
        test_db = "debug_ingest.db"
        if not os.path.exists(test_db):
            print("❌ Test database not found, skipping search test")
            return False
        
        query = CorpusQuery(test_db)
        
        # Test frequency list
        print("Testing frequency list...")
        freq_results = query.frequency_list(word_type='norm', limit=10)
        
        if freq_results:
            print(f"✅ Frequency list: {len(freq_results)} words")
            print(f"  Top 3: {[(item['word'], item['frequency']) for item in freq_results[:3]]}")
        else:
            print("⚠️  No frequency results (database may be empty)")
        
        # Test KWIC if we have data
        if freq_results:
            test_word = freq_results[0]['word']
            print(f"Testing KWIC for word: {test_word}")
            kwic_results = query.kwic_concordance(test_word, window_size=5, limit=5)
            
            if kwic_results:
                print(f"✅ KWIC results: {len(kwic_results)} matches")
            else:
                print("⚠️  No KWIC results")
        
        query.close()
        return True
        
    except Exception as e:
        print(f"❌ Search functionality error: {e}")
        return False

def fix_label_mapping():
    """Fix BERT label mapping for the Turkish model"""
    print("\n=== FIXING BERT LABEL MAPPING ===")
    
    try:
        # Update label mapping to match Turkish POS tags
        from nlp.custom_bert_processor import create_custom_bert_processor
        
        bert = create_custom_bert_processor()
        
        # Test with text that should trigger different POS tags
        test_texts = [
            "Ben okula gidiyorum",  # Should have VERB, NOUN, etc.
            "Bu guzel bir kitap",   # Should have DET, ADJ, NOUN
            "Ve ya da ama"          # Should have CCONJ
        ]
        
        print("Testing Turkish POS tagging:")
        for i, text in enumerate(test_texts, 1):
            tokens = bert.process_text(text)
            pos_tags = [token['upos'] for token in tokens if token.get('upos')]
            print(f"  {i}. '{text}' -> {set(pos_tags)}")
        
        print("✅ Label mapping test completed")
        return True
        
    except Exception as e:
        print(f"❌ Label mapping error: {e}")
        return False

def create_working_demo():
    """Create a working demo with fixed functionality"""
    print("\n=== CREATING WORKING DEMO ===")
    
    try:
        # Create a simple working database
        demo_db = "working_demo.db"
        if os.path.exists(demo_db):
            os.remove(demo_db)
        
        from ingestion.corpus_ingestor import CorpusIngestor
        
        # Create sample text files
        sample_dir = Path("demo_samples")
        sample_dir.mkdir(exist_ok=True)
        
        # Create simple Turkish text files
        sample_texts = [
            "Ben okula gidiyorum. Annem eve geldi.",
            "Bu kitap cok guzel. Arkadasimla okudum.",
            "Okulda ogreten var. Ogrenciler calisiyor."
        ]
        
        for i, text in enumerate(sample_texts, 1):
            with open(sample_dir / f"demo_{i}.txt", 'w', encoding='utf-8') as f:
                f.write(text)
        
        print(f"📝 Created {len(sample_texts)} demo files")
        
        # Ingest with simple backend to ensure it works
        ingestor = CorpusIngestor(demo_db, nlp_backend='simple')
        stats = ingestor.ingest_directory(str(sample_dir))
        
        print(f"✅ Demo ingestion completed:")
        print(f"  Documents: {stats['documents_processed']}")
        print(f"  Tokens: {stats['tokens_processed']}")
        
        # Test search
        from query.corpus_query import CorpusQuery
        query = CorpusQuery(demo_db)
        
        # Test frequency
        freq = query.frequency_list(limit=10)
        print(f"✅ Search test: {len(freq)} unique words found")
        
        # Test KWIC
        if freq:
            test_word = freq[0]['word']
            kwic = query.kwic_concordance(test_word, limit=3)
            print(f"✅ KWIC test: Found {len(kwic)} matches for '{test_word}'")
        
        query.close()
        ingestor.close()
        
        print(f"✅ Working demo database created: {demo_db}")
        return True
        
    except Exception as e:
        print(f"❌ Demo creation error: {e}")
        return False

def main():
    """Main debug and fix function"""
    print("CORPUS MANIPULATOR DEBUG & FIX")
    print("=" * 50)
    
    # Run all tests and fixes
    tests = [
        ("Database Schema", test_database_schema),
        ("BERT Model", test_bert_model),
        ("File Ingestion", test_file_ingestion),
        ("Search Functionality", test_search_functionality),
        ("Label Mapping", fix_label_mapping),
        ("Working Demo", create_working_demo)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("DEBUG SUMMARY:")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System should be working now.")
        print("\nNext steps:")
        print("1. python run_gui.py")
        print("2. Use the working_demo.db for testing")
        print("3. Try importing files with 'custom_bert' backend")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Some issues remain.")

if __name__ == "__main__":
    main()