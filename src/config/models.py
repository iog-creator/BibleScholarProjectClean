from pydantic import BaseModel
from typing import Any, Dict, List

class ModelConfig(BaseModel):
    description: str
    prompt_format: str
    parameters: Dict[str, Any]

class APIConfig(BaseModel):
    lm_studio_url: str
    vector_search_url: str
    database_url: str
    api_call_timeout: float

class FeatureFlags(BaseModel):
    enable_thinking: bool
    max_processing_time: int
    normalize_retries: int
    normalize_strict_mode: bool
    interaction_logging_level: str
    rule_generation_threshold: float
    retry_delay_seconds: float

class VectorSearchConfig(BaseModel):
    embedding_model: str
    embedding_prompt: str
    reranker_model: str
    reranker_prompt: str
    search_limit: int
    vector_search_timeout: float

class TestingConfig(BaseModel):
    test_validation_rules: Dict[str, int]

class UIConfig(BaseModel):
    display_fields: List[str]

class Config(BaseModel):
    models: Dict[str, ModelConfig]
    api: APIConfig
    features: FeatureFlags
    vector_search: VectorSearchConfig
    testing: TestingConfig
    ui: UIConfig
    defaults: Dict[str, str] 