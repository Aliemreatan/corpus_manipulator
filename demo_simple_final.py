#!/usr/bin/env python3
"""
Simple BERT Model Demo - Final Version
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_bert_status():
    """Show BERT model status"""
    print("=== BERT MODEL STATUS ===")
    
    try:
        from nlp.custom_bert_processor import create_custom_bert_processor
        bert = create_custom_bert_processor()
        info = bert.get_model_info()
        
        print(f"Model: {info['model_path']}")
        print(f"Loaded: {info['is_loaded']}")
        print(f"Language: {info['language']}")
        print(f"Features: {', '.join(info['supported_features'])}")
        
        if info['is_loaded']:
            print("\n=== TESTING BERT ===")
            test_text = "Türkçe dil işleme için BERT modeli."
            tokens = bert.process_text(test_text)
            
            print(f"Input: {test_text}")
            print(f"Tokens: {len(tokens)}")
            print("Results:")
            for i, token in enumerate(tokens, 1):
                confidence = token.get('bert_confidence', 'N/A')
                if isinstance(confidence, (int, float)):
                    confidence_str = f"{confidence:.3f}"
                else:
                    confidence_str = str(confidence)
                print(f"  {i}. {token['form']} -> {token['upos']} (conf: {confidence_str})")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def demo_multiformat():
    """Test multi-format support"""
    print("\n=== MULTI-FORMAT TEST ===")
    
    from ingestion.corpus_ingestor import CorpusIngestor
    
    sample_dir = "sample_turkish_corpus"
    
    if os.path.exists(sample_dir):
        try:
            print(f"Testing directory: {sample_dir}")
            ingestor = CorpusIngestor("demo_final.db", nlp_backend='custom_bert')
            
            # Test with multiple formats
            stats = ingestor.ingest_directory(sample_dir, file_patterns=['*.txt', '*.json', '*.xml'])
            
            print("Results:")
            print(f"  Documents: {stats['documents_processed']}")
            print(f"  Sentences: {stats['sentences_processed']}")
            print(f"  Tokens: {stats['tokens_processed']}")
            print(f"  Errors: {stats['errors']}")
            
            ingestor.close()
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    else:
        print(f"Directory not found: {sample_dir}")
        return False

def main():
    """Main demo"""
    print("BERT MODEL FINAL DEMO")
    print("=" * 40)
    
    # Test BERT
    bert_ok = demo_bert_status()
    
    # Test multi-format
    format_ok = demo_multiformat()
    
    print("\n" + "=" * 40)
    if bert_ok and format_ok:
        print("SUCCESS: All features working!")
        print("\nGUI Usage:")
        print("1. python run_gui.py")
        print("2. Create database")
        print("3. Import corpus with 'custom_bert' backend")
        print("4. Use BERT analysis section")
    else:
        print("Some features may need troubleshooting")

if __name__ == "__main__":
    main()