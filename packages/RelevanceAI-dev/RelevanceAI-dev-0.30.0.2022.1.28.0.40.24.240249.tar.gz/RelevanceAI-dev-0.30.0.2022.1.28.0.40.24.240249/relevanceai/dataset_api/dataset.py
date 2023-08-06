"""
Pandas like dataset API
"""
import re
import math
import warnings
import pandas as pd
import numpy as np

from doc_utils import DocUtils

from typing import Dict, List, Union, Callable, Optional

from relevanceai.dataset_api.groupby import Groupby, Agg
from relevanceai.dataset_api.centroids import Centroids

from relevanceai.vector_tools.client import VectorTools
from relevanceai.api.client import BatchAPIClient

from relevanceai.dataset_api.helpers import _build_filters


class Series(BatchAPIClient):
    """
    Dataset Series Object
    -----------------------------

    A wrapper class for being able to vectorize documents over field

    Parameters
    ----------
    project : str
        Project name on RelevanceAI
    api_key : str
        API key for RelevanceAI
    dataset_id : str
        Data type for the output Series. If not specified, this will be
        inferred from `data`.
        See the :ref:`user guide <basics.dtypes>` for more usages.
    field : str
        The name of the field with the Dataset.

    Examples
    --------
    Assuming the following code as been executed:

    .. code-block::

        from relevanceai import client
        relevanceai.datasets import get_dummy_ecommerce_dataset

        documents = get_dummy_ecommerce_dataset()
        client = Client()

        df = client.Dataset('ecommerce')
        df.create()
        df.insert_documents(documents)

    Retrieve a Series from your dataset

    .. code-block::

        product_images = df['product_image'] # A Series object of every every product image url in dataset

    """

    def __init__(self, project: str, api_key: str, dataset_id: str, field: str):
        self.project = project
        self.api_key = api_key
        self.dataset_id = dataset_id
        self.field = field
        super().__init__(project=project, api_key=api_key)

    def sample(
        self,
        n: int = 1,
        frac: float = None,
        filters: list = [],
        random_state: int = 0,
        include_vector: bool = True,
        output_format="pandas",
    ):
        """
        Return a random sample of items from a dataset.

        Parameters
        ----------
        n : int
            Number of items to return. Cannot be used with frac.
        frac: float
            Fraction of items to return. Cannot be used with n.
        filters: list
            Query for filtering the search results
        random_state: int
            Random Seed for retrieving random documents.

        Example
        -------
        .. code-block::

            from relevanceai import client

            client = Client()

            df = client.Dataset(dataset_id)
            df.sample(n=3)

        """
        select_fields = [self.field] if isinstance(self.field, str) else self.field
        if output_format == "json":
            return Dataset(self.project, self.api_key)(self.dataset_id).sample(
                n=n,
                frac=frac,
                filters=filters,
                random_state=random_state,
                select_fields=select_fields,
                include_vector=include_vector,
            )
        return Dataset(self.project, self.api_key)(self.dataset_id).sample(
            n=n,
            frac=frac,
            filters=filters,
            random_state=random_state,
            select_fields=select_fields,
            include_vector=include_vector,
        )

    head = sample

    def all(
        self,
        chunksize: int = 1000,
        filters: List = [],
        sort: List = [],
        include_vector: bool = True,
        show_progress_bar: bool = True,
    ):
        select_fields = [self.field] if isinstance(self.field, str) else self.field
        return Dataset(self.project, self.api_key)(self.dataset_id).all(
            chunksize=chunksize,
            filters=filters,
            sort=sort,
            select_fields=select_fields,
            include_vector=include_vector,
            show_progress_bar=show_progress_bar,
        )

    def vectorize(self, model) -> None:
        """
        Vectorises over a field give a model architecture

        Parameters
        ----------
        model : Machine learning model for vectorizing text`
            The dataset_id of concern

        Example
        -------
        .. code-block::

            from relevanceai import Client
            from vectorhub.encoders.text.sentence_transformers import SentenceTransformer2Vec

            model = SentenceTransformer2Vec("all-mpnet-base-v2 ")

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            text_field = "text_field"
            df.vectorize(text_field, model)
        """
        if hasattr(model, "encode_documents"):

            def encode_documents(documents):
                return model.encode_documents(self.field, documents)

        else:

            def encode_documents(documents):
                return model([self.field], documents)

        self.pull_update_push(self.dataset_id, encode_documents)

    def apply(
        self,
        func: Callable,
        output_field: str,
        axis: int = 0,
    ):
        """
        Apply a function along an axis of the DataFrame.

        Objects passed to the function are Series objects whose index is either the DataFrame’s index (axis=0) or the DataFrame’s columns (axis=1). By default (result_type=None), the final return type is inferred from the return type of the applied function. Otherwise, it depends on the result_type argument.

        Parameters
        --------------
        func: function
            Function to apply to each document

        axis: int
            Axis along which the function is applied.
            - 9 or 'index': apply function to each column
            - 1 or 'columns': apply function to each row

        output_field: str
            The field from which to output

        Example
        ---------------
        .. code-block::

            from relevanceai import Client

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            df["sample_1_label"].apply(lambda x: x + 3)

        """
        if axis == 1:
            raise ValueError("We do not support column-wise operations!")

        def bulk_fn(documents):
            for d in documents:
                try:
                    if self.is_field(self.field, d):
                        self.set_field(
                            output_field, d, func(self.get_field(self.field, d))
                        )
                except Exception as e:
                    continue
            return documents

        return self.pull_update_push(
            self.dataset_id, bulk_fn, select_fields=[self.field]
        )

    def numpy(self) -> np.ndarray:
        """
        Iterates over all documents in dataset and returns all numeric values in a numpy array.

        Parameters
        ---------
        None

        Returns
        -------
        vectors: np.ndarray
            an array/matrix of all numeric values selected

        Example
        ---------------
        .. code-block::

            from relevanceai import Client

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            field = "sample_field"
            arr = df[field].numpy()
        """
        documents = self._get_all_documents(self.dataset_id, select_fields=[self.field])
        vectors = [np.array(document[self.field]) for document in documents]
        vectors = np.array(vectors)
        return vectors

    def value_counts(
        self,
        normalize: bool = False,
        ascending: bool = False,
        sort: bool = False,
        bins: Optional[int] = None,
    ):
        """
        Return a Series containing counts of unique values (or values with in a range if bins is set).

        Parameters
        ----------
        normalize : bool, default False
            If True then the object returned will contain the relative frequencies of the unique values.
        ascending : bool, default False
            Sort in ascending order.
        bins : int, optional
            Groups categories into 'bins'. These bins are good for representing groups within continuous series

        Returns
        ----------
        Series

        Example
        ---------------
        .. code-block::

            from relevanceai import Client

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            field = "sample_field"
            value_counts_df = df[field].value_counts()
        """
        schema = self.datasets.schema(self.dataset_id)
        dtype = schema[self.field]

        if dtype == "numeric":
            agg_type = dtype
        else:
            agg_type = "category"

        groupby_query = [{"name": self.field, "field": self.field, "agg": agg_type}]
        aggregation = self.services.aggregate.aggregate(
            self.dataset_id,
            groupby=groupby_query,
            page_size=10000,
            asc=ascending,
        )

        total = self.get_number_of_documents(dataset_id=self.dataset_id)
        aggregation = pd.DataFrame(aggregation)

        if normalize:
            aggregation["frequency"] /= total

        if bins is not None:
            vals = []
            for agg in [[agg[0]] * int(agg[1]) for agg in aggregation.values]:
                vals += agg

            vals = pd.cut(vals, bins)

            categories = [
                "({}, {}]".format(interval.left, interval.right) for interval in vals
            ]
            unique_categories = list(set(categories))

            if sort:
                categories = sorted(
                    categories, key=lambda x: float(x.split(",")[0][1:])
                )

            aggregation = pd.DataFrame(
                [categories.count(cat) for cat in unique_categories],
                index=unique_categories,
            )
            aggregation.columns = ["Frequency"]

        return aggregation

    def __getitem__(self, loc: Union[int, str]):
        """
        Indexs a value with a series, usually to get a specific sample from a column in your dataset

        Parameters
        ----------
        loc : int or str, preferably a str
            if int, this operates exactly as indexing a regular python list
            if str, this will be a string corresponding to the _id of the document

        Returns
        ----------
        A single document

        Example
        ---------------
        .. code-block::

            from relevanceai import Client

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            field = "sample_field"
            id = "sample_id"
            index = 56

            document = df[field][id]
            document = df[field][index]
        """
        if isinstance(loc, int):
            warnings.warn(
                "Integer selection of dataframe is not stable at the moment. Please use a string ID if possible to ensure exact selection."
            )
            return self.get_documents(
                self.dataset_id, loc + 1, select_fields=[self.field]
            )[loc][self.field]
        elif isinstance(loc, str):
            return self.datasets.documents.get(self.dataset_id, loc)[self.field]
        raise TypeError("Incorrect data type! Must be a string or an integer")


