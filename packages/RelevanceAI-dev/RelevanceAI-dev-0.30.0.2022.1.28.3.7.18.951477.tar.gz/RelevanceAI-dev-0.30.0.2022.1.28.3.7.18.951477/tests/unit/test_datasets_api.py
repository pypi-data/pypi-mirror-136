import pandas as pd
from relevanceai.http_client import Dataset


def test_read_df_check(test_read_df, sample_vector_documents):
    assert test_read_df["inserted"] == len(
        sample_vector_documents
    ), "Did not insert properly"


def test_datasets_api(test_dataset_df: Dataset):
    """Testing the datasets API
    Simple smoke tests for now until we are happy with functionality :)
    """
    test_dataset_df.info()
    test_dataset_df.describe()
    test_dataset_df.head()
    test_dataset_df.schema
    assert True


def test_apply(test_dataset_df: Dataset):
    RANDOM_STRING = "you are the kingj"
    test_dataset_df["sample_1_label"].apply(
        lambda x: x + RANDOM_STRING, output_field="sample_1_label_2"
    )
    assert test_dataset_df["sample_1_label_2"][0].endswith(RANDOM_STRING)


def test_info(test_dataset_df: Dataset):
    info = test_dataset_df.info()
    assert isinstance(info, pd.DataFrame)


def test_df_insert_csv_successful(test_csv_df: Dataset):
    """Test Insert CSv successful"""
    response, original_length = test_csv_df
    assert response["inserted"] == original_length, "incorrect insertion"


def test_df_get_smoke(test_dataset_df: Dataset):
    """Test the df"""
    # This is to cover the 255 error before
    assert test_dataset_df.get(["321", "3421"])
