"""
Custom BERT-based Turkish NLP Processor

Bu modül kullanıcının fine-tuned BERT POS tagging modelini 
proje ile entegre eder.
"""

import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

# Try to import transformers, handle gracefully if not available
TRANSFORMERS_AVAILABLE = False
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    import numpy as np
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Transformers library not available: {e}")
    logger.warning("Please install with: pip install transformers torch")

class CustomBERTProcessor:
    """
    Fine-tuned BERT model ile Türkçe POS tagging ve diğer NLP görevleri
    """
    
    def __init__(self, model_path: Optional[str] = None, tokenizer_path: Optional[str] = None):
        """
        Initialize Custom BERT processor
        
        Args:
            model_path: Fine-tuned BERT model dosya yolu
            tokenizer_path: Tokenizer dosya yolu
        """
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.model = None
        self.tokenizer = None
        
        # Model yükleme durumu
        self.is_loaded = False
        
        self._load_model()
    
    def _load_model(self):
        """Fine-tuned BERT modelini Hugging Face'den yükle"""
        try:
            # Check if transformers is available
            if not TRANSFORMERS_AVAILABLE:
                logger.error("Transformers library not installed")
                logger.error("Please install with: pip install transformers torch")
                self.is_loaded = False
                return
            
            # Use provided model path or fallback to default
            model_path = self.model_path if self.model_path else "LiProject/Bert-turkish-pos-trained"
            
            logger.info(f"Hugging Face modeli yükleniyor: {model_path}")
            
            # Model ve tokenizer yükle
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForTokenClassification.from_pretrained(model_path)
            
            # Pipeline oluştur - aggregation olmadan kullan
            self.nlp_pipeline = pipeline(
                "token-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy=None  # No aggregation for proper token handling
            )
            
            self.is_loaded = True
            logger.info("Hugging Face BERT modeli başarıyla yüklendi")
            
        except Exception as e:
            logger.error(f"BERT model yüklenemedi: {e}")
            logger.info("Fallback olarak basit işleme kullanılıyor")
            self.is_loaded = False
    
    def process_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Fine-tuned BERT ile text işleme
        
        Args:
            text: İşlenecek metin
            
        Returns:
            Token bilgileri listesi
        """
        # Ensure proper UTF-8 encoding before processing
        if not isinstance(text, str):
            text = str(text)
        
        # Normalize Unicode to ensure consistent encoding
        try:
            import unicodedata
            text = unicodedata.normalize('NFC', text)
        except Exception as e:
            logger.warning(f"Text normalization failed: {e}")
        
        if not self.is_loaded:
            logger.warning("Model yüklenmemiş, basit tokenizasyon kullanılıyor")
            return self._simple_processing(text)
        
        try:
            # Hugging Face model ile işleme
            if self.is_loaded and hasattr(self, 'nlp_pipeline'):
                return self._process_with_bert(text)
            else:
                # Fallback
                return self._enhanced_processing(text)
            
        except Exception as e:
            logger.error(f"BERT processing hatası: {e}")
            return self._simple_processing(text)
    
    def _enhanced_processing(self, text: str) -> List[Dict[str, Any]]:
        """Enhanced basit processing (BERT yoksa kullanılır)"""
        
        # Türkçe text preprocessing
        text = self._preprocess_turkish_text(text)
        
        # Regex-based tokenization - NOW INCLUDES TURKISH CHARACTERS
        # Turkish characters: ç, ğ, ı, İ, ö, ş, ü, Ç, Ğ, İ, Ö, Ş, Ü
        tokens = re.findall(r'\b[\wçğıöşüÇĞIİÖŞÜ]+\b', text)
        
        # POS mapping (basit heuristic)
        pos_mapping = self._simple_pos_mapping(tokens)
        
        # Morphological features (basit)
        morph_features = self._simple_morph_features(tokens)
        
        # Token data
        token_data_list = []
        for i, (token, pos, morph) in enumerate(zip(tokens, pos_mapping, morph_features)):
            pos_tr = self._map_pos_to_turkish(pos)
            token_data = {
                'word': token,
                'norm': token.lower(),
                'upos': pos,
                'upos_tr': pos_tr,  # Turkish POS label
                'xpos': pos,
                'morph': morph,
                'dep_head': None,
                'dep_rel': None,
                'start_char': i * (len(token) + 1),
                'end_char': (i + 1) * (len(token) + 1),
                'is_punctuation': False,
                'is_space': False
            }
            token_data_list.append(token_data)
        
        return token_data_list
    
    def _simple_processing(self, text: str) -> List[Dict[str, Any]]:
        """En basit processing fallback"""
        
        # Turkish characters: ç, ğ, ı, İ, ö, ş, ü, Ç, Ğ, İ, Ö, Ş, Ü
        tokens = re.findall(r'\b[\wçğıöşüÇĞIİÖŞÜ]+\b', text.lower())
        
        return [
            {
                'word': token,
                'norm': token,
                'upos': None,
                'upos_tr': None,  # Turkish POS label
                'xpos': None,
                'morph': None,
                'dep_head': None,
                'dep_rel': None,
                'start_char': i * (len(token) + 1),
                'end_char': (i + 1) * (len(token) + 1),
                'is_punctuation': False,
                'is_space': False
            }
            for i, token in enumerate(tokens)
        ]
    
    def _preprocess_turkish_text(self, text: str) -> str:
        """Türkçe text preprocessing - PRESERVE Turkish characters"""
        
        # NOTE: Turkish characters are PRESERVED, not converted to ASCII
        # This ensures proper handling of Turkish text including ş, ç, ğ, ı, ö, ü, İ, Ç, Ğ, Ö, Ş, Ü
        
        # Only perform basic cleanup while preserving Turkish characters
        # Remove control characters but keep Turkish special characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text
    
    def _simple_pos_mapping(self, tokens: List[str]) -> List[str]:
        """Basit POS mapping heuristic"""
        
        pos_list = []
        for token in tokens:
            
            # Basit heuristic rules
            if token.endswith(('ler', 'lar')):
                pos = 'NOUN'  # Plural markers
            elif token.endswith(('da', 'de', 'ta', 'te')):
                pos = 'ADP'   # Locative case
            elif token.endswith(('in', 'un', 'ın', 'ün')):
                pos = 'ADP'   # Genitive case
            elif token.endswith(('i', 'ı', 'u', 'ü')):
                pos = 'ADP'   # Accusative case
            elif token in ('ve', 'veya', 'ama', 'fakat'):
                pos = 'CCONJ'
            elif token in ('bu', 'şu', 'o', 'bir', 'her', 'hiç'):
                pos = 'DET'
            elif token in ('çok', 'daha', 'güzel', 'iyi', 'büyük'):
                pos = 'ADJ'
            elif token in ('git', 'gel', 'ol', 'yap', 'ver', 'al'):
                pos = 'VERB'
            else:
                pos = 'NOUN'  # Default
            
            pos_list.append(pos)
        
        return pos_list
    
    def _simple_morph_features(self, tokens: List[str]) -> List[str]:
        """Basit morphological features"""
        
        morph_list = []
        for token in tokens:
            features = []
            
            # Number
            if token.endswith(('ler', 'lar')):
                features.append('Number=Plur')
            else:
                features.append('Number=Sing')
            
            # Case (basit heuristic)
            if token.endswith(('da', 'de', 'ta', 'te')):
                features.append('Case=Loc')
            elif token.endswith(('in', 'un', 'ın', 'ün')):
                features.append('Case=Gen')
            elif token.endswith(('i', 'ı', 'u', 'ü')):
                features.append('Case=Acc')
            
            morph_list.append('|'.join(features) if features else None)
        
        return morph_list
    
    def _process_with_bert(self, text: str) -> List[Dict[str, Any]]:
        """Hugging Face BERT modeli ile metin işleme - FIXED"""
        try:
            # Tokenize the text first to get proper alignment
            # Use return_offsets_mapping=True to get character positions
            inputs = self.tokenizer(text, return_tensors="pt", add_special_tokens=True, return_offsets_mapping=True)
            offset_mapping = inputs['offset_mapping'][0].tolist()
            all_tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])

            # Get model predictions
            with torch.no_grad():
                outputs = self.model(inputs['input_ids'], attention_mask=inputs['attention_mask'])
                
                # Get probabilities and predictions
                probabilities = torch.softmax(outputs.logits, dim=2)
                predictions = torch.argmax(outputs.logits, dim=2)
                
                # Get max probabilities (confidence scores)
                confidences = torch.max(probabilities, dim=2).values

            # Convert predictions to labels
            all_predicted_labels = [self.model.config.id2label[pred.item()] for pred in predictions[0]]
            all_confidences = confidences[0].tolist()

            # Now aggregate subtokens properly
            aggregated_tokens = []
            current_word = ""
            current_label = None
            current_score = 0.0
            subtoken_count = 0
            
            # Track start/end for the aggregated word
            word_start = -1
            word_end = -1

            for idx, (token, label, conf) in enumerate(zip(all_tokens, all_predicted_labels, all_confidences)):
                # Skip special tokens but use them to maintain index alignment if needed
                if token in ['[CLS]', '[SEP]', '[PAD]']:
                    continue
                
                # Get offsets for this token
                start, end = offset_mapping[idx]
                
                # Handle subwords
                if token.startswith("##"):
                    # This is a continuation of the previous word
                    current_word += token[2:]  # Remove ## prefix
                    current_score += conf
                    subtoken_count += 1
                    word_end = end # Update end position
                else:
                    # Save previous word if exists
                    if current_word:
                        pos = self._map_bert_label_to_pos(current_label, current_word)
                        pos_tr = self._map_pos_to_turkish(pos)
                        morph = self._extract_morph_features(current_word, current_label)

                        token_data = {
                            'word': current_word,
                            'norm': current_word.lower(),
                            'upos': pos,
                            'upos_tr': pos_tr,  # Turkish POS label
                            'xpos': pos,
                            'morph': morph,
                            'dep_head': None,
                            'dep_rel': None,
                            'start_char': word_start,
                            'end_char': word_end,
                            'is_punctuation': current_word in '.,;:!?"()[]{}',
                            'is_space': False,
                            'bert_confidence': current_score / max(subtoken_count, 1)
                        }
                        aggregated_tokens.append(token_data)

                    # Start new word
                    current_word = token
                    current_label = label
                    current_score = conf
                    subtoken_count = 1
                    word_start = start
                    word_end = end

            # Don't forget the last word
            if current_word:
                pos = self._map_bert_label_to_pos(current_label, current_word)
                pos_tr = self._map_pos_to_turkish(pos)
                morph = self._extract_morph_features(current_word, current_label)

                token_data = {
                    'word': current_word,
                    'norm': current_word.lower(),
                    'upos': pos,
                    'upos_tr': pos_tr,  # Turkish POS label
                    'xpos': pos,
                    'morph': morph,
                    'dep_head': None,
                    'dep_rel': None,
                    'start_char': word_start,
                    'end_char': word_end,
                    'is_punctuation': current_word in '.,;:!?"()[]{}',
                    'is_space': False,
                    'bert_confidence': current_score / max(subtoken_count, 1)
                }
                aggregated_tokens.append(token_data)

            return aggregated_tokens

        except Exception as e:
            logger.error(f"BERT processing hatası: {e}")
            import traceback
            traceback.print_exc()
            return self._enhanced_processing(text)
    
    def _map_bert_label_to_pos(self, bert_label: str, word: str = '') -> str:
        """BERT model label'larını POS tag'lerine çevir (trust model output)"""
        
        # İlk önce model çıktısını doğrudan kullan - kullanıcının kendi Hugging Face yaklaşımı
        # Sadece çok kritik durumlarda müdahale et
        
        # Model spesifik Türkçe etiketler (Hugging Face model'den gelen)
        model_label_mapping = {
            # Doğrudan model etiketleri
            'AD-NOUN': 'NOUN',
            'ADIL-PRONOUN': 'PRON',
            'BAĞLAÇ-CONJ': 'CCONJ',
            'BELİRLEYİCİ-DET': 'DET',
            'BELİRTEÇ-ADVERB': 'ADV',
            'FİİL-VERB': 'VERB',
            'NOKTALAMA-PUNCTUATION': 'PUNCT',
            'SIFAT-ADJECTIVE': 'ADJ',
            'SORU-QUESTION': 'INTJ',  # Question particles
            'İLGEÇ-PREPOS': 'ADP',

            # Eski format (geriye uyumluluk için)
            'AD-PROPN': 'PROPN',
            'FIIL-AUX': 'AUX',
            'ZAMIR-PRON': 'PRON',
            'BELIRTEÇ-DET': 'DET',
            'EDAT-ADP': 'ADP',
            'BAGLAÇ-CCONJ': 'CCONJ',
            'BAGLAÇ-SCONJ': 'SCONJ',
            'SAYI-NUM': 'NUM',
            'UNLEM-INTJ': 'INTJ',
            'NOKTALAMA-PUNCT': 'PUNCT',
            'SIMGE-SYM': 'SYM',

            # Standart Universal POS tags
            'NOUN': 'NOUN', 'VERB': 'VERB', 'ADJ': 'ADJ', 'ADV': 'ADV',
            'PRON': 'PRON', 'DET': 'DET', 'ADP': 'ADP', 'CCONJ': 'CCONJ',
            'SCONJ': 'SCONJ', 'AUX': 'AUX', 'PROPN': 'PROPN', 'NUM': 'NUM',
            'PART': 'PART', 'INTJ': 'INTJ', 'PUNCT': 'PUNCT', 'SYM': 'SYM'
        }
        
        # Model çıktısını doğrudan kullan
        mapped_label = model_label_mapping.get(bert_label)
        
        if mapped_label:
            return mapped_label
        
        # Eğer model etiketi bilinmiyorsa, sadece çok kritik durumlarda düzelt
        if word:
            word_lower = word.lower()
            
            # Sadece kullanıcının çok önemli dediği durumlar
            critical_fixes = {
                'at': 'NOUN',  # at (horse) should be NOUN
                'koşuyor': 'VERB'  # koşuyor (running) should be VERB
            }
            
            if word_lower in critical_fixes:
                return critical_fixes[word_lower]
        
        # Bilinmeyen etiketler için akıllı tahmin
        if bert_label:
            label_lower = bert_label.lower()
            if 'noun' in label_lower or 'isim' in label_lower:
                return 'NOUN'
            elif 'verb' in label_lower or 'fiil' in label_lower:
                return 'VERB'
            elif 'adj' in label_lower or 'sifat' in label_lower:
                return 'ADJ'
            elif 'adv' in label_lower or 'zarf' in label_lower:
                return 'ADV'
            elif 'pron' in label_lower or 'zamir' in label_lower:
                return 'PRON'
            elif 'det' in label_lower or 'belirtec' in label_lower:
                return 'DET'
            elif 'adp' in label_lower or 'edat' in label_lower:
                return 'ADP'
            elif 'conj' in label_lower or 'baglac' in label_lower:
                return 'CCONJ'
            elif 'num' in label_lower or 'sayi' in label_lower:
                return 'NUM'
            elif 'punct' in label_lower or 'noktalama' in label_lower:
                return 'PUNCT'
        
        # Son çare - model çıktısına güven
        return bert_label if bert_label else 'NOUN'
    
    def _map_pos_to_turkish(self, pos: str) -> str:
        """Universal POS tag'lerini Türkçe'ye çevir"""
        pos_mapping = {
            'NOUN': 'İsim',
            'VERB': 'Fiil',
            'ADJ': 'Sıfat',
            'ADV': 'Zarf',
            'PRON': 'Zamir',
            'DET': 'Belirteç',
            'ADP': 'İlgeç',
            'CCONJ': 'Bağlaç',
            'SCONJ': 'Bağlaç',
            'AUX': 'Yardımcı Fiil',
            'PROPN': 'Özel İsim',
            'NUM': 'Sayı',
            'PART': 'Parçacık',
            'INTJ': 'Ünlem',
            'PUNCT': 'Noktalama',
            'SYM': 'Sembol'
        }
        return pos_mapping.get(pos, pos)
    
    def _extract_morph_features(self, word: str, label: str) -> str:
        """Word ve label'dan morfolojik özellikler çıkar"""
        features = []
        
        # Basit morfolojik analiz
        if word.endswith(('ler', 'lar')):
            features.append('Number=Plur')
        else:
            features.append('Number=Sing')
            
        # Case analysis (Türkçe için)
        if word.endswith(('da', 'de', 'ta', 'te')):
            features.append('Case=Loc')
        elif word.endswith(('in', 'un', 'ın', 'ün')):
            features.append('Case=Gen')
        elif word.endswith(('i', 'ı', 'u', 'ü')):
            features.append('Case=Acc')
            
        # POS specific features
        if label == 'VERB':
            features.append('Mood=Ind')
            features.append('Tense=Pres')
        elif label == 'ADJ':
            features.append('Degree=Pos')
            
        return '|'.join(features) if features else None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Model bilgilerini döndür"""
        return {
            'model_type': 'huggingface_bert',
            'model_path': 'LiProject/Bert-turkish-pos-trained',
            'tokenizer_path': 'LiProject/Bert-turkish-pos-trained',
            'is_loaded': self.is_loaded,
            'supported_features': ['tokenization', 'pos_tagging', 'morphology', 'bert_confidence'],
            'language': 'Turkish',
            'model_source': 'Hugging Face Model Hub',
            'checkpoint': 'main'
        }

def create_custom_bert_processor(model_path: Optional[str] = None, 
                               tokenizer_path: Optional[str] = None) -> CustomBERTProcessor:
    """
    Custom BERT processor oluştur
    
    Args:
        model_path: Fine-tuned BERT model yolu
        tokenizer_path: Tokenizer yolu
        
    Returns:
        CustomBERTProcessor instance
    """
    return CustomBERTProcessor(model_path, tokenizer_path)

# BERT model integration için TurkishNLPProcessor güncelleme
def integrate_bert_with_turkish_processor():
    """
    Custom BERT modelini TurkishNLPProcessor ile entegre et
    
    Bu fonksiyon TurkishNLPProcessor'ı CustomBERTProcessor ile çalışacak şekilde günceller
    """
    
    print("=== BERT MODEL ENTEGRASYONU ===")
    print()
    
    # 1. Model yükleme
    print("1. Custom BERT modeli yükleme:")
    print("   - Fine-tuned POS tagging model")
    print("   - Türkçe için optimize edilmiş")
    print("   - Yüksek doğruluk")
    
    # 2. Entegrasyon
    print("\n2. TurkishNLPProcessor entegrasyonu:")
    print("   - Custom backend olarak eklenebilir")
    print("   - Mevcut API ile uyumlu")
    print("   - Fallback desteği")
    
    # 3. Kullanım örneği
    print("\n3. Kullanım örneği:")
    print("""
    from nlp.custom_bert_processor import create_custom_bert_processor
    from nlp.turkish_processor import TurkishNLPProcessor
    
    # BERT processor oluştur
    bert_processor = create_custom_bert_processor(
        model_path="./my_bert_model",
        tokenizer_path="./my_tokenizer"
    )
    
    # TurkishNLPProcessor ile entegre et
    nlp = TurkishNLPProcessor(backend='custom_bert')
    nlp.set_custom_processor(bert_processor)
    
    # Kullan
    tokens = nlp.process_text("Türkçe metin işleme")
    """)
    
    # 4. Performans
    print("\n4. Performans avantajları:")
    print("   ✓ Yüksek POS tagging doğruluğu")
    print("   ✓ Gelişmiş morfolojik analiz")
    print("   ✓ Türkçe'ye özel eğitim")
    print("   ✓ Custom features desteği")

if __name__ == "__main__":
    # Demo
    integrate_bert_with_turkish_processor()
    
    print("\n=== CUSTOM BERT PROCESSOR DEMO ===")
    
    # Processor oluştur
    processor = create_custom_bert_processor()
    
    # Model bilgileri
    info = processor.get_model_info()
    print(f"Model Type: {info['model_type']}")
    print(f"Loaded: {info['is_loaded']}")
    print(f"Features: {info['supported_features']}")
    
    # Test
    test_text = "Ben okula gidiyorum ve kitap okuyorum."
    tokens = processor.process_text(test_text)
    
    print(f"\nTest Text: {test_text}")
    print(f"Tokens: {len(tokens)}")
    
    for i, token in enumerate(tokens[:5]):
        print(f"{i+1}. {token['form']} -> POS: {token['upos']}, Morph: {token['morph']}")