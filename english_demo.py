#!/usr/bin/env python3
"""
English demo of Turkish CSV Mapper
==================================

A demonstration of the csv_mapper functionality using English output.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from csv_mapper import TurkishCSVMapper


def english_demo():
    """Run a demonstration of the mapper functionality."""
    print("Turkish CSV Mapper - English Demo")
    print("=" * 40)
    
    # Initialize mapper
    mapper = TurkishCSVMapper("Cleaned-for-tags.csv")
    
    # Load data
    print("1. Loading data...")
    if not mapper.load_data():
        print("FAILED to load data!")
        return
    
    print(f"SUCCESS - Loaded {len(mapper.data)} rows of data")
    
    # Build mappings
    print("\n2. Building mappings...")
    mapper.build_mappings()
    print("SUCCESS - Mappings built")
    
    # Display basic summary
    summary = mapper.get_summary()
    print(f"\n3. Data Summary:")
    print(f"   Total Records: {summary['total_records']:,}")
    print(f"   Unique Sentences: {summary['unique_sentences']:,}")
    print(f"   Unique Words: {summary['unique_words']:,}")
    print(f"   Unique Tags: {summary['unique_tags']:,}")
    
    # Example searches
    print(f"\n4. Example Searches:")
    
    # Search for a word
    print(f"\n   a) Searching for word 'hizlica' (Turkish word):")
    results = mapper.search_by_word('hizlica')
    print(f"      Found {len(results)} occurrences")
    if results:
        print(f"      Example: Sentence with tag {results[0]['Tag']}")
    
    # Search for a tag
    print(f"\n   b) Searching for tag 'BELIRTEÇ-ADVERB':")
    results = mapper.search_by_tag('BELIRTEÇ-ADVERB')
    print(f"      Found {len(results)} words with this tag")
    if results:
        print(f"      Example word: {results[0]['Word']}")
    
    # Get word tags
    print(f"\n   c) Getting tags for word 'kostu' (Turkish word):")
    tags = mapper.get_word_tags('kostu')
    print(f"      Tags: {list(tags)}")
    
    # Filter by tags
    print(f"\n   d) Filtering by tags:")
    filtered = mapper.filter_by_tags(['BELİRTEÇ-ADVERB', 'FİİL-VERB'])
    print(f"      Records with specified tags: {len(filtered)}")
    
    # Export examples
    print(f"\n5. Exporting data...")
    try:
        mapper.export_tag_mapping("demo_word_tags.csv")
        mapper.export_sentence_analysis("demo_sentence_analysis.csv")
        print("   SUCCESS - Files exported")
    except Exception as e:
        print(f"   ERROR - Export failed: {e}")
    
    print(f"\nDemo completed successfully!")


if __name__ == "__main__":
    # Change to the correct directory
    os.chdir(r'C:\Users\aliem\Documents\corpus_manipulator')
    english_demo()