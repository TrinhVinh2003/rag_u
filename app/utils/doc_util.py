import logging
import re
import uuid

import pandas as pd

from app.utils.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Generate a fommatted String for related docs
def relevant_doc(related_docs: list) -> str:  # noqa: D103
    relevant_docs = ""
    for doc in related_docs:
        relevant_docs += f"""
        - ID tài liệu: {doc["id"]}
        - Nội dung: {doc["contents"]}
        - Danh mục cấp 1: {doc["metadata"]["Danh mục cấp 1"]}
        - Danh mục cấp 2: {doc["metadata"]["Danh mục cấp 2"]}
        - Danh mục cấp 3: {doc["metadata"]["Danh mục cấp 3"]}
        """
    if not relevant_docs:
        relevant_docs = "No related information found."

    return relevant_docs


async def prepare_data(data_excel: pd.DataFrame, vector_store: VectorStore) -> None:
    """
    Prepare data from Excel and upsert it into the vector store.

    Args:
        data_excel (pd.DataFrame): The input DataFrame containing the data.
        vector_store (VectorStore): The vector store togenerate embeddings
                                    and upsert data.

    Raises:
        ValueError: If the required column is missing in the input DataFrame.
    """

    # Define columns to combine for metadata
    metadata_columns = ["Danh mục cấp 1", "Danh mục cấp 2", "Danh mục cấp 3"]
    content_column = "Danh mục cấp 4"

    # Validate input DataFrame
    if content_column not in data_excel.columns:
        raise ValueError(f"Input DataFrame must contain the column '{content_column}'.")

    # Prepare data for upsertion
    prepared_data = []
    for index, row in data_excel.iterrows():
        try:
            # Extract and validate content
            content = str(row[content_column]).strip()
            if not content or  pd.isna(content):
                logger.info(f"Skipping row {index} due to empty content.")
                continue

            # Extract metadata
            metadata = {
                col: row[col] for col in metadata_columns
                if col in row and pd.notna(row[col])
            }

            # Generate embedding
            embedding = await vector_store.get_embedding(content)

            # Create entry
            entry = {
                "id": str(uuid.uuid4()),
                "metadata": metadata,
                "contents": content,
                "embedding": embedding,
            }
            prepared_data.append(entry)
        except Exception as e:
            logger.error(f"Error processing row {index}: {e}")
            continue

    # Convert to DataFrame and upsert into the vector store
    if prepared_data:
        data = pd.DataFrame(prepared_data)
        await vector_store.upsert(data)
    else:
        logger.warning("No valid data to upsert.")



def load_excel_url(file_path: str) -> pd.DataFrame:
    """
    Load data from a Google Sheets URL into a Pandas DataFrame.

    Args:
        file_path (str): The Google Sheets URL.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the Google Sheets.

    Raises:
        ValueError: If the URL is invalid or the file cannot be loaded.
    """
    try:
        # Check if the provided URL is a valid Google Sheets URL
        if not file_path.startswith("https://docs.google.com/spreadsheets/"):
            raise ValueError("Invalid Google Sheets URL. URL must start with 'https://docs.google.com/spreadsheets/'.")

        # Extract sheet ID from the URL using re
        pattern = r"/d/([a-zA-Z0-9_-]+)/"
        match = re.search(pattern, file_path)
        if not match:
            raise ValueError("Invalid Google Sheets URL. Could not extract file ID.")

        sheet_id = match.group(1)

         # Extract gid (sheet ID) from the URL using re
        gid_pattern = r"gid=(\d+)"
        gid_match = re.search(gid_pattern, file_path)
        if not gid_match:
            raise ValueError("Invalid Google Sheets URL. Could not extract gid.")

        gid = gid_match.group(1)

        # Create export URL
        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

        # Read the CSV data from the export URL into a DataFrame
    
        return pd.read_csv(export_url)


    except ValueError as ve:
        logging.error(ve)
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise ValueError(f"An unexpected error occurred: {e}") from e
