"""
SQLite Database Schema for Corpus Data Manipulator

This module creates the database schema with tables optimized for:
- Token storage with linguistic annotations
- Efficient querying for KWIC, frequency, and collocation analysis
- Full-text search capabilities
"""

import sqlite3
from pathlib import Path
from typing import Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CorpusDatabase:
    """Manages the SQLite database for corpus storage"""
    
    def __init__(self, db_path: str = "corpus.db"):
        self.db_path = Path(db_path)
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Enable column access by name
        return self.connection
        
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def create_schema(self):
        """Create all database tables and indices"""
        cursor = self.connection.cursor()
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_name TEXT NOT NULL,
                file_path TEXT,
                file_size INTEGER,
                text_length INTEGER,
                sentence_count INTEGER,
                token_count INTEGER,
                file_hash TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sentences table (for sentence-level indexing)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sentences (
                sent_id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER NOT NULL,
                sent_number INTEGER NOT NULL,
                sent_text TEXT NOT NULL,
                token_start INTEGER NOT NULL,
                token_end INTEGER NOT NULL,
                FOREIGN KEY (doc_id) REFERENCES documents (doc_id) ON DELETE CASCADE
            )
        """)
        
        # Tokens table (main storage)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                token_id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER NOT NULL,
                sent_id INTEGER NOT NULL,
                token_number INTEGER NOT NULL,
                form TEXT NOT NULL,              -- Original surface form
                norm TEXT NOT NULL,              -- Normalized form (lowercase)
                lemma TEXT,                      -- Lemma
                upos TEXT,                       -- Universal POS tag
                xpos TEXT,                       -- Language-specific POS tag
                morph TEXT,                      -- Morphological features
                dep_head INTEGER,                -- Dependency head token_id
                dep_rel TEXT,                    -- Dependency relation
                start_char INTEGER NOT NULL,     -- Character offset in original text
                end_char INTEGER NOT NULL,       -- Character offset in original text
                is_punctuation INTEGER DEFAULT 0,
                is_space INTEGER DEFAULT 0,
                FOREIGN KEY (doc_id) REFERENCES documents (doc_id) ON DELETE CASCADE,
                FOREIGN KEY (sent_id) REFERENCES sentences (sent_id) ON DELETE CASCADE
            )
        """)
        
        # Create FTS5 virtual table for full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS tokens_fts USING fts5(
                form, norm, lemma,
                content='tokens',
                content_rowid='token_id'
            )
        """)
        
        # Create indices for performance
        self._create_indices(cursor)
        
        # Create triggers to keep FTS index in sync
        self._create_triggers(cursor)
        
        self.connection.commit()
        logger.info("Database schema created successfully")
        
    def _create_indices(self, cursor):
        """Create performance indices"""
        
        # Token-level indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_doc_id ON tokens(doc_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_sent_id ON tokens(sent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_norm ON tokens(norm)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_lemma ON tokens(lemma)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_upos ON tokens(upos)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_dep_head ON tokens(dep_head)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_dep_rel ON tokens(dep_rel)")
        
        # Compound indices for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_norm_upos ON tokens(norm, upos)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_lemma_upos ON tokens(lemma, upos)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_doc_sent ON tokens(doc_id, sent_id, token_number)")
        
        # Sentence-level indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentences_doc_id ON sentences(doc_id)")
        
        # Frequency analysis indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_lemmapos ON tokens(lemma, upos)")
        
    def _create_triggers(self, cursor):
        """Create triggers to maintain FTS index"""
        
        # Drop existing triggers to ensure updates are applied
        cursor.execute("DROP TRIGGER IF EXISTS tokens_ai")
        cursor.execute("DROP TRIGGER IF EXISTS tokens_au")
        cursor.execute("DROP TRIGGER IF EXISTS tokens_ad")
        
        # Trigger for INSERT
        cursor.execute("""
            CREATE TRIGGER tokens_ai AFTER INSERT ON tokens BEGIN
                INSERT INTO tokens_fts(rowid, form, norm, lemma) 
                VALUES (new.token_id, new.form, new.norm, new.lemma);
            END
        """)
        
        # Trigger for UPDATE
        cursor.execute("""
            CREATE TRIGGER tokens_au AFTER UPDATE ON tokens BEGIN
                INSERT INTO tokens_fts(tokens_fts, rowid, form, norm, lemma) 
                VALUES('delete', old.token_id, old.form, old.norm, old.lemma);
                INSERT INTO tokens_fts(rowid, form, norm, lemma) 
                VALUES (new.token_id, new.form, new.norm, new.lemma);
            END
        """)
        
        # Trigger for DELETE
        cursor.execute("""
            CREATE TRIGGER tokens_ad AFTER DELETE ON tokens BEGIN
                INSERT INTO tokens_fts(tokens_fts, rowid, form, norm, lemma) 
                VALUES('delete', old.token_id, old.form, old.norm, old.lemma);
            END
        """)
        
    def get_schema_info(self):
        """Get information about the database schema"""
        cursor = self.connection.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema_info = {
            'tables': {},
            'indices': {},
            'fts_table': None
        }
        
        for table in tables:
            if table.endswith('_fts'):
                schema_info['fts_table'] = table
                continue
                
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            schema_info['tables'][table] = {
                'columns': [{'name': col[1], 'type': col[2], 'pk': col[5]} for col in columns]
            }
            
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table}'")
            indices = [row[0] for row in cursor.fetchall()]
            schema_info['indices'][table] = indices
            
        return schema_info

def create_sample_database(db_path: str = "sample_corpus.db"):
    """Create a sample database for testing"""
    db = CorpusDatabase(db_path)
    db.connect()
    db.create_schema()
    
    # Print schema information
    schema_info = db.get_schema_info()
    print("\n=== DATABASE SCHEMA ===")
    for table_name, table_info in schema_info['tables'].items():
        print(f"\nTable: {table_name}")
        for col in table_info['columns']:
            pk_indicator = " (PK)" if col['pk'] else ""
            print(f"  {col['name']}: {col['type']}{pk_indicator}")
            
    if schema_info['fts_table']:
        print(f"\nFTS Table: {schema_info['fts_table']}")
        
    print(f"\nIndices created:")
    for table_name, indices in schema_info['indices'].items():
        print(f"  {table_name}: {len(indices)} indices")
        for idx in indices[:3]:  # Show first 3
            print(f"    - {idx}")
        if len(indices) > 3:
            print(f"    ... and {len(indices) - 3} more")
            
    db.close()
    return db_path

if __name__ == "__main__":
    # Create sample database
    db_path = create_sample_database()
    print(f"\nSample database created at: {db_path}")
    
    print("\n=== SCHEMA DESIGN NOTES ===")
    print("1. tokens table: Main storage with linguistic annotations")
    print("2. FTS5: Full-text search for fast KWIC queries")
    print("3. Optimized indices for frequency and collocation analysis")
    print("4. Foreign key constraints for data integrity")
    print("5. Morphological features stored as JSON-like strings")
    print("6. Character offsets for precise text reconstruction")