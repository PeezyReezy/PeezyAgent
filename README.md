# PeezyAgent

A task automation agent for RFP analysis and vendor recommendation.

## Project Goals
- Learn how to build AI agents
- Understand agent architectures  
- Practice with AI frameworks
- Build a real-world business application
- Implement proper software development practices (TDD, code reviews, sprints)

## What It Does
PeezyAgent analyzes multiple RFP (Request for Proposal) response PDFs and provides ranked recommendations on which vendor to select, along with detailed reasoning.

## Project Structure
- `src/` - Main source code
  - `core/` - Core application components (config, models, etc.)
  - `ai/` - AI integration and analysis engine
  - `processors/` - PDF processing and content extraction
  - `web/` - Web interface components
- `tests/` - Test files with comprehensive coverage
- `docs/` - Documentation
- `config/` - Configuration files
- `data/` - Sample data

## Quick Start

### Prerequisites
- Python 3.9+
- Anthropic API key

### Installation
```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/PeezyAgent.git
cd PeezyAgent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables
Create a `.env` file with:
```
ANTHROPIC_API_KEY=sk-your-anthropic-api-key-here
FLASK_SECRET_KEY=your-secret-key (optional - will auto-generate)
MAX_FILE_SIZE=10MB
SUPPORTED_FILE_TYPES=.pdf
```

## Documentation
- 📋 [Architecture](docs/ARCHITECTURE.md) - System design and technical architecture
- 🚀 [Development Guide](docs/DEVELOPMENT.md) - Setup and contribution guidelines
- 📚 [Full Documentation](docs/) - Complete documentation

## Technology Stack
- **Backend**: Python 3.9+ with Flask
- **AI Integration**: Claude API (Anthropic) for analysis
- **PDF Processing**: PyPDF2 for document extraction
- **Web Interface**: Flask with HTML/CSS/JavaScript
- **Configuration**: Environment variables with python-dotenv
- **Testing**: pytest with comprehensive test coverage

## Development Status

### 🎯 Sprint Progress
- ✅ **Sprint 0**: Architecture and design complete
- ✅ **Sprint 1**: Foundation & configuration complete
  - ✅ Task 1: Configuration management with validation, logging, and security
  - ⏳ Task 2: Core data models (next)
  - ⏳ Task 3: Logging system integration
  - ⏳ Task 4: Project dependencies finalization
- ⏳ **Sprint 2**: PDF processing
- ⏳ **Sprint 3**: AI integration with Claude
- ⏳ **Sprint 4**: Analysis engine and scoring
- ⏳ **Sprint 5**: Web interface
- ⏳ **Sprint 6**: Integration & testing

### 🔧 Current Features
- **Configuration Management**: Secure, validated environment variable handling
- **Logging System**: Comprehensive logging with proper levels
- **Input Validation**: API key format validation, file size parsing
- **Security**: Configuration freezing, secret key generation
- **Developer Experience**: Type hints, comprehensive documentation, TDD approach

### 🧪 Testing
- 12/12 tests passing
- Test-driven development approach
- Code coverage for all core functionality
- Comprehensive validation testing

## Contributing
1. Follow the TDD approach (tests first, then code)
2. All code must pass existing tests
3. New features require new tests
4. Code review process for all changes
5. Follow Python style guidelines (PEP 8)

## License
This project is for educational purposes.

---

**Next Sprint Goal**: Implement core data models for RFP proposals and analysis results.