"""
Simple CQL (Corpus Query Language) Parser

Parses basic CQL queries like:
- [pos="NOUN"]
- [lemma="git"] [pos="VERB"]
- [word="güzel"] [] [pos="NOUN"] (middle token can be anything)

Converts them into executable search logic.
"""

import re
import logging

logger = logging.getLogger(__name__)

class CQLParser:
    """Basic parser for Corpus Query Language"""
    
    def __init__(self):
        # Regex to find token specifications like [attr="value"]
        self.token_pattern = re.compile(r'\[(.*?)\]')
        # Regex to parse attributes inside brackets like pos="NOUN"
        self.attr_pattern = re.compile(r'(\w+)\s*=\s*"(.*?)"')
        
    def parse_query(self, query_string):
        """
        Parses a CQL query string into a list of token constraints.
        
        Example: '[pos="NOUN"] [lemma="git"]'
        Returns: [
            {'pos': 'NOUN'}, 
            {'lemma': 'git'}
        ]
        """
        # Remove extra whitespace
        query_string = query_string.strip()
        
        # Find all token blocks [...]
        token_blocks = self.token_pattern.findall(query_string)
        
        parsed_query = []
        
        for block in token_blocks:
            constraints = {}
            block = block.strip()
            
            # Empty brackets [] match any token
            if not block:
                parsed_query.append({}) # Empty dict means "any token"
                continue
            
            # Parse attributes
            attrs = self.attr_pattern.findall(block)
            for attr, value in attrs:
                # Map CQL attributes to DB columns
                db_attr = self._map_attribute(attr)
                constraints[db_attr] = value
                
            parsed_query.append(constraints)
            
        return parsed_query
    
    def _map_attribute(self, attr):
        """Maps CQL attributes to database columns"""
        mapping = {
            'word': 'norm', # Default to normalized form
            'form': 'form',
            'lemma': 'lemma',
            'pos': 'upos',
            'upos': 'upos',
            'tag': 'xpos'
        }
        return mapping.get(attr.lower(), attr)

    def generate_sql(self, parsed_query):
        """
        Generates optimized SQL for the first token in the sequence.
        (We use SQL for the first token to filter candidates, then Python for the sequence)
        """
        if not parsed_query:
            return None, []
            
        first_token = parsed_query[0]
        
        if not first_token:
            # If first token is wildcard [], we can't optimize much
            # Return a query that selects everything (limit applied later)
            return "SELECT sent_id, token_number FROM tokens", []
            
        conditions = []
        params = []
        
        for attr, value in first_token.items():
            conditions.append(f"{attr} = ?")
            params.append(value)
            
        where_clause = " AND ".join(conditions)
        sql = f"SELECT sent_id, token_number FROM tokens WHERE {where_clause}"
        
        return sql, params