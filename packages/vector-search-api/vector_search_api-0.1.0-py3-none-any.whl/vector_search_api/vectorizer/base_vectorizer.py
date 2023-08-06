from typing import Iterable, Tuple, Union


class BaseVectorizer:

    def __init__(self, dims: Union[int, Tuple] = 8, *args, **kwargs):

        if isinstance(dims, int) is True:
            dims = (dims, )
        self.dims: Tuple = dims

        self.args = args
        self.kwargs = kwargs

    def encode(self, values: Iterable) -> Iterable:
        """Encode the input values then return."""

        raise NotImplementedError


class BaseAsyncVectorizer(BaseVectorizer):

    def __init__(self, *args, **kwargs):
        super(BaseAsyncVectorizer, self).__init__(*args, **kwargs)

    async def encode(self, values: Iterable) -> Iterable:
        """Encode the input values then return."""

        raise NotImplementedError
