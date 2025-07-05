# Configuration Management Improvements

## Current Issues:
- Configuration scattered across multiple files (config.py, ncc_utils.py, core_utils.py)
- Environment variables hardcoded in multiple places
- No centralized settings management

## Recommended Solution:

```python
# Create: core/settings.py
from pydantic import BaseSettings
from typing import Optional
import os

class AppSettings(BaseSettings):
    # API Configuration
    GEMINI_API_KEY: str
    TEMP_CHAT: float = 0.3
    TEMP_QUIZ: float = 0.4
    MAX_TOKENS_CHAT: int = 1000
    MAX_TOKENS_QUIZ: int = 2000
    API_CALL_COOLDOWN_MINUTES: int = 2
    
    # Firebase Configuration
    FIREBASE_CONFIG_JSON: Optional[str] = None
    FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = None
    
    # App Configuration
    APP_TITLE: str = "NCC ABYAS"
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = AppSettings()
```
