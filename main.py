"""
ASV Sequence Comparison API
A simple FastAPI service for comparing ASV sequences using k-mer vectorization.
"""
import logging
import sys
import traceback
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

try:
    from search.database import ReferenceDatabase
    from query.engine import SequenceQueryEngine
    logger.info("Successfully imported modules")
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise

app = FastAPI(
    title="ASV Sequence Comparison API",
    description="Compare ASV sequences against a reference database using k-mer vectorization",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
reference_db = None
query_engine = None

class SequenceQuery(BaseModel):
    """Model for single sequence query."""
    sequence: str
    top_k: Optional[int] = 5

class SearchResult(BaseModel):
    """Model for search results."""
    sample_id: str
    sequence_id: str
    similarity_score: float
    taxonomy: Optional[str] = None

def load_reference_database():
    """Load reference database from file."""
    global reference_db, query_engine
    
    try:
        logger.info("Initializing reference database...")
        reference_db = ReferenceDatabase(k=6)
        
        # Try to load existing database, otherwise create sample database
        if not reference_db.load("reference_db.pkl"):
            logger.info("No existing database found, creating sample database...")
            reference_db.create_sample_database()
            reference_db.save("reference_db.pkl")
            logger.info("Sample database created and saved")
        else:
            logger.info("Existing database loaded successfully")
        
        # Initialize query engine
        query_engine = SequenceQueryEngine(reference_db)
        logger.info("Query engine initialized successfully")
        
    except Exception as e:
        logger.error(f"Error loading reference database: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize the API on startup."""
    try:
        logger.info("Starting up API...")
        load_reference_database()
        logger.info(f"API initialized with {len(reference_db.sequences)} reference sequences")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return JSONResponse(content={
        "message": "ASV Sequence Comparison API",
        "version": "1.0.0",
        "description": "Compare ASV sequences using k-mer vectorization",
        "endpoints": {
            "/predict": "Compare a single sequence (POST)",
            "/predict/fasta": "Compare sequences from FASTA file (POST)",
            "/database/info": "Get database information (GET)",
            "/health": "Health check (GET)"
        }
    })

@app.post("/predict")
async def predict_sequence(query: SequenceQuery):
    """
    Compare a single ASV sequence against the reference database.
    
    Returns the top-k most similar sequences with similarity scores.
    """
    try:
        logger.info(f"Processing sequence query: length={len(query.sequence)}, top_k={query.top_k}")
        
        if not query_engine:
            logger.error("Query engine not initialized")
            raise HTTPException(status_code=503, detail="Service not ready - query engine not initialized")
        
        result = query_engine.query_single_sequence(query.sequence, query.top_k)
        logger.info(f"Query completed successfully, found {result.get('matches_found', 0)} matches")
        return JSONResponse(content=result)
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/fasta")
async def predict_fasta(file: UploadFile = File(...), top_k: int = 5):
    """
    Compare ASV sequences from a FASTA file against the reference database.
    """
    try:
        logger.info(f"Processing FASTA file: filename={file.filename}, top_k={top_k}")
        
        # Validate file type
        if not file.filename.lower().endswith(('.fasta', '.fa', '.fas')):
            logger.warning("Invalid file type")
            raise HTTPException(status_code=400, detail="File must be in FASTA format")
        
        # Read file content
        content = await file.read()
        fasta_content = content.decode('utf-8')
        
        result = query_engine.query_fasta_sequences(fasta_content, top_k)
        logger.info(f"FASTA query completed successfully, found {result.get('matches_found', 0)} matches")
        return JSONResponse(content=result)
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"FASTA processing error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"FASTA processing error: {str(e)}")

@app.get("/database/info")
async def get_database_info():
    """Get information about the reference database."""
    try:
        if not reference_db:
            logger.error("Reference database not loaded")
            raise HTTPException(status_code=500, detail="Reference database not loaded")
        
        return JSONResponse(content=reference_db.get_info())
        
    except Exception as e:
        logger.error(f"Database info error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Database info error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        if not reference_db or not query_engine:
            logger.warning("Health check failed - service not ready")
            raise HTTPException(status_code=503, detail="Service not ready")
        
        health_info = {
            "status": "healthy",
            "reference_sequences": len(reference_db.sequences),
            "vectorizer_ready": reference_db.vectorizer is not None,
            "database_info": reference_db.get_info()
        }
        logger.info("Health check passed")
        return JSONResponse(content=health_info)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
