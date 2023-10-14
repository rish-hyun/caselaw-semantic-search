import os
from dotenv import load_dotenv

load_dotenv()


class ElasticSearchConfig:
    SCHEME: str = os.getenv("ELASTIC_SCHEME", "http")
    HOST: str = os.getenv("ELASTIC_HOST", "localhost")
    PORT: int = int(os.getenv("ELASTIC_PORT", 9200))
    INDEX: str = os.getenv("ELASTIC_INDEX")


class SemanticModelsConfig:
    MODEL_PATH: str = "./model/cache"
    MODEL_NAME: str = "all-MiniLM-L12-v2"
