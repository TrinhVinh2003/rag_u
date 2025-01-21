import asyncio
import logging

import pandas as pd
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from app.services.openai_util import get_chatbot_response
from app.utils.doc_util import load_excel_url, relevant_doc
from app.utils.vector_store import VectorStore
from app.web.api.gen_response.schemas import AccEval, UserRequest

router = APIRouter()


@router.post("/gen_response")
async def generate_response(request: UserRequest) -> JSONResponse:
    """
    Generate a response based on user input using a chatbot and related documents.

    Args:
        request (UserRequest): The user request containing the input text.

    Returns:
        JSONResponse: The generated response from the chatbot.

    Raises:
        HTTPException: If the input is empty or an error occurs during processing.
    """
    if not request.input_user:
        logging.info("Input required")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input provided. Please provide a valid input.",
        )

    vector_store = VectorStore()
    try:
        # Search for related documents asynchronously
        related_docs = await vector_store.search(request.input_user, limit=10)
        if not related_docs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant documents found.",
            )

        # Process the related documents
        docs = relevant_doc(related_docs)

        # Generate chatbot response
        result = get_chatbot_response(request.input_user, docs)
    except asyncio.CancelledError:
        logging.error("Request was cancelled.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Request was cancelled.",
        ) from None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request: {e!s}",
        ) from e

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.post("/acc_eval")
async def evaluate_acc(request: AccEval) -> JSONResponse:
    """
    Evaluate the accuracy of the Rag system based on the provided document URL.

    Args:
        request (AccEval): The input request containing the URL for the document to evaluate.

    Returns:
        JSONResponse: A response containing the accuracy of the model.

    Raises:
        HTTPException: If the input URL is invalid or missing.
    """

    # Validate the input URL
    if not request.path_url:
        logging.info("Input required")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No input provided. Please provide a valid input.",
        )

    # Load data from the provided URL
    try:
        logging.info(f"Loading data from {request.path_url}")
        df = load_excel_url(request.path_url)
    except ValueError as e:
        logging.error(f"Failed to load data from URL: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to load data from the provided URL: {e!s}",
        ) from e

    correct_predictions = 0 # the number of correct predictions
    total_predictions = 0 # total prediction
    vector_store = VectorStore()

    logging.info("Evaluating accuracy based on the Rag system's search results.")

    # Iterate through the rows of the loaded dataframe
    for _, row in df.iterrows():
        # Extract user input (product name)
        user_input = row.get("Tên SP")

        if pd.isna(user_input):
            logging.warning(f"Skipping row {row.name} due to missing product name.")
            continue

        # Skip rows with empty or invalid content in the "Danh mục cấp 4" column
        content_category = row.get("Danh mục cấp 4")
        if pd.isna(content_category) or not str(content_category).strip():
            logging.info(f"Skipping row {row.name} due to empty 'Danh mục cấp 4'.")
            continue

        try:
            # Perform the search in the vector store
            result = await vector_store.search(user_input, limit=10)
        except Exception as e:
            logging.error(f"Error searching for '{user_input}' in vector store: {e}")
            continue

        total_predictions += 1

        # Check if the result contains the actual category
        if content_category in str(result):
            correct_predictions += 1

    # Calculate accuracy
    if total_predictions == 0:
        logging.warning("No valid rows found to evaluate.")
        return JSONResponse(
            content={"accuracy": 0.0, "message": "No valid rows found to evaluate."}
        )

    accuracy = correct_predictions / total_predictions
    logging.info(f"Evaluation completed. Accuracy: {accuracy:.4f}")

    return JSONResponse(content={"accuracy": accuracy})
