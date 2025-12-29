# Corpus Data Manipulator - Kullanım Kılavuzu

## 🚀 Hızlı Başlangıç

### 1. Temel Kurulum
```bash
# Proje dizinine gidin
cd corpus_manipulator

# Gereksinimleri yükleyin (opsiyonel, temel işlevsellik için gerekli değil)
pip install -r requirements.txt

# Basit demo çalıştırın (güvenli)
py demo_fixed.py
```

### 2. İlk Kullanım

#### A) Python'da Kullanım
```python
import sys
sys.path.append('.')

# Temel bileşenler
from database.schema import CorpusDatabase
from nlp.turkish_processor import TurkishNLPProcessor
from ingestion.corpus_ingestor import CorpusIngestor
from query.corpus_query import CorpusQuery

# Veritabanı oluştur
db = CorpusDatabase("my_corpus.db")
db.connect()
db.create_schema()

# NLP processor oluştur
nlp = TurkishNLPProcessor(backend='simple')

# Corpus ingestor oluştur
ingestor = CorpusIngestor("my_corpus.db", nlp_backend='simple')

# Metin dosyalarını içeri aktar
ingestor.ingest_directory("./sample_turkish_corpus")

# Sorgu yap
query = CorpusQuery("my_corpus.db")
stats = query.get_processing_stats()

print(f"Toplam token: {stats['database_stats']['total_tokens']}")

# Temizlik
ingestor.close()
query.close()
db.close()
```

#### B) Basit Metin İşleme
```python
from nlp.turkish_processor import TurkishNLPProcessor

# NLP processor
nlp = TurkishNLPProcessor(backend='simple')

# Metin işle
text = "Bu bir test cümlesidir. Türkçe dil işleme için kullanılır."
tokens = nlp.process_text(text)

print(f"Token sayısı: {len(tokens)}")
for token in tokens[:5]:
    print(f"{token['form']} -> norm: {token['norm']}")
```

## 📊 Mevcut Özellikler

### ✅ Çalışan Özellikler
- **Veritabanı**: SQLite + FTS5 tabanlı depolama
- **Tokenizasyon**: Basit regex-based tokenizasyon
- **Frekans Analizi**: Kelime frekans listeleri
- **KWIC**: Bağlamlı arama (temel seviye)
- **Collocation**: PMI, log-likelihood hesaplamaları
- **Batch Processing**: Büyük dosya desteği
- **Hata Toleransı**: Fallback sistemleri

### ⚠️ Kısıtlı Özellikler (spaCy/Stanza gerekli)
- **POS Tagging**: spaCy/Stanza kuruluysa aktif
- **Lemma**: spaCy/Stanza kuruluysa aktif  
- **Dependency Parsing**: spaCy/Stanza kuruluysa aktif
- **Gelişmiş Morphology**: spaCy/Stanza kuruluysa aktif

## 🔧 Kurulum Seçenekleri

### Seçenek 1: Temel Sistem (Önerilen)
```bash
# Sadece temel özellikler
pip install numpy pandas regex tqdm

# Demo çalıştır
py demo_fixed.py
```

### Seçenek 2: spaCy ile (Önerilen)
```bash
# Python 3.13 veya altı kullanın (Python 3.14'te sorun var)
pip install spacy==3.7.4
python -m spacy download tr_core_news_sm

# Test
python -c "import spacy; nlp = spacy.load('tr_core_news_sm'); print('spaCy çalışıyor')"
```

### Seçenek 3: Stanza ile
```bash
# Stanza kurulum
pip install stanza
python -m stanza.download('tr')

# Test
python -c "import stanza; nlp = stanza.Pipeline('tr'); print('Stanza çalışıyor')"
```

### Seçenek 4: BERT Modeli ile
```bash
# PyTorch ve Transformers
pip install torch transformers

# Kendi BERT modelinizi ekleyin
# models/ klasörüne koyun
```

## 🎯 Örnek Kullanım Senaryoları

### Senaryo 1: Akademik Araştırma
```python
# Yüksek doğruluk gerektiren çalışmalar
from corpus_manipulator.query import CorpusQuery

query = CorpusQuery("research_corpus.db")

# Frekans analizi
frequencies = query.frequency_list(word_type='lemma', limit=100)

# Collocation analizi
collocations = query.collocation_analysis("demokrasi", measure='pmi')

# KWIC arama
kwic = query.kwic_concordance("anayasa", window_size=5)

print(f"En sık kelimeler: {frequencies[:10]}")
print(f"Anayasa collocations: {collocations[:5]}")
```

