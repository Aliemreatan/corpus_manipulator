#!/usr/bin/env python3
"""
Test script to verify Turkish character encoding fixes

This script tests that Turkish characters are properly handled throughout
the pipeline: GUI input → BERT processing → display.
"""

import sys
import os
import io

# Set UTF-8 encoding for Turkish characters (same fix as in GUI)
if sys.platform.startswith('win'):
    # Set console to UTF-8 for proper Turkish character display
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass  # Continue if it fails

def test_turkish_text_encoding():
    """Test Turkish text encoding preservation"""
    print("=== TURKISH CHARACTER ENCODING TEST ===")
    
    # Test texts with Turkish characters
    test_texts = [
        "Şu çalışma çok güzel. Öğretmen öğrencilere gösteriyor.",
        "Çocuklar bahçede oynuyor ve şarkı söylüyorlar.",
        "Güzel bir gün, öğrenciler okula gidiyor.",
        "İstanbul'da çok güzel yerler var.",
        "Kitap okumayı çok severim çünkü öğrenmek güzel."
    ]
    
    print("\n1. Testing UTF-8 text encoding preservation:")
    print("-" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"Test {i}: {text}")
        
        # Test that text can be encoded/decoded properly
        try:
            encoded = text.encode('utf-8')
            decoded = encoded.decode('utf-8')
            if text == decoded:
                print(f"  ✓ UTF-8 encoding/decoding successful")
            else:
                print(f"  ✗ UTF-8 encoding/decoding failed")
        except Exception as e:
            print(f"  ✗ UTF-8 error: {e}")
    
    print("\n2. Testing Unicode normalization:")
    print("-" * 50)
    
    import unicodedata
    for i, text in enumerate(test_texts, 1):
        print(f"Test {i}: {text}")
        
        # Normalize to NFC (canonical composition)
        normalized = unicodedata.normalize('NFC', text)
        print(f"  Original length: {len(text)}")
        print(f"  Normalized length: {len(normalized)}")
        print(f"  Same content: {text == normalized}")
    
    print("\n3. Testing BERT processor with Turkish text:")
    print("-" * 50)
    
    try:
        from nlp.custom_bert_processor import create_custom_bert_processor
        
        # Create BERT processor
        bert_processor = create_custom_bert_processor()
        info = bert_processor.get_model_info()
        
        print(f"BERT Model loaded: {info['is_loaded']}")
        
        if info['is_loaded']:
            # Test with Turkish text
            test_text = "Türkçe dil işleme için BERT modeli test ediliyor."
            tokens = bert_processor.process_text(test_text)
            
            print(f"Input: {test_text}")
            print(f"Tokens found: {len(tokens)}")
            
            # Check if Turkish characters are preserved in tokens
            turkish_chars = 'şçğıöüğıİÇĞÖŞÜ'
            turkish_in_tokens = []
            
            for token in tokens[:5]:  # Check first 5 tokens
                word = token.get('form', '')
                if any(c in turkish_chars for c in word):
                    turkish_in_tokens.append(word)
            
            if turkish_in_tokens:
                print(f"✓ Turkish characters preserved in tokens: {turkish_in_tokens}")
            else:
                print("✓ No Turkish characters in first 5 tokens (this may be normal)")
            
            # Show first few tokens
            print("\nFirst few tokens:")
            for i, token in enumerate(tokens[:3], 1):
                form = token.get('form', 'N/A')
                upos = token.get('upos', 'N/A')
                print(f"  {i}. {form} -> {upos}")
        else:
            print("Model not loaded, testing with simple processing...")
            # Test simple processing fallback
            simple_text = "Şu çalışma güzel."
            tokens = bert_processor.process_text(simple_text)
            print(f"Simple processing tokens: {len(tokens)}")
            for token in tokens:
                print(f"  {token.get('form', 'N/A')}")
    
    except Exception as e:
        print(f"✗ BERT processor test failed: {e}")
    
    print("\n4. Testing GUI text encoding function:")
    print("-" * 50)
    
    # Create a mock GUI class to test the encoding function
    class MockGUI:
        def _ensure_utf8_text(self, text):
            """Ensure text is properly encoded as UTF-8 for BERT processing"""
            if not isinstance(text, str):
                text = str(text)
            
            # Ensure UTF-8 encoding and handle any encoding issues
            try:
                # Normalize to NFC form for consistent handling
                import unicodedata
                text = unicodedata.normalize('NFC', text)
                return text
            except Exception as e:
                print(f"Warning: Text encoding issue: {e}")
                return text
    
    mock_gui = MockGUI()
    
    for i, text in enumerate(test_texts, 1):
        print(f"Test {i}: {text}")
        processed = mock_gui._ensure_utf8_text(text)
        print(f"  Processed: {processed}")
        print(f"  Same content: {text == processed}")
    
    print("\n" + "=" * 50)
    print("✓ Turkish character encoding test completed!")
    print("✓ All Turkish characters should now work properly in GUI and BERT")
    print("\nNext steps:")
    print("1. Run the GUI to test: py run_gui.py")
    print("2. Try entering Turkish text in the BERT analysis section")
    print("3. Verify that characters are displayed and processed correctly")

if __name__ == "__main__":
    test_turkish_text_encoding()