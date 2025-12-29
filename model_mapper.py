#!/usr/bin/env python3
"""
Turkish Corpus Model Mapper
===========================

This module provides advanced model mapping capabilities for Turkish linguistic data,
integrating with the existing CSV mapper and database schema to create comprehensive
model representations for machine learning and NLP tasks.

Features:
- Map CSV data to ML-ready formats
- Create feature vectors from linguistic annotations
- Generate training datasets for POS tagging models
- Export to multiple ML framework formats
- Integrate with existing database schema

Author: Kilo Code
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union, Any
from collections import defaultdict, Counter
import json
import pickle
import sqlite3
from pathlib import Path
import logging
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class TurkishModelMapper:
    """
    Advanced model mapper for Turkish linguistic data
    """
    
    def __init__(self, csv_path: str = "Cleaned-for-tags.csv", db_path: str = "corpus.db"):
        """
        Initialize the model mapper
        
        Args:
            csv_path: Path to the CSV file containing Turkish linguistic data
            db_path: Path to the SQLite database
        """
        self.csv_path = csv_path
        self.db_path = db_path
        self.data = None
        self.db_connection = None
        
        # Encoders for ML features
        self.word_encoder = LabelEncoder()
        self.tag_encoder = LabelEncoder()
        self.lemma_encoder = LabelEncoder()
        self.upos_encoder = LabelEncoder()
        
        # Feature scalers
        self.scaler = StandardScaler()
        
        # Vocabulary and mappings
        self.word_to_id = {}
        self.id_to_word = {}
        self.tag_to_id = {}
        self.id_to_tag = {}
        self.word_tag_pairs = defaultdict(list)
        self.context_windows = {}
        
        # Statistics
        self.vocabulary_size = 0
        self.tagset_size = 0
        self.sequence_lengths = []
        
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
    
    def connect_database(self):
        """Connect to SQLite database"""
        try:
            self.db_connection = sqlite3.connect(self.db_path)
            self.db_connection.row_factory = sqlite3.Row
            print(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def build_vocabulary(self):
        """Build vocabulary from the data"""
        if self.data is None:
            print("Error: No data loaded. Call load_data() first.")
            return
        
        print("Building vocabulary...")
        
        # Get unique words and tags
        unique_words = sorted(self.data['Word'].unique())
        unique_tags = sorted(self.data['Tag'].unique())
        
        # Create word mappings
        self.word_to_id = {word: idx for idx, word in enumerate(unique_words)}
        self.id_to_word = {idx: word for word, idx in self.word_to_id.items()}
        
        # Create tag mappings
        self.tag_to_id = {tag: idx for idx, tag in enumerate(unique_tags)}
        self.id_to_tag = {idx: tag for tag, idx in self.tag_to_id.items()}
        
        self.vocabulary_size = len(unique_words)
        self.tagset_size = len(unique_tags)
        
        print(f"Vocabulary size: {self.vocabulary_size}")
        print(f"Tagset size: {self.tagset_size}")
        
        # Fit encoders
        self.word_encoder.fit(unique_words)
        self.tag_encoder.fit(unique_tags)
        
    def extract_features(self) -> pd.DataFrame:
        """
        Extract ML features from the data
        
        Returns:
            pd.DataFrame: Features ready for ML training
        """
        if self.data is None:
            print("Error: No data loaded.")
            return pd.DataFrame()
        
        print("Extracting features...")
        
        # Basic features
        features_df = self.data.copy()
        
        # Word-level features
        features_df['word_length'] = features_df['Word'].str.len()
        features_df['word_is_capitalized'] = features_df['Word'].str[0].str.isupper().astype(int)
        features_df['word_has_digits'] = features_df['Word'].str.contains(r'\d').astype(int)
        features_df['word_has_punctuation'] = features_df['Word'].str.contains(r'[^\w\s]').astype(int)
        
        # Character n-grams (2-grams)
        features_df['word_prefix'] = features_df['Word'].str[:3]
        features_df['word_suffix'] = features_df['Word'].str[-3:]
        
        # Tag features
        features_df['tag_prefix'] = features_df['Tag'].str.split('-').str[0]
        features_df['tag_suffix'] = features_df['Tag'].str.split('-').str[-1]
        
        # Position in sentence (approximate)
        sentence_groups = features_df.groupby('Full_Sentence')
        features_df['position_in_sentence'] = sentence_groups.cumcount()
        
        # Sentence length
        sentence_lengths = sentence_groups['Word'].transform('count')
        features_df['sentence_length'] = sentence_lengths
        
        print(f"Extracted features for {len(features_df)} tokens")
        return features_df
    
    def create_sequences(self, max_seq_length: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for sequence modeling (e.g., LSTM, Transformer)
        
        Args:
            max_seq_length: Maximum sequence length
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Sequences and labels
        """
        if self.data is None:
            print("Error: No data loaded.")
            return np.array([]), np.array([])
        
        print("Creating sequences...")
        
        # Group by sentences
        sentence_groups = self.data.groupby('Full_Sentence')
        
        sequences = []
        labels = []
        
        for sentence, group in sentence_groups:
            words = group['Word'].tolist()
            tags = group['Tag'].tolist()
            
            # Convert to indices
            word_indices = [self.word_to_id.get(word, 0) for word in words]  # 0 for unknown
            tag_indices = [self.tag_to_id[tag] for tag in tags]
            
            # Pad or truncate sequences
            if len(word_indices) > max_seq_length:
                word_indices = word_indices[:max_seq_length]
                tag_indices = tag_indices[:max_seq_length]
            elif len(word_indices) < max_seq_length:
                padding_length = max_seq_length - len(word_indices)
                word_indices.extend([0] * padding_length)  # Pad with 0 (unknown)
                tag_indices.extend([0] * padding_length)   # Pad with 0 (unknown tag)
            
            sequences.append(word_indices)
            labels.append(tag_indices)
            
            self.sequence_lengths.append(len(words))
        
        sequences_array = np.array(sequences)
        labels_array = np.array(labels)
        
        print(f"Created {len(sequences)} sequences")
        print(f"Sequence shape: {sequences_array.shape}")
        print(f"Labels shape: {labels_array.shape}")
        
        return sequences_array, labels_array
    
    def create_context_windows(self, window_size: int = 2) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create context windows for word embeddings or context-based models
        
        Args:
            window_size: Size of the context window
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Context windows and target words
        """
        if self.data is None:
            print("Error: No data loaded.")
            return np.array([]), np.array([])
        
        print("Creating context windows...")
        
        contexts = []
        targets = []
        
        # Group by sentences to maintain context
        sentence_groups = self.data.groupby('Full_Sentence')
        
        for sentence, group in sentence_groups:
            words = group['Word'].tolist()
            word_indices = [self.word_to_id.get(word, 0) for word in words]
            
            for i, target_idx in enumerate(word_indices):
                # Get context indices
                start = max(0, i - window_size)
                end = min(len(word_indices), i + window_size + 1)
                
                context_indices = word_indices[start:i] + word_indices[i+1:end]
                
                # Pad context if needed
                while len(context_indices) < window_size * 2:
                    context_indices.append(0)  # Pad with unknown token
                
                contexts.append(context_indices[:window_size * 2])
                targets.append(target_idx)
        
        contexts_array = np.array(contexts)
        targets_array = np.array(targets)
        
        print(f"Created {len(contexts)} context windows")
        print(f"Context shape: {contexts_array.shape}")
        print(f"Targets shape: {targets_array.shape}")
        
        return contexts_array, targets_array
    
    def create_training_dataset(self, test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        """
        Create a complete training dataset with train/validation/test splits
        
        Args:
            test_size: Proportion of data for testing
            random_state: Random seed for reproducibility
            
        Returns:
            Dict: Training dataset with splits and metadata
        """
        if self.data is None:
            print("Error: No data loaded.")
            return {}
        
        print("Creating training dataset...")
        
        # Create sequences
        sequences, labels = self.create_sequences()
        
        # Split data
        X_train, X_temp, y_train, y_temp = train_test_split(
            sequences, labels, test_size=test_size, random_state=random_state
        )
        
        # Split temp into validation and test
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=random_state
        )
        
        dataset = {
            'train': {'sequences': X_train, 'labels': y_train},
            'validation': {'sequences': X_val, 'labels': y_val},
            'test': {'sequences': X_test, 'labels': y_test},
            'metadata': {
                'vocabulary_size': self.vocabulary_size,
                'tagset_size': self.tagset_size,
                'word_to_id': self.word_to_id,
                'id_to_word': self.id_to_word,
                'tag_to_id': self.tag_to_id,
                'id_to_tag': self.id_to_tag,
                'sequence_length': sequences.shape[1],
                'train_size': len(X_train),
                'val_size': len(X_val),
                'test_size': len(X_test)
            }
        }
        
        print(f"Training set: {len(X_train)} sequences")
        print(f"Validation set: {len(X_val)} sequences")
        print(f"Test set: {len(X_test)} sequences")
        
        return dataset
    
    def export_to_tensorflow(self, dataset: Dict[str, Any], output_dir: str = "tf_dataset"):
        """
        Export dataset to TensorFlow format
        
        Args:
            dataset: Training dataset
            output_dir: Output directory
        """
        import tensorflow as tf
        
        Path(output_dir).mkdir(exist_ok=True)
        
        # Convert to TensorFlow datasets
        train_ds = tf.data.Dataset.from_tensor_slices((
            dataset['train']['sequences'], 
            dataset['train']['labels']
        ))
        
        val_ds = tf.data.Dataset.from_tensor_slices((
            dataset['validation']['sequences'], 
            dataset['validation']['labels']
        ))
        
        test_ds = tf.data.Dataset.from_tensor_slices((
            dataset['test']['sequences'], 
            dataset['test']['labels']
        ))
        
        # Save datasets
        train_ds.save(f"{output_dir}/train")
        val_ds.save(f"{output_dir}/validation")
        test_ds.save(f"{output_dir}/test")
        
        # Save metadata
        with open(f"{output_dir}/metadata.json", 'w', encoding='utf-8') as f:
            json.dump(dataset['metadata'], f, ensure_ascii=False, indent=2)
        
        print(f"TensorFlow dataset exported to {output_dir}")
    
    def export_to_pytorch(self, dataset: Dict[str, Any], output_dir: str = "torch_dataset"):
        """
        Export dataset to PyTorch format
        
        Args:
            dataset: Training dataset
            output_dir: Output directory
        """
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save as numpy arrays
        np.save(f"{output_dir}/train_sequences.npy", dataset['train']['sequences'])
        np.save(f"{output_dir}/train_labels.npy", dataset['train']['labels'])
        np.save(f"{output_dir}/val_sequences.npy", dataset['validation']['sequences'])
        np.save(f"{output_dir}/val_labels.npy", dataset['validation']['labels'])
        np.save(f"{output_dir}/test_sequences.npy", dataset['test']['sequences'])
        np.save(f"{output_dir}/test_labels.npy", dataset['test']['labels'])
        
        # Save metadata
        with open(f"{output_dir}/metadata.json", 'w', encoding='utf-8') as f:
            json.dump(dataset['metadata'], f, ensure_ascii=False, indent=2)
        
        print(f"PyTorch dataset exported to {output_dir}")
    
    def export_to_sklearn(self, output_path: str = "sklearn_features.pkl"):
        """
        Export features for scikit-learn
        
        Args:
            output_path: Output pickle file path
        """
        features_df = self.extract_features()
        
        # Prepare features for sklearn
        X = features_df[['word_length', 'word_is_capitalized', 'word_has_digits', 
                        'word_has_punctuation', 'position_in_sentence', 'sentence_length']].values
        
        # Encode categorical features
        word_encoded = self.word_encoder.transform(features_df['Word'])
        tag_encoded = self.tag_encoder.transform(features_df['Tag'])
        
        # Combine features
        X_combined = np.column_stack([X, word_encoded, tag_encoded])
        y = tag_encoded
        
        # Save
        data = {
            'X': X_combined,
            'y': y,
            'feature_names': ['word_length', 'word_is_capitalized', 'word_has_digits', 
                             'word_has_punctuation', 'position_in_sentence', 'sentence_length',
                             'word_encoded', 'tag_encoded'],
            'word_encoder': self.word_encoder,
            'tag_encoder': self.tag_encoder,
            'metadata': {
                'n_samples': len(X_combined),
                'n_features': X_combined.shape[1],
                'vocabulary_size': self.vocabulary_size,
                'tagset_size': self.tagset_size
            }
        }
        
        with open(output_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"scikit-learn features exported to {output_path}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the dataset
        
        Returns:
            Dict: Dataset statistics
        """
        if self.data is None:
            return {}
        
        stats = {
            'basic_stats': {
                'total_tokens': len(self.data),
                'unique_words': self.vocabulary_size,
                'unique_tags': self.tagset_size,
                'unique_sentences': self.data['Full_Sentence'].nunique()
            },
            'tag_distribution': dict(self.data['Tag'].value_counts()),
            'word_frequency': dict(self.data['Word'].value_counts().head(20)),
            'sequence_stats': {
                'mean_length': np.mean(self.sequence_lengths) if self.sequence_lengths else 0,
                'median_length': np.median(self.sequence_lengths) if self.sequence_lengths else 0,
                'max_length': max(self.sequence_lengths) if self.sequence_lengths else 0,
                'min_length': min(self.sequence_lengths) if self.sequence_lengths else 0
            },
            'vocabulary_stats': {
                'most_common_words': dict(self.data['Word'].value_counts().head(10)),
                'rare_words_count': sum(1 for count in self.data['Word'].value_counts() if count == 1)
            }
        }
        
        return stats
    
    def save_mappings(self, output_path: str = "model_mappings.json"):
        """
        Save all mappings and encoders
        
        Args:
            output_path: Output JSON file path
        """
        mappings = {
            'word_to_id': self.word_to_id,
            'id_to_word': self.id_to_word,
            'tag_to_id': self.tag_to_id,
            'id_to_tag': self.id_to_tag,
            'vocabulary_size': self.vocabulary_size,
            'tagset_size': self.tagset_size,
            'sequence_lengths': self.sequence_lengths
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, ensure_ascii=False, indent=2)
        
        print(f"Mappings saved to {output_path}")
    
    def load_mappings(self, input_path: str = "model_mappings.json"):
        """
        Load mappings and encoders from file
        
        Args:
            input_path: Input JSON file path
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
            
            self.word_to_id = mappings['word_to_id']
            self.id_to_word = mappings['id_to_word']
            self.tag_to_id = mappings['tag_to_id']
            self.id_to_tag = mappings['id_to_tag']
            self.vocabulary_size = mappings['vocabulary_size']
            self.tagset_size = mappings['tagset_size']
            self.sequence_lengths = mappings.get('sequence_lengths', [])
            
            print(f"Mappings loaded from {input_path}")
            return True
            
        except Exception as e:
            print(f"Error loading mappings: {e}")
            return False


def demo_model_mapping():
    """
    Demonstrate the model mapping functionality
    """
    print("Turkish Corpus Model Mapper Demo")
    print("=" * 40)
    
    # Initialize mapper
    mapper = TurkishModelMapper()
    
    # Load data
    if not mapper.load_data():
        print("Failed to load data!")
        return
    
    # Build vocabulary
    mapper.build_vocabulary()
    
    # Extract features
    features = mapper.extract_features()
    print(f"Feature extraction completed. Shape: {features.shape}")
    
    # Create sequences
    sequences, labels = mapper.create_sequences(max_seq_length=30)
    
    # Create training dataset
    dataset = mapper.create_training_dataset(test_size=0.2)
    
    # Get statistics
    stats = mapper.get_statistics()
    
    # Display statistics
    print("\n" + "="*50)
    print("DATASET STATISTICS")
    print("="*50)
    print(f"Total tokens: {stats['basic_stats']['total_tokens']}")
    print(f"Unique words: {stats['basic_stats']['unique_words']}")
    print(f"Unique tags: {stats['basic_stats']['unique_tags']}")
    print(f"Unique sentences: {stats['basic_stats']['unique_sentences']}")
    
    print("\nTop 10 most common tags:")
    for tag, count in list(stats['tag_distribution'].items())[:10]:
        print(f"  {tag}: {count}")
    
    print("\nTop 10 most common words:")
    for word, count in list(stats['word_frequency'].items())[:10]:
        print(f"  {word}: {count}")
    
    print(f"\nSequence statistics:")
    print(f"  Mean length: {stats['sequence_stats']['mean_length']:.2f}")
    print(f"  Median length: {stats['sequence_stats']['median_length']:.2f}")
    print(f"  Max length: {stats['sequence_stats']['max_length']}")
    print(f"  Min length: {stats['sequence_stats']['min_length']}")
    
    # Export datasets
    print("\n" + "="*50)
    print("EXPORTING DATASETS")
    print("="*50)
    
    # Export to different formats
    mapper.export_to_sklearn("sklearn_features.pkl")
    mapper.export_to_pytorch(dataset, "torch_dataset")
    mapper.export_to_tensorflow(dataset, "tf_dataset")
    
    # Save mappings
    mapper.save_mappings("model_mappings.json")
    
    print("\nDemo completed successfully!")
    print("Generated files:")
    print("  - sklearn_features.pkl (scikit-learn format)")
    print("  - torch_dataset/ (PyTorch format)")
    print("  - tf_dataset/ (TensorFlow format)")
    print("  - model_mappings.json (vocabulary and tag mappings)")


if __name__ == "__main__":
    demo_model_mapping()