### Senaryo 2: Production Sistem
```python
# Hızlı ve güvenilir sistem
from ingestion.corpus_ingestor import CorpusIngestor

# Büyük corpus işleme
ingestor = CorpusIngestor("production.db", nlp_backend='simple')

# Batch processing
stats = ingestor.ingest_directory(
    "./large_corpus", 
    file_pattern="*.txt",
    max_files=1000,
    batch_size=5000
)

print(f"İşlenen: {stats['documents_processed']} dosya")
print(f"Toplam: {stats['tokens_processed']} token")
```

### Senaryo 3: Kelime Analizi
```python
from query.corpus_query import CorpusQuery

query = CorpusQuery("analysis.db")

# Word sketch
sketch = query.word_sketch("ev")

print("Ev kelimesi için dependency relations:")
for relation, words in sketch.items():
    print(f"  {relation}: {len(words)} bağlantı")
    
# Belirli relation
amod_relations = query.word_sketch("ev", relation_type="amod")
print(f"Adjectival modifiers: {amod_relations}")
```

## 🛠️ Sorun Giderme

### Yaygın Hatalar

#### 1. Python 3.14 spaCy sorunu
```bash
# Çözüm: Python 3.13 veya altını kullanın
# Veya simple backend kullanın

from nlp.turkish_processor import TurkishNLPProcessor
nlp = TurkishNLPProcessor(backend='simple')
```

#### 2. Import hataları
```bash
# Çözüm: PYTHONPATH ekleyin
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Veya sys.path kullanın
import sys
sys.path.append('.')
```

#### 3. Encoding hataları
```python
# Türkçe karakterler için UTF-8 kullanın
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()
```

#### 4. Bellek sorunları
```python
# Büyük dosyalar için batch size düşürün
ingestor.ingest_directory("./corpus", batch_size=1000)

# Veya dosyaları tek tek işleyin
for file_path in Path("./corpus").glob("*.txt"):
    ingestor.ingest_file(file_path)
```

## 📈 Performans Optimizasyonu

### Hızlı İşleme
```python
# Basit backend kullanın
nlp = TurkishNLPProcessor(backend='simple')

# Batch processing
ingestor = CorpusIngestor("fast.db", nlp_backend='simple')
stats = ingestor.ingest_directory("./corpus", batch_size=10000)
```

### Yüksek Doğruluk
```python
# spaCy kullanın (Python 3.13'te)
nlp = TurkishNLPProcessor(backend='spacy', model_name='tr_core_news_lg')

# Veya BERT modeli
from nlp.custom_bert_processor import create_custom_bert_processor
bert = create_custom_bert_processor("./my_bert_model")
```

## 📚 Ek Kaynaklar

### Dosya Yapısı
```
corpus_manipulator/
├── demo_fixed.py           # Çalışan demo (güvenli)
├── demo.py                # Ana demo (spaCy gerekli)
├── README.md              # Kapsamlı dokümantasyon
├── database/              # Veritabanı modülleri
├── nlp/                   # NLP işleme
├── ingestion/             # Corpus import
├── query/                 # Sorgu ve analiz
└── docs/                  # Dokümantasyon
```

### API Referansı
- `CorpusDatabase`: Veritabanı yönetimi
- `TurkishNLPProcessor`: NLP işleme
- `CorpusIngestor`: Corpus import
- `CorpusQuery`: Sorgu ve analiz
- `CustomBERTProcessor`: BERT model desteği

### Test Verileri
- `sample_turkish_corpus/`: Demo metinler
- `demo_simple.db`: Demo veritabanı

## 💡 İpuçları

1. **Başlangıç için**: `demo_fixed.py` çalıştırın
2. **spaCy kurulumu**: Python 3.13 kullanın
3. **Büyük corpuslar**: Batch size optimize edin
4. **Hata durumunda**: Simple backend fallback
5. **BERT modeli**: Kendi fine-tuned modelinizi kullanın

**Sistem production-ready ve tüm temel özellikler çalışıyor!**