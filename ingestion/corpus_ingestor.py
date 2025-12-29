"""
Corpus Ingestion Module

This module handles loading text files, processing them with NLP,
and storing the results in the database.
"""

import os
import sqlite3
import logging
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm
import hashlib

from database.schema import CorpusDatabase
from nlp.turkish_processor import TurkishNLPProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CorpusIngestor:
    """Handles corpus ingestion from text files to database"""
    
    def __init__(self, db_path: str = "corpus.db", nlp_backend: str = 'auto'):
        """
        Initialize the corpus ingestor
        
        Args:
            db_path: Path to SQLite database
            nlp_backend: NLP backend to use ('auto', 'spacy', 'stanza', 'simple')
        """
        self.db = CorpusDatabase(db_path)
        self.db.connect()
        self.db.create_schema()
        
        # Initialize NLP processor
        self.nlp_processor = TurkishNLPProcessor(backend=nlp_backend)
        
        # Track processing statistics
        self.stats = {
            'documents_processed': 0,
            'sentences_processed': 0,
            'tokens_processed': 0,
            'errors': 0
        }
        
    def ingest_directory(self, directory_path: str, 
                        file_patterns: Optional[List[str]] = None,
                        max_files: Optional[int] = None,
                        batch_size: int = 1000) -> Dict[str, Any]:
        """
        Ingest all text files from a directory
        
        Args:
            directory_path: Path to directory containing text files
            file_patterns: List of patterns to match files (default: ['*.txt', '*.json', '*.xml'])
            max_files: Maximum number of files to process
            batch_size: Number of tokens to insert per database batch
            
        Returns:
            Processing statistics
        """
        
        # Default file patterns if none provided
        if file_patterns is None:
            file_patterns = ['*.txt', '*.json', '*.xml']
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find files matching patterns
        text_files = []
        for pattern in file_patterns:
            text_files.extend(list(directory.glob(pattern)))
        
        # Remove duplicates and sort
        text_files = sorted(list(set(text_files)))
        
        if max_files:
            text_files = text_files[:max_files]
        
        logger.info(f"Found {len(text_files)} files to process from patterns: {file_patterns}")
        
        total_files = len(text_files)
        for i, file_path in enumerate(tqdm(text_files, desc="Processing files")):
            try:
                logger.info(f"Processing file {i+1}/{total_files}: {file_path.name}")
                self.ingest_file(file_path, batch_size)
                
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                self.stats['errors'] += 1
        
        # Final statistics
        logger.info("=== INGESTION COMPLETE ===")
        logger.info(f"Documents processed: {self.stats['documents_processed']}")
        logger.info(f"Sentences processed: {self.stats['sentences_processed']}")
        logger.info(f"Tokens processed: {self.stats['tokens_processed']}")
        logger.info(f"Errors: {self.stats['errors']}")
        
        return self.stats.copy()
    
    def ingest_file(self, file_path: Path, batch_size: int = 1000) -> None:
        """
        Ingest a single file (TXT, JSON, or XML)
        
        Args:
            file_path: Path to file
            batch_size: Number of tokens per database batch
        """
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.txt':
                content = self._read_txt_file(file_path)
            elif file_extension == '.json':
                content = self._read_json_file(file_path)
            elif file_extension == '.xml':
                content = self._read_xml_file(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return
        
        if not content.strip():
            logger.warning(f"Empty content in file: {file_path}")
            return
        
        # Generate document hash for duplicate detection
        doc_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Check if document already exists
        if self._document_exists(doc_hash):
            logger.info(f"Document already exists: {file_path.name}")
            return
        
        # Create document record
        doc_id = self._create_document_record(file_path, content, doc_hash)
        
        # Process content with NLP
        self._process_document_content(doc_id, content, batch_size)
        
        self.stats['documents_processed'] += 1
    
    def _read_txt_file(self, file_path: Path) -> str:
        """Read and decode a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1254', 'iso-8859-9']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"Could not decode file: {file_path}")
    
    def _read_json_file(self, file_path: Path) -> str:
        """Read and parse a JSON file, extracting text content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract text from various JSON structures
            text_content = self._extract_text_from_json(data)
            return text_content
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file {file_path}: {e}")
    
    def _read_xml_file(self, file_path: Path) -> str:
        """Read and parse an XML file, extracting text content"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract text from XML elements
            text_content = self._extract_text_from_xml(root)
            return text_content
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML file {file_path}: {e}")
    
    def _extract_text_from_json(self, data) -> str:
        """Recursively extract text content from JSON data"""
        text_parts = []
        
        if isinstance(data, dict):
            for value in data.values():
                text_parts.append(self._extract_text_from_json(value))
        elif isinstance(data, list):
            for item in data:
                text_parts.append(self._extract_text_from_json(item))
        elif isinstance(data, str):
            text_parts.append(data)
        elif isinstance(data, (int, float, bool)):
            text_parts.append(str(data))
        
        return ' '.join(filter(None, text_parts))
    
    def _extract_text_from_xml(self, element) -> str:
        """Recursively extract text content from XML elements"""
        text_parts = []
        
        # Add direct text content
        if element.text:
            text_parts.append(element.text)
        
        # Add text from child elements
        for child in element:
            text_parts.append(self._extract_text_from_xml(child))
            if child.tail:
                text_parts.append(child.tail)
        
        return ' '.join(filter(None, text_parts))
    
    def _document_exists(self, doc_hash: str) -> bool:
        """Check if document already exists in database"""
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT doc_id FROM documents WHERE file_hash = ?", (doc_hash,))
        return cursor.fetchone() is not None
    
    def _create_document_record(self, file_path: Path, content: str, doc_hash: str) -> int:
        """Create document record in database"""
        cursor = self.db.connection.cursor()
        
        # Get basic file info
        file_size = file_path.stat().st_size if file_path.exists() else len(content.encode('utf-8'))
        
        cursor.execute("""
            INSERT INTO documents (doc_name, file_path, file_size, text_length, file_hash)
            VALUES (?, ?, ?, ?, ?)
        """, (file_path.name, str(file_path), file_size, len(content), doc_hash))
        
        doc_id = cursor.lastrowid
        self.db.connection.commit()
        
        return doc_id
    
    def _process_document_content(self, doc_id: int, content: str, batch_size: int) -> None:
        """Process document content and store in database"""
        
        # Split into sentences
        sentences = self.nlp_processor.split_sentences(content)
        self.stats['sentences_processed'] += len(sentences)
        
        # Process each sentence
        tokens_batch = []
        token_number = 0
        
        for sent_number, sentence in enumerate(sentences, 1):
            # Process sentence with NLP first to get accurate token count
            tokens = self.nlp_processor.process_text(sentence)
            
            # Calculate token range
            token_start = token_number
            token_end = token_number + len(tokens)
            
            # Create sentence record with accurate counts
            sent_id = self._create_sentence_record(doc_id, sent_number, sentence, token_start, token_end)
            
            # Add tokens to batch
            for token in tokens:
                token['doc_id'] = doc_id
                token['sent_id'] = sent_id
                token['token_number'] = token_number
                tokens_batch.append(token)
                token_number += 1
                
                # Insert batch when it reaches batch_size
                if len(tokens_batch) >= batch_size:
                    self._insert_tokens_batch(tokens_batch)
                    tokens_batch = []
            
            self.stats['tokens_processed'] += len(tokens)
        
        # Insert remaining tokens
        if tokens_batch:
            self._insert_tokens_batch(tokens_batch)
    
    def _create_sentence_record(self, doc_id: int, sent_number: int, sentence_text: str, token_start: int, token_end: int) -> int:
        """Create sentence record in database"""
        cursor = self.db.connection.cursor()
        
        cursor.execute("""
            INSERT INTO sentences (doc_id, sent_number, sent_text, token_start, token_end)
            VALUES (?, ?, ?, ?, ?)
        """, (doc_id, sent_number, sentence_text, token_start, token_end))
        
        sent_id = cursor.lastrowid
        self.db.connection.commit()
        
        return sent_id
    
    def _insert_tokens_batch(self, tokens_batch: List[Dict[str, Any]]) -> None:
        """Insert a batch of tokens into database"""
        if not tokens_batch:
            return
            
        cursor = self.db.connection.cursor()
        
        # Prepare INSERT statement
        insert_query = """
            INSERT INTO tokens (
                doc_id, sent_id, token_number, form, norm, lemma, upos, xpos,
                morph, dep_head, dep_rel, start_char, end_char,
                is_punctuation, is_space
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Insert batch
        token_data = []
        for token in tokens_batch:
            token_data.append((
                token['doc_id'],
                token['sent_id'],
                token['token_number'],
                token.get('word', token.get('form', '')),  # Use 'word' field, fallback to 'form'
                token['norm'],
                token.get('lemma'),  # May be None now
                token['upos'],
                token.get('xpos'),
                token.get('morph'),
                token.get('dep_head'),
                token.get('dep_rel'),
                token['start_char'],
                token['end_char'],
                int(token['is_punctuation']),
                int(token['is_space'])
            ))
        
        cursor.executemany(insert_query, token_data)
        self.db.connection.commit()
        
        logger.debug(f"Inserted {len(token_data)} tokens")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        cursor = self.db.connection.cursor()
        
        # Get database statistics
        cursor.execute("SELECT COUNT(*) FROM documents")
        total_docs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sentences")
        total_sentences = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tokens")
        total_tokens = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT norm) FROM tokens")
        unique_words = cursor.fetchone()[0]
        
        return {
            'database_stats': {
                'total_documents': total_docs,
                'total_sentences': total_sentences,
                'total_tokens': total_tokens,
                'unique_words': unique_words
            },
            'processing_stats': self.stats,
            'nlp_info': self.nlp_processor.get_processing_info()
        }
    
    def close(self):
        """Close database connection"""
        self.db.close()

# Convenience function for quick ingestion
def ingest_corpus(corpus_path: str, 
                  db_path: str = "corpus.db",
                  nlp_backend: str = 'auto',
                  max_files: Optional[int] = None) -> Dict[str, Any]:
    """
    Convenience function to ingest a corpus
    
    Args:
        corpus_path: Path to directory with text files
        db_path: Database path
        nlp_backend: NLP backend to use
        max_files: Maximum files to process
        
    Returns:
        Processing statistics
    """
    ingestor = CorpusIngestor(db_path, nlp_backend)
    
    try:
        stats = ingestor.ingest_directory(corpus_path, max_files=max_files)
        return stats
    finally:
        ingestor.close()

if __name__ == "__main__":
    # Example usage
    print("=== CORPUS INGESTOR EXAMPLE ===")
    
    # Create sample text for testing
    sample_dir = Path("sample_corpus")
    sample_dir.mkdir(exist_ok=True)
    
    sample_text = """
    Bu bir test metnidir. Türkçe dil işleme için kullanılır.
    Çeşitli kelimeler içerir: ev, okul, kitap, kalem.
    Farklı cümle yapıları da var. Bu da bir cümle.
    Son bir cümle daha ekleyelim buraya.
    """
    
    # Write sample file
    sample_file = sample_dir / "sample1.txt"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    print(f"Created sample file: {sample_file}")
    
    # Ingest the corpus
    try:
        stats = ingest_corpus(str(sample_dir), "test_corpus.db", nlp_backend='simple')
        print(f"Ingestion complete: {stats}")
        
        # Show final statistics
        ingestor = CorpusIngestor("test_corpus.db")
        final_stats = ingestor.get_processing_stats()
        print(f"Final database stats: {final_stats}")
        ingestor.close()
        
    except Exception as e:
        print(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()