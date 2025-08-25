"""
Client script to test the ASV Comparison API.
This script demonstrates how to interact with the deployed API.
"""
import requests
import json

# API base URL - change this to your deployed URL
BASE_URL = "http://localhost:8000"  # For local testing
# BASE_URL = "https://your-app-name.onrender.com"  # For deployed version

def test_api_health():
    """Test the health endpoint."""
    print("=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

def test_database_info():
    """Test the database info endpoint."""
    print("=== Testing Database Info Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/database/info")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

def test_single_sequence_prediction():
    """Test single sequence prediction."""
    print("=== Testing Single Sequence Prediction ===")
    
    # Test sequence (16S rRNA gene sequence)
    test_sequence = "TACGTAGGGGGCAAGCGTTATCCGGATTTACTGGGTGTAAAGGGAGCGTAGACGGTGAGTTAAGTCTGAAGTAAAGGCAGTGGCTCAACCACTGTACGTGTTGGAAACTGACTCACTTGAGTGCAGAAGAGGAGAGTGGAACTCCATGTGTAGCGGTGAAATGCGTAGATATATGGAGGAACACCAGTGGCGAAGGCGACTCTCTGGTCTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGG"
    
    payload = {
        "sequence": test_sequence,
        "top_k": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Payload sent: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

def test_short_sequence():
    """Test with a short sequence (should return error)."""
    print("=== Testing Short Sequence (Error Case) ===")
    
    payload = {
        "sequence": "ATCG",  # Too short
        "top_k": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Payload sent: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

def test_different_sequence():
    """Test with a different sequence."""
    print("=== Testing Different Sequence ===")
    
    # Different test sequence
    test_sequence = "TACGTAGGTGGCAAGCGTTGTCCGGATTTACTGGGTGTAAAGGGAGCGTAGACGGCTTTGTAAGTCTGATGTGAAAGCCCGGGGCTCAACCCCGGGACTGCATTGGAAACTGGCATACTTGAGTGCAGGAGAGGAGAGTGGAACTCCATGTGTAGCGGTGAAATGCGTAGATATATGGAGGAACACCAGTGGCGAAGGCGACTCTCTGGTCTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGG"
    
    payload = {
        "sequence": test_sequence,
        "top_k": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Payload sent: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

def create_test_fasta():
    """Create a test FASTA file."""
    fasta_content = """>query_seq_1
TACGTAGGGGGCAAGCGTTATCCGGATTTACTGGGTGTAAAGGGAGCGTAGACGGTGAGTTAAGTCTGAAGTAAAGGCAGTGGCTCAACCACTGTACGTGTTGGAAACTGACTCACTTGAGTGCAGAAGAGGAGAGTGGAACTCCATGTGTAGCGGTGAAATGCGTAGATATATGGAGGAACACCAGTGGCGAAGGCGACTCTCTGGTCTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGG
>query_seq_2
TACGTAGGTGGCAAGCGTTGTCCGGATTTACTGGGTGTAAAGGGAGCGTAGACGGCTTTGTAAGTCTGATGTGAAAGCCCGGGGCTCAACCCCGGGACTGCATTGGAAACTGGCATACTTGAGTGCAGGAGAGGAGAGTGGAACTCCATGTGTAGCGGTGAAATGCGTAGATATATGGAGGAACACCAGTGGCGAAGGCGACTCTCTGGTCTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGG"""
    
    with open("test_query.fasta", "w") as f:
        f.write(fasta_content)

def test_fasta_upload():
    """Test FASTA file upload."""
    print("=== Testing FASTA File Upload ===")
    
    # Create test FASTA file
    create_test_fasta()
    
    try:
        with open("test_query.fasta", "rb") as f:
            files = {"file": ("test_query.fasta", f, "text/plain")}
            data = {"top_k": 3}
            
            response = requests.post(f"{BASE_URL}/predict/fasta", files=files, data=data)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print()
    except Exception as e:
        print(f"Error: {e}")
        print()

def main():
    """Run all tests."""
    print("ASV Comparison API Client Test")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print()
    
    # Run all tests
    test_api_health()
    test_database_info()
    test_single_sequence_prediction()
    test_short_sequence()
    test_different_sequence()
    test_fasta_upload()
    
    print("All tests completed!")

if __name__ == "__main__":
    main()

