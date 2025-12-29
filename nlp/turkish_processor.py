"""
Turkish NLP Processor

This module provides NLP processing capabilities for Turkish text using
multiple backends with fallback strategies.
"""

import re
import logging
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import sys
import os

# Add the nlp module to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TurkishNLPProcessor:
    """Main NLP processor with fallback strategies for Turkish text"""
    
    def __init__(self, backend='spacy', model_name='tr_core_news_sm', bert_model_path=None):
        """
        Initialize NLP processor
        
        Args:
            backend: 'spacy', 'stanza', 'simple', 'custom_bert', or 'fallback'
            model_name: Name of the model to load
            bert_model_path: Path to custom BERT model (for 'custom_bert' backend)
        """
        self.backend = backend
        self.model_name = model_name
        self.bert_model_path = bert_model_path
        self.nlp = None
        self.custom_bert_processor = None
        self.available_backends = []
        
        # Initialize processor
        self._initialize_backend()
        
    def _initialize_backend(self):
        """Initialize the selected NLP backend"""
        if self.backend == 'spacy':
            self._init_spacy()
        elif self.backend == 'stanza':
            self._init_stanza()
        elif self.backend == 'simple':
            self._init_simple()
        elif self.backend == 'custom_bert':
            self._init_custom_bert()
        else:
            # Try to find best available backend
            self._auto_detect_backend()
    
    def _init_spacy(self):
        """Initialize spaCy Turkish model"""
        try:
            import spacy
            self.nlp = spacy.load(self.model_name)
            self.available_backends.append('spacy')
            logger.info(f"spaCy Turkish model '{self.model_name}' loaded successfully")
        except ImportError:
            logger.warning("spaCy not installed")
            self._auto_detect_backend()
        except OSError:
            logger.warning(f"spaCy model '{self.model_name}' not found")
            self._auto_detect_backend()
    
    def _init_stanza(self):
        """Initialize Stanza Turkish model"""
        try:
            import stanza
            stanza.download('tr')
            self.nlp = stanza.Pipeline('tr', processors='tokenize,pos,lemma,depparse')
            self.available_backends.append('stanza')
            logger.info("Stanza Turkish model loaded successfully")
        except ImportError:
            logger.warning("Stanza not installed")
            self._auto_detect_backend()
        except Exception as e:
            logger.warning(f"Error loading Stanza model: {e}")
            self._auto_detect_backend()
    
    def _init_simple(self):
        """Initialize simple tokenizer as fallback"""
        self.available_backends.append('simple')
        logger.info("Simple Turkish tokenizer initialized")
    
    def _init_custom_bert(self):
        """Initialize custom BERT model from Hugging Face"""
        try:
            from custom_bert_processor import create_custom_bert_processor
            
            # Create BERT processor with Hugging Face model
            self.custom_bert_processor = create_custom_bert_processor(
                model_path=self.bert_model_path,
                tokenizer_path=self.bert_model_path
            )
            
            self.available_backends.append('custom_bert')
            logger.info("Custom BERT processor initialized with Hugging Face model")
            
        except ImportError as e:
            logger.warning(f"Custom BERT processor not available: {e}")
            self._auto_detect_backend()
        except Exception as e:
            logger.warning(f"Error loading custom BERT model: {e}")
            self._auto_detect_backend()
    
    def _auto_detect_backend(self):
        """Automatically detect the best available backend"""
        backends = ['spacy', 'stanza', 'simple']
        
        for backend in backends:
            try:
                self.backend = backend
                if backend == 'spacy':
                    import spacy
                    self.nlp = spacy.load(self.model_name)
                    self.available_backends.append('spacy')
                    logger.info(f"Auto-selected spaCy as backend")
                    return
                elif backend == 'stanza':
                    import stanza
                    stanza.download('tr')
                    self.nlp = stanza.Pipeline('tr', processors='tokenize,pos,lemma,depparse')
                    self.available_backends.append('stanza')
                    logger.info("Auto-selected Stanza as backend")
                    return
                elif backend == 'simple':
                    self.available_backends.append('simple')
                    logger.info("Auto-selected simple tokenizer as backend")
                    return
            except:
                continue
        
        logger.error("No NLP backend available")
        raise RuntimeError("No NLP backend available. Install spaCy or Stanza.")
    
    def process_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Process a text and return token information
        
        Args:
            text: Input text to process
            
        Returns:
            List of token dictionaries with linguistic annotations
        """
        if not text.strip():
            return []
        
        tokens = []
        
        if self.backend == 'spacy':
            tokens = self._process_with_spacy(text)
        elif self.backend == 'stanza':
            tokens = self._process_with_stanza(text)
        elif self.backend == 'custom_bert':
            tokens = self._process_with_custom_bert(text)
        else:
            tokens = self._process_simple(text)
        
        return tokens
    
    def _process_with_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Process text using spaCy"""
        doc = self.nlp(text)
        tokens = []
        
        for token in doc:
            if token.is_space:
                continue
                
            token_data = {
                'word': token.text,
                'norm': token.lemma_.lower() if token.lemma_ else token.text.lower(),
                'upos': token.pos_,
                'upos_tr': self._map_pos_to_turkish(token.pos_),
                'xpos': token.tag_,
                'morph': self._format_morph_features(token.morph),
                'dep_head': token.head.i if token.head.i != token.i else None,
                'dep_rel': token.dep_ if token.dep_ != 'ROOT' else 'root',
                'start_char': token.idx,
                'end_char': token.idx + len(token.text),
                'is_punctuation': token.is_punct,
                'is_space': token.is_space
            }
            tokens.append(token_data)
        
        return tokens
    
    def _process_with_stanza(self, text: str) -> List[Dict[str, Any]]:
        """Process text using Stanza"""
        doc = self.nlp(text)
        tokens = []
        
        for sent in doc.sentences:
            for word in sent.words:
                token_data = {
                    'word': word.text,
                    'norm': word.lemma.lower() if word.lemma else word.text.lower(),
                    'upos': word.upos,
                    'upos_tr': self._map_pos_to_turkish(word.upos),
                    'xpos': word.xpos,
                    'morph': self._format_stanza_morph(word.feats),
                    'dep_head': word.head if word.head != 0 else None,
                    'dep_rel': word.deprel if word.deprel != 'root' else 'root',
                    'start_char': word.start_char,
                    'end_char': word.end_char,
                    'is_punctuation': word.text in '.,;:!?"()[]{}',
                    'is_space': False
                }
                tokens.append(token_data)
        
        return tokens
    
    def _process_simple(self, text: str) -> List[Dict[str, Any]]:
        """Process text using simple tokenization"""
        # Simple Turkish text normalization
        text = self._normalize_turkish_text(text)
        
        # Basic tokenization using regex - NOW INCLUDES TURKISH CHARACTERS
        # Turkish characters: ç, ğ, ı, İ, ö, ş, ü, Ç, Ğ, İ, Ö, Ş, Ü
        tokens = re.findall(r'\b[\wçğıöşüÇĞIİÖŞÜ]+\b', text)
        
        token_data_list = []
        for i, token in enumerate(tokens):
            token_data = {
                'word': token,
                'norm': token.lower(),
                'upos': None,  # No POS tagging
                'upos_tr': None,  # No Turkish POS tagging
                'xpos': None,
                'morph': None,  # No morphology
                'dep_head': None,  # No dependency parsing
                'dep_rel': None,
                'start_char': i * (len(token) + 1),  # Rough estimation
                'end_char': (i + 1) * (len(token) + 1),
                'is_punctuation': False,
                'is_space': False
            }
            token_data_list.append(token_data)
        
        return token_data_list
    
    def _process_with_custom_bert(self, text: str) -> List[Dict[str, Any]]:
        """Process text using custom BERT model"""
        if self.custom_bert_processor is None:
            logger.warning("Custom BERT processor not available")
            return self._process_simple(text)
        
        try:
            tokens = self.custom_bert_processor.process_text(text)
            logger.info(f"Custom BERT processed {len(tokens)} tokens")
            return tokens
        except Exception as e:
            logger.error(f"Custom BERT processing error: {e}")
            return self._process_simple(text)
    
    def _normalize_turkish_text(self, text: str) -> str:
        """Basic Turkish text normalization - PRESERVE Turkish characters"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # NOTE: Turkish characters are PRESERVED, not converted to ASCII
        # This ensures proper handling of Turkish text including ş, ç, ğ, ı, ö, ü, İ, Ç, Ğ, Ö, Ş, Ü
        
        # Only perform basic cleanup while preserving Turkish characters
        # Remove control characters but keep Turkish special characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text
    
    def _format_stanza_morph(self, feats: str) -> str:
        """Format Stanza morphological features"""
        if not feats:
            return None
        
        # Stanza features are already in "Key=Value|Key=Value" format
        return feats

    def _format_morph_features(self, morph) -> str:
        """Format spaCy morphological features"""
        if not morph:
            return None
        
        features = []
        for key, value in morph:
            features.append(f"{key}={value}")
        
        return "|".join(features) if features else None
    
    def _map_pos_to_turkish(self, upos: str) -> str:
        """
        Map Universal POS tags to Turkish POS tag names
        
        Args:
            upos: Universal POS tag (NOUN, VERB, ADJ, etc.)
            
        Returns:
            Turkish POS tag name
        """
        pos_mapping = {
            'NOUN': 'İsim',
            'VERB': 'Fiil',
            'ADJ': 'Sıfat',
            'ADV': 'Zarf',
            'PRON': 'Zamirler',
            'DET': 'Belirteç',
            'ADP': 'Edat',
            'CONJ': 'Bağlaç',
            'CCONJ': 'Bağlaç',
            'SCONJ': 'Bağlaç',
            'PART': 'Ek',
            'INTJ': 'Ünlem',
            'NUM': 'Sayı',
            'PROPN': 'Özel İsim',
            'AUX': 'Yardımcı Fiil',
            'PUNCT': 'Noktalama',
            'SYM': 'Sembol',
            'X': 'Bilinmeyen'
        }
        
        return pos_mapping.get(upos, upos)
    
    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if self.backend == 'spacy':
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        elif self.backend == 'stanza':
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sentences if sent.text.strip()]
        else:
            # Simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [sent.strip() for sent in sentences if sent.strip()]
    
    def get_processing_info(self) -> Dict[str, Any]:
        """Get information about the current processing setup"""
        info = {
            'backend': self.backend,
            'available_backends': self.available_backends,
            'model_name': self.model_name,
            'features_available': {
                'tokenization': True,
                'pos_tagging': self.backend in ['spacy', 'stanza', 'custom_bert'],
                'lemmatization': self.backend in ['spacy', 'stanza', 'custom_bert'],
                'morphology': self.backend in ['spacy', 'stanza', 'custom_bert'],
                'dependency_parsing': self.backend in ['spacy', 'stanza'],
                'bert_confidence': self.backend == 'custom_bert'
            }
        }
        
        # Add BERT-specific info if available
        if self.backend == 'custom_bert' and self.custom_bert_processor:
            bert_info = self.custom_bert_processor.get_model_info()
            info['bert_model_info'] = bert_info
        
        return info

# Factory function for easy processor creation
def create_turkish_processor(backend='auto', model_name='tr_core_news_sm', bert_model_path=None) -> TurkishNLPProcessor:
    """
    Create a Turkish NLP processor with automatic backend detection
    
    Args:
        backend: 'auto', 'spacy', 'stanza', 'simple', or 'custom_bert'
        model_name: spaCy model name (ignored for other backends)
        bert_model_path: Path to custom BERT model (for 'custom_bert' backend)
        
    Returns:
        Configured TurkishNLPProcessor instance
    """
    if backend == 'auto':
        return TurkishNLPProcessor()
    else:
        return TurkishNLPProcessor(backend=backend, model_name=model_name, bert_model_path=bert_model_path)

# Example usage
if __name__ == "__main__":
    # Test the processor
    processor = create_turkish_processor('auto')
    
    # Get processing info
    info = processor.get_processing_info()
    print("=== PROCESSOR INFO ===")
    print(f"Backend: {info['backend']}")
    print(f"Available backends: {info['available_backends']}")
    print(f"Features: {info['features_available']}")
    
    # Test with sample text
    sample_text = "Bu bir test cümlesidir. Türkçe dil işleme için kullanılır."
    print(f"\n=== PROCESSING SAMPLE ===")
    print(f"Input: {sample_text}")
    
    tokens = processor.process_text(sample_text)
    print(f"Found {len(tokens)} tokens")
    
    # Show first few tokens
    for i, token in enumerate(tokens[:5]):
        print(f"{i+1}. {token['word']} -> norm: {token['norm']}, pos: {token['upos']}, tr_pos: {token.get('upos_tr', 'N/A')}")
    
    print("\n=== SENTENCE SPLITTING ===")
    sentences = processor.split_sentences(sample_text)
    print(f"Found {len(sentences)} sentences")
    for i, sent in enumerate(sentences):
        print(f"{i+1}. {sent}")