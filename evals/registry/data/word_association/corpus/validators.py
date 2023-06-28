import openai
import os
import numpy as np
from logger_config import logger
from abc import ABC, abstractmethod
from typing import Union, List, NamedTuple, Tuple
from collections.abc import Callable
from evals.completion_fns.openai import OpenAIChatCompletionFn

openai.api_key = os.environ.get("OPENAI_API_KEY")


class Embedding(NamedTuple):
    string: str
    vector: List[float]


class RelatedStrings(NamedTuple):
    string: str
    related_string: str | List[str]


class EmbeddingPair(NamedTuple):
    related_strings: RelatedStrings
    vectors: Tuple[Embedding]


class SimilarityTuple(NamedTuple):
    related_strings: RelatedStrings
    similar: bool


class QualityValidator(ABC):

    def __init__(self, target_score: int) -> None:
        self.target_score = target_score

    @abstractmethod
    def validate(self, related_strings: RelatedStrings) -> List[SimilarityTuple]:
        raise NotImplementedError


class EmbeddingsValidator(QualityValidator):

    def validate(self, related_strings: List[RelatedStrings],
                 similarity_function: Callable[[List[float], List[float]], float] = None) -> List[SimilarityTuple]:

        logger.info(f"Validating {len(related_strings)} related strings.")
        if similarity_function is None:
            similarity_function = self.calculate_cosine_similarity

        # flatten all strings
        all_strings = [string for pair in related_strings for string in (pair.string, pair.related_string)]
        logger.debug(f"{all_strings} flattened.")
        # get embeddings
        embeddings = self.get_embeddings(all_strings)
        logger.info(f"{len(embeddings)} embeddings processed.")
        # form EmbeddingPairs
        embedding_pairs = [
            EmbeddingPair(related_string, (embeddings[i], embeddings[i + 1]))
            for i, related_string in enumerate(related_strings)
        ]

        results = []
        # for each EmbeddingPair, compare their embeddings and form SimilarityTuple
        for pair in embedding_pairs:
            similarity = round(similarity_function(pair.vectors[0].vector, pair.vectors[1].vector), 3)
            similar = similarity > self.target_score
            results.append(SimilarityTuple(pair.related_strings, similar))
            print(f"{pair.related_strings.string},{pair.related_strings.related_string},{similar},{similarity}")
            # logger.info(f"{pair.related_strings} is similar: {similar} score:({similarity})")
        return results

    @staticmethod
    def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        vec1_norm = np.linalg.norm(vec1)
        vec2_norm = np.linalg.norm(vec2)
        similarity = np.dot(vec1, vec2) / (vec1_norm * vec2_norm)
        return similarity

    @staticmethod
    def calculate_euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
        raise NotImplementedError

    @staticmethod
    def get_embeddings(emb_input: Union[RelatedStrings, str, List[str], List[List[int]]]) -> List[Embedding]:
        response = openai.Embedding.create(model="text-embedding-ada-002", input=emb_input)
        response_data = response["data"]
        emb_list = [data["embedding"] for data in response_data]
        embeddings = [Embedding(string=string, vector=vector) for string, vector in zip(emb_input, emb_list)]
        return embeddings


class GPTValidator(QualityValidator):

    def validate(self, related_strings: RelatedStrings) -> List[SimilarityTuple]:
        raise NotImplementedError

    def get_chat_completion(self, related_strings: RelatedStrings) -> List[SimilarityTuple]:
        raise NotImplementedError


if __name__ == "__main__":
    validator = EmbeddingsValidator(0.75)
    embeddings = validator.get_embeddings(["test", "testing", "tested"])
    for embedding in embeddings:
        print(embedding.string, embedding.vector[0:5])
    similarity: SimilarityTuple = validator.validate([RelatedStrings("test", "testing"),
                                                      RelatedStrings("test", "tested")])
    print(similarity)
    # embedding = validator.get_embedding("world")
    # embedding2 = validator.get_embedding("globe, earth, man, planet")
    # similarity = validator.calculate_cosine_similarity(embedding, embedding2)
    # print(similarity)
    # validated = validator.validate("world", "globe, earth, man, planet")
    # print(validated)
