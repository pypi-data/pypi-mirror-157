from typing import TYPE_CHECKING, Any, Dict, List, Optional, Text, Tuple, Union

import numpy as np

from vector_search_api.config import settings
from vector_search_api.exceptions import EmptyVectorError
from vector_search_api.helper.utils import batch_chunks
from vector_search_api.helper.vector import cosine_similarity
from vector_search_api.searcher.base_vector_search import BaseVectorSearch

if TYPE_CHECKING:
    from vector_search_api.vectorizer.base_vectorizer import BaseVectorizer

logger = settings.logger


class InMemoryVectorSearch(BaseVectorSearch):

    def __init__(
        self,
        dims: Union[Tuple, int],
        project_name: Text,
        search_field: Text = 'text',
        metadata_field: Text = 'metadata',
        vector_field: Text = 'vector',
        similarity_field: Text = 'similarity',
        vectorizer: Optional['BaseVectorizer'] = None,
        **kwargs
    ):
        super(InMemoryVectorSearch, self).__init__(
            dims=dims,
            search_field=search_field,
            metadata_field=metadata_field,
            vector_field=vector_field,
            similarity_field=similarity_field,
            vectorizer=vectorizer,
            **kwargs
        )
        self.project_name = project_name
        self._project = {'project_name': self.project_name}

        self._data: Dict[Text, List[Any]] = {
            self.search_field: [],
            self.metadata_field: [],
            self.vector_field: [],
        }
        self._index = np.array([])

    def create_project_if_not_exists(self) -> Dict[Text, Any]:
        """Create project if not exists."""

        if self._project is None:
            self._project = {'name': self.project_name}
        return self._project

    def get_project_or_none(self) -> Dict[Text, Any]:
        """Get project information or None."""

        return self._project

    def insert_documents(
        self,
        documents: List[Dict],
        batch_size: int = 200,
        apply_vectoring: bool = False
    ) -> List:
        """Insert documents."""

        self.create_project_if_not_exists()

        if apply_vectoring is True and self.vectorizer is None:
            logger.warning(f"Apply vectoring when insert document but vectorizer is None.")
            apply_vectoring = False

        for batch_docs in batch_chunks(documents, batch_size=batch_size):

            if apply_vectoring is True:
                vectors = self.vectorizer.encode(
                    values=[doc[self.search_field] for doc in batch_docs]
                )
            else:
                vectors = [(
                    doc[self.vector_field] if doc[self.vector_field] is not None
                    else self._raise_empty_vector_error('A document has empty vector.')
                ) for doc in batch_docs]

            for doc, vec in zip(batch_docs, vectors):
                self._data[self.search_field] += [doc[self.search_field]]
                self._data[self.metadata_field] += [doc[self.metadata_field]]
                self._data[self.vector_field] += [vec]

        self._set_index(vectors=self._data[self.vector_field])
        return self._data

    def search_documents(self, query: List, size: int = 3) -> List:
        """Search documents."""

        cos_sim = cosine_similarity(np.array(query), targets=self._index)
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

    def refresh_documents(
        self,
        documents: List[Dict],
        batch_size: int = 200,
        apply_vectoring: bool = False
    ) -> List:
        """Refresh by new documents."""

        self._data: Dict[Text, List[Any]] = {
            self.search_field: [],
            self.metadata_field: [],
            self.vector_field: [],
        }
        self.insert_documents(
            documents=documents,
            batch_size=batch_size,
            apply_vectoring=apply_vectoring
        )
        return self._data

    def count_documents(self) -> int:
        """Count documents."""

        return len(self._data.get(self.vector_field, []))


    def _set_index(self, vectors: List[List[float]]) -> np.array:
        """Set searching index."""

        self._index = np.array(vectors)

    def _raise_empty_vector_error(self, msg: Text):
        """If vector is empty, then raise Error."""

        raise EmptyVectorError(msg)
