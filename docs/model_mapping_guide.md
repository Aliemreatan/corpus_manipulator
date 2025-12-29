# Turkish Corpus Model Mapping Guide

## Overview

The Turkish Corpus Model Mapper provides advanced capabilities for converting Turkish linguistic data into machine learning-ready formats. This guide explains how to use the model mapping system to create datasets for various ML frameworks and training scenarios.

## Architecture

The model mapping system consists of several interconnected modules:

### Core Modules

1. **`model_mapper.py`** - Main model mapper for traditional ML frameworks
2. **`model_bert_mapper.py`** - Specialized BERT model mapper
3. **`model_integration.py`** - Unified integration pipeline
4. **`config/model_config.py`** - Configuration settings

### Integration with Existing System

- **CSV Mapper** (`csv_mapper.py`) - Data loading and basic analysis
- **Database Schema** (`database/schema.py`) - Storage and indexing
- **BERT Processor** (`nlp/custom_bert_processor.py`) - NLP processing

## Quick Start

### Basic Model Mapping

```python
from corpus_manipulator.model_mapper import TurkishModelMapper

# Initialize mapper
mapper = TurkishModelMapper()

# Load data
mapper.load_data()

# Build vocabulary
mapper.build_vocabulary()

# Create training dataset
dataset = mapper.create_training_dataset(test_size=0.2)

# Export to different formats
mapper.export_to_sklearn("sklearn_features.pkl")
mapper.export_to_pytorch(dataset, "torch_dataset")
mapper.export_to_tensorflow(dataset, "tf_dataset")
```

### BERT Model Mapping

```python
from corpus_manipulator.model_bert_mapper import BERTModelMapper

# Initialize BERT mapper
bert_mapper = BERTModelMapper(
    bert_model_name="dbmdz/bert-base-turkish-128k-cased",
    max_seq_length=128
)

# Load data
bert_mapper.load_data()

# Create BERT dataset
splits = bert_mapper.create_bert_training_splits(
    test_size=0.2, val_size=0.1
)

# Export for different frameworks
bert_mapper.export_for_huggingface(splits, "hf_bert_dataset")
bert_mapper.export_for_pytorch_lightning(splits, "pl_bert_dataset")
```

### Full Integration Pipeline

```python
from corpus_manipulator.model_integration import CorpusModelIntegration

# Initialize integration
integration = CorpusModelIntegration()

# Run complete pipeline
results = integration.run_full_pipeline(
    include_bert=True,
    include_traditional=True,
    test_size=0.2
)
```

## Data Formats

### Input Format

The system expects CSV files with the following columns:
- `Full_Sentence`: Complete sentence text
- `Word`: Individual word/token
- `Tag`: Part-of-speech tag

Example:
```
Full_Sentence,Word,Tag
"Ben okula gidiyorum.",Ben,PRON
"Ben okula gidiyorum.",okula,NOUN
"Ben okula gidiyorum.",gidiyorum,VERB
```

### Output Formats

#### Traditional ML Formats

1. **scikit-learn** (`.pkl`)
   - Feature matrices and labels
   - Encoders for categorical features
   - Metadata and statistics

2. **PyTorch** (`.npy` files)
   - Numpy arrays for sequences and labels
   - Separate files for train/validation/test
   - Metadata JSON file

3. **TensorFlow** (`.tfrecord` or saved datasets)
   - TensorFlow dataset objects
   - Compatible with tf.data API
   - Metadata and configuration

#### BERT Formats

1. **Hugging Face** (JSON format)
   - Input IDs, attention masks, labels
   - Compatible with 🤗 Transformers
   - Dataset info and metadata

2. **PyTorch Lightning** (`.pt` files)
   - PyTorch tensors
   - Compatible with LightningDataModule
   - Metadata and configuration

## Configuration

### Model Configuration

Edit `config/model_config.py` to customize:

```python
MODEL_CONFIG = {
    'max_sequence_length': 50,      # Maximum sequence length
    'batch_size': 32,               # Training batch size
    'learning_rate': 0.001,         # Optimizer learning rate
    'test_size': 0.2,               # Test set proportion
    'random_state': 42,             # Random seed for reproducibility
    # ... more settings
}
```

### Framework-Specific Configuration

```python
FRAMEWORK_CONFIGS = {
    'tensorflow': {
        'layers': {
            'embedding': {'mask_zero': True},
            'lstm': {'return_sequences': True, 'dropout': 0.2},
            'dense': {'activation': 'softmax'}
        },
        'optimizer': 'adam',
        'loss': 'sparse_categorical_crossentropy'
    },
    'pytorch': {
        'model_architecture': {
            'embedding': {'padding_idx': 0},
            'lstm': {'batch_first': True, 'dropout': 0.2}
        },
        'optimizer': 'Adam',
        'loss_function': 'CrossEntropyLoss'
    }
}
```

## Advanced Features

### Feature Engineering

The model mapper automatically extracts various features:

#### Word-Level Features
- Word length
- Capitalization patterns
- Digit presence
- Punctuation presence
- Prefixes and suffixes

#### Context Features
- Position in sentence
- Sentence length
- Word context windows

#### Morphological Features
- Turkish case suffixes
- Number and person markers
- Verb tense and aspect

### Vocabulary Management

```python
# Access vocabulary mappings
word_to_id = mapper.word_to_id
id_to_word = mapper.id_to_word
tag_to_id = mapper.tag_to_id
id_to_tag = mapper.id_to_tag

# Save/load mappings
mapper.save_mappings("vocabulary.json")
mapper.load_mappings("vocabulary.json")
```

