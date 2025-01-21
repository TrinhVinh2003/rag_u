import logging
from typing import Dict, List

import openai

logging.basicConfig(level=logging.INFO)


def get_completion_from_messages(
    messages: List[Dict[str, str]],
    model: str = "gpt-3.5-turbo",
    temperature: float = 0,
    max_tokens: int = 100,
) -> str:
    """
    Sends a list of messages to OpenAI's GPT model and retrieves the completion.

    Args:
    - messages: List of message objects for the conversation.
    - model: The model to use for completion (default is gpt-3.5-turbo).
    - temperature: Controls randomness of the response (default is 0).
    - max_tokens: The maximum number of tokens for the response (default is 1000).

    Returns:
    - str: The model's response content.
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message["content"]
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        return "An error occurred while processing your request."
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "An unexpected error occurred."


def get_chatbot_response(user_input: str, relevant_docs: str) -> str:
    """
    Generates a chatbot response based on user input and relevant documentation.

    Args:
    - user_input: The query or message from the user.
    - relevant_docs: Relevant documentation or information that the chatbot can reference.

    Returns:
    - str: The chatbot's response.
    """  # noqa: E501
    system_message = """
    Bạn là một chatbot hỗ trợ khách hàng về các phụ tùng ô tô. 
    Khi người dùng hỏi về sản phẩm, hãy tìm các từ khóa liên quan trong câu hỏi và cung cấp thông tin tương ứng, chẳng hạn như tên sản phẩm, danh mục, hoặc các đặc điểm chính.
    Trả lời nên ngắn gọn và có tính chuyên nghiệp, chỉ tập trung vào các từ hoặc câu liên quan trực tiếp đến sản phẩm hoặc dịch vụ mà người dùng yêu cầu.
    """  # noqa: E501

    # Prepare the message to send to the API
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": relevant_docs},
    ]


    # Return the chatbot response
    return get_completion_from_messages(messages)
