"""
Corpus Query Module

This module provides query functionality for corpus analysis including:
- KWIC (Key Word In Context) concordance
- Frequency analysis
- Collocation analysis  
- Word sketches based on dependency relations
- CQL (Corpus Query Language) search
- Advanced Statistics
"""

import sqlite3
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
import logging

from database.schema import CorpusDatabase
from analysis.stats import CorpusStatistics
from query.cql_parser import CQLParser

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CorpusQuery:
    """Main class for corpus querying and analysis"""
    
    def __init__(self, db_path: str = "corpus.db"):
        """
        Initialize corpus query interface
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.db = CorpusDatabase(db_path)
        self.db.connect()
        self.conn = self.db.connection
        self.cql_parser = CQLParser()
        
    def kwic_concordance(self, 
                        search_term: str,
                        search_type: str = 'form',  # 'form', 'norm', 'lemma'
                        case_sensitive: bool = False,
                        window_size: int = 5,
                        limit: int = 100,
                        pos_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate KWIC (Key Word In Context) concordance
        """
        cursor = self.conn.cursor()
        
        # Build query based on search type
        if search_type == 'form':
            search_field = 'form'
        elif search_type == 'norm':
            search_field = 'norm'
        elif search_type == 'lemma':
            search_field = 'lemma'
        else:
            raise ValueError(f"Invalid search_type: {search_type}")
        
        # Build SQL query
        query = f"""
            SELECT 
                t1.token_id,
                t1.doc_id,
                t1.sent_id,
                t1.token_number,
                t1.{search_field} as search_term,
                t1.upos,
                t1.lemma,
                GROUP_CONCAT(t2.form, ' ') as context,
                GROUP_CONCAT(t2.token_id, ',') as context_token_ids
            FROM tokens t1
            JOIN tokens t2 ON t1.sent_id = t2.sent_id 
                AND ABS(t2.token_number - t1.token_number) <= ?
            WHERE t1.{search_field} LIKE ?
        """
        
        params = [window_size, f"%{search_term}%"]
        
        # Add POS filter if specified
        if pos_filter:
            query += " AND t1.upos = ?"
            params.append(pos_filter)
        
        # Add case sensitivity
        if not case_sensitive:
            query += f" AND LOWER(t1.{search_field}) LIKE LOWER(?)"
            params.append(f"%{search_term}%")
        
        query += """
            GROUP BY t1.token_id
            ORDER BY t1.doc_id, t1.sent_id, t1.token_number
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Process results
        concordance_results = []
        for row in results:
            try:
                # Parse context token IDs with error handling
                if row[8] and ',' in str(row[8]): # Index 8 is context_token_ids
                    context_ids = [int(tid) for tid in str(row[8]).split(',') if tid.strip()]
                else:
                    context_ids = [int(row[0])]  # Fallback to keyword only
                
                keyword_pos = context_ids.index(row[0]) if row[0] in context_ids else 0
                
                # Extract left and right context
                left_context_ids = context_ids[:keyword_pos]
                right_context_ids = context_ids[keyword_pos + 1:]
                
                # Get left context tokens
                left_context = ""
                if left_context_ids:
                    cursor.execute("""
                        SELECT form FROM tokens 
                        WHERE token_id IN ({})
                        ORDER BY token_number
                    """.format(','.join(map(str, left_context_ids[-window_size:]))))
                    left_tokens = [r[0] for r in cursor.fetchall()]
                    left_context = ' '.join(left_tokens)
                
                # Get right context tokens
                right_context = ""
                if right_context_ids:
                    cursor.execute("""
                        SELECT form FROM tokens 
                        WHERE token_id IN ({})
                        ORDER BY token_number
                    """.format(','.join(map(str, right_context_ids[:window_size]))))
                    right_tokens = [r[0] for r in cursor.fetchall()]
                    right_context = ' '.join(right_tokens)
                
                result = {
                    'left_context': left_context,
                    'keyword': row[4],
                    'right_context': right_context,
                    'pos': row[5],
                    'lemma': row[6],
                    'doc_id': row[1],
                    'sent_id': row[2],
                    'token_number': row[3]
                }
                concordance_results.append(result)
                
            except Exception as e:
                # Skip problematic rows and continue
                logger.warning(f"Skipping KWIC result due to error: {e}")
                continue
        
        return concordance_results
    
    def frequency_list(self, 
                      word_type: str = 'norm',  # 'form', 'norm', 'lemma'
                      pos_filter: Optional[str] = None,
                      min_freq: int = 1,
                      limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Generate frequency list
        """
        cursor = self.conn.cursor()
        
        # Build query
        if word_type == 'form':
            group_field = 'form'
            select_field = 'form'
        elif word_type == 'norm':
            group_field = 'norm'
            select_field = 'norm'
        elif word_type == 'lemma':
            group_field = 'lemma'
            select_field = 'lemma'
        else:
            raise ValueError(f"Invalid word_type: {word_type}")
        
        query = f"""
            SELECT {select_field}, upos, COUNT(*) as frequency
            FROM tokens
            WHERE {select_field} IS NOT NULL 
                AND {select_field} != ''
                AND is_punctuation = 0
        """
        
        params = []
        
        # Add POS filter
        if pos_filter:
            query += " AND upos = ?"
            params.append(pos_filter)
        
        query += f"""
            GROUP BY {group_field}
            HAVING frequency >= ?
            ORDER BY frequency DESC
            LIMIT ?
        """
        params.extend([min_freq, limit])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [
            {
                'word': row[0],
                'pos': row[1],
                'frequency': row[2]
            }
            for row in results
        ]

    def cql_search(self, query_string: str, limit: int = 100):
        """
        Execute a CQL search
        Example: [pos="ADJ"] [lemma="insan"]
        """
        parsed_query = self.cql_parser.parse_query(query_string)
        if not parsed_query:
            return []
            
        sequence_len = len(parsed_query)
        
        # 1. Find candidates for the first token
        sql, params = self.cql_parser.generate_sql(parsed_query)
        
        cursor = self.conn.cursor()
        cursor.execute(sql + f" LIMIT {limit * 10}") # Fetch more candidates than limit
        candidates = cursor.fetchall()
        
        results = []
        
        # 2. Verify sequences
        for cand in candidates:
            if len(results) >= limit:
                break
                
            sent_id = cand['sent_id']
            start_token_num = cand['token_number']
            
            # Fetch the sequence of tokens
            # We need (sequence_len) tokens starting from start_token_num
            seq_sql = """
                SELECT token_number, form, norm, lemma, upos 
                FROM tokens 
                WHERE sent_id = ? AND token_number >= ? AND token_number < ?
                ORDER BY token_number
            """
            cursor.execute(seq_sql, (sent_id, start_token_num, start_token_num + sequence_len))
            sequence_tokens = cursor.fetchall()
            
            # Check length
            if len(sequence_tokens) != sequence_len:
                continue
                
            # Match each token against constraints
            match = True
            for i, token_constraints in enumerate(parsed_query):
                db_token = sequence_tokens[i]
                
                for attr, val in token_constraints.items():
                    # Check if attribute matches (case-insensitive for text)
                    db_val = db_token[attr]
                    if db_val is None: 
                        match = False
                        break
                        
                    if str(db_val).lower() != str(val).lower():
                        match = False
                        break
                
                if not match:
                    break
            
            if match:
                # Get context
                context_sql = """
                    SELECT form FROM tokens 
                    WHERE sent_id = ? 
                    ORDER BY token_number
                """
                cursor.execute(context_sql, (sent_id,))
                all_sent_tokens = [t['form'] for t in cursor.fetchall()]
                
                keyword_tokens = [t['form'] for t in sequence_tokens]
                keyword_str = " ".join(keyword_tokens)
                
                # Context extraction
                # We know start_token_num. Since we fetched all tokens ordered by token_number,
                # we can approximate the index. For robustness, if token_numbers are not 0-indexed, this might be slightly off
                # but for this corpus tool we assume token_number corresponds to position.
                # A safer way would be to find index in all_sent_tokens.
                
                # Simplified context:
                left_start = max(0, start_token_num - 5)
                left_context = " ".join(all_sent_tokens[left_start:start_token_num])
                
                right_end = min(len(all_sent_tokens), start_token_num + sequence_len + 5)
                right_context = " ".join(all_sent_tokens[start_token_num + sequence_len:right_end])
                
                results.append({
                    'left_context': left_context,
                    'keyword': keyword_str,
                    'right_context': right_context,
                    'match_info': f"Sent {sent_id}"
                })
                
        return results

    def collocation_analysis(self,
                           target_word: str,
                           word_type: str = 'norm',
                           window_size: int = 5,
                           min_freq: int = 2,
                           colloc_min_freq: int = 2,
                           measure: str = 'pmi',  # 'pmi', 'log_likelihood', 't_score'
                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        Perform collocation analysis
        """
        cursor = self.conn.cursor()
        
        # Build search field
        if word_type == 'form':
            search_field = 'form'
        elif word_type == 'norm':
            search_field = 'norm'
        elif word_type == 'lemma':
            search_field = 'lemma'
        else:
            raise ValueError(f"Invalid word_type: {word_type}")
        
        # Get target word frequency
        cursor.execute(f"""
            SELECT COUNT(*) FROM tokens
            WHERE {search_field} = ? AND is_punctuation = 0
        """, [target_word])
        
        target_freq = cursor.fetchone()[0]
        if target_freq < min_freq:
            return []
        
        # Get total tokens
        cursor.execute("SELECT COUNT(*) FROM tokens WHERE is_punctuation = 0")
        total_tokens = cursor.fetchone()[0]
        
        # Find collocations
        collocations = []
        
        # Get all occurrences of target word
        cursor.execute(f"""
            SELECT sent_id, token_number 
            FROM tokens 
            WHERE {search_field} = ? AND is_punctuation = 0
        """, [target_word])
        
        target_occurrences = cursor.fetchall()
        
        # Count collocates
        collocate_counts = Counter()
        
        for sent_id, token_num in target_occurrences:
            # Get words in window
            cursor.execute("""
                SELECT form FROM tokens
                WHERE sent_id = ?
                    AND ABS(token_number - ?) <= ?
                    AND is_punctuation = 0
                    AND token_id != (
                        SELECT token_id FROM tokens 
                        WHERE sent_id = ? AND token_number = ?
                    )
                ORDER BY token_number
            """, [sent_id, token_num, window_size, sent_id, token_num])
            
            window_words = [row[0] for row in cursor.fetchall()]
            
            # Add to collocate counts
            for word in window_words:
                collocate_counts[word] += 1
        
        # Calculate association measures
        for collocate, co_occurrence_count in collocate_counts.items():
            if co_occurrence_count < colloc_min_freq:
                continue
            
            # Get collocate frequency
            cursor.execute("""
                SELECT COUNT(*) FROM tokens
                WHERE form = ? AND is_punctuation = 0
            """, [collocate])
            
            collocate_freq = cursor.fetchone()[0]
            
            if collocate_freq == 0:
                continue
            
            # Calculate association measures
            if measure == 'pmi':
                score = self._calculate_pmi(target_freq, collocate_freq, co_occurrence_count, total_tokens)
            elif measure == 'log_likelihood':
                score = self._calculate_log_likelihood(target_freq, collocate_freq, co_occurrence_count, total_tokens)
            elif measure == 't_score':
                score = self._calculate_t_score(target_freq, collocate_freq, co_occurrence_count, total_tokens)
            else:
                raise ValueError(f"Invalid measure: {measure}")
            
            collocations.append({
                'collocate': collocate,
                'co_occurrence_count': co_occurrence_count,
                'target_freq': target_freq,
                'collocate_freq': collocate_freq,
                'score': score
            })
        
        # Sort by score and limit
        collocations.sort(key=lambda x: x['score'], reverse=True)
        return collocations[:limit]

    def _calculate_pmi(self, target_freq: int, collocate_freq: int, 
                      co_occurrence_count: int, total_tokens: int) -> float:
        """Calculate Pointwise Mutual Information"""
        if co_occurrence_count == 0:
            return 0.0
        
        p_target = target_freq / total_tokens
        p_collocate = collocate_freq / total_tokens
        p_co_occurrence = co_occurrence_count / total_tokens
        
        if p_target == 0 or p_collocate == 0 or p_co_occurrence == 0:
            return 0.0
        
        pmi = math.log(p_co_occurrence / (p_target * p_collocate))
        return pmi
    
    def _calculate_log_likelihood(self, target_freq: int, collocate_freq: int,
                                co_occurrence_count: int, total_tokens: int) -> float:
        """Calculate Log-likelihood statistic"""
        if co_occurrence_count == 0:
            return 0.0
        
        expected_co_occurrence = (target_freq * collocate_freq) / total_tokens
        
        if expected_co_occurrence == 0:
            return float('inf') if co_occurrence_count > 0 else 0.0
        
        ll = co_occurrence_count * math.log(co_occurrence_count / expected_co_occurrence)
        return ll
    
    def _calculate_t_score(self, target_freq: int, collocate_freq: int,
                          co_occurrence_count: int, total_tokens: int) -> float:
        """Calculate T-score"""
        if co_occurrence_count == 0:
            return 0.0
        
        expected_co_occurrence = (target_freq * collocate_freq) / total_tokens
        t_score = (co_occurrence_count - expected_co_occurrence) / math.sqrt(co_occurrence_count)
        return t_score
    
    def word_sketch(self, 
                   lemma: str,
                   relation_type: Optional[str] = None,
                   limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate word sketch based on dependency relations
        """
        cursor = self.conn.cursor()
        
        # Get dependency relations for the lemma
        query = """
            SELECT 
                t1.dep_rel as relation,
                t2.lemma as related_lemma,
                t2.form as related_form,
                t1.lemma as head_lemma,
                COUNT(*) as frequency
            FROM tokens t1
            JOIN tokens t2 ON t1.dep_head = t2.token_id
            WHERE t1.lemma = ?
                AND t1.dep_rel IS NOT NULL
                AND t1.dep_rel != 'root'
                AND t2.lemma IS NOT NULL
        """
        
        params = [lemma]
        
        if relation_type:
            query += " AND t1.dep_rel = ?"
            params.append(relation_type)
        
        query += """
            GROUP BY t1.dep_rel, t2.lemma, t2.form, t1.lemma
            ORDER BY frequency DESC
            LIMIT ?
        """
        params.append(limit * 10) 
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Group by relation type
        sketch = defaultdict(list)
        for row in results:
            relation = row[0]
            if relation and len(sketch[relation]) < limit:
                sketch[relation].append({
                    'related_word': row[1],
                    'related_form': row[2],
                    'head_word': row[3],
                    'frequency': row[4]
                })
        
        return sketch

    def get_pos_distribution(self):
        """Get distribution of POS tags"""
        cursor = self.conn.cursor()
        
        query = """
            SELECT upos, COUNT(*) as count 
            FROM tokens 
            WHERE upos IS NOT NULL 
            GROUP BY upos 
            ORDER BY count DESC
        """
        
        cursor.execute(query)
        return [{'pos': row[0], 'count': row[1]} for row in cursor.fetchall()]

    def get_advanced_stats(self):
        """Calculate advanced corpus statistics"""
        cursor = self.conn.cursor()
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM tokens")
        total_tokens = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT norm) FROM tokens")
        unique_types = cursor.fetchone()[0]
        
        stats['total_tokens'] = total_tokens
        stats['unique_types'] = unique_types
        stats['ttr'] = (unique_types / total_tokens) if total_tokens > 0 else 0
        
        cursor.execute("SELECT COUNT(*) FROM sentences")
        total_sentences = cursor.fetchone()[0]
        stats['total_sentences'] = total_sentences
        stats['avg_sent_len'] = (total_tokens / total_sentences) if total_sentences > 0 else 0
        
        cursor.execute("SELECT upos, COUNT(*) as cnt FROM tokens GROUP BY upos ORDER BY cnt DESC LIMIT 5")
        stats['top_pos'] = cursor.fetchall()
        
        return stats

    def get_all_tokens_for_export(self):
        """Yields all tokens for CoNLL-U export"""
        cursor = self.conn.cursor()
        
        query = """
            SELECT 
                t.sent_id,
                t.token_number,
                t.form,
                t.lemma,
                t.upos,
                t.xpos,
                t.morph,
                t.dep_head,
                t.dep_rel,
                s.sent_text,
                d.doc_name
            FROM tokens t
            JOIN sentences s ON t.sent_id = s.sent_id
            JOIN documents d ON t.doc_id = d.doc_id
            ORDER BY t.doc_id, t.sent_id, t.token_number
        """
        
        cursor.execute(query)
        
        current_sent_id = None
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
                
            sent_id = row[0]
            is_new_sentence = (sent_id != current_sent_id)
            current_sent_id = sent_id
            
            yield row, is_new_sentence

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get basic processing stats"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT doc_id) FROM tokens")
            total_documents = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT sent_id) FROM tokens")
            total_sentences = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM tokens")
            total_tokens = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT norm) FROM tokens WHERE norm IS NOT NULL")
            unique_words = cursor.fetchone()[0] or 0
            
            return {
                'database_stats': {
                    'total_documents': total_documents,
                    'total_sentences': total_sentences,
                    'total_tokens': total_tokens,
                    'unique_words': unique_words
                }
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}

    def close(self):
        """Close database connection"""
        self.db.close()
