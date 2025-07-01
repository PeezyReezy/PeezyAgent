import pytest
import os
import logging
from unittest.mock import patch
from src.core.config import Config, ConfigError


class TestConfig:
    """Test configuration management functionality."""
    
    def test_config_loads_from_environment_variables(self):
        """Test that Config can load values from environment variables."""
        # Arrange: Set up test environment variables with realistic values
        test_env_vars = {
            'ANTHROPIC_API_KEY': 'sk-test-api-key-123456789abcdef',  # Realistic format
            'FLASK_SECRET_KEY': 'test-secret-key-456',
            'MAX_FILE_SIZE': '10MB',
            'SUPPORTED_FILE_TYPES': '.pdf'
        }
        
        # Act: Load config with mocked environment
        with patch.dict(os.environ, test_env_vars):
            config = Config(load_dotenv=False)  # Skip dotenv loading in tests
        
        # Assert: Verify config loaded correctly
        assert config.anthropic_api_key == 'sk-test-api-key-123456789abcdef'
        assert config.flask_secret_key == 'test-secret-key-456'
        assert config.max_file_size == '10MB'
        assert config.max_file_size_bytes == 10485760  # 10MB in bytes
        assert config.supported_file_types == '.pdf'

    def test_config_raises_error_for_missing_required_keys(self):
        """Test that Config raises error when required environment variables are missing."""
        # Arrange: Clear environment of required variables
        with patch.dict(os.environ, {}, clear=True):
            # Act & Assert: Should raise ConfigError
            with pytest.raises(ConfigError, match="Missing required environment variable"):
                Config(load_dotenv=False)

    def test_config_provides_default_values(self):
        """Test that Config provides sensible defaults for optional settings."""
        # Arrange: Set only required variables with realistic format
        required_vars = {
            'ANTHROPIC_API_KEY': 'sk-test-key-for-defaults-123'
        }
        
        # Act: Load config with minimal environment
        with patch.dict(os.environ, required_vars, clear=True):
            config = Config(load_dotenv=False)
        
        # Assert: Should have default values
        assert config.max_file_size == '10MB'  # default
        assert config.max_file_size_bytes == 10485760  # default in bytes
        assert config.supported_file_types == '.pdf'  # default
        assert config.flask_secret_key is not None  # should generate one
        assert len(config.flask_secret_key) == 64  # 32 bytes hex = 64 chars

    def test_config_validates_api_key_format(self):
        """Test that Config validates API key format."""
        # Arrange: Set invalid API key format
        invalid_env_vars = {
            'ANTHROPIC_API_KEY': 'invalid-key-format'  # Doesn't start with 'sk-'
        }
        
        # Act & Assert: Should raise ConfigError
        with patch.dict(os.environ, invalid_env_vars, clear=True):
            with pytest.raises(ConfigError, match="ANTHROPIC_API_KEY must start with 'sk-'"):
                Config(load_dotenv=False)

    def test_config_validates_file_size_format(self):
        """Test that Config validates file size format."""
        # Arrange: Set invalid file size format
        invalid_env_vars = {
            'ANTHROPIC_API_KEY': 'sk-valid-key-123',
            'MAX_FILE_SIZE': 'invalid-size'  # Invalid format
        }
        
        # Act & Assert: Should raise ConfigError
        with patch.dict(os.environ, invalid_env_vars, clear=True):
            with pytest.raises(ConfigError, match="Invalid file size format"):
                Config(load_dotenv=False)

    def test_config_validates_supported_file_types(self):
        """Test that Config validates supported file types format."""
        # Arrange: Set invalid file types format
        invalid_env_vars = {
            'ANTHROPIC_API_KEY': 'sk-valid-key-123',
            'SUPPORTED_FILE_TYPES': 'pdf'  # Missing dot
        }
        
        # Act & Assert: Should raise ConfigError
        with patch.dict(os.environ, invalid_env_vars, clear=True):
            with pytest.raises(ConfigError, match="SUPPORTED_FILE_TYPES must start with '.'"):
                Config(load_dotenv=False)

    def test_config_handles_empty_environment_variables(self):
        """Test that Config handles empty environment variables properly."""
        # Arrange: Set empty values
        empty_env_vars = {
            'ANTHROPIC_API_KEY': '   ',  # Only whitespace
        }
        
        # Act & Assert: Should raise ConfigError
        with patch.dict(os.environ, empty_env_vars, clear=True):
            with pytest.raises(ConfigError, match="Environment variable ANTHROPIC_API_KEY cannot be empty"):
                Config(load_dotenv=False)

    def test_config_parses_different_file_sizes(self):
        """Test that Config correctly parses different file size formats."""
        test_cases = [
            ('5MB', 5242880),
            ('1GB', 1073741824),
            ('2.5MB', 2621440),
            ('100KB', 102400),
            ('1TB', 1099511627776)
        ]
        
        for size_str, expected_bytes in test_cases:
            # Arrange
            env_vars = {
                'ANTHROPIC_API_KEY': 'sk-test-key-123',
                'MAX_FILE_SIZE': size_str
            }
            
            # Act
            with patch.dict(os.environ, env_vars, clear=True):
                config = Config(load_dotenv=False)
            
            # Assert
            assert config.max_file_size == size_str
            assert config.max_file_size_bytes == expected_bytes

    def test_config_is_frozen_after_initialization(self):
        """Test that Config cannot be modified after initialization."""
        # Arrange: Create a valid config
        env_vars = {
            'ANTHROPIC_API_KEY': 'sk-test-key-123'
        }
        
        # Act: Try to modify config after creation
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config(load_dotenv=False)
        
        # Assert: Should raise ConfigError when trying to modify
        with pytest.raises(ConfigError, match="Configuration is frozen"):
            config.anthropic_api_key = 'sk-new-key'

    def test_config_logging_initialization(self, caplog):
        """Test that Config logs initialization process."""
        # Arrange: Set up test environment
        test_env_vars = {
            'ANTHROPIC_API_KEY': 'sk-test-key-123'
        }
        
        # Act: Create config with logging
        with patch.dict(os.environ, test_env_vars, clear=True):
            with caplog.at_level(logging.INFO):
                config = Config(load_dotenv=False)
        
        # Assert: Check that initialization was logged
        assert "Loading configuration from environment variables" in caplog.text
        assert "Configuration loaded successfully" in caplog.text
        assert config.logger.name == "src.core.config"

    def test_config_to_dict_excludes_sensitive_data(self):
        """Test that to_dict() excludes sensitive data by default."""
        # Arrange
        env_vars = {
            'ANTHROPIC_API_KEY': 'sk-secret-key-123'
        }
        
        # Act
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config(load_dotenv=False)
            config_dict = config.to_dict()
        
        # Assert: Sensitive data should not be included
        assert 'anthropic_api_key' not in config_dict
        assert 'flask_secret_key' not in config_dict
        assert config_dict['api_key_set'] is True
        assert config_dict['max_file_size'] == '10MB'

    def test_config_to_dict_includes_sensitive_data_when_requested(self):
        """Test that to_dict() includes sensitive data when explicitly requested."""
        # Arrange
        env_vars = {
            'ANTHROPIC_API_KEY': 'sk-secret-key-123'
        }
        
        # Act
        with patch.dict(os.environ, env_vars, clear=True):
            config = Config(load_dotenv=False)
            config_dict = config.to_dict(include_sensitive=True)
        
        # Assert: Sensitive data should be included
        assert config_dict['anthropic_api_key'] == 'sk-secret-key-123'
        assert 'flask_secret_key' in config_dict
        assert config_dict['api_key_set'] is True