class Read(BatchAPIClient):
    """

    Dataset Read
    -------------------

    A Pandas Like datatset API for interacting with the RelevanceAI python package
    """

    def __init__(self, project: str, api_key: str):
        self.project = project
        self.api_key = api_key
        self.vector_tools = VectorTools(project=project, api_key=api_key)
        super().__init__(project=project, api_key=api_key)

    def __call__(
        self,
        dataset_id: str,
        image_fields: List = [],
        text_fields: List = [],
        audio_fields: List = [],
        highlight_fields: dict = {},
        output_format: str = "pandas",
    ):
        self.dataset_id = dataset_id
        self.image_fields = image_fields
        self.text_fields = text_fields
        self.audio_fields = audio_fields
        self.highlight_fields = highlight_fields
        self.output_format = output_format
        self.groupby = Groupby(self.project, self.api_key, self.dataset_id)
        self.agg = Agg(self.project, self.api_key, self.dataset_id)
        self.centroids = Centroids(self.project, self.api_key, self.dataset_id)

        return self

    @property
    def shape(self):
        """
        Returns the shape (N x C) of a dataset
        N = number of samples in the Dataset
        C = number of columns in the Dataset

        Returns
        -------
        Tuple
            (N, C)

        Example
        ---------------
        .. code-block::

            from relevanceai import Client

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            length, width = df.shape
        """
        schema = self.datasets.schema(self.dataset_id)
        n_documents = self.get_number_of_documents(dataset_id=self.dataset_id)
        return (n_documents, len(schema))

    def __getitem__(self, field):
        """
        Returns a Series Object that selects a particular field within a dataset

        Parameters
        ----------
        field
            the particular field within the dataset

        Returns
        -------
        Tuple
            (N, C)

        Example
        ---------------
        .. code-block::

            from relevanceai import Client

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            field = "sample_field"
            series = df[field]
        """
        return Series(self.project, self.api_key, self.dataset_id, field)

    def _get_possible_dtypes(self, schema):
        possible_dtypes = []
        for v in schema.values():
            if isinstance(v, str):
                possible_dtypes.append(v)
            elif isinstance(v, dict):
                if list(v)[0] == "vector":
                    possible_dtypes.append("vector_")
        return possible_dtypes

    def _get_dtype_count(self, schema: dict):
        possible_dtypes = self._get_possible_dtypes(schema)
        dtypes = {
            dtype: list(schema.values()).count(dtype) for dtype in possible_dtypes
        }
        return dtypes

    def _get_schema(self):
        # stores schema in memory to save users API usage/reloading
        if hasattr(self, "_schema"):
            return self._schema
        self._schema = self.datasets.schema(self.dataset_id)
        return self._schema

    def info(self, dtype_count: bool = False) -> pd.DataFrame:
        """
        Return a dictionary that contains information about the Dataset
        including the index dtype and columns and non-null values.

        Parameters
        -----------
        dtype_count: bool
            If dtype_count is True, prints a value_counts of the data type


        Returns
        ---------
        Dict
            Dictionary of information

        Example
        ---------------
        .. code-block::

            from relevanceai import Client

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)
        """
        health: dict = self.datasets.monitor.health(self.dataset_id)
        schema: dict = self._get_schema()
        info_json = [
            {
                "Column": column,
                "Non-Null Count": health[column]["missing"],
                "Dtype": schema[column],
            }
            for column in schema
        ]
        info_df = pd.DataFrame(info_json)
        if dtype_count:
            dtypes_info = self._get_dtype_count(schema)
            print(dtypes_info)
        return info_df

    def head(
        self, n: int = 5, raw_json: bool = False, **kw
    ) -> Union[dict, pd.DataFrame]:
        """
        Return the first `n` rows.
        returns the first `n` rows of your dataset.
        It is useful for quickly testing if your object
        has the right type of data in it.

        Parameters
        ----------
        n : int, default 5
            Number of rows to select.
        raw_json: bool
            If True, returns raw JSON and not Pandas Dataframe
        kw:
            Additional arguments to feed into show_json

        Returns
        -------
        Pandas DataFrame or Dict, depending on args
            The first 'n' rows of the caller object.

        Example
        ---------
        .. code-block::

            from relevanceai import Client

            client = Client()

            df = client.Dataset("sample_dataset", image_fields=["image_url])

            df.head()
        """
        head_documents = self.get_documents(
            dataset_id=self.dataset_id,
            number_of_documents=n,
        )
        if raw_json:
            return head_documents
        else:
            try:
                return self._show_json(head_documents, **kw)
            except Exception as e:
                warnings.warn(
                    "Displaying using Pandas. To get image functionality please install RelevanceAI[notebook]. "
                    + str(e)
                )
                return pd.json_normalize(head_documents).head(n=n)

    def _show_json(self, documents, **kw):
        from jsonshower import show_json

        if not self.text_fields:
            text_fields = pd.json_normalize(documents).columns.tolist()
        else:
            text_fields = self.text_fields
        return show_json(
            documents,
            image_fields=self.image_fields,
            audio_fields=self.audio_fields,
            highlight_fields=self.highlight_fields,
            text_fields=text_fields,
        )

    def sample(
        self,
        n: int = 1,
        frac: float = None,
        filters: list = [],
        random_state: int = 0,
        select_fields: list = [],
        include_vector: bool = True,
        output_format: str = "json",
    ):

        """
        Return a random sample of items from a dataset.

        Parameters
        ----------
        n : int
            Number of items to return. Cannot be used with frac.
        frac: float
            Fraction of items to return. Cannot be used with n.
        filters: list
            Query for filtering the search results
        random_state: int
            Random Seed for retrieving random documents.
        select_fields: list
            Fields to include in the search results, empty array/list means all fields.

        Example
        ---------

        .. code-block::

            from relevanceai import Client
            client = Client()
            df = client.Dataset("sample_dataset", image_fields=["image_url])
            df.sample()
        """

        if frac and n:
            raise ValueError("Only one of n or frac can be provided")

        if frac:
            if frac > 1 or frac < 0:
                raise ValueError("Fraction must be between 0 and 1")
            n = math.ceil(
                self.get_number_of_documents(self.dataset_id, filters=filters) * frac
            )

        documents = self.datasets.documents.get_where(
            dataset_id=self.dataset_id,
            filters=filters,
            page_size=n,
            random_state=random_state,
            is_random=True,
            select_fields=select_fields,
            include_vector=include_vector,
        )["documents"]
        if output_format == "json":
            return documents
        elif output_format == "pandas":
            return pd.DataFrame.from_dict(documents, orient="records")

    def get_all_documents(
        self,
        chunksize: int = 1000,
        filters: List = [],
        sort: List = [],
        select_fields: List = [],
        include_vector: bool = True,
        show_progress_bar: bool = True,
    ):

        """
        Retrieve all documents with filters. Filter is used to retrieve documents that match the conditions set in a filter query. This is used in advance search to filter the documents that are searched. For more details see documents.get_where.

        Parameters
        ------------
        chunksize: list
            Number of documents to retrieve per retrieval
        include_vector: bool
            Include vectors in the search results
        sort: list
            Fields to sort by. For each field, sort by descending or ascending. If you are using descending by datetime, it will get the most recent ones.
        filters: list
            Query for filtering the search results
        select_fields : list
            Fields to include in the search results, empty array/list means all fields.

        Example
        ----------

        .. code-block::

            from relevanceai import Client
            client = Client()
            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)
            documents = df.get_all_documents()
        """

        return self._get_all_documents(
            dataset_id=self.dataset_id,
            chunksize=chunksize,
            filters=filters,
            sort=sort,
            select_fields=select_fields,
            include_vector=include_vector,
            show_progress_bar=show_progress_bar,
        )

    def get_documents_by_ids(
        self, document_ids: Union[List, str], include_vector: bool = True
    ):
        """
        Retrieve a document by its ID ("_id" field). This will retrieve the document faster than a filter applied on the "_id" field.

        Parameters
        ----------
        document_ids: Union[list, str]
            ID of a document in a dataset.
        include_vector: bool
            Include vectors in the search results

        Example
        --------

        .. code-block::

            from relevanceai import Client, Dataset
            client = Client()
            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)
            df.get_documents_by_ids(["sample_id"], include_vector=False)
        """
        if isinstance(document_ids, str):
            return self.datasets.documents.get(
                self.dataset_id, id=document_ids, include_vector=include_vector
            )
        elif isinstance(document_ids, list):
            return self.datasets.documents.bulk_get(
                self.dataset_id, ids=document_ids, include_vector=include_vector
            )
        raise TypeError("Document IDs needs to be a string or a list")

    def get(self, document_ids: Union[List, str], include_vector: bool = True):
        """
        Retrieve a document by its ID ("_id" field). This will retrieve the document faster than a filter applied on the "_id" field.
        This has the same functionality as get_document_by_ids.

        Parameters
        ----------
        document_ids: Union[list, str]
            ID of a document in a dataset.
        include_vector: bool
            Include vectors in the search results

        Example
        --------

        .. code-block::

            from relevanceai import Client
            client = Client()
            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)
            df.get(["sample_id"], include_vector=False)
        """
        if isinstance(document_ids, str):
            return self.datasets.documents.get(
                self.dataset_id, id=document_ids, include_vector=include_vector
            )
        elif isinstance(document_ids, list):
            return self.datasets.documents.bulk_get(
                self.dataset_id, ids=document_ids, include_vector=include_vector
            )
        raise TypeError("Document IDs needs to be a string or a list")

    @property
    def schema(self) -> Dict:
        """
        Returns the schema of a dataset. Refer to datasets.create for different field types available in a VecDB schema.

        Example
        -----------------

        .. code-block::

            from relevanceai import Client
            client = Client()
            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)
            df.schema
        """
        return self.datasets.schema(self.dataset_id)

    @property
    def columns(self) -> List[str]:
        """
        Returns a list of columns

        Example
        ----------

        .. code-block::

            from relevanceai import Client
            client = Client()
            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)
            df.columns

        """
        return list(self.schema)

    def filter(
        self,
        index: Union[str, None] = None,
        items: Union[List, None] = None,
        like: Union[str, None] = None,
        regex: Union[str, None] = None,
        axis: Union[int, str] = 0,
    ):
        """
        Returns a subset of the dataset, filtered by the parameters given

        Parameters
        ----------
        items : str, default None
            the column on which to filter, if None then defaults to the _id column
        items : list-like
            Keep labels from axis which are in items.
        like : str
            Keep labels from axis for which "like in label == True".
        regex : str (regular expression)
            Keep labels from axis for which re.search(regex, label) == True.
        axis : {0 or `index`, 1 or `columns`},
            The axis on which to perform the search

        Returns
        ---------
        list of documents

        Example
        ----------

        .. code-block::

            from relevanceai import Client
            client = Client()
            df = client.Dataset("pokedex")
            filtered = df.filter(items=["Bulbasaur"])
            filtered = df.filter(index="abilities", like="Blaze")
            filtered = df.filter(index="type1", regex=".F")

        """
        fields = []
        filters = []

        schema = list(self.schema)

        if index:
            axis = 0
        else:
            axis = 1
            index = "_id"

        rows = axis in [0, "index"]
        columns = axis in [1, "columns"]

        if items is not None:
            if columns:
                fields += items

            elif rows:
                filters += _build_filters(items, filter_type="exact_match", index=index)

        elif like:
            if columns:
                fields += [column for column in schema if like in column]

            elif rows:
                filters += _build_filters(like, filter_type="contains", index=index)

        elif regex:
            if columns:
                query = re.compile(regex)
                re_fields = list(filter(query.match, schema))
                fields += re_fields

            elif rows:
                filters += _build_filters(regex, filter_type="regexp", index=index)

        else:
            raise TypeError("Must pass either `items`, `like` or `regex`")

        filters = [{"filter_type": "or", "condition_value": filters}]

        return self.get_all_documents(select_fields=fields, filters=filters)


