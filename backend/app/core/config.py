import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Calculate the project's root directory dynamically.
# This walks up three levels from the current file (config.py -> core -> app -> PROJECT_ROOT)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#Define the path to the .env file using the project root.
ENV_PATH = os.path.join(PROJECT_ROOT, '.env')

class Settings(BaseSettings):
    """
    Defines the application's settings, loaded from the .env file.
    """
    # --- Database Settings ---
    DATABASE_URL: str
    PROJECT_NAME: str = 'LodgeOps Api'

    # --- Security & JWT Settings ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configure Pydantic to load settings from the specified .env file.
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
