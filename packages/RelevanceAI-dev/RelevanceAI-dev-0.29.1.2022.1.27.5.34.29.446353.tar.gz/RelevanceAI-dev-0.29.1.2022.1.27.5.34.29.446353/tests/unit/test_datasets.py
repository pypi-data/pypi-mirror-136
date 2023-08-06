import pytest


def test_get_sample_ecommerce_dataset():
    from relevanceai.datasets import get_ecommerce_1_dataset

    assert len(get_ecommerce_1_dataset(number_of_documents=100)) == 100


def test_get_games_dataset_subset():
    from relevanceai.datasets import get_games_dataset

    assert len(get_games_dataset(number_of_documents=100)) == 100


@pytest.mark.skip(reason="Min time to insight")
def test_get_games_dataset_full():
    from relevanceai.datasets import get_games_dataset

    assert len(get_games_dataset(number_of_documents=None)) == 365


@pytest.mark.skip(reason="Skipping as large file in memory")
def test_get_online_retail_dataset_subset():
    from relevanceai.datasets import get_online_retail_dataset

    assert len(get_online_retail_dataset(number_of_documents=1000)) == 1000


@pytest.mark.skip(reason="Skipping as large file in memory")
def test_get_online_retail_dataset_full():
    from relevanceai.datasets import get_online_retail_dataset

    assert len(get_online_retail_dataset(number_of_documents=None)) == 406829


@pytest.mark.skip(reason="Dataset is officially down.")
def test_get_news_dataset_subset():
    from relevanceai.datasets import get_news_dataset

    assert len(get_news_dataset(number_of_documents=100)) == 100


@pytest.mark.skip(reason="Min time to insight")
def test_get_news_dataset_full():
    from relevanceai.datasets import get_news_dataset

    assert len(get_news_dataset(number_of_documents=None)) == 250


def test_get_ecommerce_dataset_subset():
    from relevanceai.datasets import get_ecommerce_3_dataset

    assert len(get_ecommerce_3_dataset(number_of_documents=1000)) == 1000


@pytest.mark.skip(reason="Min time to insight")
def test_get_ecommerce_dataset_full():
    from relevanceai.datasets import get_ecommerce_3_dataset

    assert len(get_ecommerce_3_dataset(number_of_documents=None)) == 15528
