#!/usr/bin/env python3
"""
Example: Using the Turkish Corpus Model Mapper
==============================================

This script demonstrates how to use the model mapping system
to create machine learning datasets from Turkish linguistic data.
"""

import sys
import os
from pathlib import Path

# Add the corpus_manipulator to the path
sys.path.insert(0, str(Path(__file__).parent))

from corpus_manipulator.model_mapper import TurkishModelMapper
from corpus_manipulator.model_bert_mapper import BERTModelMapper
from corpus_manipulator.model_integration import CorpusModelIntegration

def example_traditional_ml():
    """Example: Create traditional ML datasets"""
    print("=== Traditional ML Example ===")
    
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
    print(f"Extracted features shape: {features.shape}")
    
    # Create training dataset
    dataset = mapper.create_training_dataset(test_size=0.2)
    
    print(f"Training sequences: {dataset['train']['sequences'].shape}")
    print(f"Validation sequences: {dataset['validation']['sequences'].shape}")
    print(f"Test sequences: {dataset['test']['sequences'].shape}")
    
    # Export to different formats
    mapper.export_to_sklearn("example_sklearn_features.pkl")
    mapper.export_to_pytorch(dataset, "example_pytorch_dataset")
    mapper.export_to_tensorflow(dataset, "example_tensorflow_dataset")
    
    # Save mappings
    mapper.save_mappings("example_vocabulary_mappings.json")
    
    # Get statistics
    stats = mapper.get_statistics()
    print(f"\\nDataset statistics:")
    print(f"  Total tokens: {stats['basic_stats']['total_tokens']}")
    print(f"  Unique words: {stats['basic_stats']['unique_words']}")
    print(f"  Unique tags: {stats['basic_stats']['unique_tags']}")
    
    print("\\nTraditional ML example completed!\\n")


def example_bert_mapping():
    """Example: Create BERT datasets"""
    print("=== BERT Mapping Example ===")
    
    # Initialize BERT mapper
    bert_mapper = BERTModelMapper(
        bert_model_name="dbmdz/bert-base-turkish-128k-cased",
        max_seq_length=128
    )
    
    # Load data
    if not bert_mapper.load_data():
        print("Failed to load data!")
        return
    
    # Create BERT training splits
    splits = bert_mapper.create_bert_training_splits(
        test_size=0.2, val_size=0.1
    )
    
    if not splits:
        print("Failed to create BERT splits!")
        return
    
    print(f"BERT dataset created:")
    print(f"  Train: {splits['train']['input_ids'].shape}")
    print(f"  Validation: {splits['validation']['input_ids'].shape}")
    print(f"  Test: {splits['test']['input_ids'].shape}")
    
    # Export for different frameworks
    bert_mapper.export_for_huggingface(splits, "example_hf_bert_dataset")
    bert_mapper.export_for_pytorch_lightning(splits, "example_pl_bert_dataset")
    
    # Create BERT config
    bert_mapper.create_bert_config("example_bert_config.json")
    
    # Get statistics
    stats = bert_mapper.get_bert_statistics()
    print(f"\\nBERT statistics:")
    print(f"  Model: {stats['bert_stats']['model_name']}")
    print(f"  Vocab size: {stats['bert_stats']['vocab_size']}")
    print(f"  Total tokens: {stats['basic_stats']['total_tokens']}")
    print(f"  Total subwords: {stats['basic_stats']['total_subwords']}")
    print(f"  Alignment issues: {stats['basic_stats']['alignment_issues']}")
    
    print("\\nBERT mapping example completed!\\n")


def example_full_integration():
    """Example: Run the complete integration pipeline"""
    print("=== Full Integration Example ===")
    
    # Initialize integration
    integration = CorpusModelIntegration(
        output_base="example_integration_output"
    )
    
    # Run complete pipeline
    results = integration.run_full_pipeline(
        include_bert=True,
        include_traditional=True,
        test_size=0.2,
        bert_model="dbmdz/bert-base-turkish-128k-cased"
    )
    
    # Print summary
    summary = integration.get_integration_summary()
    
    print(f"Integration completed successfully!")
    print(f"Total time: {results['summary']['total_time']:.2f} seconds")
    
    print(f"\\nSummary:")
    print(f"  CSV data loaded: {summary['csv_mapper']['data_loaded']}")
    print(f"  Unique sentences: {summary['csv_mapper']['unique_sentences']}")
    print(f"  Vocabulary size: {summary['model_mapper']['vocabulary_size']}")
    print(f"  BERT model loaded: {summary['bert_mapper']['model_loaded']}")
    
    print(f"\\nOutput directories:")
    for name, path in summary['output_directories'].items():
        print(f"  {name}: {path}")
    
    print("\\nFull integration example completed!\\n")


