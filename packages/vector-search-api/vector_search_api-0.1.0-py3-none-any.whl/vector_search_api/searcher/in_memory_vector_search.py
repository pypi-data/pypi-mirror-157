from typing import Any, Dict, List, Text

import numpy as np

from vector_search_api.helper.vector import cosine_similarity
from vector_search_api.helper.utils import batch_chunks
from vector_search_api.searcher.base_vector_search import BaseVectorSearch


class InMemoryVectorSearch(BaseVectorSearch):

    def __init__(self, project_name: Text, *args, **kwargs):
        super(InMemoryVectorSearch, self).__init__(*args, **kwargs)
        self.project_name = project_name
        self._data: Dict[Text, List[Any]] = {
            self.search_field: [],
            self.metadata_field: [],
            self.vector_field: [],
        }

    def create_project_if_not_exists(self) -> Dict[Text, Any]:
        """Create project if not exists."""

        if self._project is None:
            self._project = {'name': self.project_name}
        return self._project

    def get_project_or_none(self) -> Dict[Text, Any]:
        """Get project information or None."""

        return self._project

    def insert_documents(self, documents: List[Dict], batch_size: int = 200) -> List:
        """Insert documents."""

        self.create_project_if_not_exists()

        for batch_docs in batch_chunks(documents, batch_size=batch_size):
            for doc in batch_docs:
                self._data[self.search_field] += [doc[self.search_field]]
                self._data[self.metadata_field] += [doc[self.metadata_field]]
                self._data[self.vector_field] += [doc[self.vector_field]]

        self._data[self.vector_field] = np.array(self._data[self.vector_field])
        return self._data

    def search_documents(self, query: List, size: int = 3) -> List:
        """Search documents."""

        query = np.array(query)
        cos_sim = cosine_similarity(query, targets=self._data[self.vector_field])
        max_k_idx = np.argsort(cos_sim)[-size:][::-1]

        result: List[Dict] = [
            {
                self.search_field: self._data[self.search_field][idx],
                self.metadata_field: self._data[self.metadata_field][idx],
                self.vector_field: self._data[self.vector_field][idx],
                self.similarity_field: cos_sim[idx],
            } for idx in max_k_idx
        ]
        return result

    def refresh_documents(self, documents: List[Dict], batch_size: int = 200) -> List:
        self._data: Dict[Text, List[Any]] = {
            self.search_field: [],
            self.metadata_field: [],
            self.vector_field: [],
        }
        self.insert_documents(documents=documents, batch_size=batch_size)
        return self._data

    def count_documents(self) -> int:
        """Count documents."""

        return len(self._data.get(self.vector_field, []))
