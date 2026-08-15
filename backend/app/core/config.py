import os

from pydantic import field_validator, computed_field
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


    #CORS origins and development/production configuration
    DEBUG: bool
    DEV_CORS_ORIGINS: str = ''
    CORS_ORIGINS: str

    # --- Security & JWT Settings ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @classmethod
    @field_validator('DATABASE_URL')
    def validate_db_url(cls, db_url: str) -> str:
        if db_url.startswith('sqlite:///./'):
            file_name = db_url.split('./')[1]
            db_path = os.path.join(PROJECT_ROOT, file_name)
            return f'sqlite:///{db_path}'
        return db_url


    @computed_field 
    @property
    def final_cors_origins(self) -> list[str]:
        if not self.CORS_ORIGINS:
            raise ValueError('no cors origins for production provided in the .env file')

        prod_origins_list = self.CORS_ORIGINS.split(',')
        dev_origins_list = self.DEV_CORS_ORIGINS.split(',') if self.DEV_CORS_ORIGINS else []

        if self.DEBUG:
            return  [*prod_origins_list, *dev_origins_list]
        return  prod_origins_list
        
    # Configure Pydantic to load settings from the specified .env file.
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
