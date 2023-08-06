"""
Clusterer class to run clustering. It is intended to be integrated with 
models that inherit from `ClusterBase`.

Those that inherit from `ClusterBase`.

You can run the Clusterer as such:

.. code-block::

    from relevanceai import Client 
    from relevanceai.cluster import KMeansModel
    client = Client()
    model = KMeansModel(n_clusters=2)
    clusterer = client.Clusterer(model, alias="kmeans_2")
    df = client.Dataset("_github_repo_vectorai")
    clusterer.fit(df, ["documentation_vector_"])

"""
import os
import json
import getpass

import numpy as np

from relevanceai.api.client import BatchAPIClient
from typing import Union, List, Dict, Optional
from relevanceai.clusterer.cluster_base import ClusterBase, CentroidClusterBase

# We use the second import because the first one seems to be causing errors with isinstance
# from relevanceai.dataset_api import Dataset
from relevanceai.dataset_api.dataset import Dataset

from doc_utils import DocUtils


class Clusterer(BatchAPIClient):

    _cred_fn = ".creds.json"

    """
    Clusterer class allows users to set up any clustering model to fit on a Dataset.

    You can read about the other parameters here: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

    Example
    -----------

    .. code-block::

        from relevanceai import Client
        from sklearn.cluster import KMeans

        model = KMeans(n_clusters=2)
        clusterer = client.Clusterer(model, alias="kmeans_2")

        df = client.Dataset("sample")
        clusterer.fit(df, vector_fields=["sample_vector_"])

    """

    def __init__(
        self,
        model: Union[ClusterBase, CentroidClusterBase],
        alias: str,
        project: Union[str, None] = None,
        api_key: Union[str, None] = None,
        cluster_field: str = "_cluster_",
    ):
        self.alias = alias
        self.cluster_field = cluster_field
        self.model = self._assign_model(model)

        if project is None or api_key is None:
            project, api_key = self._token_to_auth()
        else:
            self.project: str = project
            self.api_key: str = api_key

        super().__init__(project=project, api_key=api_key)

    def _assign_model(self, model):
        # Check if this is a model that will fit
        # otherwise - forces a Clusterbase
        if isinstance(model, ClusterBase):
            return model
        elif hasattr(model, "fit_documents"):
            return model
        elif hasattr(model, "fit_transform"):
            # Support for SKLEARN interface
            data = {"fit_transform": model.fit_transform, "metadata": model.__dict__}
            ClusterModel = type("ClusterBase", (ClusterBase,), data)
            return ClusterModel()
        elif hasattr(model, "fit_predict"):
            data = {"fit_transform": model.fit_predict, "metadata": model.__dict__}
            ClusterModel = type("ClusterBase", (ClusterBase,), data)
            return ClusterModel()
        raise TypeError("Model should be inherited from ClusterBase.")

    def _token_to_auth(self):
        SIGNUP_URL = "https://cloud.relevance.ai/sdk/api"
        if not os.path.exists(self._cred_fn):
            # We repeat it twice because of different behaviours
            print(f"Authorization token (you can find it here: {SIGNUP_URL} )")
            token = getpass.getpass(f"Auth token:")
            project = token.split(":")[0]
            api_key = token.split(":")[1]
            self._write_credentials(project, api_key)
        else:
            data = self._read_credentials()
            project = data["project"]
            api_key = data["api_key"]
        return project, api_key

    def _read_credentials(self):
        return json.load(open(self._cred_fn))

    def _write_credentials(self, project, api_key):
        json.dump({"project": project, "api_key": api_key}, open(self._cred_fn, "w"))

    def _init_dataset(self, dataset):
        if isinstance(dataset, Dataset):
            self.dataset_id = dataset.dataset_id
            self.dataset: Dataset = dataset
        elif isinstance(dataset, str):
            self.dataset_id = dataset
            self.dataset = Dataset(project=self.project, api_key=self.api_key)
        else:
            raise ValueError(
                "Dataset type needs to be either a string or Dataset instance."
            )

    def fit(
        self, dataset: Union[Dataset, str], vector_fields: List, filters: list = []
    ):
        """
        This function takes in the dataset and the relevant vector fields.
        Under the hood, it runs fit_dataset. Sometimes, you may want to modify the behavior
        to adapt it to your needs.

        Parameters
        -------------

        dataset: Union[Dataset, str]
            The dataset to fit the clusterer on
        vector_fields: List[str],
            The vector fields to fit it on

        Example
        ---------
        .. code-block::

            from relevanceai import Client
            client = Client()
            from relevanceai import ClusterBase
            import random

            class CustomClusterModel(ClusterBase):
                def __init__(self):
                    pass

                def fit_documents(self, documents, *args, **kw):
                    X = self.get_field_across_documents("sample_vector_", documents)
                    y = self.get_field_across_documents("entropy", documents)
                    cluster_labels = self.fit_transform(documents, entropy)
                    self.set_cluster_labels_across_documents(cluster_labels, documents)

                def fit_transform(self, X, y):
                    cluster_labels = []
                    for y_value in y:
                        if y_value == "auto":
                            cluster_labels.append(1)
                        else:
                            cluster_labels.append(random.randint(0, 100))
                    return cluster_labels

            model = CustomClusterModel()
            clusterer = client.Clusterer(model)
            df = client.Dataset("sample")
            clusterer.fit(df)

        """
        self.fit_dataset(dataset, vector_fields=vector_fields, filters=filters)
        self._insert_centroid_documents()

    def _insert_centroid_documents(self):
        if hasattr(self.model, "get_centroid_documents"):
            centers = self.model.get_centroid_documents()

            # Change centroids insertion
            results = self.services.cluster.centroids.insert(
                dataset_id=self.dataset_id,
                cluster_centers=centers,
                vector_fields=self.vector_fields,
                alias=self.alias,
            )
            self.logger.info(results)

            self.datasets.cluster.centroids.list_closest_to_center(
                self.dataset_id,
                vector_fields=self.vector_fields,
                alias=self.alias,
                centroid_vector_fields=self.vector_fields,
                page_size=20,
            )
        return

    @property
    def centroids(self):
        """
        See your centroids if there are any.
        """
        return self.services.cluster.centroids.list(
            self.dataset_id,
            vector_fields=self.vector_fields,
            alias=self.alias,
            page_size=10000,
            # cursor: str = None,
            include_vector=True,
        )

    def delete_centroids(self):
        """Delete the centroids after clustering."""
        # TODO: Fix delete centroids once its moved over to Node JS
        import requests

        base_url = self.config["api.base_url"]
        response = requests.post(
            base_url + "/services/cluster/centroids/delete",
            headers={"Authorization": self.project + ":" + self.api_key},
            params={
                "dataset_id": "_github_repo_vectorai",
                "vector_field": ["documentation_vector_"],
                "alias": self.alias,
            },
        )
        return response.json()["status"]

    def fit_dataset(
        self, dataset: Union[Dataset, str], vector_fields: List, filters: List = []
    ):
        """
        This function fits a cluster model onto a dataset.

        Parameters
        ---------------
        dataset: Union[Dataset, str],
            The dataset object to fit it on
        vector_fields: list
            The vector fields to fit the model on
        filters: list
            The filters to run it on
        include_filters_for_vector_fields: bool
            If True, only cluster on those with the vector fields inside it.

        Example
        ---------

        .. code-block::

            from relevanceai import Client
            client = Client()
            from relevanceai import ClusterBase
            import random

            class CustomClusterModel(ClusterBase):
                def __init__(self):
                    pass

                def fit_documents(self, documents, *args, **kw):
                    X = self.get_field_across_documents("sample_vector_", documents)
                    y = self.get_field_across_documents("entropy", documents)
                    cluster_labels = self.fit_transform(documents, entropy)
                    self.set_cluster_labels_across_documents(cluster_labels, documents)

                def fit_transform(self, X, y):
                    cluster_labels = []
                    for y_value in y:
                        if y_value == "auto":
                            cluster_labels.append(1)
                        else:
                            cluster_labels.append(random.randint(0, 100))
                    return cluster_labels

            model = CustomClusterModel()
            clusterer = client.Clusterer(model)
            df = client.Dataset("sample")
            clusterer.fit_dataset(df, vector_fields=["sample_vector_])

        """

        # load the documents
        self.logger.warning(
            "Retrieving documents... This can take a while if the dataset is large."
        )

        self._init_dataset(dataset)
        self.vector_fields = vector_fields

        # make sure to only get fields where vector fields exist
        filters += [
            {
                "field": f,
                "filter_type": "exists",
                "condition": "==",
                "condition_value": " ",
            }
            for f in vector_fields
        ]
        docs = self._get_all_documents(
            dataset_id=self.dataset_id, filters=filters, select_fields=vector_fields
        )

        clustered_docs = self.model.fit_documents(
            vector_fields,
            docs,
            alias=self.alias,
            cluster_field=self.cluster_field,
            return_only_clusters=True,
            inplace=False,
        )

        # Updating the db
        results = self.update_documents(
            self.dataset_id, clustered_docs, chunksize=10000
        )
        self.logger.info(results)

        # Update the centroid collection
        self.model.vector_fields = vector_fields

    # def list_closest_to_center(self):
    #     return self.datasets.cluster.centroids.list_closest_to_center(
    #         dataset_id=self.dataset_id,
    #         vector_fields=self.vector_fields
    #         alias=self.alias
    #     )

    def _concat_vectors_from_list(self, list_of_vectors: list):
        """Concatenate 2 vectors together in a pairwise fashion"""
        return [np.concatenate(x) for x in list_of_vectors]

    def _get_vectors_from_documents(self, vector_fields: list, documents: List[Dict]):
        if len(vector_fields) == 1:
            # filtering out entries not containing the specified vector
            documents = list(filter(DocUtils.list_doc_fields, documents))
            vectors = self.get_field_across_documents(
                vector_fields[0], documents, missing_treatment="skip"
            )
        else:
            # In multifield clusering, we get all the vectors in each document
            # (skip if they are missing any of the vectors)
            # Then run clustering on the result
            documents = list(self.filter_docs_for_fields(vector_fields, documents))
            all_vectors = self.get_fields_across_documents(
                vector_fields, documents, missing_treatment="skip_if_any_missing"
            )
            # Store the vector field lengths to de-concatenate them later
            self._vector_field_length: dict = {}
            prev_vf = 0
            for i, vf in enumerate(self.vector_fields):
                self._vector_field_length[vf] = {}
                self._vector_field_length[vf]["start"] = prev_vf
                end_vf = prev_vf + len(all_vectors[0][i])
                self._vector_field_length[vf]["end"] = end_vf
                # Update the ending
                prev_vf = end_vf

            # Store the vector lengths
            vectors = self._concat_vectors_from_list(all_vectors)

        return vectors

    def fit_documents(
        self,
        vector_fields: list,
        documents: List[Dict],
        return_only_clusters: bool = True,
        inplace: bool = True,
    ):
        """
        Train clustering algorithm on documents and then store the labels
        inside the documents.

        Parameters
        -----------
        vector_field: list
            The vector field of the documents
        docs: list
            List of documents to run clustering on
        alias: str
            What the clusters can be called
        cluster_field: str
            What the cluster fields should be called
        return_only_clusters: bool
            If True, return only clusters, otherwise returns the original document
        inplace: bool
            If True, the documents are edited inplace otherwise, a copy is made first
        kwargs: dict
            Any other keyword argument will go directly into the clustering algorithm

        Example
        -----------

        .. code-block::

            from relevanceai import Client, ClusterBase
            import random
            client = Client()
            class CustomClusterModel(ClusterBase):
                def __init__(self):
                    pass

                def fit_documents(self, documents, *args, **kw):
                    X = self.get_field_across_documents("sample_vector_", documents)
                    y = self.get_field_across_documents("entropy", documents)
                    cluster_labels = self.fit_transform(documents, entropy)
                    self.set_cluster_labels_across_documents(cluster_labels, documents)

                def fit_transform(self, X, y):
                    cluster_labels = []
                    for y_value in y:
                        if y_value == "auto":
                            cluster_labels.append(1)
                        else:
                            cluster_labels.append(random.randint(0, 100))
                    return cluster_labels

            clusterer = client.CustomClusterModel()
            df = client.Dataset("sample")
            clusterer.fit(df, ["sample_vector_"])

        """
        self.vector_fields = vector_fields

        vectors = self._get_vectors_from_documents(vector_fields, documents)

        cluster_labels = self.model.fit_transform(vectors)

        # Label the clusters
        cluster_labels = self._label_clusters(cluster_labels)

        return self.set_cluster_labels_across_documents(
            cluster_labels,
            documents,
            inplace=inplace,
            return_only_clusters=return_only_clusters,
        )

    def set_cluster_labels_across_documents(
        self,
        cluster_labels: list,
        documents: List[Dict],
        inplace: bool = True,
        return_only_clusters: bool = True,
    ):
        """
        Utility function to allow users to set cluster labels

        Parameters
        ------------
        cluster_labels: List[str, int]
            A list of integers of string. If it is an integer - it will automatically add a 'cluster-' prefix
            to help avoid incorrect data type parsing. You can override this behavior by setting clusters
            as strings.
        documents: List[dict]
            When the documents are in
        inplace: bool
            If True, then the clusters are set in place.
        return_only_clusters: bool
            If True, then the return_only_clusters will return documents with just the cluster field and ID.
            This can be helpful when you want to upsert quickly without having to re-insert the entire document.

        Example:

        .. code-block::

            labels = list(range(10))
            documents = [{"_id": str(x)} for x in range(10)]
            clusterer.set_cluster_labels_across_documents(labels, documents)

        """
        if inplace:
            self.set_cluster_labels_across_documents(cluster_labels, documents)
            if return_only_clusters:
                return [
                    {"_id": d.get("_id"), self.cluster_field: d.get(self.cluster_field)}
                    for d in documents
                ]
            return documents

        new_documents = documents.copy()

        self.set_cluster_labels_across_documents(cluster_labels, new_documents)
        if return_only_clusters:
            return [
                {"_id": d.get("_id"), self.cluster_field: d.get(self.cluster_field)}
                for d in new_documents
            ]
        return new_documents

    def _set_cluster_labels_across_documents(self, cluster_labels, documents):
        if isinstance(self.vector_fields, list):
            set_cluster_field = (
                f"{self.cluster_field}.{'.'.join(self.vector_fields)}.{self.alias}"
            )
        elif isinstance(self.vector_fields, str):
            set_cluster_field = (
                f"{self.cluster_field}.{self.vector_fields}.{self.alias}"
            )
        self.set_field_across_documents(set_cluster_field, cluster_labels, documents)

    def _label_cluster(self, label: Union[int, str]):
        if isinstance(label, (int, float)):
            return "cluster-" + str(label)
        return str(label)

    def _label_clusters(self, labels):
        return [self._label_cluster(x) for x in labels]

    def list_furthest_from_center(self):
        """
        List of documents furthest from the centre.

        Parameters
        ----------
        cluster_ids: list
            Any of the cluster ids
        select_fields: list
            Fields to include in the search results, empty array/list means all fields
        approx: int
            Used for approximate search to speed up search. The higher the number, faster the search but potentially less accurate
        sum_fields: bool
            Whether to sum the multiple vectors similarity search score as 1 or seperate
        page_size: int
            Size of each page of results
        page: int
            Page of the results
        similarity_metric: string
            Similarity Metric, choose from ['cosine', 'l1', 'l2', 'dp']
        filters: list
            Query for filtering the search results
        facets: list
            Fields to include in the facets, if [] then all
        min_score: int
            Minimum score for similarity metric
        include_vectors: bool
            Include vectors in the search results
        include_count: bool
            Include the total count of results in the search results
        include_facets: bool
            Include facets in the search results

        Example
        ---------
        .. code-block::

            from relevanceai import Client
            client = Client()
            df = client.Dataset("_github_repo_vectorai")
            from relevanceai.clusterer import KMeansModel
            model = KMeansModel()
            cluster = client.Clusterer(3)
            clusterer.fit(df)
            clusterer.list_furthest_from_center()

        """
        return self.datasets.cluster.centroids.list_furthest_from_center(
            dataset_id=self.dataset_id,
            vector_fields=self.vector_fields,
            alias=self.alias,
        )

    def list_closest_to_center(
        self,
        cluster_ids: List = [],
        centroid_vector_fields: List = [],
        select_fields: List = [],
        approx: int = 0,
        sum_fields: bool = True,
        page_size: int = 1,
        page: int = 1,
        similarity_metric: str = "cosine",
        filters: List = [],
        # facets: List = [],
        min_score: int = 0,
        include_vector: bool = False,
        include_count: bool = True,
    ):
        """
        List of documents closest from the centre.

        Parameters
        ----------
        cluster_ids: lsit
            Any of the cluster ids
        centroid_vector_fields: list
            Vector fields stored
        select_fields: list
            Fields to include in the search results, empty array/list means all fields
        approx: int
            Used for approximate search to speed up search. The higher the number, faster the search but potentially less accurate
        sum_fields: bool
            Whether to sum the multiple vectors similarity search score as 1 or seperate
        page_size: int
            Size of each page of results
        page: int
            Page of the results
        similarity_metric: string
            Similarity Metric, choose from ['cosine', 'l1', 'l2', 'dp']
        filters: list
            Query for filtering the search results
        facets: list
            Fields to include in the facets, if [] then all
        min_score: int
            Minimum score for similarity metric
        include_vectors: bool
            Include vectors in the search results
        include_count: bool
            Include the total count of results in the search results
        include_facets: bool
            Include facets in the search results

        Example
        --------------
        .. code-block::

            from relevanceai import Client
            client = Client()
            df = client.Dataset("sample_dataset")

            from relevanceai.clusterer import KMeansModel
            kmeans = KMeans(n_clusters=5)
            clusterer = client.Clusterer(kmeans)
            clusterer.fit(df, ["sample_vector_"])
            clusterer.list_closest_to_center()

        """
        return self.datasets.cluster.centroids.list_closest_to_center(
            dataset_id=self.dataset_id,
            vector_fields=self.vector_fields,
            alias=self.alias,
            cluster_ids=cluster_ids,
            centroid_vector_fields=centroid_vector_fields,
            select_fields=select_fields,
            approx=approx,
            sum_fields=sum_fields,
            page_size=page_size,
            page=page,
            similarity_metric=similarity_metric,
            filters=filters,
            min_score=min_score,
            include_vector=include_vector,
            include_count=include_count,
        )

    def aggregate(
        self,
        metrics: list = [],
        sort: list = [],
        groupby: list = [],
        filters: list = [],
        page_size: int = 20,
        page: int = 1,
        asc: bool = False,
        flatten: bool = True,
    ):
        """
        Takes an aggregation query and gets the aggregate of each cluster in a collection. This helps you interpret each cluster and what is in them.
        It can only can be used after a vector field has been clustered. \n

        For more information about aggregations check out services.aggregate.aggregate.

        Parameters
        ----------
        metrics: list
            Fields and metrics you want to calculate
        groupby: list
            Fields you want to split the data into
        filters: list
            Query for filtering the search results
        page_size: int
            Size of each page of results
        page: int
            Page of the results
        asc: bool
            Whether to sort results by ascending or descending order
        flatten: bool
            Whether to flatten

        Example
        ---------

        .. code-block::

            from relevanceai import Client
            client = Client()
            df = client.Dataset("sample_dataset")

            from relevanceai.cluster import KMeansModel
            clusterer = client.Clusterer(5)
            clusterer.fit(df, ["sample_vector_"])
            clusterer.aggregate(
                groupby=[],
                metrics=[
                    {"name": "average_score", "field": "final_score", "agg": "avg"},
                ]
            )

        """
        return self.services.cluster.aggregate(
            dataset_id=self.dataset_id,
            vector_fields=self.vector_fields,
            groupby=groupby,
            metrics=metrics,
            sort=sort,
            filters=filters,
            alias=self.alias,
            page_size=page_size,
            page=page,
            asc=asc,
            flatten=flatten,
        )

    @property
    def metadata(self):
        """
        If metadata is none, retrieves metadata about a dataset. notably description, data source, etc
        Otherwise, you can store the metadata about your cluster here.

        Example
        ----------

        .. code-block::

            from relevanceai import Client
            client = Client()
            df = client.Dataset("_github_repo_vectorai")
            from relevanceai.clusterer import KMeansModel

            model = KMeansModel()
            kmeans = client.Clusterer(model, alias="kmeans_sample")
            kmeans.fit(df, vector_fields=["sample_1_vector_"])
            kmeans.metadata
            # {"k": 10}

        """
        return self.services.cluster.centroids.metadata(
            dataset_id=self.dataset_id,
            vector_fields=self.vector_fields,
            alias=self.alias,
        )

    @metadata.setter
    def metadata(self, metadata: dict):
        """
        If metadata is none, retrieves metadata about a dataset. notably description, data source, etc
        Otherwise, you can store the metadata about your cluster here.

        Parameters
        ----------
        metadata: dict
           If None, it will retrieve the metadata, otherwise
           it will overwrite the metadata of the cluster

        Example
        ----------

        .. code-block::


            from relevanceai import Client
            client = Client()
            df = client.Dataset("_github_repo_vectorai")
            from relevanceai.clusterer import KMeansModel

            model = KMeansModel()
            kmeans = client.Clusterer(model, alias="kmeans_sample")
            kmeans.fit(df, vector_fields=["sample_1_vector_"])
            kmeans.metadata
            # {"k": 10}

        """
        return self.services.cluster.centroids.metadata(
            dataset_id=self.dataset_id,
            vector_fields=self.vector_fields,
            alias=self.alias,
            metadata=metadata,
        )
