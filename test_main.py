import os
from unittest.mock import MagicMock
import openai
import logging
import time
import utility


# Mock the OpenAI API client
def mock_prompt_openai(text, m13id):
    # Simulate the API response you expect
    mock_response = """
    ```{
        "name_result": "Tian",
        "occupation_result": "Engineer",
        "education_result": "Bachelor's Degree",
        "age_result": "30",
        "handphone_result": "08123456789",
        "marriage_result": "Single",
        "persona_initial_problem": "Looking for a job",
        "persona_initial_theme": "Economy/Work",
        "persona_pressing_problem": "Needs urgent help",
        "persona_pressing_theme": "Economy/Work",
        "gender_result": "Male",
        "address_province_result": "Jawa Barat",
        "address_city_result": "Bandung",
        "address_kecamatan_result": "Sumur Bandung",
        "address_detail_result": "No specific details",
        "suku_result": "Sunda",
        "status_hp_result": "WA",
        "attitude_result": "Open",
        "comments": "This is a mock conversation summary.",
        "comments_idn": "Ini adalah ringkasan percakapan mock.",
        "recommendation": "Approach with care.",
        "extra_info": "Available after 6 PM."
    }``garbage
    """

    # Log the mock output for debugging purposes
    logging.debug(f"Mock response for conversation ID {m13id}: {mock_response}")

    # Return the mock response
    return mock_response


# Replacing the actual OpenAI API method with the mock
openai.OpenAI = MagicMock()
openai.OpenAI.chat.completions.create = mock_prompt_openai

# Test the API mock integration in the program
if __name__ == "__main__":
    # Simulate an input conversation text and m13id
    conversation_text = (
        "This is a mock conversation where we talk about career and personal issues."
    )
    m13id = "A 1234"

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Test the mocked prompt_openai function
    response = mock_prompt_openai(conversation_text, m13id)
    print(f"response type: {type(response)}")

    # Testing utility functions
    response = utility.clean_json(input_string=response)
    print(f"After clean up: \n{response}")

    contact = utility.parse_json_to_contact(json_data=response)
    utility.contacts_to_excel(contacts=[contact], excel_file_name="mock_test.xlsx")
