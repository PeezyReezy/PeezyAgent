import pytest
from datetime import datetime
from src.core.models import RFPProposal, AnalysisResult, ModelValidationError


class TestRFPProposal:
    """Test RFP Proposal data model functionality."""
    
    def test_rfp_proposal_creation_with_required_fields(self):
        """Test that RFPProposal can be created with required fields."""
        # Arrange
        proposal_data = {
            'id': 'prop-001',
            'filename': 'vendor_a_proposal.pdf',
            'content': 'This is the extracted PDF content...'
        }
        
        # Act
        proposal = RFPProposal(**proposal_data)
        
        # Assert
        assert proposal.id == 'prop-001'
        assert proposal.filename == 'vendor_a_proposal.pdf'
        assert proposal.content == 'This is the extracted PDF content...'
        assert proposal.extracted_data == {}  # Default empty dict
        assert proposal.analysis_score is None  # Default None
        assert isinstance(proposal.created_at, datetime)

    def test_rfp_proposal_validates_required_fields(self):
        """Test that RFPProposal raises error for missing required fields."""
        # Act & Assert: Missing required fields should raise error
        with pytest.raises(ModelValidationError, match="Missing required field"):
            RFPProposal()  # No fields provided
        
        with pytest.raises(ModelValidationError, match="Missing required field"):
            RFPProposal(id='prop-001')  # Missing filename and content

    def test_rfp_proposal_validates_field_types(self):
        """Test that RFPProposal validates field types."""
        # Act & Assert: Wrong field types should raise error
        with pytest.raises(ModelValidationError, match="Field 'id' must be a string"):
            RFPProposal(id=123, filename='test.pdf', content='content')

    def test_rfp_proposal_to_dict_serialization(self):
        """Test that RFPProposal can be serialized to dictionary."""
        # Arrange
        proposal = RFPProposal(
            id='prop-001',
            filename='test.pdf',
            content='test content',
            extracted_data={'vendor': 'ACME Corp'},
            analysis_score=85.5
        )
        
        # Act
        proposal_dict = proposal.to_dict()
        
        # Assert
        assert proposal_dict['id'] == 'prop-001'
        assert proposal_dict['filename'] == 'test.pdf'
        assert proposal_dict['extracted_data']['vendor'] == 'ACME Corp'
        assert proposal_dict['analysis_score'] == 85.5
        assert 'created_at' in proposal_dict

    def test_rfp_proposal_from_dict_deserialization(self):
        """Test that RFPProposal can be created from dictionary."""
        # Arrange
        proposal_dict = {
            'id': 'prop-002',
            'filename': 'vendor_b.pdf',
            'content': 'Vendor B proposal content...',
            'extracted_data': {'vendor': 'Beta Corp', 'price': 50000},
            'analysis_score': 78.3
        }
        
        # Act
        proposal = RFPProposal.from_dict(proposal_dict)
        
        # Assert
        assert proposal.id == 'prop-002'
        assert proposal.filename == 'vendor_b.pdf'
        assert proposal.content == 'Vendor B proposal content...'
        assert proposal.extracted_data['vendor'] == 'Beta Corp'
        assert proposal.extracted_data['price'] == 50000
        assert proposal.analysis_score == 78.3

    def test_rfp_proposal_from_dict_ignores_extra_fields(self):
        """Test that from_dict ignores unknown fields gracefully."""
        # Arrange
        proposal_dict = {
            'id': 'prop-003',
            'filename': 'test.pdf',
            'content': 'test content',
            'unknown_field': 'should be ignored',
            'another_unknown': 123
        }
        
        # Act
        proposal = RFPProposal.from_dict(proposal_dict)
        
        # Assert
        assert proposal.id == 'prop-003'
        assert proposal.filename == 'test.pdf'
        assert proposal.content == 'test content'
        # Unknown fields should not cause errors

    def test_rfp_proposal_from_dict_validates_data(self):
        """Test that from_dict still validates required fields."""
        # Arrange: Missing required field
        invalid_dict = {
            'id': 'prop-004',
            'filename': 'test.pdf'
            # Missing 'content' field
        }
        
        # Act & Assert
        with pytest.raises(ModelValidationError, match="Missing required field"):
            RFPProposal.from_dict(invalid_dict)

    def test_rfp_proposal_repr_excludes_sensitive_data(self):
        """Test that __repr__ shows useful info without sensitive content."""
        # Arrange
        proposal = RFPProposal(
            id='prop-001',
            filename='sensitive_proposal.pdf',
            content='This contains confidential business information...',
            analysis_score=85.5
        )
        
        # Act
        repr_str = repr(proposal)
        
        # Assert
        assert 'prop-001' in repr_str
        assert 'sensitive_proposal.pdf' in repr_str
        assert '85.5' in repr_str
        assert 'confidential business information' not in repr_str  # Content not exposed
        assert 'RFPProposal' in repr_str

    def test_rfp_proposal_validates_filename_security(self):
        """Test that RFPProposal prevents path traversal attacks in filenames."""
        # Test various path traversal attempts
        dangerous_filenames = [
            '../../../etc/passwd',
            '..\\windows\\system32\\config',
            'normal_file/../../../secret.txt',
            'file\\with\\backslashes.pdf'
        ]
        
        for dangerous_filename in dangerous_filenames:
            with pytest.raises(ModelValidationError, match="Invalid filename format"):
                RFPProposal(
                    id='test-prop',
                    filename=dangerous_filename,
                    content='test content'
                )

    def test_rfp_proposal_validates_file_extension(self):
        """Test that RFPProposal only accepts PDF files."""
        # Test invalid extensions
        invalid_extensions = [
            'malicious_file.exe',
            'document.docx',
            'image.jpg',
            'script.js',
            'data.txt',
            'proposal'  # No extension
        ]
        
        for invalid_filename in invalid_extensions:
            with pytest.raises(ModelValidationError, match="Only PDF files are supported"):
                RFPProposal(
                    id='test-prop',
                    filename=invalid_filename,
                    content='test content'
                )
        
        # Test valid PDF extensions (should work)
        valid_extensions = ['proposal.pdf', 'DOCUMENT.PDF', 'file.Pdf']
        for valid_filename in valid_extensions:
            # Should not raise an exception
            proposal = RFPProposal(
                id='test-prop',
                filename=valid_filename,
                content='test content'
            )
            assert proposal.filename == valid_filename

    def test_rfp_proposal_validates_content_length(self):
        """Test that RFPProposal prevents memory exhaustion from huge content."""
        # Arrange: Create content that's too large (10MB + 1 byte)
        max_size = 10_000_000
        huge_content = 'x' * (max_size + 1)
        
        # Act & Assert: Should raise error for content too large
        with pytest.raises(ModelValidationError, match="Content too large"):
            RFPProposal(
                id='test-prop',
                filename='huge_file.pdf',
                content=huge_content
            )
        
        # Test boundary: exactly at limit should work
        boundary_content = 'x' * max_size
        proposal = RFPProposal(
            id='test-prop',
            filename='boundary_file.pdf',
            content=boundary_content
        )
        assert len(proposal.content) == max_size


