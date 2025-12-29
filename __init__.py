"""
Corpus Data Manipulator - Ana API Modülü

Türkçe metin korpusları için Sketch Engine benzeri analiz aracı.

Özellikler:
- Büyük Türkçe metin korpuslarını içeri alma
- Türkçe dilsel anotasyon (tokenizasyon, lemma, POS, dependency)
- Hızlı sorgu ve analiz (KWIC, frekans, collocation, word sketch)

Kullanım:
    from corpus_manipulator import CorpusManipulator
    
    # Korpus oluştur
    corpus = CorpusManipulator("corpus.db")
    
    # Korpus içeri aktar
    corpus.ingest_directory("./text_files")
    
    # KWIC arama
    results = corpus.kwic_search("ev", window_size=5)
    
    # Frekans analizi
    freq = corpus.frequency_list(word_type="lemma")
    
    # Collocation analizi
    colloc = corpus.collocation_analysis("ev")
    
    # Word sketch
    sketch = corpus.word_sketch("ev")
"""

from nlp.turkish_processor import TurkishNLPProcessor, create_turkish_processor
from database.schema import CorpusDatabase, create_sample_database
from ingestion.corpus_ingestor import CorpusIngestor, ingest_corpus
from query.corpus_query import CorpusQuery, kwic_search, frequency_analysis, collocation_analysis

__version__ = "1.0.0"
__author__ = "Corpus Data Manipulator Team"

class CorpusManipulator:
    """
    Ana sınıf - tüm corpus işlevselliğini birleştirir
    """
    
    def __init__(self, db_path: str = "corpus.db", nlp_backend: str = 'auto'):
        """
        Corpus Manipulator'ı başlat
        
        Args:
            db_path: Veritabanı dosya yolu
            nlp_backend: NLP backend ('auto', 'spacy', 'stanza', 'simple')
        """
        self.db_path = db_path
        self.nlp_backend = nlp_backend
        
        # Alt bileşenleri başlat
        self.nlp = TurkishNLPProcessor(backend=nlp_backend)
        self.db = CorpusDatabase(db_path)
        self.db.connect()
        
        # Tabloları oluştur
        self.db.create_schema()
        
    # Ingestion methods
    def ingest_file(self, file_path: str) -> dict:
        """Tek dosya içeri aktar"""
        ingestor = CorpusIngestor(self.db_path, self.nlp_backend)
        try:
            ingestor.ingest_file(file_path)
            stats = ingestor.get_processing_stats()
            return stats
        finally:
            ingestor.close()
    
    def ingest_directory(self, directory_path: str, 
                        file_pattern: str = "*.txt",
                        max_files: int = None) -> dict:
        """Dizindeki tüm dosyaları içeri aktar"""
        ingestor = CorpusIngestor(self.db_path, self.nlp_backend)
        try:
            stats = ingestor.ingest_directory(directory_path, file_pattern, max_files)
            return stats
        finally:
            ingestor.close()
    
    def ingest_corpus(self, corpus_path: str, **kwargs) -> dict:
        """Convenience method - ingest_directory ile aynı"""
        return self.ingest_directory(corpus_path, **kwargs)
    
    # Query methods
    def kwic_search(self, search_term: str, **kwargs) -> list:
        """KWIC arama"""
        query = CorpusQuery(self.db_path)
        try:
            return query.kwic_concordance(search_term, **kwargs)
        finally:
            query.close()
    
    def frequency_list(self, **kwargs) -> list:
        """Frekans listesi"""
        query = CorpusQuery(self.db_path)
        try:
            return query.frequency_list(**kwargs)
        finally:
            query.close()
    
    def frequency_list_lemmapos(self, **kwargs) -> list:
        """Lemma + POS frekans listesi"""
        query = CorpusQuery(self.db_path)
        try:
            return query.frequency_list_lemmapos(**kwargs)
        finally:
            query.close()
    
    def collocation_analysis(self, target_word: str, **kwargs) -> list:
        """Collocation analizi"""
        query = CorpusQuery(self.db_path)
        try:
            return query.collocation_analysis(target_word, **kwargs)
        finally:
            query.close()
    
    def word_sketch(self, lemma: str, **kwargs) -> dict:
        """Word sketch analizi"""
        query = CorpusQuery(self.db_path)
        try:
            return query.word_sketch(lemma, **kwargs)
        finally:
            query.close()
    
    # Utility methods
    def get_stats(self) -> dict:
        """Veritabanı istatistikleri"""
        query = CorpusQuery(self.db_path)
        try:
            return query.get_processing_stats()
        finally:
            query.close()
    
    def get_nlp_info(self) -> dict:
        """NLP processor bilgileri"""
        return self.nlp.get_processing_info()
    
    def search_by_form(self, form: str, **kwargs) -> list:
        """Form ile arama (norm ile aynı sonucu verir)"""
        return self.kwic_search(form, search_type='form', **kwargs)
    
    def search_by_lemma(self, lemma: str, **kwargs) -> list:
        """Lemma ile arama"""
        return self.kwic_search(lemma, search_type='lemma', **kwargs)
    
    def close(self):
        """Bağlantıyı kapat"""
        self.db.close()
    
    def __enter__(self):
        """Context manager desteği"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager çıkışı"""
        self.close()

# Convenience functions
def create_corpus(db_path: str = "corpus.db", nlp_backend: str = 'auto') -> CorpusManipulator:
    """Yeni corpus oluştur"""
    return CorpusManipulator(db_path, nlp_backend)

def quick_ingest(corpus_path: str, db_path: str = "corpus.db", **kwargs) -> dict:
    """Hızlı corpus içeri aktarma"""
    return ingest_corpus(corpus_path, db_path, **kwargs)

def quick_kwic(db_path: str, search_term: str, **kwargs) -> list:
    """Hızlı KWIC arama"""
    return kwic_search(db_path, search_term, **kwargs)

def quick_frequency(db_path: str, **kwargs) -> list:
    """Hızlı frekans analizi"""
    return frequency_analysis(db_path, **kwargs)

def quick_collocation(db_path: str, target_word: str, **kwargs) -> list:
    """Hızlı collocation analizi"""
    return collocation_analysis(db_path, target_word, **kwargs)

# Export all main classes and functions
__all__ = [
    'CorpusManipulator',
    'create_corpus', 
    'quick_ingest',
    'quick_kwic',
    'quick_frequency', 
    'quick_collocation',
    'TurkishNLPProcessor',
    'CorpusDatabase',
    'CorpusIngestor',
    'CorpusQuery'
]