from . import LOG
from huey import SqliteHuey
import tempfile

import typesense

ts_db_name = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
LOG.info(f"Typesense SQLite DB: {ts_db_name}")
huey = SqliteHuey(filename=ts_db_name)


@huey.task()
def ts_index(ts_client, collection, data, document_id, document_path):

    LOG.debug(f"Indexing {document_id} : {document_path}")

    try:
        ts_client.collections[collection].documents.upsert(data)
    except typesense.exceptions.ObjectNotFound:
        LOG.error(f"Collection {collection} does not seem to exist")
        raise


@huey.task()
def ts_unindex(ts_client, collection, document_id, document_path):

    LOG.debug(f"Unindexing {document_id} : {document_path}")

    try:
        ts_client.collections[collection].documents[document_id].delete()
    except typesense.exceptions.ObjectNotFound:
        pass
