"""
HuggingFace Inference API for embeddings
No local models - all processing done by HF servers
"""
import requests
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

# HuggingFace API configuration
HF_API_TOKEN = os.getenv("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

# Cache for API requests
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


def get_embedding(text):
    """
    Get embedding for text using HuggingFace Inference API
    
    Args:
        text: String or list of strings to embed
    
    Returns:
        numpy array of embeddings
    """
    if not HF_API_TOKEN:
        raise ValueError("HF_TOKEN not set in environment variables")
    
    # Ensure text is a list
    if isinstance(text, str):
        texts = [text]
        single = True
    else:
        texts = text
        single = False
    
    # Call HuggingFace API
    response = requests.post(
        HF_API_URL,
        headers=HEADERS,
        json={"inputs": texts, "options": {"wait_for_model": True}}
    )
    
    if response.status_code != 200:
        raise Exception(f"HuggingFace API error: {response.status_code} - {response.text}")
    
    embeddings = response.json()
    
    # Convert to numpy array
    embeddings = np.array(embeddings)
    
    # Return single embedding if single input
    if single:
        return embeddings[0]
    
    return embeddings


def cosine_similarity(emb1, emb2):
    """
    Calculate cosine similarity between two embeddings
    
    Args:
        emb1: First embedding (numpy array)
        emb2: Second embedding (numpy array)
    
    Returns:
        Similarity score (0-1)
    """
    emb1 = np.array(emb1)
    emb2 = np.array(emb2)
    
    # Calculate cosine similarity
    dot_product = np.dot(emb1, emb2)
    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def batch_cosine_similarity(emb, emb_list):
    """
    Calculate cosine similarity between one embedding and a list of embeddings
    
    Args:
        emb: Single embedding (numpy array)
        emb_list: List of embeddings (list of numpy arrays)
    
    Returns:
        List of similarity scores
    """
    emb = np.array(emb)
    emb_list = np.array(emb_list)
    
    # Normalize
    emb_norm = emb / np.linalg.norm(emb)
    emb_list_norm = emb_list / np.linalg.norm(emb_list, axis=1, keepdims=True)
    
    # Calculate similarities
    similarities = np.dot(emb_list_norm, emb_norm)
    
    return similarities.tolist()