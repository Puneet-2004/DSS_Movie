from abc import ABC, abstractmethod
from typing import List, Dict, Any

from app.retrieval.models import RetrievalQuery


class BaseMovieFetcher(ABC):
    @abstractmethod
    def fetch(self, query: RetrievalQuery) -> List[Dict[str, Any]]:
        raise NotImplementedError