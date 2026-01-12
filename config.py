from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    perplexity_api_key: str | None

    # Model choices (tweak anytime)
    openai_model: str = "gpt-4o-mini"
    perplexity_model: str = "sonar-pro"

    @staticmethod
    def load() -> "Settings":
        # Loads from .env into environment variables
        load_dotenv()

        return Settings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
        )
