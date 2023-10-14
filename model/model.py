from sentence_transformers.util import cos_sim
from sentence_transformers import SentenceTransformer

from config import SemanticModelsConfig as SMConfig


class SemanticSearchModel:
    """
    A class to handle semantic search model
    """

    def __init__(self) -> None:
        """
        Initialize the model
        """
        self.model = SentenceTransformer(
            SMConfig.MODEL_NAME, cache_folder=SMConfig.MODEL_PATH
        )

    def get_embedding_dims(self) -> int:
        """
        Get the embedding dimension of the model

        Returns:
            int: embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()

    def encode(self, text: str) -> list:
        """
        Encode the text

        Args:
            text: string

        Returns:
            list: list of float
        """
        return self.model.encode(text)

    def search(self, query: str, corpus: list, top_k: int = 5) -> list:
        """
        Search for the query in the corpus

        Args:
            query: string
            corpus: list of string
            top_k: int

        Returns:
            list: list of tuple (score, index)
        """
        query_embedding = self.encode(query)
        corpus_embeddings = self.encode(corpus)
        distances = cos_sim(query_embedding, corpus_embeddings)
        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1], reverse=True)
        return results[:top_k]
