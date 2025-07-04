"""Data models for PeezyAgent.

This module contains the core data models for RFP proposals and analysis results.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import json


class ModelValidationError(Exception):
    """Raised when model validation fails."""
    pass


@dataclass
class RFPProposal:
    """Represents an RFP proposal document.
    
    This class encapsulates all data related to an uploaded RFP proposal,
    including the original content, extracted structured data, and analysis results.
    """
    
    id: Optional[str] = None
    filename: Optional[str] = None
    content: Optional[str] = None
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    analysis_score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate data after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate all fields."""
        # Check required fields
        if self.id is None or not self.id:
            raise ModelValidationError("Missing required field: id")
        if self.filename is None or not self.filename:
            raise ModelValidationError("Missing required field: filename")
        if self.content is None or not self.content:
            raise ModelValidationError("Missing required field: content")
        
        # Check field types
        if not isinstance(self.id, str):
            raise ModelValidationError("Field 'id' must be a string")
        if not isinstance(self.filename, str):
            raise ModelValidationError("Field 'filename' must be a string")
        if not isinstance(self.content, str):
            raise ModelValidationError("Field 'content' must be a string")
        
        # Security Enhancement 1: Validate filename for path traversal
        if '../' in self.filename or '\\' in self.filename:
            raise ModelValidationError("Invalid filename format - path traversal not allowed")
        
        # Security Enhancement 2: Validate file extension (only PDF allowed)
        if not self.filename.lower().endswith('.pdf'):
            raise ModelValidationError("Only PDF files are supported")
        
        # Security Enhancement 3: Validate content length to prevent memory exhaustion
        max_content_length = 10_000_000  # 10MB text limit
        if len(self.content) > max_content_length:
            raise ModelValidationError(f"Content too large - maximum {max_content_length:,} characters allowed")
        
        # Validate optional fields if provided
        if self.analysis_score is not None:
            if not isinstance(self.analysis_score, (int, float)):
                raise ModelValidationError("Field 'analysis_score' must be a number")
            if not 0 <= self.analysis_score <= 100:
                raise ModelValidationError("Analysis score must be between 0 and 100")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'filename': self.filename,
            'content': self.content,
            'extracted_data': self.extracted_data,
            'analysis_score': self.analysis_score,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RFPProposal':
        """Create RFPProposal from dictionary data.
        
        Args:
            data: Dictionary containing proposal data
            
        Returns:
            New RFPProposal instance
            
        Raises:
            ModelValidationError: If required fields are missing or invalid
        """
        # Handle datetime field if present
        proposal_data = data.copy()  # Don't modify original
        if 'created_at' in proposal_data:
            if isinstance(proposal_data['created_at'], str):
                # Parse ISO format datetime string
                from datetime import datetime
                proposal_data['created_at'] = datetime.fromisoformat(proposal_data['created_at'].replace('Z', '+00:00'))
        
        # Filter only known fields to ignore extra fields gracefully
        known_fields = {'id', 'filename', 'content', 'extracted_data', 'analysis_score', 'created_at'}
        filtered_data = {k: v for k, v in proposal_data.items() if k in known_fields}
        
        # Create instance (this will trigger validation)
        return cls(**filtered_data)
    
    def __repr__(self) -> str:
        """Return string representation for debugging (excludes sensitive content)."""
        return (f"RFPProposal(id='{self.id}', filename='{self.filename}', "
                f"score={self.analysis_score}, "
                f"data_keys={list(self.extracted_data.keys()) if self.extracted_data else []})")


@dataclass
class AnalysisResult:
    """Represents the result of analyzing an RFP proposal.
    
    This class contains all analysis data including scores, rankings,
    and qualitative assessments.
    """
    
    # Default criteria weights for scoring
    DEFAULT_CRITERIA_WEIGHTS = {
        'price': 0.30,
        'technical_approach': 0.25,
        'experience': 0.20,
        'timeline': 0.15,
        'risk': 0.10
    }
    
    proposal_id: str
    criteria_scores: Dict[str, float]
    overall_score: Optional[float] = None
    strengths: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    recommendation_rank: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    _frozen: bool = field(default=False, init=False)
    
    def __post_init__(self):
        """Validate and calculate scores after initialization."""
        self._validate()
        
        # Calculate overall score if not provided
        if self.overall_score is None:
            self.overall_score = self._calculate_overall_score()
        
        # Freeze the object to make it immutable
        object.__setattr__(self, '_frozen', True)
    
    def __setattr__(self, name: str, value: Any):
        """Prevent modification after initialization."""
        if hasattr(self, '_frozen') and self._frozen:
            raise ModelValidationError("AnalysisResult is immutable after creation")
        super().__setattr__(name, value)
    
    def _validate(self):
        """Validate all fields."""
        # Check required fields
        if not self.proposal_id:
            raise ModelValidationError("Missing required field: proposal_id")
        if not self.criteria_scores:
            raise ModelValidationError("Missing required field: criteria_scores")
        
        # Validate score ranges
        if self.overall_score is not None:
            if not 0 <= self.overall_score <= 100:
                raise ModelValidationError("Score must be between 0 and 100")
        
        # Validate criteria scores
        for criterion, score in self.criteria_scores.items():
            if not isinstance(score, (int, float)):
                raise ModelValidationError(f"Criteria score for '{criterion}' must be a number")
            if not 0 <= score <= 100:
                raise ModelValidationError("Score must be between 0 and 100")
    
    def _calculate_overall_score(self) -> float:
        """Calculate weighted overall score from criteria scores."""
        total_score = 0.0
        total_weight = 0.0
        
        for criterion, score in self.criteria_scores.items():
            # Use default weight or equal weight if not in defaults
            weight = self.DEFAULT_CRITERIA_WEIGHTS.get(criterion, 1.0 / len(self.criteria_scores))
            total_score += score * weight
            total_weight += weight
        
        # Normalize to 0-100 scale
        return round(total_score / total_weight if total_weight > 0 else 0.0, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'proposal_id': self.proposal_id,
            'overall_score': self.overall_score,
            'criteria_scores': self.criteria_scores,
            'strengths': self.strengths,
            'concerns': self.concerns,
            'recommendation_rank': self.recommendation_rank,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """Create AnalysisResult from dictionary data.
        
        Args:
            data: Dictionary containing analysis result data
            
        Returns:
            New AnalysisResult instance
            
        Raises:
            ModelValidationError: If required fields are missing or invalid
        """
        # Handle datetime field if present
        result_data = data.copy()  # Don't modify original
        if 'created_at' in result_data:
            if isinstance(result_data['created_at'], str):
                # Parse ISO format datetime string
                from datetime import datetime
                result_data['created_at'] = datetime.fromisoformat(result_data['created_at'].replace('Z', '+00:00'))
        
        # Filter only known fields to ignore extra fields gracefully
        known_fields = {'proposal_id', 'criteria_scores', 'overall_score', 'strengths', 
                       'concerns', 'recommendation_rank', 'created_at'}
        filtered_data = {k: v for k, v in result_data.items() if k in known_fields}
        
        # Create instance (this will trigger validation and score calculation)
        return cls(**filtered_data)
    
    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return (f"AnalysisResult(proposal_id='{self.proposal_id}', "
                f"score={self.overall_score}, rank={self.recommendation_rank}, "
                f"criteria_count={len(self.criteria_scores)})")