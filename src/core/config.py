"""Configuration management for PeezyAgent.

This module provides centralized configuration management for the PeezyAgent
application, loading settings from environment variables with proper validation
and sensible defaults.
"""
import os
import secrets
import logging
import re
from typing import Optional
from functools import lru_cache


class ConfigError(Exception):
    """Raised when there are configuration errors.
    
    This exception is raised when required environment variables are missing
    or when configuration validation fails.
    """
    pass


class Config:
    """Manages application configuration from environment variables.
    
    This class centralizes all configuration management, loading settings
    from environment variables with proper validation and defaults.
    
    Required Environment Variables:
        ANTHROPIC_API_KEY: API key for Claude integration
    
    Optional Environment Variables:
        FLASK_SECRET_KEY: Secret key for Flask sessions (auto-generated if not provided)
        MAX_FILE_SIZE: Maximum file upload size (default: 10MB)
        SUPPORTED_FILE_TYPES: Supported file extensions (default: .pdf)
        LOAD_DOTENV: Whether to load .env file (default: true in development)
    
    Example:
        >>> config = Config()
        >>> print(config.anthropic_api_key)
        'sk-...'
        >>> print(config.max_file_size_bytes)
        10485760
    """
    
    # Default values for optional configuration
    DEFAULT_MAX_FILE_SIZE = '10MB'
    DEFAULT_SUPPORTED_FILE_TYPES = '.pdf'
    DEFAULT_LOAD_DOTENV = 'true'
    
    # File size conversion constants
    FILE_SIZE_UNITS = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4
    }
    
    def __init__(self, load_dotenv: bool = True):
        """Initialize configuration from environment variables.
        
        Args:
            load_dotenv: Whether to attempt loading .env file
        
        Raises:
            ConfigError: If required environment variables are missing.
        """
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Loading configuration from environment variables")
        
        # Load .env file if requested and available
        if load_dotenv:
            self._load_dotenv_if_available()
        
        # Load required configuration
        self.anthropic_api_key = self._get_required_env('ANTHROPIC_API_KEY')
        
        # Load optional configuration with defaults
        self.flask_secret_key = self._get_optional_env('FLASK_SECRET_KEY', self._generate_secret_key())
        self.max_file_size = self._get_optional_env('MAX_FILE_SIZE', self.DEFAULT_MAX_FILE_SIZE)
        self.supported_file_types = self._get_optional_env('SUPPORTED_FILE_TYPES', self.DEFAULT_SUPPORTED_FILE_TYPES)
        
        # Parse file size into bytes for easier use
        self.max_file_size_bytes = self._parse_file_size_to_bytes(self.max_file_size)
        
        # Validate configuration
        self.validate()
        
        # Log successful initialization
        self.logger.info(f"Configuration loaded successfully. Max upload: {self.max_file_size}")
        
        # Freeze configuration to prevent accidental modification
        self._frozen = True
    
    def _load_dotenv_if_available(self) -> None:
        """Load .env file if python-dotenv is available and .env exists."""
        try:
            from dotenv import load_dotenv
            if os.path.exists('.env'):
                load_dotenv()
                self.logger.info("Loaded configuration from .env file")
            else:
                self.logger.debug("No .env file found, using system environment variables only")
        except ImportError:
            self.logger.debug("python-dotenv not installed, using system environment variables only")
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise ConfigError.
        
        Args:
            key: The environment variable name.
            
        Returns:
            The environment variable value (stripped of whitespace).
            
        Raises:
            ConfigError: If the environment variable is not set or empty.
        """
        raw_value = os.environ.get(key)
        if raw_value is None:
            raise ConfigError(f"Missing required environment variable: {key}")
        
        value = raw_value.strip()
        if not value:
            raise ConfigError(f"Environment variable {key} cannot be empty")
        
        self.logger.debug(f"Loaded required environment variable: {key}")
        return value
    
    def _get_optional_env(self, key: str, default: str) -> str:
        """Get optional environment variable with default fallback.
        
        Args:
            key: The environment variable name.
            default: Default value if environment variable is not set.
            
        Returns:
            The environment variable value (stripped) or default.
        """
        raw_value = os.environ.get(key)
        if raw_value is None:
            self.logger.debug(f"Using default for {key}: {default}")
            return default
        
        value = raw_value.strip()
        if not value:
            self.logger.debug(f"Empty value for {key}, using default: {default}")
            return default
            
        self.logger.debug(f"Loaded optional environment variable: {key}")
        return value
    
    @lru_cache(maxsize=1)
    def _generate_secret_key(self) -> str:
        """Generate a cryptographically secure secret key for Flask.
        
        Returns:
            A 64-character hexadecimal secret key.
        """
        key = secrets.token_hex(32)
        self.logger.info("Generated new Flask secret key")
        return key
    
    def validate(self) -> None:
        """Validate the current configuration.
        
        Performs additional validation beyond basic presence checks.
        
        Raises:
            ConfigError: If configuration is invalid.
        """
        self.logger.debug("Validating configuration")
        
        # Validate API key format (basic check)
        if not self.anthropic_api_key.startswith('sk-'):
            raise ConfigError("ANTHROPIC_API_KEY must start with 'sk-'")
        
        # Validate file size format
        if not self._is_valid_file_size(self.max_file_size):
            raise ConfigError(f"Invalid MAX_FILE_SIZE format: {self.max_file_size}")
        
        # Validate supported file types
        if not self.supported_file_types.startswith('.'):
            raise ConfigError(f"SUPPORTED_FILE_TYPES must start with '.': {self.supported_file_types}")
        
        self.logger.debug("Configuration validation passed")
    
    def _is_valid_file_size(self, size_str: str) -> bool:
        """Check if file size string is valid.
        
        Args:
            size_str: File size string like '10MB', '5GB', etc.
            
        Returns:
            True if valid format, False otherwise.
        """
        pattern = r'^\d+(?:\.\d+)?[KMGT]?B$'
        return bool(re.match(pattern, size_str.upper()))
    
    def _parse_file_size_to_bytes(self, size_str: str) -> int:
        """Parse file size string to bytes.
        
        Args:
            size_str: File size string like '10MB', '5GB', etc.
            
        Returns:
            Size in bytes.
            
        Raises:
            ConfigError: If size format is invalid.
        """
        if not self._is_valid_file_size(size_str):
            raise ConfigError(f"Invalid file size format: {size_str}")
        
        size_str = size_str.upper()
        
        # Extract number and unit
        match = re.match(r'(\d+(?:\.\d+)?)([KMGT]?B)', size_str)
        if not match:
            raise ConfigError(f"Could not parse file size: {size_str}")
        
        number, unit = match.groups()
        
        try:
            size_bytes = int(float(number) * self.FILE_SIZE_UNITS[unit])
            self.logger.debug(f"Parsed {size_str} to {size_bytes} bytes")
            return size_bytes
        except (ValueError, KeyError) as e:
            raise ConfigError(f"Invalid file size: {size_str} - {e}")
    
    def __setattr__(self, name: str, value) -> None:
        """Prevent modification after initialization."""
        if hasattr(self, '_frozen') and self._frozen:
            raise ConfigError(f"Configuration is frozen. Cannot modify {name}")
        super().__setattr__(name, value)
    
    def __repr__(self) -> str:
        """Return string representation of config (without sensitive data)."""
        return (f"Config(api_key_set={bool(self.anthropic_api_key)}, "
                f"max_file_size='{self.max_file_size}' ({self.max_file_size_bytes} bytes), "
                f"supported_types='{self.supported_file_types}')")
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert configuration to dictionary.
        
        Args:
            include_sensitive: Whether to include sensitive values like API keys.
            
        Returns:
            Dictionary representation of configuration.
        """
        config_dict = {
            'max_file_size': self.max_file_size,
            'max_file_size_bytes': self.max_file_size_bytes,
            'supported_file_types': self.supported_file_types,
            'api_key_set': bool(self.anthropic_api_key),
        }
        
        if include_sensitive:
            config_dict['anthropic_api_key'] = self.anthropic_api_key
            config_dict['flask_secret_key'] = self.flask_secret_key
        
        return config_dict