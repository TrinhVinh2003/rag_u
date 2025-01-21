from app.core.settings import settings
from app.services.openai_util import get_chatbot_response
from app.utils.doc_util import relevant_doc
from app.utils.vector_store import VectorStore


def generate_res(input:str)-> str:
    """Generate text ."""
    vector_store = VectorStore(settings.db_url, settings.open_api_key)
    vector_store.create_tables()
    related_docs =vector_store.search(input, limit=10)
    docs = relevant_doc(related_docs)
    return get_chatbot_response(input, docs)
