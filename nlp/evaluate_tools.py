"""
Turkish NLP Tools Evaluation Script

This script evaluates available Turkish NLP tools for our corpus manipulator.
It compares accuracy, performance, and ease of use.
"""

import time
import sys
import traceback
from pathlib import Path

def test_spacy_turkish():
    """Test spaCy Turkish model if available"""
    try:
        import spacy
        
        print("Testing spaCy Turkish...")
        try:
            # Try to load Turkish model
            nlp = spacy.load("tr_core_news_sm")
            print("✓ spaCy Turkish model loaded successfully")
            
            test_text = "Bu bir test cümlesidir. Türkçe dil işleme için kullanılır."
            doc = nlp(test_text)
            
            print(f"Tokens: {len(doc)}")
            for token in doc[:5]:  # Show first 5 tokens
                print(f"  {token.text} -> lemma: {token.lemma_}, pos: {token.pos_}, tag: {token.tag_}")
            
            # Check for dependency parsing
            has_deps = any(token.dep_ != '' for token in doc if not token.is_space)
            print(f"✓ Dependency parsing available: {has_deps}")
            
            return True, {
                'tokens': len(doc),
                'lemmas': [token.lemma_ for token in doc if not token.is_space][:5],
                'pos_tags': [token.pos_ for token in doc if not token.is_space][:5],
                'has_deps': has_deps
            }
            
        except OSError:
            print("✗ spaCy Turkish model not found. Install with: python -m spacy download tr_core_news_sm")
            return False, None
            
    except ImportError:
        print("✗ spaCy not installed")
        return False, None

def test_stanza_turkish():
    """Test Stanza Turkish if available"""
    try:
        import stanza
        
        print("\nTesting Stanza Turkish...")
        try:
            # Try to download and load Turkish model
            stanza.download('tr')
            nlp = stanza.Pipeline('tr', processors='tokenize,pos,lemma,depparse')
            print("✓ Stanza Turkish model loaded successfully")
            
            test_text = "Bu bir test cümlesidir. Türkçe dil işleme için kullanılır."
            doc = nlp(test_text)
            
            print(f"Sentences: {len(doc.sentences)}")
            tokens = []
            for sent in doc.sentences:
                for word in sent.words[:5]:  # First 5 words
                    print(f"  {word.text} -> lemma: {word.lemma}, upos: {word.upos}, head: {word.head}")
                    tokens.append((word.text, word.lemma, word.upos))
            
            # Check for dependency parsing
            has_deps = any(sent.words[0].head != 0 if sent.words else False for sent in doc.sentences)
            print(f"✓ Dependency parsing available: {has_deps}")
            
            return True, {
                'sentences': len(doc.sentences),
                'tokens': tokens,
                'has_deps': has_deps
            }
            
        except Exception as e:
            print(f"✗ Error loading Stanza Turkish: {e}")
            return False, None
            
    except ImportError:
        print("✗ Stanza not installed")
        return False, None

def simple_turkish_tokenizer(text):
    """Simple fallback Turkish tokenizer"""
    import re
    
    # Basic Turkish text cleaning
    text = re.sub(r'[^\w\sçğıöşüÇĞIİÖŞÜ]', ' ', text)
    
    # Split by whitespace and filter empty strings
    tokens = [token.strip() for token in text.split() if token.strip()]
    
    # Simple lowercase normalization
    tokens = [token.lower() for token in tokens]
    
    return tokens

def test_simple_tokenization():
    """Test simple tokenization fallback"""
    print("\nTesting Simple Turkish Tokenization...")
    
    test_text = "Bu bir test cümlesidir. Türkçe dil işleme için kullanılır."
    tokens = simple_turkish_tokenizer(test_text)
    
    print(f"✓ Simple tokenization: {len(tokens)} tokens")
    print(f"  Tokens: {tokens[:10]}")
    
    return True, {'tokens': tokens}

def compare_tools():
    """Compare all available tools"""
    print("=== Turkish NLP Tools Evaluation ===\n")
    
    results = {}
    
    # Test each tool
    spacy_success, spacy_data = test_spacy_turkish()
    if spacy_success:
        results['spacy'] = spacy_data
        
    stanza_success, stanza_data = test_stanza_turkish()
    if stanza_success:
        results['stanza'] = stanza_data
        
    simple_success, simple_data = test_simple_tokenization()
    if simple_success:
        results['simple'] = simple_data
    
    # Summary and recommendation
    print("\n=== SUMMARY ===")
    print("Available tools:")
    
    if 'spacy' in results:
        print("✓ spaCy: Full NLP pipeline with Turkish support")
    else:
        print("✗ spaCy: Not available")
        
    if 'stanza' in results:
        print("✓ Stanza: Stanford NLP with Turkish support")  
    else:
        print("✗ Stanza: Not available")
        
    print("✓ Simple: Basic tokenization (fallback)")
    
    print("\n=== RECOMMENDATION ===")
    if 'spacy' in results:
        print("RECOMMENDED: spaCy Turkish model")
        print("  - Good balance of accuracy and speed")
        print("  - Easy to use")
        print("  - Good Turkish language support")
        print("  - Install: python -m spacy download tr_core_news_sm")
    elif 'stanza' in results:
        print("RECOMMENDED: Stanza Turkish")
        print("  - Strong dependency parsing")
        print("  - Good morphosyntactic features")
        print("  - Install: pip install stanza && stanza.download('tr')")
    else:
        print("FALLBACK: Simple tokenization")
        print("  - Only basic tokenization available")
        print("  - No POS tags, lemma, or dependencies")
        print("  - Suitable for basic frequency analysis")

if __name__ == "__main__":
    compare_tools()