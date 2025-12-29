# Türkçe NLP Araçları Değerlendirmesi

## Araçlar ve Özellikler

### 1. spaCy Türkçe Modeli
**Önerilen Ana Seçenek**

#### Artıları:
- ✅ Hızlı performans (Cython tabanlı)
- ✅ Kolay kurulum ve kullanım
- ✅ İyi Türkçe dil desteği (`tr_core_news_sm/lg/xl`)
- ✅ Tokenizasyon, POS tagging, lemma, dependency parsing
- ✅ Pipeline-based yaklaşım, esnek
- ✅ Production-ready, industrial scale

#### Eksileri:
- ❌ Büyük modeller diskte yer kaplar (lg: ~500MB, xl: ~1GB)
- ❌ Dependency parsing kalitesi Stanza kadar iyi değil
- ❌ Gelişmiş morfolojik özellikler sınırlı

#### Kurulum:
```bash
pip install spacy
python -m spacy download tr_core_news_sm  # Küçük model
# veya
python -m spacy download tr_core_news_lg  # Büyük model
```

### 2. Stanza (Stanford NLP)
**Güçlü Dependency Parsing için Alternatif**

#### Artıları:
- ✅ Mükemmel dependency parsing
- ✅ Zengin morfolojik özellikler
- ✅ Daha doğru linguistic analysis
- ✅ Aktif geliştiriliyor

#### Eksileri:
- ❌ spaCy'den yavaş (Java tabanlı)
- ❌ Kurulum daha karmaşık
- ❌ Bellek kullanımı yüksek
- ❌ Pipeline setup daha zor

#### Kurulum:
```bash
pip install stanza
python -m stanza.download('tr')
```

### 3. Zemberek (Türkçe Özel)
**Fallback ve Morfolojik Analiz için**

#### Artıları:
- ✅ Türkçe'ye özel optimize edilmiş
- ✅ Güçlü morfolojik analiz
- ✅ Eklemeli dil özellikleri için tasarlanmış
- ✅ Açık kaynak

#### Eksileri:
- ❌ Sadece morfolojik analiz
- ❌ POS tagging ve dependency parsing yok
- ❌ Eski Java tabanlı, entegrasyon zor

#### Kurulum:
```bash
# Zeyrek wrapper (Python)
pip install zeyrek
```

## Karşılaştırma Matrisi

| Özellik | spaCy | Stanza | Zemberek |
|---------|-------|--------|----------|
| **Hız** | 🟢 Çok Hızlı | 🟡 Orta | 🟡 Orta |
| **Kurulum Kolaylığı** | 🟢 Kolay | 🟡 Orta | 🔴 Zor |
| **Tokenizasyon** | 🟢 İyi | 🟢 İyi | 🟡 Temel |
| **POS Tagging** | 🟢 İyi | 🟢 İyi | 🔴 Yok |
| **Lemma** | 🟢 İyi | 🟢 İyi | 🟢 Mükemmel |
| **Dependency Parsing** | 🟡 Orta | 🟢 Mükemmel | 🔴 Yok |
| **Morphology** | 🟡 Orta | 🟢 İyi | 🟢 Mükemmel |
| **Bellek Kullanımı** | 🟢 Az | 🔴 Yüksek | 🟡 Orta |
| **Production Ready** | 🟢 Evet | 🟡 Evet | 🔴 Hayır |

## Önerilen Yaklaşım

### MVP (Minimum Viable Product) için:
**spaCy Türkçe Modeli** (`tr_core_news_sm`)
- ✅ Hızlı başlangıç
- ✅ Tüm temel özellikler mevcut
- ✅ Performans odaklı
- ✅ Kolay entegrasyon

### Gelişmiş Özellikler için:
**spaCy + Zemberek Kombinasyonu**
- spaCy: Tokenizasyon, POS, temel lemma
- Zemberek: Gelişmiş morfolojik analiz

### Maksimum Doğruluk için:
**Stanza Türkçe**
- En iyi dependency parsing
- En zengin linguistic features
- Research odaklı projeler için

## Fallback Stratejileri

### Durum 1: spaCy mevcut değil
```python
# Basit regex-based tokenizasyon
import re

def simple_tokenize(text):
    tokens = re.findall(r'\b\w+\b', text.lower())
    return [(token, token, None, None) for token in tokens]  # (form, norm, lemma, pos)
```

### Durum 2: Hiçbir NLP aracı yok
```python
# Sadece yüzey form analizi
def surface_only_analysis(tokens):
    return [(token, token.lower(), token.lower(), None) for token in tokens]
```

### Durum 3: Bellek kısıtlı
```python
# Batch processing ile küçük parçalar halinde
def process_in_batches(text, batch_size=1000):
    sentences = text.split('.')
    # Her batch'i ayrı işle
```

## Performance Optimizasyonları

### İndeksleme:
```sql
-- En önemli indeksler
CREATE INDEX idx_tokens_norm ON tokens(norm);
CREATE INDEX idx_tokens_lemma ON tokens(lemma);
CREATE INDEX idx_tokens_upos ON tokens(upos);
CREATE INDEX idx_tokens_lemmapos ON tokens(lemma, upos);
```

### Batch Processing:
```python
# Büyük dosyalar için
def batch_insert_tokens(tokens_batch, batch_size=10000):
    # 10K token'lık batchler halinde insert
    pass
```

### FTS5 Full-Text Search:
```sql
-- KWIC için hızlı arama
SELECT * FROM tokens_fts WHERE tokens_fts MATCH 'kelime';
```

## Sonuç

**Önerilen Stack:**
1. **spaCy** (`tr_core_news_sm`) - Ana NLP işleme
2. **SQLite + FTS5** - Veri depolama ve arama
3. **Fallback sistemleri** - Hata durumları için

Bu kombinasyon en iyi performans/doğruluk dengesi sunuyor ve production-ready.