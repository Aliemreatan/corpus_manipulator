#!/usr/bin/env python3
"""
Model Integration Module
========================

This module provides integration between the CSV mapper, model mapper, and BERT mapper,
creating a unified interface for Turkish corpus model development and training.

Features:
- Unified model creation pipeline
- Cross-framework compatibility
- Database integration
- Performance optimization
- Model evaluation utilities

Author: Kilo Code
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import json
import logging
import time
from datetime import datetime

# Import our modules
from csv_mapper import TurkishCSVMapper
from model_mapper import TurkishModelMapper
from model_bert_mapper import BERTModelMapper
from config.model_config import MODEL_CONFIG, FRAMEWORK_CONFIGS, OUTPUT_STRUCTURE
from database.schema import CorpusDatabase

logger = logging.getLogger(__name__)

class CorpusModelIntegration:
    """
    Unified integration for Turkish corpus model development
    """
    
    def __init__(self, 
                 csv_path: str = "Cleaned-for-tags.csv",
                 db_path: str = "corpus.db",
                 output_base: str = "model_outputs"):
        """
        Initialize the integration
        
        Args:
            csv_path: Path to CSV file
            db_path: Path to database
            output_base: Base output directory
        """
        self.csv_path = csv_path
        self.db_path = db_path
        self.output_base = Path(output_base)
        
        # Initialize components
        self.csv_mapper = TurkishCSVMapper(csv_path)
        self.model_mapper = TurkishModelMapper(csv_path, db_path)
        self.bert_mapper = BERTModelMapper(csv_path)
        
        # Integration state
        self.integration_log = []
        self.performance_metrics = {}
        
        # Create output directories
        self._setup_output_directories()
    
    def _setup_output_directories(self):
        """Create output directory structure"""
        self.output_base.mkdir(exist_ok=True)
        
        subdirs = ['traditional_ml', 'bert_models', 'unified_datasets', 'evaluations', 'logs']
        for subdir in subdirs:
            (self.output_base / subdir).mkdir(exist_ok=True)
    
    def run_full_pipeline(self, 
                         include_bert: bool = True,
                         include_traditional: bool = True,
                         test_size: float = 0.2,
                         bert_model: str = "dbmdz/bert-base-turkish-128k-cased") -> Dict[str, Any]:
        """
        Run the complete model creation pipeline
        
        Args:
            include_bert: Whether to include BERT model creation
            include_traditional: Whether to include traditional ML models
            test_size: Test set proportion
            bert_model: BERT model name
            
        Returns:
            Dict: Pipeline results and metadata
        """
        start_time = time.time()
        
        pipeline_results = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'include_bert': include_bert,
                'include_traditional': include_traditional,
                'test_size': test_size,
                'bert_model': bert_model
            },
            'stages': {},
            'summary': {}
        }
        
        # Stage 1: Data Loading and Analysis
        logger.info("Stage 1: Data Loading and Analysis")
        stage_start = time.time()
        
        data_loaded = self._stage_data_loading()
        pipeline_results['stages']['data_loading'] = data_loaded
        
        stage_time = time.time() - stage_start
        logger.info(f"Stage 1 completed in {stage_time:.2f} seconds")
        
        # Stage 2: Traditional ML Models
        if include_traditional:
            logger.info("Stage 2: Traditional ML Model Creation")
            stage_start = time.time()
            
            traditional_results = self._stage_traditional_ml()
            pipeline_results['stages']['traditional_ml'] = traditional_results
            
            stage_time = time.time() - stage_start
            logger.info(f"Stage 2 completed in {stage_time:.2f} seconds")
        
        # Stage 3: BERT Models
        if include_bert:
            logger.info("Stage 3: BERT Model Creation")
            stage_start = time.time()
            
            bert_results = self._stage_bert_models(bert_model)
            pipeline_results['stages']['bert_models'] = bert_results
            
            stage_time = time.time() - stage_start
            logger.info(f"Stage 3 completed in {stage_time:.2f} seconds")
        
        # Stage 4: Unified Dataset Creation
        logger.info("Stage 4: Unified Dataset Creation")
        stage_start = time.time()
        
        unified_results = self._stage_unified_datasets()
        pipeline_results['stages']['unified_datasets'] = unified_results
        
        stage_time = time.time() - stage_start
        logger.info(f"Stage 4 completed in {stage_time:.2f} seconds")
        
        # Stage 5: Evaluation Setup
        logger.info("Stage 5: Evaluation Setup")
        stage_start = time.time()
        
        eval_results = self._stage_evaluation_setup()
        pipeline_results['stages']['evaluation'] = eval_results
        
        stage_time = time.time() - stage_start
        logger.info(f"Stage 5 completed in {stage_time:.2f} seconds")
        
        # Calculate total time
        total_time = time.time() - start_time
        pipeline_results['summary']['total_time'] = total_time
        pipeline_results['summary']['completion_time'] = datetime.now().isoformat()
        
        # Save pipeline results
        self._save_pipeline_results(pipeline_results)
        
        logger.info(f"Pipeline completed in {total_time:.2f} seconds")
        return pipeline_results
    
    def _stage_data_loading(self) -> Dict[str, Any]:
        """Stage 1: Load and analyze data"""
        results = {}
        
        # Load data with CSV mapper
        if self.csv_mapper.load_data():
            self.csv_mapper.build_mappings()
            summary = self.csv_mapper.get_summary()
            results['csv_mapper'] = summary
        
        # Load data with model mapper
        if self.model_mapper.load_data():
            self.model_mapper.build_vocabulary()
            features = self.model_mapper.extract_features()
            results['model_mapper'] = {
                'vocabulary_size': self.model_mapper.vocabulary_size,
                'tagset_size': self.model_mapper.tagset_size,
                'feature_shape': features.shape if features is not None else None
            }
        
        # Load data with BERT mapper
        if self.bert_mapper.load_data():
            results['bert_mapper'] = {
                'data_loaded': True,
                'total_rows': len(self.bert_mapper.data) if self.bert_mapper.data is not None else 0
            }
        
        return results
    
    def _stage_traditional_ml(self) -> Dict[str, Any]:
        """Stage 2: Create traditional ML datasets"""
        results = {}
        
        # Create training dataset
        dataset = self.model_mapper.create_training_dataset(test_size=0.2)
        
        # Export to different formats
        sklearn_path = self.output_base / "traditional_ml" / "sklearn_features.pkl"
        torch_dir = self.output_base / "traditional_ml" / "pytorch"
        tf_dir = self.output_base / "traditional_ml" / "tensorflow"
        
        self.model_mapper.export_to_sklearn(str(sklearn_path))
        self.model_mapper.export_to_pytorch(dataset, str(torch_dir))
        self.model_mapper.export_to_tensorflow(dataset, str(tf_dir))
        
        # Save mappings
        mappings_path = self.output_base / "traditional_ml" / "vocabulary_mappings.json"
        self.model_mapper.save_mappings(str(mappings_path))
        
        results = {
            'dataset_shape': {
                'train': dataset['train']['sequences'].shape,
                'validation': dataset['validation']['sequences'].shape,
                'test': dataset['test']['sequences'].shape
            },
            'vocabulary_size': self.model_mapper.vocabulary_size,
            'tagset_size': self.model_mapper.tagset_size,
            'exported_formats': ['sklearn', 'pytorch', 'tensorflow'],
            'files_created': [
                str(sklearn_path),
                str(torch_dir),
                str(tf_dir),
                str(mappings_path)
            ]
        }
        
        return results
    
    def _stage_bert_models(self, bert_model: str) -> Dict[str, Any]:
        """Stage 3: Create BERT datasets"""
        results = {}
        
        # Update BERT model if specified
        if bert_model != "dbmdz/bert-base-turkish-128k-cased":
            self.bert_mapper.bert_model_name = bert_model
            self.bert_mapper._load_bert_components()
        
        # Create BERT training splits
        splits = self.bert_mapper.create_bert_training_splits(
            test_size=0.2, val_size=0.1
        )
        
        if not splits:
            results['error'] = "Failed to create BERT splits"
            return results
        
        # Export for different frameworks
        hf_dir = self.output_base / "bert_models" / "huggingface"
        pl_dir = self.output_base / "bert_models" / "pytorch_lightning"
        
        self.bert_mapper.export_for_huggingface(splits, str(hf_dir))
        self.bert_mapper.export_for_pytorch_lightning(splits, str(pl_dir))
        
        # Save BERT config
        config_path = self.output_base / "bert_models" / "bert_config.json"
        self.bert_mapper.create_bert_config(str(config_path))
        
        # Get statistics
        stats = self.bert_mapper.get_bert_statistics()
        
        results = {
            'model_name': self.bert_mapper.bert_model_name,
            'max_seq_length': self.bert_mapper.max_seq_length,
            'dataset_shape': {
                'train': splits['train']['input_ids'].shape,
                'validation': splits['validation']['input_ids'].shape,
                'test': splits['test']['input_ids'].shape
            },
            'vocab_size': stats['bert_stats']['vocab_size'],
            'num_labels': stats['label_stats']['num_labels'],
            'alignment_stats': {
                'total_tokens': stats['basic_stats']['total_tokens'],
                'total_subwords': stats['basic_stats']['total_subwords'],
                'alignment_issues': stats['basic_stats']['alignment_issues']
            },
            'exported_formats': ['huggingface', 'pytorch_lightning'],
            'files_created': [
                str(hf_dir),
                str(pl_dir),
                str(config_path)
            ]
        }
        
        return results
    
    def _stage_unified_datasets(self) -> Dict[str, Any]:
        """Stage 4: Create unified datasets"""
        results = {}
        
        # Create unified metadata
        unified_metadata = {
            'integration_timestamp': datetime.now().isoformat(),
            'csv_source': self.csv_path,
            'database_source': self.db_path,
            'vocabulary_size': self.model_mapper.vocabulary_size,
            'tagset_size': self.model_mapper.tagset_size,
            'total_tokens': len(self.model_mapper.data) if self.model_mapper.data is not None else 0,
            'frameworks_supported': ['sklearn', 'pytorch', 'tensorflow', 'huggingface'],
            'output_directories': {
                'traditional_ml': str(self.output_base / "traditional_ml"),
                'bert_models': str(self.output_base / "bert_models"),
                'unified_datasets': str(self.output_base / "unified_datasets"),
                'evaluations': str(self.output_base / "evaluations")
            }
        }
        
        # Save unified metadata
        metadata_path = self.output_base / "unified_datasets" / "unified_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(unified_metadata, f, ensure_ascii=False, indent=2)
        
        # Create dataset manifest
        manifest = {
            'datasets': [
                {
                    'name': 'traditional_ml',
                    'description': 'Traditional machine learning datasets',
                    'formats': ['sklearn', 'pytorch', 'tensorflow'],
                    'path': str(self.output_base / "traditional_ml")
                },
                {
                    'name': 'bert_models',
                    'description': 'BERT-compatible datasets for fine-tuning',
                    'formats': ['huggingface', 'pytorch_lightning'],
                    'path': str(self.output_base / "bert_models")
                }
            ],
            'mappings': [
                {
                    'name': 'vocabulary_mappings',
                    'description': 'Word and tag mappings',
                    'path': str(self.output_base / "traditional_ml" / "vocabulary_mappings.json")
                },
                {
                    'name': 'bert_config',
                    'description': 'BERT model configuration',
                    'path': str(self.output_base / "bert_models" / "bert_config.json")
                }
            ]
        }
        
        manifest_path = self.output_base / "unified_datasets" / "dataset_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        results = {
            'metadata_path': str(metadata_path),
            'manifest_path': str(manifest_path),
            'total_datasets': 2,
            'total_mappings': 2,
            'frameworks_supported': unified_metadata['frameworks_supported']
        }
        
        return results
    
    def _stage_evaluation_setup(self) -> Dict[str, Any]:
        """Stage 5: Setup evaluation framework"""
        results = {}
        
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
        eval_config_path = self.output_base / "evaluations" / "evaluation_config.json"
        with open(eval_config_path, 'w', encoding='utf-8') as f:
            json.dump(eval_config, f, ensure_ascii=False, indent=2)
        
        # Create evaluation scripts template
        eval_script = f'''#!/usr/bin/env python3
"""
Evaluation Script for Turkish Corpus Models
Generated by CorpusModelIntegration
"""

import json
import numpy as np
from pathlib import Path

def load_evaluation_config():
    """Load evaluation configuration"""
    config_path = Path("{eval_config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def evaluate_model(model, X_test, y_test, config):
    """Evaluate a trained model"""
    # Implementation would go here
    pass

if __name__ == "__main__":
    config = load_evaluation_config()
    print("Evaluation configuration loaded")
    print(f"Metrics: {{config['metrics']}}")
    print(f"Cross-validation folds: {{config['cross_validation']['folds']}}")
'''
        
        eval_script_path = self.output_base / "evaluations" / "evaluate_models.py"
        with open(eval_script_path, 'w', encoding='utf-8') as f:
            f.write(eval_script)
        
        results = {
            'config_path': str(eval_config_path),
            'script_path': str(eval_script_path),
            'metrics': eval_config['metrics'],
            'cross_validation': eval_config['cross_validation'],
            'benchmark_models': eval_config['benchmark_models']
        }
        
        return results
    
    def _save_pipeline_results(self, results: Dict[str, Any]):
        """Save pipeline results to file"""
        results_path = self.output_base / "logs" / "pipeline_results.json"
        results_path.parent.mkdir(exist_ok=True)
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Also save a summary log
        summary_log = self.output_base / "logs" / "pipeline_summary.log"
        with open(summary_log, 'w', encoding='utf-8') as f:
            f.write(f"Pipeline Execution Summary\\n")
            f.write(f"==========================\\n")
            f.write(f"Start Time: {results['timestamp']}\\n")
            f.write(f"Total Time: {results['summary']['total_time']:.2f} seconds\\n")
            f.write(f"\\nStages Completed:\\n")
            for stage_name in results['stages'].keys():
                f.write(f"  - {stage_name}\\n")
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Get summary of the integration"""
        summary = {
            'csv_mapper': {
                'data_loaded': self.csv_mapper.data is not None,
                'unique_sentences': len(self.csv_mapper.unique_sentences) if hasattr(self.csv_mapper, 'unique_sentences') else 0,
                'unique_words': len(self.csv_mapper.unique_words) if hasattr(self.csv_mapper, 'unique_words') else 0,
                'unique_tags': len(self.csv_mapper.unique_tags) if hasattr(self.csv_mapper, 'unique_tags') else 0
            },
            'model_mapper': {
                'vocabulary_size': self.model_mapper.vocabulary_size,
                'tagset_size': self.model_mapper.tagset_size,
                'data_loaded': self.model_mapper.data is not None
            },
            'bert_mapper': {
                'model_loaded': self.bert_mapper.tokenizer is not None,
                'bert_model': self.bert_mapper.bert_model_name
            },
            'output_directories': {
                'base': str(self.output_base),
                'traditional_ml': str(self.output_base / "traditional_ml"),
                'bert_models': str(self.output_base / "bert_models"),
                'unified_datasets': str(self.output_base / "unified_datasets"),
                'evaluations': str(self.output_base / "evaluations")
            }
        }
        
        return summary


