from .elastic_client import ElasticSearchClient
from utils.data_loader import PublicBulkDataLoader


es_client = ElasticSearchClient()
data_loader = PublicBulkDataLoader()

if es_client.is_empty():
    es_client.create_index()
    es_client.populate(data_loader.df)
