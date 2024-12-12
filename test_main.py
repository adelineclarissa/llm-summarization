import os
from unittest.mock import MagicMock
import openai
import logging
import utility


# Mock the OpenAI API client
def mock_prompt_openai(text, m13id):
    # Simulate the API response you expect
    mock_response = """
    ```json
{
    "name_result": "Tian",
    "name_reasoning": "The contact's name is anonymized as 'Tian'.",
    "name_confidence": "100%",
    "occupation_result": "",
    "occupation_reasoning": "The conversation indicates that Tian is currently not successfully running a business and is involved in informal work, but no specific occupation is provided.",
    "occupation_confidence": "60%",
    "education_result": "SMA",
    "education_reasoning": "Tian mentions having graduated from 'SMA' during the conversation.",
    "education_confidence": "90%",
    "age_result": "52",
    "age_reasoning": "Tian explicitly states that he is 52 years old.",
    "age_confidence": "100%",
    "handphone_result": "082143633180",
    "handphone_reasoning": "Tian provides this phone number during the conversation.",
    "handphone_confidence": "100%",
    "marriage_result": "Lajang",
    "marriage_reasoning": "There is no information indicating that Tian is married; he mentions only himself and converses as an individual.",
    "marriage_confidence": "70%",
    "persona_initial_problem": "Merasa gelisah setelah pandemi.",
    "persona_initial_theme": "Spiritual (Rohani)",
    "persona_pressing_problem": "Belum mendapatkan petunjuk dari Allah.",
    "persona_pressing_theme": "Spiritual (Rohani)",
    "gender_result": "",
    "gender_reasoning": "The gender is not explicitly stated in the conversation, but the context suggests a male speaker.",
    "gender_confidence": "70%",
    "address_province_result": "Jawa Timur",
    "address_province_reasoning": "Tian mentions living in Banyuwangi, which is in East Java (Jawa Timur).",
    "address_province_confidence": "90%",
    "address_city_result": "Banyuwangi",
    "address_city_reasoning": "Tian states that he lives in 'banyuwangi'.",
    "address_city_confidence": "90%",
    "address_kecamatan_result": "Licin",
    "address_kecamatan_reasoning": "Tian mentions 'Kec Licin' while discussing where he lives.",
    "address_kecamatan_confidence": "90%",
    "address_detail_result": "",
    "address_detail_reasoning": "Specific details beyond the kecamatan and city are not provided in the conversation.",
    "address_detail_confidence": "70%",
    "suku_result": "",
    "suku_reasoning": "No ethnic group or tribe is mentioned during the conversation.",
    "suku_confidence": "100%",
    "status_hp_result": "WA",
    "status_hp_reasoning": "Tian provides his phone number for further communication, implying he has WhatsApp.",
    "status_hp_confidence": "90%",
    "attitude_result": "Open (Terbuka)",
    "attitude_reasoning": "Tian expresses willingness to learn about how to become clean from sin and engages in the conversation positively.",
    "attitude_confidence": "80%",
    "comments": "COD expressed feelings of distress and discussed his relationship with sin, showing openness to seek guidance.",
    "comments_idn": "COD mengekspresikan perasaan gelisah dan mendiskusikan hubungannya dengan dosa, menunjukkan keterbukaan untuk mencari bimbingan.",
    "recommendation": "Approach Tian with compassionate dialogue about faith and personal growth, offering resources for studying.",
    "extra_info": "Tian is open to conversations about faith and personal issues; schedule for further discussion via WhatsApp."
}
```

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
    utility.setup_logging(logfile="test_main")

    # Test the mocked prompt_openai function
    response = mock_prompt_openai(conversation_text, m13id)
    print(f"response type: {type(response)}")

    # Testing utility functions
    response = utility.clean_json(input_string=response)
    print(f"After clean up: \n{response}")

    contact = utility.parse_json_to_contact(json_data=response)
    utility.contacts_to_excel(contacts=[contact], excel_file_name="mock_test.xlsx")