### Statistics and Analysis

```python
# Get comprehensive statistics
stats = mapper.get_statistics()

# Access different types of statistics
basic_stats = stats['basic_stats']      # Dataset size, unique counts
tag_distribution = stats['tag_distribution']  # Tag frequency
word_frequency = stats['word_frequency']      # Word frequency
sequence_stats = stats['sequence_stats']      # Sequence length stats
```

## Turkish Language Features

### POS Tag Mappings

The system includes mappings for Turkish POS tags:

```python
TURKISH_FEATURES['pos_mappings'] = {
    'AD-NOUN': 'NOUN',
    'SIFAT-ADJECTIVE': 'ADJ',
    'FIIL-VERB': 'VERB',
    'ZAMIR-PRON': 'PRON',
    # ... more mappings
}
```

### Morphological Analysis

Turkish-specific features include:
- Vowel harmony detection
- Agglutination patterns
- Case suffix analysis
- POS tag hierarchy

### BERT Tokenization

For BERT models, the system handles:
- Subword tokenization
- Word-to-subword alignment
- Special token handling
- Attention mask generation

## Performance Optimization

### Memory Management

```python
# Use memory-efficient processing
MODEL_CONFIG['memory_efficient'] = True

# Enable caching
MODEL_CONFIG['cache_features'] = True

# Use parallel processing
MODEL_CONFIG['use_parallel_processing'] = True
```

### Batch Processing

```python
# Process data in chunks
chunk_size = 10000
for chunk in pd.read_csv('data.csv', chunksize=chunk_size):
    # Process chunk
    pass
```

## Evaluation Setup

### Cross-Validation

```python
from sklearn.model_selection import cross_val_score

# Use the exported sklearn features
with open('sklearn_features.pkl', 'rb') as f:
    data = pickle.load(f)

X = data['X']
y = data['y']

# Cross-validation
scores = cross_val_score(model, X, y, cv=5)
```

### Benchmark Models

The integration creates benchmark models:
- Baseline random classifier
- Majority class classifier
- Traditional ML models
- BERT fine-tuning

### Evaluation Metrics

Supported metrics:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

## Troubleshooting

### Common Issues

1. **Memory Errors**
   - Use `memory_efficient=True`
   - Process data in smaller chunks
   - Increase system memory

2. **BERT Tokenization Issues**
   - Check model availability
   - Verify tokenizer compatibility
   - Handle unknown tokens properly

3. **Data Loading Errors**
   - Verify CSV format
   - Check file paths
   - Ensure proper encoding

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug output
mapper = TurkishModelMapper()
mapper.load_data()  # Will show detailed logs
```

## Examples

### Complete Training Pipeline

```python
from corpus_manipulator.model_integration import CorpusModelIntegration

# Run complete pipeline
integration = CorpusModelIntegration()
results = integration.run_full_pipeline(
    include_bert=True,
    include_traditional=True,
    test_size=0.2
)

# Train traditional ML model
from sklearn.ensemble import RandomForestClassifier
import pickle

with open('model_outputs/traditional_ml/sklearn_features.pkl', 'rb') as f:
    data = pickle.load(f)

model = RandomForestClassifier(n_estimators=100)
model.fit(data['X'], data['y'])

# Train BERT model
from transformers import AutoModelForTokenClassification, Trainer, TrainingArguments

# Load BERT dataset
with open('model_outputs/bert_models/huggingface/train.json', 'r') as f:
    train_data = json.load(f)

# Fine-tune BERT model
model = AutoModelForTokenClassification.from_pretrained(
    'dbmdz/bert-base-turkish-128k-cased',
    num_labels=len(data['label_to_id'])
)
```

### Custom Model Training

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# Load PyTorch dataset
train_data = torch.load('model_outputs/traditional_ml/pytorch/train.pt')

# Create data loader
train_loader = DataLoader(
    TensorDataset(
        train_data['input_ids'],
        train_data['labels']
    ),
    batch_size=32,
    shuffle=True
)

# Define model
class SimpleModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_classes):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.classifier = nn.Linear(hidden_dim, num_classes)
    
    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        return self.classifier(lstm_out)

# Train model
model = SimpleModel(vocab_size=10000, embedding_dim=100, hidden_dim=128, num_classes=16)
optimizer = torch.optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss()

for epoch in range(10):
    for batch in train_loader:
        inputs, labels = batch
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs.view(-1, outputs.size(-1)), labels.view(-1))
        loss.backward()
        optimizer.step()
```

## Best Practices

1. **Data Quality**: Ensure clean, well-formatted CSV data
2. **Vocabulary Size**: Balance between coverage and memory usage
3. **Sequence Length**: Choose appropriate max sequence length
4. **Evaluation**: Use proper train/validation/test splits
5. **Reproducibility**: Set random seeds for consistent results
6. **Monitoring**: Track training progress and metrics
7. **Version Control**: Save model configurations and mappings

## Next Steps

After creating your datasets:

1. **Train Models**: Use the exported datasets with your preferred framework
2. **Evaluate Performance**: Use the evaluation setup to compare models
3. **Fine-tune**: Adjust hyperparameters and retrain
4. **Deploy**: Export trained models for production use
5. **Monitor**: Track model performance on new data

For more information, see the individual module documentation and example scripts.