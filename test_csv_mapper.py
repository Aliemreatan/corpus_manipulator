#!/usr/bin/env python3
"""
Test script for Turkish CSV Mapper
==================================

This script tests the functionality of the csv_mapper module
with the Cleaned-for-tags.csv data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from csv_mapper import TurkishCSVMapper


def test_basic_functionality():
    """Test basic functionality of the mapper."""
    print("Testing Turkish CSV Mapper...")
    print("=" * 40)
    
    # Initialize mapper
    mapper = TurkishCSVMapper("Cleaned-for-tags.csv")
    
    # Load data
    print("1. Loading data...")
    if not mapper.load_data():
        print("❌ Failed to load data!")
        return False
    print("✅ Data loaded successfully")
    
    # Build mappings
    print("\n2. Building mappings...")
    mapper.build_mappings()
    print("✅ Mappings built successfully")
    
    # Display summary
    print("\n3. Data summary:")
    mapper.display_summary()
    
    return True


def test_search_functionality():
    """Test search functionality."""
    print("\n" + "=" * 40)
    print("TESTING SEARCH FUNCTIONALITY")
    print("=" * 40)
    
    mapper = TurkishCSVMapper("Cleaned-for-tags.csv")
    
    if not mapper.load_data():
        return False
    
    mapper.build_mappings()
    
    # Test word search
    print("\n1. Testing word search:")
    print("   Searching for 'hızlıca':")
    results = mapper.search_by_word('hızlıca')
    print(f"   Found {len(results)} occurrences")
    if results:
        print(f"   Example: {results[0]['Full_Sentence']} -> {results[0]['Tag']}")
    
    # Test tag search
    print("\n2. Testing tag search:")
    print("   Searching for 'BELİRTEÇ-ADVERB':")
    results = mapper.search_by_tag('BELİRTEÇ-ADVERB')
    print(f"   Found {len(results)} occurrences")
    if results:
        print(f"   Example: {results[0]['Word']} in '{results[0]['Full_Sentence']}'")
    
    # Test sentence search
    print("\n3. Testing sentence search:")
    print("   Searching for specific sentence...")
    results = mapper.search_by_sentence('hızlıca koştu')
    print(f"   Found {len(results)} words in sentence")
    if results:
        for word_info in results:
            print(f"     {word_info['Word']} -> {word_info['Tag']}")
    
    # Test word tags lookup
    print("\n4. Testing word tags lookup:")
    print("   Getting tags for 'koştu':")
    tags = mapper.get_word_tags('koştu')
    print(f"   Tags: {list(tags)}")
    
    return True


def test_analysis_functionality():
    """Test analysis and export functionality."""
    print("\n" + "=" * 40)
    print("TESTING ANALYSIS FUNCTIONALITY")
    print("=" * 40)
    
    mapper = TurkishCSVMapper("Cleaned-for-tags.csv")
    
    if not mapper.load_data():
        return False
    
    mapper.build_mappings()
    
    # Test statistics
    print("\n1. Tag statistics (top 5):")
    tag_stats = mapper.get_tag_statistics()
    for tag, count in list(tag_stats.items())[:5]:
        print(f"   {tag}: {count}")
    
    print("\n2. Word frequency (top 5):")
    word_freq = mapper.get_word_frequency()
    for word, count in list(word_freq.items())[:5]:
        print(f"   {word}: {count}")
    
    # Test filtering
    print("\n3. Testing tag filtering:")
    filtered = mapper.filter_by_tags(['BELİRTEÇ-ADVERB', 'FİİL-VERB'])
    print(f"   Records with BELİRTEÇ-ADVERB or FİİL-VERB: {len(filtered)}")
    
    # Test pattern search
    print("\n4. Testing pattern search:")
    results = mapper.search_by_pattern(r'^hızlı.*')
    print(f"   Words starting with 'hızlı': {len(results)}")
    if results:
        print(f"   Example: {results[0]['Word']}")
    
    # Test export functionality
    print("\n5. Testing export functionality:")
    try:
        mapper.export_tag_mapping("test_word_tags.csv")
        mapper.export_sentence_analysis("test_sentence_analysis.csv")
        print("   ✅ Export completed successfully")
    except Exception as e:
        print(f"   ❌ Export failed: {e}")
        return False
    
    return True


def test_advanced_features():
    """Test advanced features."""
    print("\n" + "=" * 40)
    print("TESTING ADVANCED FEATURES")
    print("=" * 40)
    
    mapper = TurkishCSVMapper("Cleaned-for-tags.csv")
    
    if not mapper.load_data():
        return False
    
    mapper.build_mappings()
    
    # Test sentences with specific tag
    print("\n1. Sentences containing 'FİİL-VERB':")
    sentences = mapper.get_sentences_with_tag('FİİL-VERB')
    print(f"   Found {len(sentences)} sentences")
    if sentences:
        print(f"   Example: {sentences[0]}")
    
    # Test sentence structure
    print("\n2. Sentence structure analysis:")
    if sentences:
        sentence = sentences[0]
        structure = mapper.get_sentence_structure(sentence)
        print(f"   Sentence: {sentence}")
        print(f"   Structure: {structure}")
    
    print("\n3. Summary statistics:")
    summary = mapper.get_summary()
    print(f"   Total records: {summary.get('total_records', 0)}")
    print(f"   Unique sentences: {summary.get('unique_sentences', 0)}")
    print(f"   Unique words: {summary.get('unique_words', 0)}")
    print(f"   Unique tags: {summary.get('unique_tags', 0)}")
    
    return True


def main():
    """Main test function."""
    print("TURKISH CSV MAPPER TEST SUITE")
    print("=" * 50)
    
    # Change to the correct directory
    os.chdir(r'C:\Users\aliem\Documents\corpus_manipulator')
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Search Functionality", test_search_functionality),
        ("Analysis Functionality", test_analysis_functionality),
        ("Advanced Features", test_advanced_features)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed successfully!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()