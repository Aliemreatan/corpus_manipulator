#!/usr/bin/env python3
"""
Model Mapper Configuration
==========================

Configuration settings and constants for the Turkish Corpus Model Mapper.
This file contains all configurable parameters for different ML frameworks
and training scenarios.
"""

import os
from pathlib import Path
from typing import Dict, List, Any

# Default paths
DEFAULT_CSV_PATH = "Cleaned-for-tags.csv"
DEFAULT_DB_PATH = "corpus.db"
DEFAULT_OUTPUT_DIR = "model_outputs"

# Model configuration
MODEL_CONFIG = {
    # Sequence modeling parameters
    'max_sequence_length': 50,
    'context_window_size': 2,
    'embedding_dim': 100,
    'hidden_size': 128,
    'num_layers': 2,
    
    # Training parameters
    'batch_size': 32,
    'learning_rate': 0.001,
    'num_epochs': 50,
    'dropout_rate': 0.2,
    
    # Data splitting
    'test_size': 0.2,
    'val_size': 0.1,
    'random_state': 42,
    
    # Vocabulary settings
    'min_word_frequency': 1,
    'max_vocab_size': 10000,
    'unknown_token': '<UNK>',
    'padding_token': '<PAD>',
    
    # Feature extraction
    'include_word_features': True,
    'include_position_features': True,
    'include_sentence_features': True,
    'include_ngram_features': True,
    'ngram_range': (2, 3),
    
    # Output formats
    'export_tensorflow': True,
    'export_pytorch': True,
    'export_sklearn': True,
    'export_mappings': True,
    
    # Performance settings
    'use_parallel_processing': True,
    'memory_efficient': False,
    'cache_features': True
}

# Framework-specific configurations
FRAMEWORK_CONFIGS = {
    'tensorflow': {
        'version': '2.x',
        'layers': {
            'embedding': {'mask_zero': True},
            'lstm': {'return_sequences': True, 'dropout': 0.2},
            'dense': {'activation': 'softmax'}
        },
        'optimizer': 'adam',
        'loss': 'sparse_categorical_crossentropy',
        'metrics': ['accuracy']
    },
    
    'pytorch': {
        'version': '1.x',
        'model_architecture': {
            'embedding': {'padding_idx': 0},
            'lstm': {'batch_first': True, 'dropout': 0.2},
            'linear': {}
        },
        'optimizer': 'Adam',
        'loss_function': 'CrossEntropyLoss',
        'scheduler': 'StepLR'
    },
    
    'sklearn': {
        'classifier': 'RandomForestClassifier',
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42,
        'feature_scaling': True
    }
}

# Turkish-specific linguistic features
TURKISH_FEATURES = {
    'vowel_harmony': True,
    'agglutination': True,
    'suffix_analysis': True,
    'pos_tag_hierarchy': True,
    
    # Turkish POS tag mappings
    'pos_mappings': {
        'AD-NOUN': 'NOUN',
        'AD-PROPN': 'PROPN', 
        'SIFAT-ADJECTIVE': 'ADJ',
        'FIIL-VERB': 'VERB',
        'FIIL-AUX': 'AUX',
        'ZAMIR-PRON': 'PRON',
        'BELIRTEÇ-DET': 'DET',
        'EDAT-ADP': 'ADP',
        'BAGLAÇ-CCONJ': 'CCONJ',
        'BAGLAÇ-SCONJ': 'SCONJ',
        'SAYI-NUM': 'NUM',
        'UNLEM-INTJ': 'INTJ',
        'NOKTALAMA-PUNCT': 'PUNCT',
        'SIMGE-SYM': 'SYM'
    },
    
    # Turkish morphological features
    'morphological_features': [
        'Number',      # Singular, Plural
        'Case',        # Nominative, Accusative, Dative, Locative, Ablative, Genitive
        'Person',      # First, Second, Third
        'Tense',       # Present, Past, Future
        'Aspect',      # Perfect, Imperfect
        'Mood',        # Indicative, Conditional, Imperative, Optative
        'Voice',       # Active, Passive, Causative, Reflexive
        'Degree'       # Positive, Comparative, Superlative
    ],
    
    # Turkish case suffixes
    'case_suffixes': {
        'ACC': ['i', 'ı', 'u', 'ü'],
        'DAT': ['e', 'a'],
        'LOC': ['de', 'da', 'te', 'ta'],
        'ABL': ['den', 'dan', 'ten', 'tan'],
        'GEN': ['in', 'ın', 'un', 'ün', 'nin', 'nın', 'nun', 'nün']
    }
}

