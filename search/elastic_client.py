from model import SemanticSearchModel
from elasticsearch import Elasticsearch, helpers
from config import ElasticSearchConfig as ESConfig


class ElasticSearchClient:
    def __init__(self) -> None:
        self._connect()
        self.model = SemanticSearchModel()

    def _connect(self) -> None:
        self.client = Elasticsearch(
            hosts=[
                {
                    "scheme": ESConfig.SCHEME,
                    "host": ESConfig.HOST,
                    "port": ESConfig.PORT,
                }
            ],
            retry_on_timeout=True,
        )

    def is_empty(self) -> bool:
        return not self.client.indices.exists(index=ESConfig.INDEX)

    def create_index(self) -> None:
        self.client.indices.create(
            index=ESConfig.INDEX,
            body={
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "url": {"type": "keyword"},
                        "name": {"type": "text"},
                        "decision_date": {"type": "date"},
                        "docket_number": {"type": "text"},
                        "first_page": {"type": "text"},
                        "last_page": {"type": "text"},
                        "citations": {"type": "text"},
                        "cites_to": {"type": "text"},
                        "frontend_url": {"type": "keyword"},
                        "volume": {
                            "properties": {
                                "barcode": {"type": "keyword"},
                                "volume_number": {"type": "integer"},
                                "url": {"type": "keyword"},
                            }
                        },
                        "reporter": {
                            "properties": {
                                "id": {"type": "keyword"},
                                "full_name": {"type": "text"},
                                "url": {"type": "keyword"},
                            }
                        },
                        "court": {
                            "properties": {
                                "id": {"type": "keyword"},
                                "name": {"type": "text"},
                                "url": {"type": "keyword"},
                            }
                        },
                        "jurisdiction": {
                            "properties": {
                                "id": {"type": "keyword"},
                                "name_long": {"type": "text"},
                                "whitelisted": {"type": "boolean"},
                                "url": {"type": "keyword"},
                            }
                        },
                        "casebody": {
                            "properties": {
                                "embedding": {
                                    "type": "dense_vector",
                                    "dims": self.model.get_embedding_dims(),
                                },
                                "head_matter": {"type": "text"},
                                "opinions": {"type": "text"},
                                "attorneys": {"type": "text"},
                                "judges": {"type": "text"},
                                "corrections": {"type": "text"},
                            }
                        },
                    }
                }
            },
        )

    def populate(self, df) -> None:
        def _generate():
            for _, row in df.iterrows():
                yield {
                    "_index": ESConfig.INDEX,
                    "_id": row["id"],
                    "_source": {
                        "id": row["id"],
                        "url": row["url"],
                        "name": row["name"],
                        "decision_date": row["decision_date"],
                        "docket_number": row["docket_number"],
                        "first_page": row["first_page"],
                        "last_page": row["last_page"],
                        # "citations": row["citations"],
                        "cites_to": row.get("cites_to"),
                        "frontend_url": row["frontend_url"],
                        "volume": {
                            "barcode": row["volume.barcode"],
                            "volume_number": row["volume.volume_number"],
                            "url": row["volume.url"],
                        },
                        "reporter": {
                            "id": row["reporter.id"],
                            "full_name": row["reporter.full_name"],
                            "url": row["reporter.url"],
                        },
                        "court": {
                            "id": row["court.id"],
                            "name": row["court.name"],
                            "url": row["court.url"],
                        },
                        "jurisdiction": {
                            "id": row["jurisdiction.id"],
                            "name_long": row["jurisdiction.name_long"],
                            "whitelisted": row["jurisdiction.whitelisted"],
                            "url": row["jurisdiction.url"],
                        },
                        "casebody": {
                            "head_matter": row["casebody.data.head_matter"],
                            "embedding": self.model.encode(
                                row["casebody.data.head_matter"]
                            ),
                            # "opinions": row["casebody.data.opinions"],
                            "attorneys": row["casebody.data.attorneys"],
                            "judges": row["casebody.data.judges"],
                            "corrections": row["casebody.data.corrections"],
                        },
                    },
                }

        helpers.bulk(self.client, _generate())

    def search(self, query: str) -> list:
        embedding = self.model.encode(query)
        script_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'casebody.embedding') + 1.0",
                    "params": {"query_vector": embedding.tolist()},
                },
            }
        }
        response = self.client.search(
            index=ESConfig.INDEX,
            body={
                "size": 10,
                "query": script_query,
                "_source": {
                    "includes": [
                        "casebody.head_matter",
                    ]
                },
            },
        )
        return response["hits"]["hits"]
