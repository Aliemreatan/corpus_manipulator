#!/usr/bin/env python3
"""
CSV Mapper for Turkish Linguistic Data
======================================

This module provides functionality to extract and map data from the 
Cleaned-for-tags.csv file, which contains Turkish sentences with 
part-of-speech tags.

Features:
- Load and parse CSV data
- Map words to their grammatical tags
- Search by sentence, word, or tag
- Extract statistics and insights
- Export filtered results

Author: Kilo Code
"""

import pandas as pd
import csv
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict, Counter
import re


class TurkishCSVMapper:
    """
    A comprehensive mapper for Turkish linguistic data from CSV files.
    """
    
    def __init__(self, csv_path: str = "Cleaned-for-tags.csv"):
        """
        Initialize the mapper with CSV file path.
        
        Args:
            csv_path (str): Path to the CSV file containing Turkish linguistic data
        """
        self.csv_path = csv_path
        self.data = None
        self.unique_sentences = set()
        self.unique_words = set()
        self.unique_tags = set()
        self.word_tag_mapping = defaultdict(set)
        self.sentence_word_mapping = defaultdict(list)
        
    def load_data(self) -> bool:
        """
        Load data from CSV file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"Loading data from {self.csv_path}...")
            # Use 'utf-8-sig' to handle potential BOM
            self.data = pd.read_csv(self.csv_path, encoding='utf-8')
            
            # Normalize column names: strip whitespace and replace spaces with underscores
            self.data.columns = self.data.columns.str.strip().str.replace(' ', '_')
            
            # Clean and prepare data
            if 'Full_Sentence' in self.data.columns:
                self.data['Full_Sentence'] = self.data['Full_Sentence'].str.strip()
            if 'Word' in self.data.columns:
                self.data['Word'] = self.data['Word'].str.strip()
            if 'Tag' in self.data.columns:
                self.data['Tag'] = self.data['Tag'].str.strip()
            
            # Remove any rows with missing data
            self.data = self.data.dropna()
            
            print(f"Loaded {len(self.data)} rows of data")
            return True
            
        except FileNotFoundError:
            print(f"Error: File {self.csv_path} not found!")
            return False
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def build_mappings(self):
        """
        Build internal mappings for efficient querying.
        """
        if self.data is None:
            print("Error: No data loaded. Call load_data() first.")
            return
        
        print("Building mappings...")
        
        # Build unique sets
        self.unique_sentences = set(self.data['Full_Sentence'].unique())
        self.unique_words = set(self.data['Word'].unique())
        self.unique_tags = set(self.data['Tag'].unique())
        
        # Build word-to-tags mapping
        for _, row in self.data.iterrows():
            word = row['Word']
            tag = row['Tag']
            sentence = row['Full_Sentence']
            
            self.word_tag_mapping[word].add(tag)
            self.sentence_word_mapping[sentence].append((word, tag))
        
        print(f"Built mappings for:")
        print(f"  - {len(self.unique_sentences)} unique sentences")
        print(f"  - {len(self.unique_words)} unique words")
        print(f"  - {len(self.unique_tags)} unique tags")
    
    def search_by_word(self, word: str) -> List[Dict]:
        """
        Search for all occurrences of a specific word.
        
        Args:
            word (str): The word to search for
            
        Returns:
            List[Dict]: List of dictionaries containing sentence, word, and tag
        """
        if self.data is None:
            return []
        
        word = word.strip()
        results = self.data[self.data['Word'].str.lower() == word.lower()]
        
        return results.to_dict('records')
    
    def search_by_tag(self, tag: str) -> List[Dict]:
        """
        Search for all words with a specific grammatical tag.
        
        Args:
            tag (str): The grammatical tag to search for
            
        Returns:
            List[Dict]: List of dictionaries containing sentence, word, and tag
        """
        if self.data is None:
            return []
        
        tag = tag.strip()
        results = self.data[self.data['Tag'] == tag]
        
        return results.to_dict('records')
    
    def search_by_sentence(self, sentence: str) -> List[Dict]:
        """
        Search for all words in a specific sentence.
        
        Args:
            sentence (str): The sentence to search for
            
        Returns:
            List[Dict]: List of dictionaries containing word and tag for the sentence
        """
        if self.data is None:
            return []
        
        sentence = sentence.strip()
        results = self.data[self.data['Full_Sentence'] == sentence]
        
        return results.to_dict('records')
    
    def get_word_tags(self, word: str) -> Set[str]:
        """
        Get all grammatical tags associated with a word.
        
        Args:
            word (str): The word to look up
            
        Returns:
            Set[str]: Set of grammatical tags for the word
        """
        return self.word_tag_mapping.get(word.lower(), set())
    
    def get_sentence_structure(self, sentence: str) -> List[Tuple[str, str]]:
        """
        Get the word-tag structure of a sentence.
        
        Args:
            sentence (str): The sentence to analyze
            
        Returns:
            List[Tuple[str, str]]: List of (word, tag) tuples
        """
        return self.sentence_word_mapping.get(sentence.strip(), [])
    
    def get_tag_statistics(self) -> Dict[str, int]:
        """
        Get statistics about tag frequency.
        
        Returns:
            Dict[str, int]: Dictionary mapping tags to their frequencies
        """
        if self.data is None:
            return {}
        
        return self.data['Tag'].value_counts().to_dict()
    
    def get_word_frequency(self) -> Dict[str, int]:
        """
        Get statistics about word frequency.
        
        Returns:
            Dict[str, int]: Dictionary mapping words to their frequencies
        """
        if self.data is None:
            return {}
        
        return self.data['Word'].value_counts().to_dict()
    
    def filter_by_tags(self, tags: List[str]) -> pd.DataFrame:
        """
        Filter data by one or more grammatical tags.
        
        Args:
            tags (List[str]): List of tags to filter by
            
        Returns:
            pd.DataFrame: Filtered dataframe
        """
        if self.data is None:
            return pd.DataFrame()
        
        mask = self.data['Tag'].isin(tags)
        return self.data[mask]
    
    def search_by_pattern(self, pattern: str) -> List[Dict]:
        """
        Search for words matching a regex pattern.
        
        Args:
            pattern (str): Regular expression pattern to match
            
        Returns:
            List[Dict]: List of matching records
        """
        if self.data is None:
            return []
        
        try:
            mask = self.data['Word'].str.contains(pattern, case=False, na=False, regex=True)
            results = self.data[mask]
            return results.to_dict('records')
        except re.error as e:
            print(f"Invalid regex pattern: {e}")
            return []
    
    def get_sentences_with_tag(self, tag: str) -> List[str]:
        """
        Get all sentences that contain words with a specific tag.
        
        Args:
            tag (str): The grammatical tag to look for
            
        Returns:
            List[str]: List of sentences containing the tag
        """
        if self.data is None:
            return []
        
        mask = self.data['Tag'] == tag
        return self.data[mask]['Full_Sentence'].unique().tolist()
    
    def export_tag_mapping(self, output_path: str = "word_tag_mapping.csv"):
        """
        Export word-to-tag mappings to a CSV file.
        
        Args:
            output_path (str): Path for the output CSV file
        """
        if not self.word_tag_mapping:
            print("No mappings available. Build mappings first.")
            return
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Word', 'Tags'])
            
            for word in sorted(self.word_tag_mapping.keys()):
                tags = sorted(list(self.word_tag_mapping[word]))
                writer.writerow([word, '|'.join(tags)])
        
        print(f"Word-tag mapping exported to {output_path}")
    
    def export_sentence_analysis(self, output_path: str = "sentence_analysis.csv"):
        """
        Export sentence structure analysis to a CSV file.
        
        Args:
            output_path (str): Path for the output CSV file
        """
        if not self.sentence_word_mapping:
            print("No mappings available. Build mappings first.")
            return
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Sentence', 'Word_Count', 'Tag_Count', 'Word_Tag_Pairs'])
            
            for sentence in sorted(self.sentence_word_mapping.keys()):
                word_tags = self.sentence_word_mapping[sentence]
                word_count = len(word_tags)
                tag_count = len(set(tag for _, tag in word_tags))
                word_tag_pairs = '|'.join([f"{word}:{tag}" for word, tag in word_tags])
                
                writer.writerow([sentence, word_count, tag_count, word_tag_pairs])
        
        print(f"Sentence analysis exported to {output_path}")
    
    def get_summary(self) -> Dict:
        """
        Get a summary of the loaded data.
        
        Returns:
            Dict: Summary statistics
        """
        if self.data is None:
            return {}
        
        return {
            'total_records': len(self.data),
            'unique_sentences': len(self.unique_sentences),
            'unique_words': len(self.unique_words),
            'unique_tags': len(self.unique_tags),
            'most_common_tags': dict(list(self.get_tag_statistics().items())[:10]),
            'most_common_words': dict(list(self.get_word_frequency().items())[:10])
        }
    
    def display_summary(self):
        """
        Display a formatted summary of the data.
        """
        summary = self.get_summary()
        if not summary:
            print("No data loaded.")
            return
         
        print("\n" + "="*50)
        print("TURKISH LINGUISTIC DATA SUMMARY")
        print("="*50)
        print(f"Total Records: {summary['total_records']}")
        print(f"Unique Sentences: {summary['unique_sentences']}")
        print(f"Unique Words: {summary['unique_words']}")
        print(f"Unique Tags: {summary['unique_tags']}")
        
        print("\nMost Common Tags:")
        for tag, count in summary['most_common_tags'].items():
            print(f"  {tag}: {count}".encode('utf-8', errors='replace').decode('utf-8'))
        
        print("\nMost Common Words:")
        for word, count in summary['most_common_words'].items():
            print(f"  {word}: {count}".encode('utf-8', errors='replace').decode('utf-8'))
        
        print("="*50)


def demo_usage():
    """
    Demonstrate the usage of the TurkishCSVMapper.
    """
    print("Turkish CSV Mapper Demo")
    print("=" * 30)
    
    # Initialize mapper
    mapper = TurkishCSVMapper()
    
    # Load data
    if not mapper.load_data():
        print("Failed to load data!")
        return
    
    # Build mappings
    mapper.build_mappings()
    
    # Display summary
    mapper.display_summary()
    
    # Example searches
    print("\n" + "="*30)
    print("EXAMPLE SEARCHES")
    print("="*30)
    
    # Search by word
    print("\n1. Searching for word 'hızlıca':")
    results = mapper.search_by_word('hızlıca')
    for result in results[:5]:  # Show first 5 results
        print(f"   Sentence: {result['Full_Sentence']}")
        print(f"   Tag: {result['Tag']}")
        print()
    
    # Search by tag
    print("2. Searching for tag 'BELİRTEÇ-ADVERB' (first 3 results):")
    results = mapper.search_by_tag('BELİRTEÇ-ADVERB')
    for result in results[:3]:
        print(f"   Word: {result['Word']}")
        print(f"   Sentence: {result['Full_Sentence']}")
        print()
    
    # Get word tags
    print("3. All tags for word 'koştu':")
    tags = mapper.get_word_tags('koştu')
    print(f"   Tags: {list(tags)}")
    
    # Filter by multiple tags
    print("4. Filtering by multiple tags:")
    filtered = mapper.filter_by_tags(['BELİRTEÇ-ADVERB', 'FİİL-VERB'])
    print(f"   Records with BELİRTEÇ-ADVERB or FİİL-VERB: {len(filtered)}")
    
    # Export results
    print("\n5. Exporting data...")
    mapper.export_tag_mapping("exported_word_tags.csv")
    mapper.export_sentence_analysis("exported_sentence_analysis.csv")
    
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    demo_usage()