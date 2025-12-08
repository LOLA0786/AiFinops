import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class LLMConfig:
    provider: str | None = None  # 'xai', 'openai', 'gemini', 'anthropic'

@dataclass
class Settings:
    aws_profile: str | None = None
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    llm_config: LLMConfig | None = None

def get_settings() -> Settings:
    provider = os.getenv("LLM_PROVIDER")
    llm_cfg = LLMConfig(provider=provider) if provider else None
    return Settings(
        aws_profile=os.getenv("AWS_PROFILE"),
        aws_region=os.getenv("AWS_REGION", "us-east-1"),
        llm_config=llm_cfg,
    )