def example_custom_configuration():
    """Example: Using custom configuration"""
    print("=== Custom Configuration Example ===")
    
    # Import configuration
    from corpus_manipulator.config.model_config import MODEL_CONFIG, update_config
    
    # Modify configuration
    print("Original configuration:")
    print(f"  Max sequence length: {MODEL_CONFIG['max_sequence_length']}")
    print(f"  Batch size: {MODEL_CONFIG['batch_size']}")
    print(f"  Test size: {MODEL_CONFIG['test_size']}")
    
    # Update configuration
    update_config('max_sequence_length', 100)
    update_config('batch_size', 64)
    update_config('test_size', 0.3)
    
    print("\\nUpdated configuration:")
    print(f"  Max sequence length: {MODEL_CONFIG['max_sequence_length']}")
    print(f"  Batch size: {MODEL_CONFIG['batch_size']}")
    print(f"  Test size: {MODEL_CONFIG['test_size']}")
    
    # Use with custom configuration
    mapper = TurkishModelMapper()
    if mapper.load_data():
        mapper.build_vocabulary()
        dataset = mapper.create_training_dataset(
            test_size=MODEL_CONFIG['test_size']
        )
        print(f"\\nCreated dataset with custom config:")
        print(f"  Train size: {len(dataset['train']['sequences'])}")
        print(f"  Test size: {len(dataset['test']['sequences'])}")
    
    print("\\nCustom configuration example completed!\\n")


def example_evaluation_setup():
    """Example: Setting up evaluation"""
    print("=== Evaluation Setup Example ===")
    
    # Create evaluation directory
    eval_dir = Path("example_evaluation")
    eval_dir.mkdir(exist_ok=True)
    
    # Create evaluation configuration
    eval_config = {
        'metrics': ['accuracy', 'precision', 'recall', 'f1_score'],
        'evaluation_sets': ['train', 'validation', 'test'],
        'cross_validation': {
            'enabled': True,
            'folds': 5,
            'stratified': True
        },
        'benchmark_models': [
            'baseline_random',
            'baseline_majority_class',
            'traditional_ml_models',
            'bert_models'
        ]
    }
    
    # Save evaluation config
    import json
    with open(eval_dir / "evaluation_config.json", 'w', encoding='utf-8') as f:
        json.dump(eval_config, f, ensure_ascii=False, indent=2)
    
    # Create simple evaluation script
    eval_script = '''#!/usr/bin/env python3
"""
Simple Evaluation Script
"""

import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def evaluate_predictions(y_true, y_pred, labels=None):
    """Evaluate model predictions"""
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average='weighted', labels=labels
    )
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }

if __name__ == "__main__":
    print("Evaluation script template created")
'''
    
    with open(eval_dir / "simple_eval.py", 'w', encoding='utf-8') as f:
        f.write(eval_script)
    
    print(f"Evaluation setup created in: {eval_dir}")
    print(f"Configuration saved: {eval_dir / 'evaluation_config.json'}")
    print(f"Script template: {eval_dir / 'simple_eval.py'}")
    
    print("\\nEvaluation setup example completed!\\n")


def main():
    """Run all examples"""
    print("Turkish Corpus Model Mapper Examples")
    print("=" * 50)
    print()
    
    # Check if CSV file exists
    csv_path = "Cleaned-for-tags.csv"
    if not Path(csv_path).exists():
        print(f"Warning: {csv_path} not found!")
        print("Please ensure the CSV file is in the current directory.")
        print("Or modify the path in the examples.")
        return
    
    try:
        # Run examples
        example_traditional_ml()
        example_bert_mapping()
        example_custom_configuration()
        example_evaluation_setup()
        example_full_integration()
        
        print("All examples completed successfully!")
        print("\\nGenerated files:")
        print("  - example_sklearn_features.pkl")
        print("  - example_pytorch_dataset/")
        print("  - example_tensorflow_dataset/")
        print("  - example_vocabulary_mappings.json")
        print("  - example_hf_bert_dataset/")
        print("  - example_pl_bert_dataset/")
        print("  - example_bert_config.json")
        print("  - example_integration_output/")
        print("  - example_evaluation/")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()