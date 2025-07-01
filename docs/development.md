# Development Guide

## Quick Setup

### Prerequisites
- Python 3.9 or higher
- Git
- Anthropic API account

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/PeezyAgent.git
   cd PeezyAgent
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your actual values
   # Get your API key from: https://console.anthropic.com/
   ```

5. **Verify installation**
   ```bash
   python -m pytest tests/ -v
   ```

## Environment Configuration

### Required Variables
- `ANTHROPIC_API_KEY`: Your Anthropic API key (starts with 'sk-')

### Optional Variables
- `FLASK_SECRET_KEY`: Secret key for Flask sessions (auto-generated if not provided)
- `MAX_FILE_SIZE`: Maximum upload size (default: 10MB)
- `SUPPORTED_FILE_TYPES`: Supported file extensions (default: .pdf)

### Example .env File
```
ANTHROPIC_API_KEY=sk-your-anthropic-api-key-here
FLASK_SECRET_KEY=your-super-secret-key-for-flask
MAX_FILE_SIZE=50MB
SUPPORTED_FILE_TYPES=.pdf
```

## Project Structure

```
PeezyAgent/
├── src/                    # Main source code
│   ├── core/              # Core application components
│   │   ├── config.py      # Configuration management ✅
│   │   ├── models.py      # Data models (next sprint)
│   │   └── logger.py      # Logging configuration (next sprint)
│   ├── ai/                # AI integration
│   ├── processors/        # PDF processing
│   └── web/               # Web interface
├── tests/                 # Test files
│   ├── test_config.py     # Configuration tests ✅
│   └── ...
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # Project overview
```

## Development Workflow

### Test-Driven Development (TDD)
We follow strict TDD practices:

1. **RED**: Write a failing test that describes desired behavior
2. **GREEN**: Write minimal code to make the test pass
3. **REFACTOR**: Improve code quality while keeping tests green

### Example TDD Cycle
```bash
# 1. Write test (should fail)
python -m pytest tests/test_new_feature.py -v

# 2. Write minimal code to pass
# Edit source files...

# 3. Run tests (should pass)
python -m pytest tests/test_new_feature.py -v

# 4. Refactor and ensure tests still pass
python -m pytest tests/ -v
```

### Code Review Process
Every feature goes through:
1. **Implementation**: TDD cycle with tests
2. **Self-review**: Check against coding standards
3. **Peer review**: Code review for quality, security, performance
4. **Documentation**: Update relevant docs
5. **Integration**: Ensure all tests pass

## Running Tests

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test File
```bash
python -m pytest tests/test_config.py -v
```

### Run Tests with Coverage
```bash
pip install pytest-cov
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Categories
- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **Validation tests**: Test input validation and error handling

## Code Standards

### Python Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maximum line length: 88 characters (Black formatter)

### Documentation Requirements
- All public functions must have docstrings
- Include parameter types and return types
- Provide usage examples for complex functions
- Update relevant docs when changing functionality

### Testing Requirements
- All new code must have tests
- Test coverage should be > 90%
- Test both happy path and error conditions
- Use descriptive test names and docstrings

## Current Sprint Status

### Sprint 1: Foundation & Configuration ✅
**Completed:**
- [x] Configuration management with environment variables
- [x] Input validation and sanitization
- [x] Logging integration
- [x] Security features (config freezing, secret generation)
- [x] Comprehensive test coverage (12/12 tests passing)
- [x] Code review and refactoring

**Key Features Implemented:**
- Secure API key handling
- File size parsing with unit conversion
- Configuration validation
- .env file support
- Immutable configuration after initialization

### Next Sprint: Core Data Models
**Planned:**
- [ ] RFP Proposal data model
- [ ] Analysis Result data model
- [ ] Data validation and serialization
- [ ] Model relationships and constraints

## Troubleshooting

### Common Issues

**"python not found"**
- Ensure Python is in your PATH
- Try `py` instead of `python` on Windows

**"pytest not found"**
```bash
pip install pytest
```

**"ModuleNotFoundError: No module named 'src'"**
- Ensure you're running from the project root directory
- Check that `src/__init__.py` exists

**API key validation errors**
- Ensure your API key starts with 'sk-'
- Check for whitespace in .env file
- Verify the key is active in Anthropic console

### Getting Help
1. Check this documentation
2. Run tests to identify specific issues
3. Review error messages carefully
4. Check environment variable configuration

## Contributing

### Before Making Changes
1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Ensure all tests pass: `python -m pytest tests/ -v`
3. Follow TDD workflow for new features

### Submitting Changes
1. Write tests for your changes
2. Ensure all tests pass
3. Update documentation if needed
4. Create clear commit messages
5. Push and create pull request

### Commit Message Format
```
Add feature: Brief description of what was added

- Detailed bullet point of changes
- Another important change
- Any breaking changes noted
```

---

**Happy coding! 🚀**