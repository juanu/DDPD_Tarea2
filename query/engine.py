"""
Query engine for ASV sequence comparison.
"""
from typing import Dict, Any
import io
from model.kmer import cosine_similarity
from search.database import ReferenceDatabase


def parse_fasta_content(fasta_content: str):
    """Simple FASTA parser for string content without biopython dependency."""
    sequences = []
    lines = fasta_content.strip().split('\n')
    current_id = None
    current_seq = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('>'):
            # Save previous sequence if exists
            if current_id is not None:
                sequences.append({
                    'id': current_id,
                    'seq': ''.join(current_seq)
                })
            # Start new sequence
            current_id = line[1:]  # Remove '>' character
            current_seq = []
        elif line:
            current_seq.append(line)
    
    # Don't forget the last sequence
    if current_id is not None:
        sequences.append({
            'id': current_id,
            'seq': ''.join(current_seq)
        })
    
    return sequences


class SequenceQueryEngine:
    """Engine for querying sequences against reference database."""
    
    def __init__(self, reference_db: ReferenceDatabase):
        self.reference_db = reference_db
        self.vectorizer = reference_db.vectorizer
    
    def query_single_sequence(self, sequence: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Query a single sequence against the reference database.
        
        Args:
            sequence: DNA sequence to query
            top_k: Number of top matches to return
            
        Returns:
            Dictionary with query results
        """
        # Validate sequence
        if not sequence or len(sequence) < self.vectorizer.k:
            raise ValueError(f"Sequence must be at least {self.vectorizer.k} bases long")
        
        # Vectorize query sequence
        query_vector = self.vectorizer.vectorize(sequence)
        
        # Calculate similarities
        similarities = []
        for ref_seq in self.reference_db.sequences:
            similarity = cosine_similarity(query_vector, ref_seq["vector"])
            similarities.append({
                "sample_id": ref_seq["sample_id"],
                "sequence_id": ref_seq["sequence_id"],
                "similarity_score": float(similarity),
                "taxonomy": ref_seq["taxonomy"]
            })
        
        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_matches = similarities[:top_k]
        
        return {
            "query_sequence": sequence,
            "query_length": len(sequence),
            "matches_found": len(top_matches),
            "results": top_matches
        }
    
    def query_fasta_sequences(self, fasta_content: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Query multiple sequences from FASTA content against the reference database.
        
        Args:
            fasta_content: FASTA format string content
            top_k: Number of top matches to return per sequence
            
        Returns:
            Dictionary with query results for all sequences
        """
        # Parse FASTA sequences
        sequences = parse_fasta_content(fasta_content)
        
        if not sequences:
            raise ValueError("No valid sequences found in FASTA content")
        
        # Process each sequence
        results = []
        for seq_data in sequences:
            query_vector = self.vectorizer.vectorize(seq_data["seq"])
            
            # Calculate similarities
            similarities = []
            for ref_seq in self.reference_db.sequences:
                similarity = cosine_similarity(query_vector, ref_seq["vector"])
                similarities.append({
                    "sample_id": ref_seq["sample_id"],
                    "sequence_id": ref_seq["sequence_id"],
                    "similarity_score": float(similarity),
                    "taxonomy": ref_seq["taxonomy"]
                })
            
            # Sort and get top matches
            similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
            top_matches = similarities[:top_k]
            
            results.append({
                "query_sequence_id": seq_data["id"],
                "query_length": len(seq_data["seq"]),
                "matches": top_matches
            })
        
        return {
            "total_sequences": len(sequences),
            "results": results
        }
    
    def query_fasta_file(self, fasta_file: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Query sequences from a FASTA file against the reference database.
        
        Args:
            fasta_file: Path to FASTA file
            top_k: Number of top matches to return per sequence
            
        Returns:
            Dictionary with query results for all sequences
        """
        with open(fasta_file, 'r') as f:
            fasta_content = f.read()
        
        return self.query_fasta_sequences(fasta_content, top_k)
