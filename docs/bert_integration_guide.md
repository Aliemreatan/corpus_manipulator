# Hugging Face BERT Model Integration

Bu doküman yeni Hugging Face BERT modelinin nasıl kullanılacağını açıklar.

## Model Bilgileri

- **Model**: `Sarpyy/LiSyntaxDeneme` (checkpoint-3375)
- **Kaynak**: Hugging Face Model Hub
- **Dil**: Türkçe
- **Görev**: Token Classification (POS Tagging)

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

Gerekli paketler:
- transformers>=4.30.0
- torch>=2.0.0
- tokenizers>=0.13.0
- numpy>=1.24.0
- pandas>=2.0.0

## Kullanım

### 1. Doğrudan BERT Processor Kullanımı

```python
from nlp.custom_bert_processor import create_custom_bert_processor

# BERT processor oluştur
bert_processor = create_custom_bert_processor()

# Model bilgilerini al
info = bert_processor.get_model_info()
print(f"Model loaded: {info['is_loaded']}")
print(f"Model path: {info['model_path']}")

# Metin işle
text = "Ben okula gidiyorum ve kitap okuyorum."
tokens = bert_processor.process_text(text)

# Sonuçları göster
for token in tokens:
    print(f"{token['form']} -> POS: {token['upos']}, Morph: {token['morph']}")
```

### 2. TurkishNLPProcessor ile Entegrasyon

```python
from nlp.turkish_processor import create_turkish_processor

# BERT backend ile Turkish processor oluştur
nlp = create_turkish_processor(backend='custom_bert')

# İşlem bilgilerini al
info = nlp.get_processing_info()
print(f"Backend: {info['backend']}")
print(f"Features: {info['features_available']}")

# Metin işle
text = "Türkçe dil işleme için yeni BERT modelini test ediyoruz."
tokens = nlp.process_text(text)

# Sonuçları göster
for token in tokens:
    confidence = token.get('bert_confidence', 'N/A')
    print(f"{token['form']} -> POS: {token['upos']}, Confidence: {confidence}")
```

### 3. Diğer Backend'lerle Karşılaştırma

```python
from nlp.turkish_processor import create_turkish_processor

# Farklı backend'leri test et
backends = ['simple', 'spacy', 'stanza', 'custom_bert']
text = "Bu bir test cümlesidir."

for backend in backends:
    try:
        nlp = create_turkish_processor(backend=backend)
        tokens = nlp.process_text(text)
        print(f"{backend}: {len(tokens)} tokens")
    except Exception as e:
        print(f"{backend}: Error - {e}")
```

## Çıktı Formatı

Her token için aşağıdaki bilgiler döndürülür:

```python
{
    'form': 'kelime',           # Orijinal kelime
    'norm': 'kelime',           # Normalleştirilmiş hali
    'lemma': 'kelime',          # Lemma (kök)
    'upos': 'NOUN',            # Universal POS tag
    'xpos': 'NOUN',            # Language-specific POS tag
    'morph': 'Number=Sing',     # Morfolojik özellikler
    'dep_head': None,          # Dependency head
    'dep_rel': None,           # Dependency relation
    'start_char': 0,           # Başlangıç karakteri
    'end_char': 6,             # Bitiş karakteri
    'is_punctuation': False,   # Noktalama işareti mi?
    'is_space': False,         # Boşluk mu?
    'bert_confidence': 0.95    # BERT model güven skoru (sadece BERT backend)
}
```

## Özellikler

### Desteklenen Özellikler
- ✅ Tokenization
- ✅ POS Tagging (Universal Dependencies)
- ✅ Basit Morfolojik Analiz
- ✅ Confidence Scores
- ✅ Türkçe karakter desteği

### Sınırlamalar
- Dependency parsing mevcut değil
- Lemmatization basit heuristic tabanlı
- Morfolojik analiz sınırlı

## Hata Ayıklama

### Yaygın Sorunlar

1. **Model yüklenemiyor**
   - İnternet bağlantısı kontrol edin
   - Hugging Face erişimi kontrol edin
   - transformers ve torch paketlerinin doğru yüklendiğini kontrol edin

2. **Import hatası**
   ```python
   # Bu import hatası alıyorsanız:
   from nlp.custom_bert_processor import create_custom_bert_processor
   
   # Çözüm: Python path'ini ayarlayın
   import sys
   sys.path.append('/path/to/corpus_manipulator')
   ```

3. **Memory hatası**
   - Model büyük olabilir, daha küçük batch size kullanın
   - GPU memory'i kontrol edin

### Log Seviyeleri

```python
import logging
logging.basicConfig(level=logging.INFO)

# Şimdi detaylı log mesajları göreceksiniz
```

## Test Etme

Test script'ini çalıştırın:

```bash
cd corpus_manipulator
python test_bert_model.py
```

Bu script:
- Custom BERT processor'ı test eder
- TurkishNLPProcessor entegrasyonunu test eder
- Farklı backend'leri karşılaştırır

## Performans

### Hız
- İlk yükleme: 10-30 saniye (model download)
- Sonraki işlemler: ~100-500ms per sentence

### Doğruluk
- Model checkpoint-3375'te eğitilmiş
- Türkçe POS tagging için optimize edilmiş
- Confidence skorları ile güvenilirlik ölçümü

## Lisans ve Atıf

Bu model Hugging Face'den `Sarpyy/LiSyntaxDeneme` projesinden kullanılmaktadır. Model lisansını kontrol edin ve uygun atıf yapın.

## Güncelleme Geçmişi

- **v1.0**: Hugging Face BERT modeli entegre edildi
  - Model: Sarpyy/LiSyntaxDeneme (checkpoint-3375)
  - TurkishNLPProcessor desteği eklendi
  - Confidence skorları eklendi
  - Comprehensive test suite eklendi