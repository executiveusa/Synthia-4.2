"""
🔒 INPUT VALIDATION & SECURITY MODULE 🔒

Protects against spam, prompt injection, and malicious inputs
Applied to all API endpoints and agent inputs
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from functools import wraps
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration"""
    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|above|prior)",
        r"disregard\s+(instructions?|rules?|constraints?)",
        r"forget\s+(everything|all|instructions?)",
        r"you\s+are\s+now\s+",
        r"system\s*:\s*",
        r"assistant\s*:\s*",
        r"user\s*:\s*",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
        r"\[SYSTEM\",
        r"\[INST\",
        r"<<SYS>>",
        r"###\s*(System|Instruction)",
        r"new\s+instructions?:",
        r"override\s+(previous|settings?)",
        r"bypass\s+(security|restrictions?)",
        r"hack\s+(system|agent)",
        r"expose\s+(credentials|secrets?|keys?)",
        r"shell\s*exec",
        r"os\.system",
        r"subprocess",
        r"eval\s*\(",
        r"exec\s*\(",
        r"__import__",
        r"getattr\s*\(__builtins__",
        r"\b(cat|ls|pwd|whoami|id|env)\s*",
    ]
    
    # Spam patterns
    SPAM_PATTERNS = [
        r"(.)\1{10,}",  # Repeated characters
        r"[A-Z]{20,}",   # ALL CAPS shouting
        r"https?://\S{100,}",  # Very long URLs
        r"(buy|cheap|discount|sale|click\s+here).{0,50}(now|today|limited)",
        r"\$\d+\s*(million|billion)?\s*(offer|prize|won|winner)",
        r"(viagra|cialis|casino|lottery|inheritance|nigerian)",
        r"\b\d{16,}\b",  # Credit card-like numbers
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
    ]
    
    # Rate limiting
    MAX_INPUT_LENGTH = 10000
    MAX_REQUESTS_PER_MINUTE = 60


class InputValidator:
    """Validates and sanitizes all inputs"""
    
    def __init__(self):
        self.injection_regex = re.compile(
            "|".join(SecurityConfig.INJECTION_PATTERNS),
            re.IGNORECASE
        )
        self.spam_regex = re.compile(
            "|".join(SecurityConfig.SPAM_PATTERNS),
            re.IGNORECASE
        )
    
    def validate_text(self, text: str, context: str = "input") -> Tuple[bool, str, Optional[str]]:
        """
        Validate text input
        Returns: (is_valid, sanitized_text, error_message)
        """
        if not text:
            return True, "", None
        
        # Check length
        if len(text) > SecurityConfig.MAX_INPUT_LENGTH:
            return False, "", f"Input exceeds maximum length of {SecurityConfig.MAX_INPUT_LENGTH}"
        
        # Check for prompt injection
        if self.injection_regex.search(text):
            logger.warning(f"Prompt injection detected in {context}")
            return False, "", "Potentially harmful input detected"
        
        # Check for spam
        if self.spam_regex.search(text):
            logger.warning(f"Spam detected in {context}")
            return False, "", "Input flagged as spam"
        
        # Sanitize
        sanitized = self._sanitize(text)
        
        return True, sanitized, None
    
    def _sanitize(self, text: str) -> str:
        """Sanitize text input"""
        # Remove null bytes
        text = text.replace("\x00", "")
        
        # Normalize whitespace
        text = " ".join(text.split())
        
        # Remove control characters except newlines
        text = "".join(char for char in text if ord(char) >= 32 or char == "\n")
        
        # Escape HTML
        text = text.replace("<", "<").replace(">", ">")
        
        return text.strip()
    
    def validate_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """Validate code for dangerous patterns"""
        dangerous_patterns = [
            r"os\.system\s*\(",
            r"subprocess\.call\s*\(",
            r"subprocess\.run\s*\(",
            r"subprocess\.Popen\s*\(",
            r"eval\s*\(",
            r"exec\s*\(",
            r"__import__\s*\(",
            r"import\s+os\s*;\s*os\.system",
            r"open\s*\(\s*['\"]/etc/",
            r"open\s*\(\s*['\"]C:\\\\Windows",
            r"environ\[",
            r"getenv\s*\(",
            r"\.bashrc",
            r"\.ssh/",
            r"id_rsa",
            r"\.env",
            r"password\s*=",
            r"api_key\s*=",
            r"secret\s*=",
            r"token\s*=",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                logger.warning(f"Dangerous code pattern detected: {pattern}")
                return False, f"Dangerous code pattern detected: {pattern}"
        
        return True, None


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed under rate limit"""
        now = __import__('time').time()
        minute_ago = now - 60
        
        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > minute_ago
            ]
        else:
            self.requests[client_id] = []
        
        # Check limit
        if len(self.requests[client_id]) >= SecurityConfig.MAX_REQUESTS_PER_MINUTE:
            return False
        
        # Record request
        self.requests[client_id].append(now)
        return True


# Global instances
_validator = InputValidator()
_rate_limiter = RateLimiter()


def validate_input(func):
    """Decorator to validate function inputs"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Validate string arguments
        for key, value in kwargs.items():
            if isinstance(value, str):
                is_valid, sanitized, error = _validator.validate_text(value, key)
                if not is_valid:
                    raise HTTPException(status_code=400, detail=error)
                kwargs[key] = sanitized
        
        return await func(*args, **kwargs)
    return wrapper


def validate_api_input(data: Dict) -> Tuple[bool, Dict, Optional[str]]:
    """Validate API input data"""
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            is_valid, clean_value, error = _validator.validate_text(value, key)
            if not is_valid:
                return False, {}, error
            sanitized[key] = clean_value
        elif isinstance(value, dict):
            is_valid, nested, error = validate_api_input(value)
            if not is_valid:
                return False, {}, error
            sanitized[key] = nested
        elif isinstance(value, list):
            clean_list = []
            for item in value:
                if isinstance(item, str):
                    is_valid, clean_item, error = _validator.validate_text(item, key)
                    if not is_valid:
                        return False, {}, error
                    clean_list.append(clean_item)
                else:
                    clean_list.append(item)
            sanitized[key] = clean_list
        else:
            sanitized[key] = value
    
    return True, sanitized, None


def check_rate_limit(client_id: str) -> bool:
    """Check rate limit for client"""
    return _rate_limiter.is_allowed(client_id)


class SecureHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def get_headers() -> Dict[str, str]:
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }


# Encryption for sensitive data
class DataEncryption:
    """Simple encryption for sensitive data"""
    
    def __init__(self, key: Optional[str] = None):
        self.key = key or os.getenv("ENCRYPTION_KEY", "default-key-change-in-production")
    
    def encrypt(self, data: str) -> str:
        """Simple XOR encryption (use proper encryption in production)"""
        import base64
        encrypted = ""
        for i, char in enumerate(data):
            key_char = self.key[i % len(self.key)]
            encrypted += chr(ord(char) ^ ord(key_char))
        return base64.b64encode(encrypted.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data"""
        import base64
        try:
            encrypted = base64.b64decode(encrypted_data).decode()
            decrypted = ""
            for i, char in enumerate(encrypted):
                key_char = self.key[i % len(self.key)]
                decrypted += chr(ord(char) ^ ord(key_char))
            return decrypted
        except Exception:
            return ""


import os

__all__ = [
    "InputValidator",
    "validate_input",
    "validate_api_input",
    "check_rate_limit",
    "SecureHeaders",
    "DataEncryption",
    "SecurityConfig"
]