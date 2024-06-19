# Importaciones necesarias
import asyncio
import numpy as np
from typing import List, Optional, Union, Dict
from annoy import AnnoyIndex
from nemoguardrails.embeddings.index import EmbeddingsIndex, IndexItem
from nemoguardrails.embeddings.embedding_providers import (
    EmbeddingModel,
    init_embedding_model,
)
from nemoguardrails import LLMRails

class SimpleEmbeddingSearchProvider(EmbeddingsIndex):


    def __init__(self,
                 embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2',
                 embedding_engine: str = 'SentenceTransformers',
                 embedding_size: int = 384,
                 use_batching: bool = False,
                 max_batch_size: int = 10,
                 max_batch_hold: float = 0.01):
        self.embedding_model = embedding_model
        self.embedding_engine = embedding_engine
        self._embedding_size = embedding_size
        self.use_batching = use_batching
        self.max_batch_size = max_batch_size
        self.max_batch_hold = max_batch_hold

        self._model: Optional[EmbeddingModel] = None
        self._index: Optional[AnnoyIndex] = AnnoyIndex(self._embedding_size, 'angular')  # Cambio aquí
        self._items: List[IndexItem] = []
        self._embeddings: List[List[float]] = []

        self._init_model()

    @property
    def embedding_size(self):
        return self._embedding_size

    def _init_model(self):
        self._model = init_embedding_model(embedding_model=self.embedding_model,
                                           embedding_engine=self.embedding_engine)

    async def add_item(self, item: IndexItem):
        embedding = await self._get_embedding(item.text)
        self._embeddings.append(embedding)
        self._items.append(item)
        self._index.add_item(len(self._items) - 1, embedding)

    async def add_items(self, items: List[IndexItem]):
        for item in items:
            await self.add_item(item)

    async def build(self):
        self._index.build(10)

    async def _get_embedding(self, text: str) -> List[float]:
        if self._model is None:
            self._init_model()
        embedding = await self._model.encode_async([text])
        return embedding[0]


    async def search(self, text: str, max_results: int = 5, distance_threshold: float = 1) -> List[IndexItem]:



        query_embedding = await self._get_embedding(text)
        ids, distances = self._index.get_nns_by_vector(query_embedding, 5, include_distances=True)


        results = []
        for id_, dist in zip(ids, distances):
            if distance_threshold is None or dist <= distance_threshold:
                #print(f"Palabra: {self._items[id_].text}, Distancia: {dist}")
                results.append(self._items[id_])


        #print(results)
        return results

def init(app: LLMRails):
    app.register_embedding_search_provider("simple", SimpleEmbeddingSearchProvider)