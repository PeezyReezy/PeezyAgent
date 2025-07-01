# PeezyAgent System Architecture

## Project Vision
**PeezyAgent** is an RFP analysis and recommendation system that helps users make informed vendor selection decisions by analyzing multiple proposal PDFs and providing ranked recommendations.

## System Overview

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │────│  Application    │────│   AI Analysis   │
│   (Flask/HTML)  │    │     Core        │    │  (Claude API)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │  PDF Processor  │
                       │   (PyPDF2)      │
                       └─────────────────┘
```

### Technology Stack
- **Backend**: Python 3.9+
- **Web Framework**: Flask (lightweight, perfect for MVP)
- **PDF Processing**: PyPDF2 or pdfplumber
- **AI Integration**: Anthropic Claude API (Sonnet 4)
- **Frontend**: HTML/CSS/JavaScript (minimal)
- **Data Storage**: In-memory (Python objects)

## Component Design

### 1. Web Interface Layer
**Responsibilities:**
- File upload handling (multiple PDFs)
- Display analysis results
- Export functionality (CSV/JSON)

**Key Files:**
- `src/web/app.py` - Flask application
- `src/web/templates/` - HTML templates
- `src/web/static/` - CSS/JS assets

### 2. Application Core
**Responsibilities:**
- Orchestrate the analysis workflow
- Manage in-memory data storage
- Coordinate between components

**Key Files:**
- `src/core/agent.py` - Main PeezyAgent class
- `src/core/models.py` - Data models (RFP, Analysis, etc.)
- `src/core/workflow.py` - Analysis workflow orchestration

### 3. PDF Processor
**Responsibilities:**
- Extract text from PDF files
- Structure extracted content
- Handle various PDF formats

**Key Files:**
- `src/processors/pdf_processor.py` - PDF text extraction
- `src/processors/content_parser.py` - Structure extracted content

### 4. AI Analysis Engine
**Responsibilities:**
- Interface with Claude API
- Generate analysis prompts
- Process AI responses into structured data

**Key Files:**
- `src/ai/claude_client.py` - Claude API integration
- `src/ai/prompt_templates.py` - Analysis prompts
- `src/ai/response_parser.py` - Parse AI responses

## Data Models

### RFP Proposal
```python
@dataclass
class RFPProposal:
    id: str
    filename: str
    content: str
    extracted_data: Dict[str, Any]
    analysis_score: Optional[float] = None
```

### Analysis Criteria (Fixed for MVP)
- **Price/Cost** (30% weight)
- **Technical Approach** (25% weight)
- **Experience/Qualifications** (20% weight)
- **Timeline/Delivery** (15% weight)
- **Risk Assessment** (10% weight)

### Analysis Result
```python
@dataclass
class AnalysisResult:
    proposal_id: str
    overall_score: float
    criteria_scores: Dict[str, float]
    strengths: List[str]
    concerns: List[str]
    recommendation_rank: int
```

## API Design

### Claude Integration
```python
class ClaudeAnalyzer:
    def analyze_proposal(self, content: str) -> AnalysisResult
    def compare_proposals(self, proposals: List[RFPProposal]) -> List[AnalysisResult]
    def generate_recommendation(self, analyses: List[AnalysisResult]) -> str
```

## Sprint Breakdown

### Sprint 1: Foundation & Configuration
- Project setup and dependencies
- Configuration management (API keys, settings)
- Basic logging system
- Core data models

### Sprint 2: PDF Processing
- PDF text extraction
- Content parsing and structuring
- Error handling for malformed PDFs

### Sprint 3: AI Integration
- Claude API client
- Prompt engineering for RFP analysis
- Response parsing and validation

### Sprint 4: Analysis Engine
- Scoring algorithm implementation
- Criteria weighting system
- Comparative analysis logic

### Sprint 5: Web Interface
- Flask application setup
- File upload functionality
- Results display and export

### Sprint 6: Integration & Testing
- End-to-end workflow testing
- Error handling and edge cases
- Performance optimization

## Configuration Requirements

### Environment Variables
```
ANTHROPIC_API_KEY=your_api_key_here
FLASK_SECRET_KEY=your_secret_key
MAX_FILE_SIZE=10MB
SUPPORTED_FILE_TYPES=.pdf
```

### Dependencies (requirements.txt)
```
flask>=2.3.0
anthropic>=0.3.0
PyPDF2>=3.0.0
python-dotenv>=1.0.0
werkzeug>=2.3.0
```

## Future Enhancements (Post-MVP)
- Configurable analysis criteria
- Database persistence (SQLite/PostgreSQL)
- User authentication
- Progress tracking for large uploads
- Advanced export formats
- Batch processing capabilities

## Success Criteria
- Successfully process 3-5 RFP PDFs simultaneously
- Generate meaningful analysis and rankings
- Provide clear reasoning for recommendations
- Complete analysis workflow in under 2 minutes
- Export results in usable format