class TestAnalysisResult:
    """Test Analysis Result data model functionality."""
    
    def test_analysis_result_creation_with_required_fields(self):
        """Test that AnalysisResult can be created with required fields."""
        # Arrange
        result_data = {
            'proposal_id': 'prop-001',
            'overall_score': 87.5,
            'criteria_scores': {
                'price': 90.0,
                'technical_approach': 85.0,
                'experience': 88.0
            }
        }
        
        # Act
        result = AnalysisResult(**result_data)
        
        # Assert
        assert result.proposal_id == 'prop-001'
        assert result.overall_score == 87.5
        assert result.criteria_scores['price'] == 90.0
        assert result.strengths == []  # Default empty list
        assert result.concerns == []  # Default empty list
        assert result.recommendation_rank is None  # Default None

    def test_analysis_result_validates_score_ranges(self):
        """Test that AnalysisResult validates score ranges (0-100)."""
        # Act & Assert: Invalid scores should raise error
        with pytest.raises(ModelValidationError, match="Score must be between 0 and 100"):
            AnalysisResult(
                proposal_id='prop-001',
                overall_score=150.0,  # Invalid: > 100
                criteria_scores={'price': 90.0}
            )
        
        with pytest.raises(ModelValidationError, match="Score must be between 0 and 100"):
            AnalysisResult(
                proposal_id='prop-001',
                overall_score=85.0,
                criteria_scores={'price': -10.0}  # Invalid: < 0
            )

    def test_analysis_result_calculates_overall_score_from_criteria(self):
        """Test that AnalysisResult can calculate overall score from criteria."""
        # Arrange: Don't provide overall_score, let it calculate
        criteria_scores = {
            'price': 80.0,                  # 30% weight = 24.0
            'technical_approach': 90.0,     # 25% weight = 22.5
            'experience': 85.0,             # 20% weight = 17.0
            'timeline': 75.0,               # 15% weight = 11.25
            'risk': 70.0                    # 10% weight = 7.0
        }
        
        # Act
        result = AnalysisResult(
            proposal_id='prop-001',
            criteria_scores=criteria_scores
        )
        
        # Assert: Should calculate weighted average
        expected_score = 24.0 + 22.5 + 17.0 + 11.25 + 7.0  # = 81.75
        assert abs(result.overall_score - expected_score) < 0.1

    def test_analysis_result_immutable_after_creation(self):
        """Test that AnalysisResult cannot be modified after creation."""
        # Arrange
        result = AnalysisResult(
            proposal_id='prop-001',
            overall_score=85.0,
            criteria_scores={'price': 90.0}
        )
        
        # Act & Assert: Should not be able to modify
        with pytest.raises(ModelValidationError, match="AnalysisResult is immutable"):
            result.overall_score = 95.0

    def test_analysis_result_from_dict_deserialization(self):
        """Test that AnalysisResult can be created from dictionary."""
        # Arrange
        result_dict = {
            'proposal_id': 'prop-001',
            'overall_score': 87.5,
            'criteria_scores': {
                'price': 90.0,
                'technical_approach': 85.0,
                'experience': 88.0
            },
            'strengths': ['Strong technical team', 'Competitive pricing'],
            'concerns': ['Tight timeline', 'Limited experience in this domain'],
            'recommendation_rank': 2
        }
        
        # Act
        result = AnalysisResult.from_dict(result_dict)
        
        # Assert
        assert result.proposal_id == 'prop-001'
        assert result.overall_score == 87.5
        assert result.criteria_scores['price'] == 90.0
        assert result.strengths == ['Strong technical team', 'Competitive pricing']
        assert result.concerns == ['Tight timeline', 'Limited experience in this domain']
        assert result.recommendation_rank == 2

    def test_analysis_result_repr_shows_key_info(self):
        """Test that __repr__ shows key information for debugging."""
        # Arrange
        result = AnalysisResult(
            proposal_id='prop-001',
            overall_score=87.5,
            criteria_scores={'price': 90.0, 'technical_approach': 85.0},
            recommendation_rank=1
        )
        
        # Act
        repr_str = repr(result)
        
        # Assert
        assert 'prop-001' in repr_str
        assert '87.5' in repr_str
        assert 'rank=1' in repr_str or 'recommendation_rank=1' in repr_str
        assert 'AnalysisResult' in repr_str