class Stats(Read):
    def value_counts(self, field: str):
        """
        Return a Series containing counts of unique values.

        Parameters
        ----------
        field: str
            dataset field to which to do value counts on

        Returns
        -------
        Series

        Example
        -----------------
        .. code-block::

            from relevanceai import Client
            client = Client()
            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)
            field = "sample_field"
            value_counts_df = df.value_counts(field)

        """
        return Series(self.project, self.api_key, self.dataset_id, field).value_counts()

    def describe(self) -> dict:
        """
        Descriptive statistics include those that summarize the central tendency
        dispersion and shape of a dataset's distribution, excluding NaN values.


        Example
        -----------------
        .. code-block::

            from relevanceai import Client
            client = Client()
            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)
            field = "sample_field"
            df.describe()

        """
        return self.datasets.facets(self.dataset_id)


class Write(Read):
    def insert_documents(  # type: ignore
        self,
        documents: list,
        bulk_fn: Callable = None,
        max_workers: int = 8,
        retry_chunk_mult: float = 0.5,
        show_progress_bar: bool = False,
        chunksize: int = 0,
        use_json_encoder: bool = True,
        *args,
        **kwargs,
    ) -> Dict:

        """
        Insert a list of documents with multi-threading automatically enabled.

        - When inserting the document you can optionally specify your own id for a document by using the field name "_id", if not specified a random id is assigned.
        - When inserting or specifying vectors in a document use the suffix (ends with) "_vector_" for the field name. e.g. "product_description_vector_".
        - When inserting or specifying chunks in a document the suffix (ends with) "_chunk_" for the field name. e.g. "products_chunk_".
        - When inserting or specifying chunk vectors in a document's chunks use the suffix (ends with) "_chunkvector_" for the field name. e.g. "products_chunk_.product_description_chunkvector_".

        Documentation can be found here: https://ingest-api-dev-aueast.relevance.ai/latest/documentation#operation/InsertEncode

        Parameters
        ----------
        documents: list
            A list of documents. Document is a JSON-like data that we store our metadata and vectors with. For specifying id of the document use the field '_id', for specifying vector field use the suffix of '_vector_'
        bulk_fn : callable
            Function to apply to documents before uploading
        max_workers : int
            Number of workers active for multi-threading
        retry_chunk_mult: int
            Multiplier to apply to chunksize if upload fails
        chunksize : int
            Number of documents to upload per worker. If None, it will default to the size specified in config.upload.target_chunk_mb
        use_json_encoder : bool
            Whether to automatically convert documents to json encodable format

        Example
        --------
        .. code-block::

            from relevanceai import Client

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            documents = [
                {
                    "_id": "10",
                    "value": 5
                },
                {
                    "_id": "332",
                    "value": 10
                }
            ]

            df.insert_documents(documents)

        """
        return self._insert_documents(  # type: ignore
            dataset_id=self.dataset_id,
            documents=documents,
            bulk_fn=bulk_fn,
            max_workers=max_workers,
            retry_chunk_mult=retry_chunk_mult,
            show_progress_bar=show_progress_bar,
            chunksize=chunksize,
            use_json_encoder=use_json_encoder,
            *args,
            **kwargs,
        )

    def insert_csv(  # type: ignore
        self,
        filepath_or_buffer,
        chunksize: int = 10000,
        max_workers: int = 8,
        retry_chunk_mult: float = 0.5,
        show_progress_bar: bool = False,
        index_col: int = None,
        csv_args: dict = {},
        col_for_id: str = None,
        auto_generate_id: bool = True,
    ) -> Dict:

        """
        Insert data from csv file

        Parameters
        ----------
        dataset_id : string
            Unique name of dataset
        filepath_or_buffer :
            Any valid string path is acceptable. The string could be a URL. Valid URL schemes include http, ftp, s3, gs, and file.
        chunksize : int
            Number of lines to read from csv per iteration
        max_workers : int
            Number of workers active for multi-threading
        retry_chunk_mult: int
            Multiplier to apply to chunksize if upload fails
        csv_args : dict
            Optional arguments to use when reading in csv. For more info, see https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
        index_col : None
            Optional argument to specify if there is an index column to be skipped (e.g. index_col = 0)
        col_for_id : str
            Optional argument to use when a specific field is supposed to be used as the unique identifier ('_id')
        auto_generate_id: bool = True
            Automatically generateds UUID if auto_generate_id is True and if the '_id' field does not exist

        Example
        ---------
        .. code-block::

            from relevanceai import Client
            client = Client()
            df = client.Dataset("sample_dataset")

            csv_filename = "temp.csv"
            df.insert_csv(csv_filename)

        """
        return self._insert_csv(
            dataset_id=self.dataset_id,
            filepath_or_buffer=filepath_or_buffer,
            chunksize=chunksize,
            max_workers=max_workers,
            retry_chunk_mult=retry_chunk_mult,
            show_progress_bar=show_progress_bar,
            index_col=index_col,
            csv_args=csv_args,
            col_for_id=col_for_id,
            auto_generate_id=auto_generate_id,
        )

    def upsert_documents(
        self,
        documents: list,
        bulk_fn: Callable = None,
        max_workers: int = 8,
        retry_chunk_mult: float = 0.5,
        chunksize: int = 0,
        show_progress_bar=False,
        use_json_encoder: bool = True,
    ) -> Dict:

        """
        Update a list of documents with multi-threading automatically enabled.
        Edits documents by providing a key value pair of fields you are adding or changing, make sure to include the "_id" in the documents.


        Parameters
        ----------
        dataset_id : string
            Unique name of dataset
        documents : list
            A list of documents. Document is a JSON-like data that we store our metadata and vectors with. For specifying id of the document use the field '_id', for specifying vector field use the suffix of '_vector_'
        bulk_fn : callable
            Function to apply to documents before uploading
        max_workers : int
            Number of workers active for multi-threading
        retry_chunk_mult: int
            Multiplier to apply to chunksize if upload fails
        chunksize : int
            Number of documents to upload per worker. If None, it will default to the size specified in config.upload.target_chunk_mb
        use_json_encoder : bool
            Whether to automatically convert documents to json encodable format


        Example
        ----------
        .. code-block::

            from relevanceai import Client

            client = Client()

            documents = [
                {
                    "_id": "321",
                    "value": 10
                },
                {
                    "_id": "4243",
                    "value": 100
                }
            ]

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            df.upsert_documents(dataset_id, documents)

        """
        return self.update_documents(
            self.dataset_id,
            documents=documents,
            bulk_fn=bulk_fn,
            max_workers=max_workers,
            retry_chunk_mult=retry_chunk_mult,
            show_progress_bar=show_progress_bar,
            chunksize=chunksize,
            use_json_encoder=use_json_encoder,
        )

    def apply(
        self,
        func: Callable,
        retrieve_chunksize: int = 100,
        max_workers: int = 8,
        filters: list = [],
        select_fields: list = [],
        show_progress_bar: bool = True,
        use_json_encoder: bool = True,
        axis: int = 0,
    ):
        """
        Apply a function along an axis of the DataFrame.

        Objects passed to the function are Series objects whose index is either the DataFrame’s index (axis=0) or the DataFrame’s columns (axis=1). By default (result_type=None), the final return type is inferred from the return type of the applied function. Otherwise, it depends on the result_type argument.

        Parameters
        --------------
        func: function
            Function to apply to each document
        retrieve_chunksize: int
            The number of documents that are received from the original collection with each loop iteration.
        max_workers: int
            The number of processors you want to parallelize with
        max_error: int
            How many failed uploads before the function breaks
        json_encoder : bool
            Whether to automatically convert documents to json encodable format
        axis: int
            Axis along which the function is applied.
            - 9 or 'index': apply function to each column
            - 1 or 'columns': apply function to each row

        Example
        ---------
        .. code-block::

            from relevanceai import Client

            client = Client()

            df = client.Dataset("sample_dataset")

            def update_doc(doc):
                doc["value"] = 2
                return doc

            df.apply(update_doc)

        """
        if axis == 1:
            raise ValueError("We do not support column-wise operations!")

        def bulk_fn(documents):
            new_documents = []
            for d in documents:
                new_d = func(d)
                new_documents.append(new_d)
            return documents

        return self.pull_update_push(
            self.dataset_id,
            bulk_fn,
            retrieve_chunk_size=retrieve_chunksize,
            max_workers=max_workers,
            filters=filters,
            select_fields=select_fields,
            show_progress_bar=show_progress_bar,
            use_json_encoder=use_json_encoder,
        )

    def bulk_apply(
        self,
        bulk_func: Callable,
        retrieve_chunksize: int = 100,
        max_workers: int = 8,
        filters: list = [],
        select_fields: list = [],
        show_progress_bar: bool = True,
        use_json_encoder: bool = True,
    ):
        """
        Apply a bulk function along an axis of the DataFrame.

        Parameters
        ------------
        bulk_func: function
            Function to apply to a bunch of documents at a time
        retrieve_chunksize: int
            The number of documents that are received from the original collection with each loop iteration.
        max_workers: int
            The number of processors you want to parallelize with
        max_error: int
            How many failed uploads before the function breaks
        json_encoder : bool
            Whether to automatically convert documents to json encodable format
        axis: int
            Axis along which the function is applied.
            - 9 or 'index': apply function to each column
            - 1 or 'columns': apply function to each row

        Example
        ---------
        .. code-block::

            from relevanceai import Client

            client = Client()

            df = client.Dataset("sample_dataset")

            def update_documents(document):
                for d in documents:
                    d["value"] = 10
                return documents

            df.apply(update_documents)
        """
        return self.pull_update_push(
            self.dataset_id,
            bulk_func,
            retrieve_chunk_size=retrieve_chunksize,
            max_workers=max_workers,
            filters=filters,
            select_fields=select_fields,
            show_progress_bar=show_progress_bar,
            use_json_encoder=use_json_encoder,
        )

    def cat(self, vector_name: Union[str, None] = None, fields: List = []):
        """
        Concatenates numerical fields along an axis and reuploads this vector for other operations

        Parameters
        ----------
        vector_name: str, default None
            name of the new concatenated vector field
        fields: List
            fields alone which the new vector will concatenate

        Example
        -----------------
        .. code-block::

            from relevanceai import Client

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            fields = [
                "numeric_field1",
                "numeric_field2",
                "numeric_field3"
            ]

            df.cat(fields)
            df.concat(fields)

            concat_vector_field_name = "concat_vector_"
            df.cat(vector_name=concat_vector_field_name, fields=fields)
            df.concat(vector_name=concat_vector_field_name, fields=fields)
        """
        if vector_name is None:
            vector_name = "_".join(fields) + "_cat_vector_"

        def cat_fields(documents, field_name):
            cat_vector_documents = [
                {"_id": sample["_id"], field_name: [sample[field] for field in fields]}
                for sample in documents
            ]
            return cat_vector_documents

        self.pull_update_push(
            self.dataset_id, cat_fields, updating_args={"field_name": vector_name}
        )

    concat = cat

    def vectorize(self, field, model):
        """
        Vectorizes a Particular field (text) of the dataset

        Parameters
        ----------
        field : str
            The text field to select
        model
            a Type deep learning model that vectorizes text

        Examples
        --------

        .. code-block::

            from relevanceai import Client
            client = Client()
            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            from vectorhub.encoders.text.tfhub import USE2Vec
            model = USE2Vec()

            text_field = "text_field"
            df[text_field].vectorize(model)

        """
        series = Series(self)
        series(self.dataset_id, field).vectorize(model)

    # def insert_csv(self, filename: str, **kwargs):
    #     """
    #     Wrapper for client.insert_csv

    #     Parameters
    #     ----------
    #     filename: str
    #         path to .csv file
    #     kwargs: Optional
    #         see client.insert_csv() for extra args
    #     """
    #     warnings.warn("Functionality of this may change. Make sure to use insert_csv if possible")
    #     return self.insert_csv(self.dataset_id, filename, **kwargs)

    def _label_cluster(self, label: Union[int, str]):
        if isinstance(label, (int, float)):
            return "cluster-" + str(label)
        return str(label)

    def _label_clusters(self, labels):
        return [self._label_cluster(x) for x in labels]

    def set_cluster_labels(self, vector_fields, alias, labels):
        def add_cluster_labels(documents):
            documents = self.get_all_documents(self.dataset_id)
            documents = list(filter(DocUtils.list_doc_fields, documents))
            set_cluster_field = (
                "_cluster_" + ".".join(vector_fields).lower() + "." + alias
            )
            self.set_field_across_documents(
                set_cluster_field,
                self._label_clusters(list(labels)),
                documents,
            )
            return documents

        self.pull_update_push(self.dataset_id, add_cluster_labels)

    def create(self, schema: dict = {}) -> Dict:
        """
        A dataset can store documents to be searched, retrieved, filtered and aggregated (similar to Collections in MongoDB, Tables in SQL, Indexes in ElasticSearch).
        A powerful and core feature of VecDB is that you can store both your metadata and vectors in the same document. When specifying the schema of a dataset and inserting your own vector use the suffix (ends with) "_vector_" for the field name, and specify the length of the vector in dataset_schema. \n

        For example:

        .. code-block::
            {
                "product_image_vector_": 1024,
                "product_text_description_vector_" : 128
            }

        These are the field types supported in our datasets: ["text", "numeric", "date", "dict", "chunks", "vector", "chunkvector"]. \n

        For example:

        .. code-block::

            {
                "product_text_description" : "text",
                "price" : "numeric",
                "created_date" : "date",
                "product_texts_chunk_": "chunks",
                "product_text_chunkvector_" : 1024
            }

        You don't have to specify the schema of every single field when creating a dataset, as VecDB will automatically detect the appropriate data type for each field (vectors will be automatically identified by its "_vector_" suffix). Infact you also don't always have to use this endpoint to create a dataset as /datasets/bulk_insert will infer and create the dataset and schema as you insert new documents. \n

        Note:

            - A dataset name/id can only contain undercase letters, dash, underscore and numbers.
            - "_id" is reserved as the key and id of a document.
            - Once a schema is set for a dataset it cannot be altered. If it has to be altered, utlise the copy dataset endpoint.

        For more information about vectors check out the 'Vectorizing' section, services.search.vector or out blog at https://relevance.ai/blog. For more information about chunks and chunk vectors check out services.search.chunk.

        Parameters
        ----------
        schema : dict
            Schema for specifying the field that are vectors and its length

        Example
        ----------
        .. code-block::

            from relevanceai import Client
            client = Client()

            documents = [
                {
                    "_id": "321",
                    "value": 10
                },
                {
                    "_id": "4243",
                    "value": 100
                }
            ]

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)
            df.create()

            df.insert_documents(documents)
        """
        return self.datasets.create(self.dataset_id, schema=schema)

    def delete(self):
        """
        Delete a dataset

        Example
        ---------
        .. code-block::

            from relevanceai import Client
            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)
            df.delete()

        """
        return self.datasets.delete(self.dataset_id)


