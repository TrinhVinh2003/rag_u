import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.utils.doc_util import load_excel_url, prepare_data
from app.utils.vector_store import VectorStore

logger = logging.getLogger(__name__)

router = APIRouter()
vector_store = VectorStore()


@router.post("/upload")
async def upload_file(url_str: str) -> JSONResponse:
    """
    Upload a file from a URL and save its data to the vector store.

    Args:
        url_str (str): The URL of the Excel file to be uploaded.

    Returns:
        JSONResponse: A message indicating success or failure.

    Raises:
        HTTPException: If the URL is empty or an error occurs during processing.
    """
    if not url_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input provided. Please provide a valid URL.",
        )

    # check and ensure table exist
    if await vector_store.table_exists():
        logger.info("Table already exists. Dropping and recreating it.")
        await vector_store.drop_tables()
    await vector_store.create_tables()

    try:
        # Load data from the Excel URL
        df = load_excel_url(url_str)

        # Prepare and upsert data into the vector store
        await prepare_data(data_excel=df, vector_store=vector_store)

        return JSONResponse(
            content={"message": "File uploaded and processed successfully."},
            status_code=status.HTTP_200_OK,
        )
    except HTTPException:
        raise  # Re-raise HTTPException to preserve the original status code and detail
    except Exception as e:
        logger.error(f"An error occurred while processing the file: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e!s}",
        ) from e
