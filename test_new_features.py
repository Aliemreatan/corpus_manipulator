
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

from query.cql_parser import CQLParser
from analysis.stats import CorpusStatistics

def test_new_features():
    print("=== TESTING NEW FEATURES ===")
    
    # Test CQL Parser
    print("\n1. Testing CQL Parser...")
    parser = CQLParser()
    query = '[pos="NOUN"] [lemma="ev"]'
    parsed = parser.parse(query)
    print(f"Query: {query}")
    print(f"Parsed: {parsed}")
    
    sql, params = parser.to_sql(parsed)
    print(f"SQL Condition: {sql}")
    print(f"Params: {params}")
    
    if len(parsed) == 2 and parsed[0]['upos'] == 'NOUN':
        print(">> CQL Parser: PASS")
    else:
        print(">> CQL Parser: FAIL")

    # Test Stats
    print("\n2. Testing Stats Module...")
    ll = CorpusStatistics.calculate_log_likelihood(100, 10000, 50, 10000)
    print(f"Log-Likelihood (100 vs 50 in 10k): {ll:.4f}")
    
    if ll > 0:
        print(">> Stats: PASS")
    else:
        print(">> Stats: FAIL")

if __name__ == "__main__":
    test_new_features()
