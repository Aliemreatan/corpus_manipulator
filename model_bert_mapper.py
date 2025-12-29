#!/usr/bin/env python3
"""
BERT Model Mapper for Turkish Corpus
====================================

This module provides specialized mapping capabilities for BERT-based models,
integrating with the existing BERT processor to create optimized datasets
for fine-tuning and evaluation of Turkish BERT models.

Features:
- BERT-specific tokenization and alignment
- Subword handling for Turkish agglutination
- Attention mask and token type ID generation
- BERT-compatible dataset formats
- Integration with Hugging Face transformers

Author: Kilo Code
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Union
from collections import defaultdict
import json
import pickle
from pathlib import Path
import logging
import warnings
from sklearn.model_selection import train_test_split
warnings.filterwarnings('ignore')

# Try to import transformers
TRANSFORMERS_AVAILABLE = False
try:
    from transformers import AutoTokenizer, AutoConfig
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logging.warning("Transformers library not available for BERT mapping")

logger = logging.getLogger(__name__)

class BERTModelMapper:
    """
    BERT-specific model mapper for Turkish linguistic data
    """
    
    def __init__(self, 
                 csv_path: str = "Cleaned-for-tags.csv",
                 bert_model_name: str = "dbmdz/bert-base-turkish-128k-cased",
                 max_seq_length: int = 128):
        """
        Initialize BERT model mapper
        
        Args:
            csv_path: Path to CSV file
            bert_model_name: BERT model name for tokenization
            max_seq_length: Maximum sequence length for BERT
        """
        self.csv_path = csv_path
        self.bert_model_name = bert_model_name
        self.max_seq_length = max_seq_length
        self.data = None
        
        # BERT components
        self.tokenizer = None
        self.config = None
        
        # Mappings
        self.word_to_subwords = {}
        self.subword_to_word = {}
        self.label_to_id = {}
        self.id_to_label = {}
        
        # Statistics
        self.total_tokens = 0
        self.total_subwords = 0
        self.alignment_issues = 0
        
        # Load BERT tokenizer if available
        if TRANSFORMERS_AVAILABLE:
            self._load_bert_components()
    
    def _load_bert_components(self):
        """Load BERT tokenizer and config"""
        try:
            print(f"Loading BERT tokenizer: {self.bert_model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.bert_model_name)
            self.config = AutoConfig.from_pretrained(self.bert_model_name)
            print("BERT components loaded successfully")
        except Exception as e:
            print(f"Error loading BERT components: {e}")
            self.tokenizer = None
            self.config = None
    
    def load_data(self) -> bool:
        """Load data from CSV file"""
        try:
            print(f"Loading data from {self.csv_path}...")
            # Use 'utf-8-sig' to handle potential BOM
            self.data = pd.read_csv(self.csv_path, encoding='utf-8')
            
            # Normalize column names: strip whitespace and replace spaces with underscores
            self.data.columns = self.data.columns.str.strip().str.replace(' ', '_')
            
            # Clean data
            if 'Full_Sentence' in self.data.columns:
                self.data['Full_Sentence'] = self.data['Full_Sentence'].str.strip()
            if 'Word' in self.data.columns:
                self.data['Word'] = self.data['Word'].str.strip()
            if 'Tag' in self.data.columns:
                self.data['Tag'] = self.data['Tag'].str.strip()
            
            self.data = self.data.dropna()
            
            print(f"Loaded {len(self.data)} rows of data")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def create_bert_dataset(self, 
                           output_dir: str = "bert_dataset",
                           include_alignment: bool = True) -> Dict[str, Any]:
        """
        Create BERT-compatible dataset
        
        Args:
            output_dir: Output directory
            include_alignment: Whether to include word-subword alignment
            
        Returns:
            Dict: BERT dataset with metadata
        """
        if self.data is None:
            print("Error: No data loaded")
            return {}
        
        if not TRANSFORMERS_AVAILABLE:
            print("Error: Transformers library not available")
            return {}
        
        print("Creating BERT dataset...")
        
        # Group by sentences
        sentence_groups = self.data.groupby('Full_Sentence')
        
        input_ids = []
        attention_masks = []
        token_type_ids = []
        labels = []
        word_subword_mapping = []
        
        for sentence, group in sentence_groups:
            words = group['Word'].tolist()
            tags = group['Tag'].tolist()
            
            # BERT tokenization with alignment
            bert_tokens, bert_labels, alignment = self._align_tokens_with_bert(words, tags)
            
            if bert_tokens is None:
                continue  # Skip if alignment failed
            
            # Convert to IDs
            input_id = self.tokenizer.convert_tokens_to_ids(bert_tokens)
            label_ids = [self.label_to_id.get(label, 0) for label in bert_labels]
            
            # Create attention mask
            attention_mask = [1] * len(input_id)
            
            # Pad sequences
            while len(input_id) < self.max_seq_length:
                input_id.append(0)  # Pad token ID
                attention_mask.append(0)
                label_ids.append(-100)  # Ignore index for padding
            
            # Truncate if too long
            if len(input_id) > self.max_seq_length:
                input_id = input_id[:self.max_seq_length]
                attention_mask = attention_mask[:self.max_seq_length]
                label_ids = label_ids[:self.max_seq_length]
            
            input_ids.append(input_id)
            attention_masks.append(attention_mask)
            labels.append(label_ids)
            
            if include_alignment:
                word_subword_mapping.append(alignment)
        
        # Convert to numpy arrays
        input_ids = np.array(input_ids)
        attention_masks = np.array(attention_masks)
        labels = np.array(labels)
        
        dataset = {
            'input_ids': input_ids,
            'attention_mask': attention_masks,
            'labels': labels,
            'metadata': {
                'model_name': self.bert_model_name,
                'max_seq_length': self.max_seq_length,
                'vocab_size': len(self.tokenizer.get_vocab()),
                'num_labels': len(self.label_to_id),
                'label_to_id': self.label_to_id,
                'id_to_label': self.id_to_label,
                'total_sequences': len(input_ids),
                'alignment_issues': self.alignment_issues,
                'total_tokens': self.total_tokens,
                'total_subwords': self.total_subwords
            }
        }
        
        if include_alignment:
            dataset['word_subword_mapping'] = word_subword_mapping
        
        # Save dataset
        Path(output_dir).mkdir(exist_ok=True)
        self._save_bert_dataset(dataset, output_dir)
        
        print(f"BERT dataset created with {len(input_ids)} sequences")
        return dataset
    
    def _align_tokens_with_bert(self, words: List[str], tags: List[str]) -> Tuple[Optional[List[str]], Optional[List[str]], Dict]:
        """
        Align words with BERT subword tokens
        
        Args:
            words: List of words
            tags: List of corresponding tags
            
        Returns:
            Tuple of (bert_tokens, bert_labels, alignment_dict)
        """
        bert_tokens = []
        bert_labels = []
        alignment = {}
        
        current_token_idx = 0
        
        for word_idx, (word, tag) in enumerate(zip(words, tags)):
            # Tokenize word with BERT
            word_tokens = self.tokenizer.tokenize(word)
            
            if not word_tokens:
                self.alignment_issues += 1
                continue
            
            # Add tokens to sequence
            for subword_idx, subword in enumerate(word_tokens):
                bert_tokens.append(subword)
                bert_labels.append(tag)
                
                # Map subword to original word
                alignment[current_token_idx] = {
                    'word_idx': word_idx,
                    'word': word,
                    'subword_idx': subword_idx,
                    'subword': subword,
                    'tag': tag
                }
                
                current_token_idx += 1
            
            self.total_tokens += 1
            self.total_subwords += len(word_tokens)
        
        # Add special tokens
        bert_tokens = [self.tokenizer.cls_token] + bert_tokens + [self.tokenizer.sep_token]
        bert_labels = ['O'] + bert_labels + ['O']  # O for special tokens
        
        # Update alignment indices for special tokens
        alignment[-1] = {'special_token': 'CLS', 'tag': 'O'}
        alignment[len(bert_tokens) - 1] = {'special_token': 'SEP', 'tag': 'O'}
        
        return bert_tokens, bert_labels, alignment
    
    def create_bert_training_splits(self, 
                                   test_size: float = 0.2,
                                   val_size: float = 0.1,
                                   random_state: int = 42) -> Dict[str, Any]:
        """
        Create train/validation/test splits for BERT training
        
        Args:
            test_size: Test set proportion
            val_size: Validation set proportion
            random_state: Random seed
            
        Returns:
            Dict: Training splits
        """
        dataset = self.create_bert_dataset()
        
        if not dataset:
            return {}
        
        # Split indices
        indices = np.arange(len(dataset['input_ids']))
        
        # First split: separate test set
        train_val_indices, test_indices = train_test_split(
            indices, test_size=test_size, random_state=random_state
        )
        
        # Second split: separate validation from train
        val_size_adjusted = val_size / (1 - test_size)
        train_indices, val_indices = train_test_split(
            train_val_indices, test_size=val_size_adjusted, random_state=random_state
        )
        
        splits = {
            'train': {
                'input_ids': dataset['input_ids'][train_indices],
                'attention_mask': dataset['attention_mask'][train_indices],
                'labels': dataset['labels'][train_indices]
            },
            'validation': {
                'input_ids': dataset['input_ids'][val_indices],
                'attention_mask': dataset['attention_mask'][val_indices],
                'labels': dataset['labels'][val_indices]
            },
            'test': {
                'input_ids': dataset['input_ids'][test_indices],
                'attention_mask': dataset['attention_mask'][test_indices],
                'labels': dataset['labels'][test_indices]
            },
            'metadata': dataset['metadata']
        }
        
        return splits
    
    def export_for_huggingface(self, 
                              splits: Dict[str, Any], 
                              output_dir: str = "hf_dataset"):
        """
        Export dataset in Hugging Face format
        
        Args:
            splits: Training splits
            output_dir: Output directory
        """
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save each split
        for split_name, split_data in splits.items():
            if split_name == 'metadata':
                continue
            
            split_file = Path(output_dir) / f"{split_name}.json"
            split_dict = {
                'input_ids': split_data['input_ids'].tolist(),
                'attention_mask': split_data['attention_mask'].tolist(),
                'labels': split_data['labels'].tolist()
            }
            
            with open(split_file, 'w', encoding='utf-8') as f:
                json.dump(split_dict, f, ensure_ascii=False, indent=2)
        
        # Save metadata
        metadata_file = Path(output_dir) / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(splits['metadata'], f, ensure_ascii=False, indent=2)
        
        # Create dataset info file
        dataset_info = {
            'description': 'Turkish POS tagging dataset for BERT fine-tuning',
            'citation': 'Generated from Cleaned-for-tags.csv',
            'license': 'Custom',
            'features': {
                'input_ids': {'dtype': 'int32', 'shape': [self.max_seq_length]},
                'attention_mask': {'dtype': 'int32', 'shape': [self.max_seq_length]},
                'labels': {'dtype': 'int32', 'shape': [self.max_seq_length]}
            },
            'splits': {
                'train': len(splits['train']['input_ids']),
                'validation': len(splits['validation']['input_ids']),
                'test': len(splits['test']['input_ids'])
            }
        }
        
        info_file = Path(output_dir) / "dataset_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(dataset_info, f, ensure_ascii=False, indent=2)
        
        print(f"Hugging Face dataset exported to {output_dir}")
    
    def export_for_pytorch_lightning(self, 
                                    splits: Dict[str, Any], 
                                    output_dir: str = "pl_dataset"):
        """
        Export dataset for PyTorch Lightning
        
        Args:
            splits: Training splits
            output_dir: Output directory
        """
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save as PyTorch tensors
        for split_name, split_data in splits.items():
            if split_name == 'metadata':
                continue
            
            # Convert to tensors
            input_ids_tensor = torch.tensor(split_data['input_ids'], dtype=torch.long)
            attention_mask_tensor = torch.tensor(split_data['attention_mask'], dtype=torch.long)
            labels_tensor = torch.tensor(split_data['labels'], dtype=torch.long)
            
            # Save tensors
            torch.save({
                'input_ids': input_ids_tensor,
                'attention_mask': attention_mask_tensor,
                'labels': labels_tensor
            }, Path(output_dir) / f"{split_name}.pt")
        
        # Save metadata
        metadata_file = Path(output_dir) / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(splits['metadata'], f, ensure_ascii=False, indent=2)
        
        print(f"PyTorch Lightning dataset exported to {output_dir}")
    
    def get_bert_statistics(self) -> Dict[str, Any]:
        """Get BERT-specific statistics"""
        if self.data is None:
            return {}
        
        stats = {
            'basic_stats': {
                'total_tokens': self.total_tokens,
                'total_subwords': self.total_subwords,
                'alignment_issues': self.alignment_issues,
                'avg_subwords_per_token': self.total_subwords / max(1, self.total_tokens)
            },
            'bert_stats': {
                'model_name': self.bert_model_name,
                'vocab_size': len(self.tokenizer.get_vocab()) if self.tokenizer else 0,
                'max_seq_length': self.max_seq_length,
                'special_tokens': {
                    'cls': self.tokenizer.cls_token if self.tokenizer else None,
                    'sep': self.tokenizer.sep_token if self.tokenizer else None,
                    'pad': self.tokenizer.pad_token if self.tokenizer else None
                }
            },
            'label_stats': {
                'num_labels': len(self.label_to_id),
                'label_distribution': dict(Counter(self.data['Tag'].tolist())) if self.data is not None else {}
            }
        }
        
        return stats
    
    def _save_bert_dataset(self, dataset: Dict[str, Any], output_dir: str):
        """Save BERT dataset to files"""
        # Save as numpy arrays
        np.save(Path(output_dir) / "input_ids.npy", dataset['input_ids'])
        np.save(Path(output_dir) / "attention_mask.npy", dataset['attention_mask'])
        np.save(Path(output_dir) / "labels.npy", dataset['labels'])
        
        # Save metadata
        with open(Path(output_dir) / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(dataset['metadata'], f, ensure_ascii=False, indent=2)
        
        # Save label mappings
        with open(Path(output_dir) / "label_mappings.json", 'w', encoding='utf-8') as f:
            json.dump({
                'label_to_id': self.label_to_id,
                'id_to_label': self.id_to_label
            }, f, ensure_ascii=False, indent=2)
    
    def create_bert_config(self, output_path: str = "bert_config.json"):
        """Create BERT configuration file"""
        if not TRANSFORMERS_AVAILABLE or self.config is None:
            print("Error: BERT config not available")
            return
        
        config_dict = {
            'model_name': self.bert_model_name,
            'max_seq_length': self.max_seq_length,
            'vocab_size': self.config.vocab_size,
            'hidden_size': self.config.hidden_size,
            'num_hidden_layers': self.config.num_hidden_layers,
            'num_attention_heads': self.config.num_attention_heads,
            'intermediate_size': self.config.intermediate_size,
            'num_labels': len(self.label_to_id),
            'label_to_id': self.label_to_id,
            'id_to_label': self.id_to_label
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        
        print(f"BERT config saved to {output_path}")


def demo_bert_mapping():
    """Demonstrate BERT model mapping"""
    print("BERT Model Mapper Demo")
    print("=" * 30)
    
    # Initialize mapper
    bert_mapper = BERTModelMapper(
        max_seq_length=128,
        bert_model_name="dbmdz/bert-base-turkish-128k-cased"
    )
    
    # Load data
    if not bert_mapper.load_data():
        print("Failed to load data!")
        return
    
    # Create training splits
    splits = bert_mapper.create_bert_training_splits(
        test_size=0.2,
        val_size=0.1
    )
    
    if not splits:
        print("Failed to create splits!")
        return
    
    # Export for different frameworks
    bert_mapper.export_for_huggingface(splits, "hf_bert_dataset")
    bert_mapper.export_for_pytorch_lightning(splits, "pl_bert_dataset")
    
    # Get statistics
    stats = bert_mapper.get_bert_statistics()
    
    print("\n" + "="*50)
    print("BERT DATASET STATISTICS")
    print("="*50)
    print(f"Total tokens: {stats['basic_stats']['total_tokens']}")
    print(f"Total subwords: {stats['basic_stats']['total_subwords']}")
    print(f"Alignment issues: {stats['basic_stats']['alignment_issues']}")
    print(f"Avg subwords per token: {stats['basic_stats']['avg_subwords_per_token']:.2f}")
    print(f"Vocabulary size: {stats['bert_stats']['vocab_size']}")
    print(f"Number of labels: {stats['label_stats']['num_labels']}")
    
    print("\nGenerated files:")
    print("  - hf_bert_dataset/ (Hugging Face format)")
    print("  - pl_bert_dataset/ (PyTorch Lightning format)")
    print("  - bert_config.json (BERT configuration)")


if __name__ == "__main__":
    demo_bert_mapping()