# Output directory structure
OUTPUT_STRUCTURE = {
    'base_dir': DEFAULT_OUTPUT_DIR,
    'subdirs': {
        'tensorflow': 'tensorflow_models',
        'pytorch': 'pytorch_models',
        'sklearn': 'sklearn_models',
        'mappings': 'model_mappings',
        'features': 'extracted_features',
        'logs': 'training_logs',
        'visualizations': 'visualizations'
    }
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'model_mapper.log',
    'console': True,
    'max_file_size': 10*1024*1024,  # 10MB
    'backup_count': 5
}

# Performance optimization settings
PERFORMANCE_CONFIG = {
    'use_multiprocessing': True,
    'chunk_size': 10000,
    'memory_limit': '4GB',
    'cache_size': 1000,
    'enable_profiling': False,
    'profile_output': 'performance_profile.prof'
}

# Validation settings
VALIDATION_CONFIG = {
    'cross_validation_folds': 5,
    'stratified_split': True,
    'early_stopping': True,
    'patience': 5,
    'validation_metric': 'accuracy',
    'save_best_model': True
}

# Export settings
EXPORT_CONFIG = {
    'include_metadata': True,
    'include_statistics': True,
    'include_sample_data': True,
    'compress_outputs': False,
    'format_version': '1.0'
}

def get_config(key: str = None) -> Any:
    """
    Get configuration value by key
    
    Args:
        key: Configuration key (e.g., 'tensorflow', 'pytorch', 'sklearn')
        
    Returns:
        Configuration dictionary or value
    """
    if key is None:
        return MODEL_CONFIG
    
    if key in FRAMEWORK_CONFIGS:
        return FRAMEWORK_CONFIGS[key]
    
    if key in globals():
        return globals()[key]
    
    return None

def update_config(key: str, value: Any):
    """
    Update configuration value
    
    Args:
        key: Configuration key
        value: New value
    """
    if key in globals():
        globals()[key] = value
    elif key in MODEL_CONFIG:
        MODEL_CONFIG[key] = value
    else:
        raise KeyError(f"Configuration key '{key}' not found")

def create_output_directories():
    """
    Create output directory structure
    """
    base_dir = Path(OUTPUT_STRUCTURE['base_dir'])
    base_dir.mkdir(exist_ok=True)
    
    for subdir_name in OUTPUT_STRUCTURE['subdirs'].values():
        subdir = base_dir / subdir_name
        subdir.mkdir(exist_ok=True)
    
    print(f"Output directories created in: {base_dir}")

def get_output_path(subdir: str, filename: str) -> str:
    """
    Get full output path for a file
    
    Args:
        subdir: Subdirectory name
        filename: File name
        
    Returns:
        Full path string
    """
    base_dir = OUTPUT_STRUCTURE['base_dir']
    subdir_path = OUTPUT_STRUCTURE['subdirs'].get(subdir, subdir)
    return os.path.join(base_dir, subdir_path, filename)

def validate_config():
    """
    Validate configuration settings
    """
    errors = []
    
    # Check required directories
    for subdir in OUTPUT_STRUCTURE['subdirs'].values():
        if not isinstance(subdir, str):
            errors.append(f"Invalid subdir type: {subdir}")
    
    # Check model parameters
    if MODEL_CONFIG['max_sequence_length'] <= 0:
        errors.append("max_sequence_length must be positive")
    
    if MODEL_CONFIG['batch_size'] <= 0:
        errors.append("batch_size must be positive")
    
    if not 0 < MODEL_CONFIG['test_size'] < 1:
        errors.append("test_size must be between 0 and 1")
    
    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(errors))
    
    return True

# Initialize output directories on import
if __name__ != "__main__":
    try:
        create_output_directories()
        validate_config()
    except Exception as e:
        print(f"Warning: Configuration initialization failed: {e}")