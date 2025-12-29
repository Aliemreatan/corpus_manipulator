#!/usr/bin/env python3
"""
Test script for the new Hugging Face BERT model integration

Bu script yeni Hugging Face BERT modelinin nasıl kullanılacağını gösterir.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nlp.turkish_processor import create_turkish_processor
from nlp.custom_bert_processor import create_custom_bert_processor

def test_custom_bert_processor():
    """Test the custom BERT processor directly"""
    print("=== CUSTOM BERT PROCESSOR TEST ===")
    
    try:
        # Create BERT processor
        bert_processor = create_custom_bert_processor()
        
        # Get model info
        info = bert_processor.get_model_info()
        print(f"Model Type: {info['model_type']}")
        print(f"Model Path: {info['model_path']}")
        print(f"Is Loaded: {info['is_loaded']}")
        print(f"Features: {info['supported_features']}")
        print()
        
        # Test with Turkish text
        test_text = "Ben okula gidiyorum ve kitap okuyorum."
        print(f"Test Text: {test_text}")
        
        tokens = bert_processor.process_text(test_text)
        print(f"Processed {len(tokens)} tokens")
        print()
        
        # Show results
        print("Token Analysis:")
        for i, token in enumerate(tokens):
            confidence = token.get('bert_confidence', 'N/A')
            print(f"{i+1:2d}. {token['form']:10s} -> POS: {token['upos']:6s} | "
                  f"Morph: {token['morph'] or 'None':20s} | Confidence: {confidence:.3f}")
        
        return True
        
    except Exception as e:
        print(f"Error testing custom BERT processor: {e}")
        return False

def test_turkish_processor_with_bert():
    """Test TurkishNLPProcessor with custom BERT backend"""
    print("\n=== TURKISH PROCESSOR WITH BERT BACKEND TEST ===")
    
    try:
        # Create Turkish processor with BERT backend
        nlp = create_turkish_processor(backend='custom_bert')
        
        # Get processing info
        info = nlp.get_processing_info()
        print(f"Backend: {info['backend']}")
        print(f"Available backends: {info['available_backends']}")
        print(f"Features: {info['features_available']}")
        
        if 'bert_model_info' in info:
            print(f"BERT Model: {info['bert_model_info']['model_path']}")
        print()
        
        # Test with Turkish text
        test_text = "Türkçe dil işleme için yeni BERT modelini test ediyoruz."
        print(f"Test Text: {test_text}")
        
        tokens = nlp.process_text(test_text)
        print(f"Processed {len(tokens)} tokens")
        print()
        
        # Show results
        print("Token Analysis:")
        for i, token in enumerate(tokens):
            confidence = token.get('bert_confidence', 'N/A')
            print(f"{i+1:2d}. {token['form']:15s} -> POS: {token['upos']:6s} | "
                  f"Morph: {token['morph'] or 'None':25s} | Confidence: {confidence}")
        
        return True
        
    except Exception as e:
        print(f"Error testing Turkish processor with BERT: {e}")
        return False

def compare_backends():
    """Compare backends - focusing on BERT vs others (removed simple/spacy outputs)"""
    print("\n=== BACKEND COMPARISON ===")
    
    test_text = "Bu bir test cümlesidir. Türkçe NLP için BERT modelini test ediyoruz."
    
    # Only test BERT and other advanced backends (removed simple/spacy from output)
    backends = ['stanza', 'custom_bert']
    
    for backend in backends:
        print(f"\n--- {backend.upper()} BACKEND ---")
        try:
            if backend == 'custom_bert':
                nlp = create_turkish_processor(backend='custom_bert')
            else:
                nlp = create_turkish_processor(backend=backend)
            
            tokens = nlp.process_text(test_text)
            print(f"Tokens found: {len(tokens)}")
            
            # Show first few tokens
            for i, token in enumerate(tokens[:3]):
                confidence_info = ""
                if backend == 'custom_bert' and 'bert_confidence' in token:
                    confidence_info = f" (conf: {token['bert_confidence']:.3f})"
                print(f"  {i+1}. {token['form']} -> {token['upos']} | {token['morph'] or 'No morph'}{confidence_info}")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    print("Hugging Face BERT Model Integration Test")
    print("=" * 50)
    
    # Test 1: Custom BERT Processor
    success1 = test_custom_bert_processor()
    
    # Test 2: Turkish Processor with BERT
    success2 = test_turkish_processor_with_bert()
    
    # Test 3: Backend comparison
    compare_backends()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ All tests completed successfully!")
        print("\nUsage Examples:")
        print("1. Direct BERT usage:")
        print("   from nlp.custom_bert_processor import create_custom_bert_processor")
        print("   bert = create_custom_bert_processor()")
        print("   tokens = bert.process_text('Your Turkish text here')")
        print()
        print("2. Through TurkishNLPProcessor:")
        print("   from nlp.turkish_processor import create_turkish_processor")
        print("   nlp = create_turkish_processor(backend='custom_bert')")
        print("   tokens = nlp.process_text('Your Turkish text here')")
    else:
        print("❌ Some tests failed. Check the error messages above.")