def demo_integration():
    """Demonstrate the integration pipeline"""
    print("Corpus Model Integration Demo")
    print("=" * 40)
    
    # Initialize integration
    integration = CorpusModelIntegration()
    
    # Run full pipeline
    results = integration.run_full_pipeline(
        include_bert=True,
        include_traditional=True,
        test_size=0.2,
        bert_model="dbmdz/bert-base-turkish-128k-cased"
    )
    
    # Print summary
    summary = integration.get_integration_summary()
    
    print("\\n" + "="*50)
    print("INTEGRATION SUMMARY")
    print("="*50)
    
    print(f"CSV Mapper:")
    print(f"  Data loaded: {summary['csv_mapper']['data_loaded']}")
    print(f"  Unique sentences: {summary['csv_mapper']['unique_sentences']}")
    print(f"  Unique words: {summary['csv_mapper']['unique_words']}")
    print(f"  Unique tags: {summary['csv_mapper']['unique_tags']}")
    
    print(f"\\nModel Mapper:")
    print(f"  Vocabulary size: {summary['model_mapper']['vocabulary_size']}")
    print(f"  Tagset size: {summary['model_mapper']['tagset_size']}")
    
    print(f"\\nBERT Mapper:")
    print(f"  Model loaded: {summary['bert_mapper']['model_loaded']}")
    print(f"  Model name: {summary['bert_mapper']['bert_model']}")
    
    print(f"\\nOutput directories created:")
    for name, path in summary['output_directories'].items():
        print(f"  {name}: {path}")
    
    print(f"\\nPipeline completed in {results['summary']['total_time']:.2f} seconds")
    print(f"Results saved to: {integration.output_base}")


if __name__ == "__main__":
    demo_integration()