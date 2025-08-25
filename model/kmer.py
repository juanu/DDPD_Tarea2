"""
K-mer vectorization module for DNA sequences.
"""
import numpy as np
import itertools
from collections import Counter


class KmerVectorizer:
    """Simple k-mer vectorizer for DNA sequences."""
    
    def __init__(self, k=6):
        self.k = k
        bases = ['A', 'T', 'C', 'G']
        self.vocab = {kmer: idx for idx, kmer in enumerate([''.join(p) for p in itertools.product(bases, repeat=k)])}
        self.vocab_size = len(self.vocab)
    
    def tokenize(self, sequence):
        """Convert sequence to k-mers."""
        sequence = sequence.upper().replace('N', 'A')
        kmers = []
        for i in range(len(sequence) - self.k + 1):
            kmer = sequence[i:i + self.k]
            if all(base in 'ATCG' for base in kmer):
                kmers.append(kmer)
        return kmers
    
    def vectorize(self, sequence):
        """Convert sequence to k-mer frequency vector."""
        kmers = self.tokenize(sequence)
        kmer_counts = Counter(kmers)
        
        vector = np.zeros(self.vocab_size)
        for kmer, count in kmer_counts.items():
            if kmer in self.vocab:
                vector[self.vocab[kmer]] = count
        
        # Normalize
        total = len(kmers)
        if total > 0:
            vector = vector / total
        
        return vector


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return np.dot(vec1, vec2) / (norm1 * norm2)
