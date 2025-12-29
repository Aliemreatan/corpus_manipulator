"""
Statistical Analysis Module for Corpus Linguistics

This module provides functions for calculating statistical significance,
keyness, and association measures used in corpus linguistics.
"""

import math
from typing import Dict, Any, List, Tuple
from collections import Counter

class CorpusStatistics:
    """Statistical calculations for corpus analysis"""
    
    @staticmethod
    def calculate_log_likelihood(target_freq: int, target_size: int, 
                               ref_freq: int, ref_size: int) -> float:
        """
        Calculate Log-Likelihood (G2) for a word.
        
        Formula: 2 * ((a * ln(a/E1)) + (b * ln(b/E2)))
        where:
        a = target_freq
        b = ref_freq
        c = target_size
        d = ref_size
        E1 = c * (a+b) / (c+d)
        E2 = d * (a+b) / (c+d)
        """
        if target_freq == 0 and ref_freq == 0:
            return 0.0
            
        a = float(target_freq)
        b = float(ref_freq)
        c = float(target_size)
        d = float(ref_size)
        
        # Expected values
        total_freq = a + b
        total_size = c + d
        
        E1 = c * total_freq / total_size
        E2 = d * total_freq / total_size
        
        # Calculation with protection against log(0)
        sum_a = 0.0
        if a > 0:
            sum_a = a * math.log(a / E1)
            
        sum_b = 0.0
        if b > 0:
            sum_b = b * math.log(b / E2)
            
        return 2 * (sum_a + sum_b)

    @staticmethod
    def calculate_simple_math(target_freq: int, target_size: int, 
                            ref_freq: int, ref_size: int) -> float:
        """
        Calculate simple frequency per million difference (normalized).
        """
        norm_target = (target_freq / target_size) * 1_000_000
        norm_ref = (ref_freq / ref_size) * 1_000_000
        
        if norm_ref == 0:
            return norm_target  # Infinite relative frequency, just return normalized
            
        return norm_target / norm_ref

    @staticmethod
    def get_default_reference_stats() -> Dict[str, Any]:
        """
        Returns a small, built-in reference frequency list for Turkish.
        This serves as a fallback "Reference Corpus" for keyness analysis.
        Based on approximations of common Turkish function words.
        """
        # This is a tiny subset of a general Turkish frequency list
        # In a real app, this would be loaded from a larger file
        return {
            'total_tokens': 1000000,
            'word_counts': {
                'bir': 30000, 've': 25000, 'bu': 15000, 'da': 12000, 
                'de': 11000, 'için': 8000, 'ile': 7000, 'o': 6000,
                'çok': 5000, 'ama': 4000, 'var': 3500, 'gibi': 3500,
                'sonra': 3000, 'en': 2500, 'ne': 2500, 'kadar': 2500,
                'olan': 2000, 'daha': 2000, 'ben': 1500, 'sen': 1000,
                'evet': 500, 'hayır': 500
            }
        }