class Export(Read):
    def to_csv(self, filename: str, **kwargs):
        """
        Download a dataset from Relevance AI to a local .csv file

        Parameters
        ----------
        filename: str
            path to downloaded .csv file
        kwargs: Optional
            see client.get_all_documents() for extra args

        Example
        -------
        .. code-block::

            from relevanceai import Client

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            csv_fname = "path/to/csv/file.csv"
            df.to_csv(csv_fname)
        """
        documents = self.get_all_documents(**kwargs)
        df = pd.DataFrame(documents)
        df.to_csv(filename)

    def to_dict(self, orient: str = "records"):
        """
        Returns the raw list of dicts from Relevance AI

        Parameters
        ----------
        None

        Returns
        -------
        list of documents in dictionary format

        Example
        -------
        .. code-block::

            from relevanceai import Client

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            dict = df.to_dict(orient="records")
        """
        if orient == "records":
            return self.get_all_documents()
        else:
            raise NotImplementedError


class Dataset(Export, Write, Stats):
    def vectorize(self, field, model):
        """
        Vectorizes a Particular field (text) of the dataset

        Parameters
        ----------
        field : str
            The text field to select
        model
            a Type deep learning model that vectorizes text

        Example
        -------
        .. code-block::

            from relevanceai import Client
            from vectorhub.encoders.text.sentence_transformers import SentenceTransformer2Vec

            model = SentenceTransformer2Vec("all-mpnet-base-v2 ")

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            text_field = "text_field"
            df.vectorize(text_field, model)
        """
        series = Series(self)
        series(self.dataset_id, field).vectorize(model)

    def cluster(self, model, alias, vector_fields, **kwargs):
        """
        Performs KMeans Clustering on over a vector field within the dataset.

        Parameters
        ----------
        model : Class
            The clustering model to use
        vector_fields : str
            The vector fields over which to cluster

        Example
        -------
        .. code-block::

            from relevanceai import Client
            from relevanceai.clusterer import Clusterer
            from relevanceai.clusterer.kmeans_clusterer import KMeansModel

            client = Client()

            dataset_id = "sample_dataset"
            df = client.Dataset(dataset_id)

            vector_field = "vector_field_"
            n_clusters = 10

            model = KMeansModel(k=n_clusters)

            df.cluster(model=model, alias=f"kmeans-{n_clusters}", vector_fields=[vector_field])
        """

        from relevanceai.clusterer import Clusterer

        clusterer = Clusterer(
            model=model, alias=alias, api_key=self.api_key, project=self.project
        )
        return clusterer.fit(dataset=self, vector_fields=vector_fields)


class Datasets(BatchAPIClient):
    """Dataset class for multiple datasets"""

    def __init__(self, project: str, api_key: str):
        self.project = project
        self.api_key = api_key
        super().__init__(project=project, api_key=api_key)
