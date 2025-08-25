"""
Reference database operations for ASV sequence comparison.
"""
import pickle
import os
from typing import Dict, Any
from Bio import SeqIO
from model.kmer import KmerVectorizer


class ReferenceDatabase:
    """Reference database for ASV sequences."""
    
    def __init__(self, k=6):
        self.vectorizer = KmerVectorizer(k=k)
        self.sequences = []
    
    def create_from_fasta(self, fasta_file: str, taxonomy_mapping: Dict[str, str] = None):
        """
        Create reference database from a FASTA file.
        
        Args:
            fasta_file: Path to FASTA file
            taxonomy_mapping: Optional mapping of sequence_id to taxonomy
        """
        self.sequences = []
        
        for record in SeqIO.parse(fasta_file, "fasta"):
            sequence_data = {
                "sample_id": "reference",  # Default sample ID
                "sequence_id": record.id,
                "sequence": str(record.seq),
                "taxonomy": taxonomy_mapping.get(record.id) if taxonomy_mapping else None
            }
            
            # Vectorize sequence
            vector = self.vectorizer.vectorize(sequence_data["sequence"])
            sequence_data["vector"] = vector
            
            self.sequences.append(sequence_data)
    
    def create_sample_database(self):
        """Create a sample reference database for testing."""
        sample_sequences = [
            {
                "sample_id": "sample1",
                "sequence_id": "asv1",
                "sequence": "TACGTAGGGGGCAAGCGTTATCCGGATTTACTGGGTGTAAAGGGAGCGTAGACGGTGAGTTAAGTCTGAAGTAAAGGCAGTGGCTCAACCACTGTACGTGTTGGAAACTGACTCACTTGAGTGCAGAAGAGGAGAGTGGAACTCCATGTGTAGCGGTGAAATGCGTAGATATATGGAGGAACACCAGTGGCGAAGGCGACTCTCTGGTCTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGG",
                "taxonomy": "Bacteria;Proteobacteria;Gammaproteobacteria;Enterobacteriales;Enterobacteriaceae;Escherichia"
            },
            {
                "sample_id": "sample1",
                "sequence_id": "asv2", 
                "sequence": "TACGTAGGTGGCAAGCGTTGTCCGGATTTACTGGGTGTAAAGGGAGCGTAGACGGCTTTGTAAGTCTGATGTGAAAGCCCGGGGCTCAACCCCGGGACTGCATTGGAAACTGGCATACTTGAGTGCAGGAGAGGAGAGTGGAACTCCATGTGTAGCGGTGAAATGCGTAGATATATGGAGGAACACCAGTGGCGAAGGCGACTCTCTGGTCTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGG",
                "taxonomy": "Bacteria;Firmicutes;Bacilli;Lactobacillales;Lactobacillaceae;Lactobacillus"
            },
            {
                "sample_id": "sample2",
                "sequence_id": "asv1",
                "sequence": "TACGTAGGTGGCAAGCGTTGTCCGGATTTACTGGGTGTAAAGGGAGCGTAGACGGCTTTGTAAGTCTGATGTGAAAGCCCGGGGCTCAACCCCGGGACTGCATTGGAAACTGGCATACTTGAGTGCAGGAGAGGAGAGTGGAACTCCATGTGTAGCGGTGAAATGCGTAGATATATGGAGGAACACCAGTGGCGAAGGCGACTCTCTGGTCTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGG",
                "taxonomy": "Bacteria;Firmicutes;Bacilli;Lactobacillales;Lactobacillaceae;Lactobacillus"
            },
            {
                "sample_id": "sample3",
                "sequence_id": "asv1",
                "sequence": "TACGTAGGTGGCAAGCGTTGTCCGGATTTACTGGGTGTAAAGGGAGCGTAGACGGCTTTGTAAGTCTGATGTGAAAGCCCGGGGCTCAACCCCGGGACTGCATTGGAAACTGGCATACTTGAGTGCAGGAGAGGAGAGTGGAACTCCATGTGTAGCGGTGAAATGCGTAGATATATGGAGGAACACCAGTGGCGAAGGCGACTCTCTGGTCTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGG",
                "taxonomy": "Bacteria;Bacteroidetes;Bacteroidia;Bacteroidales;Bacteroidaceae;Bacteroides"
            }
        ]
        
        self.sequences = []
        for seq_data in sample_sequences:
            vector = self.vectorizer.vectorize(seq_data["sequence"])
            seq_data["vector"] = vector
            self.sequences.append(seq_data)
    
    def save(self, filepath: str):
        """Save database to pickle file."""
        with open(filepath, "wb") as f:
            pickle.dump(self.sequences, f)
    
    def load(self, filepath: str):
        """Load database from pickle file."""
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, "rb") as f:
            self.sequences = pickle.load(f)
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Get database information."""
        if not self.sequences:
            return {"total_sequences": 0}
        
        unique_samples = set(seq["sample_id"] for seq in self.sequences)
        
        return {
            "total_sequences": len(self.sequences),
            "unique_samples": len(unique_samples),
            "sample_ids": list(unique_samples),
            "vector_dimension": len(self.sequences[0]["vector"]) if self.sequences else 0,
            "k_mer_size": self.vectorizer.k
        }
