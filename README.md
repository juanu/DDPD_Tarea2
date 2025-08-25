# ASV Sequence Comparison 

This is a prototype tool to quickly compare an DNA sequence from an amplicon study (amplicon sequence variant, ASV), against a reference database using vecotorization. The goal is to quickly identify a similar sequence in a database.

## API

**Deployed API URL**: [https://ddpd-tarea2.onrender.com/](https://ddpd-tarea2.onrender.com/)

**API Documentation**: [https://ddpd-tarea2.onrender.com/docs](https://ddpd-tarea2.onrender.com/docs)

## Tool features

- **Vectorization**: Converts DNA sequences into numerical vectors. Currently using k-mers (6-mer size), but the goal is to use more complex DNA language models, such as DNABERT.
- **Cosine Similarity**: Finds the most similar sequences using cosine similarity scoring
- **Single Sequence Comparison**: Compare individual ASV sequences via JSON payload
- **FASTA File Upload**: Process multiple sequences from FASTA files
- **Reference Database**: Pre-loaded with sample 16S rRNA sequences


## Installation & Local Setup

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Locally

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

##  API Endpoints

### 1. Root Endpoint
- **GET** `/`
- Returns API information and available endpoints

### 2. Single Sequence Prediction
- **POST** `/predict`
- Compare a single ASV sequence against the reference database

**Request Body:**
```json
{
  "sequence": "TACGTAGGGGGCAAGCGTTATCCGGATTTACTGGGTGTAAAGGGAGCGTAGACGGTGAGTTAAGTCTGAAGTAAAGGCAGTGGCTCAACCACTGTACGTGTTGGAAACTGACTCACTTGAGTGCAGAAGAGGAGAGTGGAACTCCATGTGTAGCGGTGAAATGCGTAGATATATGGAGGAACACCAGTGGCGAAGGCGACTCTCTGGTCTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGG",
  "top_k": 5
}
```

**Response:**
```json
{
  "query_sequence": "TACGTAGGGGGCAAGCGT...",
  "query_length": 251,
  "matches_found": 5,
  "results": [
    {
      "sample_id": "sample1",
      "sequence_id": "asv1",
      "similarity_score": 1.0,
      "taxonomy": "Bacteria;Proteobacteria;Gammaproteobacteria;Enterobacteriales;Enterobacteriaceae;Escherichia"
    }
  ]
}
```

### 3. FASTA File Upload
- **POST** `/predict/fasta`
- Upload a FASTA file with multiple sequences

**Parameters:**
- `file`: FASTA file (.fasta, .fa, .fas)
- `top_k`: Number of top matches per sequence (default: 5)

### 4. Database Information
- **GET** `/database/info`
- Get information about the reference database

### 5. Health Check
- **GET** `/health`
- Check API status and readiness

##  Testing the API

### Using the Client Script

Run the provided test client:

```bash
python client.py
```

This will test all endpoints with sample data and show the results.

### Manual Testing with curl

To test the Render app, replace

```
http://localhost:8000
```

with

```
https://ddpd-tarea2.onrender.com
```

**Test single sequence:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": "TACGTAGGGGGCAAGCGTTATCCGGATTTACTGGGTGTAAAGGGAGCGTAGACGGTGAGTTAAGTCTGAAGTAAAGGCAGTGGCTCAACCACTGTACGTGTTGGAAACTGACTCACTTGAGTGCAGAAGAGGAGAGTGGAACTCCATGTGTAGCGGTGAAATGCGTAGATATATGGAGGAACACCAGTGGCGAAGGCGACTCTCTGGTCTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGG",
    "top_k": 3
  }'
```

**Test database info:**
```bash
curl -X GET "http://localhost:8000/database/info"
```

**Test health:**
```bash
curl -X GET "http://localhost:8000/health"
```

### Using Python requests

```python
import requests
import json

# Test single sequence
url = "http://localhost:8000/predict"
payload = {
    "sequence": "TACGTAGGGGGCAAGCGTTATCCGGATTTACTGGGTGTAAAGGGAGCGTAGACGGTGAGTTAAGTCTGAAGTAAAGGCAGTGGCTCAACCACTGTACGTGTTGGAAACTGACTCACTTGAGTGCAGAAGAGGAGAGTGGAACTCCATGTGTAGCGGTGAAATGCGTAGATATATGGAGGAACACCAGTGGCGAAGGCGACTCTCTGGTCTGTAACTGACGCTGAGGCGCGAAAGCGTGGGGAGCAAACAGG",
    "top_k": 5
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
```

## Sample Data

The API comes with a pre-loaded reference database containing sample 16S rRNA sequences from different bacterial taxa:

- **Sample 1**: Escherichia (Proteobacteria)
- **Sample 2**: Lactobacillus (Firmicutes) 
- **Sample 3**: Bacteroides (Bacteroidetes)

Each sequence is approximately 250 base pairs long and represents typical ASV sequences from microbial community studies.

## Input Requirements

### Sequence Format
- **Minimum length**: 6 base pairs (due to k-mer size)
- **Valid bases**: A, T, C, G (N will be converted to A)
- **Format**: Plain DNA sequence string (no headers)

### FASTA Files
- **Extensions**: .fasta, .fa, .fas
- **Format**: Standard FASTA format with sequence IDs
- **Encoding**: UTF-8

### Parameters
- **top_k**: Integer between 1-10 (number of top matches to return)
- **sequence**: DNA sequence string (minimum 6 bases)

## Deployment on Render

This API is configured for easy deployment on [Render](https://render.com):

1. **Fork this repository** to your GitHub account
2. **Create a new Web Service** on Render
3. **Connect your repository**
4. **Use these settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Deploy**

The `render.yaml` file contains the deployment configuration.

## How It Works

1. **K-mer Tokenization**: DNA sequences are converted into overlapping 6-mers (e.g., "ATCGAT" → ["ATCGAT", "TCGATC", "CGATCG"])

2. **Vectorization**: K-mer frequencies are calculated and normalized to create numerical vectors

3. **Similarity Calculation**: Cosine similarity is computed between query and reference vectors

4. **Ranking**: Results are sorted by similarity score (1.0 = identical, 0.0 = no similarity)

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid sequence length or format
- **422 Unprocessable Entity**: Invalid JSON payload
- **500 Internal Server Error**: Processing errors
- **503 Service Unavailable**: API not ready

# Future work

This is just a proof of concept of the tool. The goal is to generate a tool that will be able to compare not at the individual sequence level, but a the sample level. The goal is to provide a set of samples and find the most similar samples to the query. Some ideas for this:

- Use DNABERT or other DNA-trained language model to better capture the DNA language.
- Create a vectorial database with reference samples (e.g. microbiome samples from Chile).
- A possible extension is to train a classifier based on samples, to not only find the closest set of samples, but also to classify a sample into a specific category. For example, samples associated to a specific disease.

