# from pydantic import BaseModel
# from datetime import datetime

# class Memory(BaseModel):
#     session_id: str
#     type: str
#     key: str
#     value: str
#     confidence: float
#     source_turn: int
#     last_used_turn: int
#     created_at: datetime = datetime.utcnow()
"""
Memory Schema with Enhanced Fields for Long-Term Recall
Supports 1000+ turn conversations with better metadata tracking
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class MemoryType(str, Enum):
    """Memory type enumeration for better type safety"""
    PREFERENCE = "preference"
    FACT = "fact"
    CONSTRAINT = "constraint"
    HABIT = "habit"
    GOAL = "goal"
    REFLECTION = "reflection"
    EPISODIC_SUMMARY = "episodic_summary"

class Memory(BaseModel):
    """
    Enhanced Memory model with fields optimized for long-term recall
    
    IMPROVEMENTS:
    1. Added importance_score for better ranking over 1000+ turns
    2. Added access_count to track how often memory is used
    3. Added tags for better categorization and retrieval
    4. Added metadata for context preservation
    5. Strong validation to ensure data quality
    """
    
    # Core Identifiers
    session_id: str = Field(..., min_length=1, max_length=100)
    
    # Memory Content
    type: MemoryType = Field(..., description="Memory category")
    key: str = Field(..., min_length=1, max_length=100, description="Unique identifier for memory topic")
    value: str = Field(..., min_length=1, max_length=2000, description="Actual memory content")
    
    # Quality Metrics
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence (0-1)")
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Computed importance for ranking")
    
    # Temporal Tracking (Critical for 1000+ turns)
    source_turn: int = Field(..., ge=1, description="Turn when memory was created")
    last_used_turn: int = Field(..., ge=1, description="Most recent turn when memory was recalled")
    access_count: int = Field(default=0, ge=0, description="Number of times memory was retrieved")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Enhanced Metadata
    tags: List[str] = Field(default_factory=list, description="Categorization tags for better retrieval")
    related_memories: List[str] = Field(default_factory=list, description="IDs of related memories")
    context: Optional[str] = Field(default=None, max_length=500, description="Additional context from conversation")
    
    @validator('key')
    def validate_key(cls, v):
        """Ensure key is lowercase and alphanumeric with underscores"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Key must be alphanumeric with optional underscores/hyphens')
        return v.lower()
    
    @validator('tags', pre=True)
    def validate_tags(cls, v):
        """Ensure tags are lowercase and unique"""
        if isinstance(v, list):
            return list(set(tag.lower().strip() for tag in v if tag))
        return []
    
    @validator('importance_score', always=True)
    def calculate_importance(cls, v, values):
        """
        Auto-calculate importance based on type and confidence
        Can be overridden manually
        """
        if v != 0.5:  # Already set
            return v
        
        # Type-based importance weights
        type_weights = {
            MemoryType.CONSTRAINT: 0.9,  # High importance
            MemoryType.GOAL: 0.8,
            MemoryType.PREFERENCE: 0.7,
            MemoryType.FACT: 0.6,
            MemoryType.HABIT: 0.6,
            MemoryType.REFLECTION: 0.5,
            MemoryType.EPISODIC_SUMMARY: 0.4
        }
        
        memory_type = values.get('type')
        confidence = values.get('confidence', 0.5)
        
        base_importance = type_weights.get(memory_type, 0.5)
        
        # Combine with confidence
        return (base_importance * 0.7) + (confidence * 0.3)
    
    class Config:
        use_enum_values = True


