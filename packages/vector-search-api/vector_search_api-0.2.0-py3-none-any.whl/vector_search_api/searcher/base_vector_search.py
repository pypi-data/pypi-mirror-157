from typing import TYPE_CHECKING, Any, Dict, List, Optional, Text, Tuple, Union

import numpy as np
from pydantic import BaseModel

if TYPE_CHECKING:
    from vector_search_api.vectorizer.base_vectorizer import BaseVectorizer


class BaseVectorSearch:
    """Base Vector Search ABC."""

    def __init__(
        self,
        *args,
        dims: Union[Tuple, int],
        search_field: Text = 'text',
        metadata_field: Text = 'metadata',
        vector_field: Text = 'vector',
        similarity_field: Text = 'similarity',
        vectorizer: Optional['BaseVectorizer'] = None,
        **kwargs
    ):
        if isinstance(dims, int) is True:
            dims = (dims, )
        self.dims: Tuple = dims

        self.search_field = search_field
        self.metadata_field = metadata_field
        self.vector_field = vector_field
        self.similarity_field = similarity_field
        self.vectorizer = vectorizer

        self._project: Optional[Union[BaseModel, Dict[Text, Any]]] = None

        self.args = args
        self.kwargs = kwargs

        if self.vectorizer is not None and self.dims != self.vectorizer.dims:
            raise ValueError(
                f"The dimension is mismatched, {self.dims} v.s. {vectorizer.dims}."
            )

    def create_project_if_not_exists(
        self, *args, **kwargs
    ) -> Union[BaseModel, Dict[Text, Any]]:
        """Create project."""

        raise NotImplementedError

    def get_project_or_none(
        self, *args, **kwargs
    ) -> Optional[Union[BaseModel, Dict[Text, Any]]]:
        """Get project information, return None if not exists.."""

        raise NotImplementedError

    def insert_documents(
        self,
        documents: List,
        batch_size: int = 200,
        apply_vectoring: bool = False,
        **kwargs
    ) -> List:
        """Insert documents"""

        raise NotImplementedError

    def search_documents(
        self, query: List, size: int = 20, *args, **kwargs
    ) -> List:
        """search documents"""

        raise NotImplementedError

    def refresh_documents(self) -> List:
        """Refresh vectors."""

        raise NotImplementedError

    def count_documents(self) -> int:
        """Count documents."""

        raise NotImplementedError


class BaseAsyncVectorSearch(BaseVectorSearch):
    """Base Asynchronized Vector Search ABC."""

    def __init__(self, *args, **kwargs):
        super(BaseAsyncVectorSearch, self).__init__(*args, **kwargs)

    # override
    async def create_project_if_not_exists(
        self, *args, **kwargs
    ) -> Union[BaseModel, Dict[Text, Any]]:
        """Create project."""

        raise NotImplementedError

    # override
    async def get_project_or_none(
        self, *args, **kwargs
    ) -> Optional[Union[BaseModel, Dict[Text, Any]]]:
        """Get project information, return None if not exists.."""

        raise NotImplementedError

    # override
    async def insert_documents(
        self,
        documents: List,
        batch_size: int = 200,
        apply_vectoring: bool = False,
        **kwargs
    ) -> List:
        """Insert documents"""

        raise NotImplementedError

    # override
    async def search_documents(
        self, query: List, size: int = 20, *args, **kwargs
    ) -> List:
        """search documents"""

        raise NotImplementedError

    # override
    async def refresh_documents(self) -> List:
        """Refresh vectors."""

        raise NotImplementedError

    # override
    async def count_documents(self) -> int:
        """Count documents."""

        raise NotImplementedError


class DummyTestVectorSearch(BaseVectorSearch):

    def __init__(self, project_name: Text, *args, **kwargs):
        super(DummyTestVectorSearch, self).__init__(*args, **kwargs)
        self.project_name = project_name
        self._data: List[Dict] = []

    def create_project_if_not_exists(self) -> Dict[Text, Any]:
        if self._project is None:
            self._project = {'name': self.project_name}
        return self._project

    def get_project_or_none(self) -> Dict[Text, Any]:
        return self._project

    def insert_documents(
        self,
        documents: List[Dict],
        batch_size: int = 200,
        apply_vectoring: bool = False
    ) -> List:

        self._data.extend([{
            self.search_field: doc[self.search_field],
            self.metadata_field: doc[self.metadata_field],
            self.vector_field: doc[self.vector_field],
        } for doc in documents])
        return self._data

    def search_documents(self, query: List, size: int = 3) -> List:
        import random

        result = random.choices(self._data, k=size)
        scores = np.random.random_sample(size)
        for doc, score in zip(result, scores):
            doc[self.similarity_field] = score

        return result

    def refresh_documents(self, documents: List[Dict], batch_size: int = 200) -> List:
        self._data = []
        self.insert_documents(documents=documents, batch_size=batch_size)
        return self._data

    def count_documents(self) -> int:
        return len(self._data)

