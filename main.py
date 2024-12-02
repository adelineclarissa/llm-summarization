import re
from databasemanager import DatabaseManager
import logging
import openai
import os
import utility
from dotenv import load_dotenv
from httpx import HTTPStatusError
import time

PHONE_PLACEHOLDER = "08123456789"
NAME_PLACEHOLDER = "Tian"


# Anonymizes a full name in a conversation, accounting for first, middle (if any), and last names.
def anonymize(
    conversation,
    original_name,
    name_placeholder=NAME_PLACEHOLDER,
    phone_placeholder=PHONE_PLACEHOLDER,
):
    """
    Anonymizes a conversation by replacing occurrences of a name and phone numbers.
    Stores original phone numbers in a list.

    :param conversation: The original conversation text (str).
    :param original_name: The full name to anonymize (str), e.g., "John Michael Doe".
    :param name_placeholder: The placeholder to replace the name with (default is "Anonymous").
    :param phone_placeholder: The placeholder to replace phone numbers with (default is "08123456789").
    :return: A tuple containing:
             - Anonymized conversation (str)
             - The original name (str)
             - List of original phone numbers (list)
    """

    # Split the name into components (first, middle, last)
    name_parts = original_name.split()
    name_pattern = r"\b" + r"\s+".join([rf"({part})?" for part in name_parts]) + r"\b"
    name_regex = re.compile(name_pattern, re.IGNORECASE)
    conversation = name_regex.sub(name_placeholder, conversation)

    # Anonymize phone numbers
    phone_pattern = r"(?<!\d)(?:\+62|08)\d{9,}\b"
    phone_regex = re.compile(phone_pattern)
    original_phone_numbers = phone_regex.findall(conversation)
    conversation = phone_regex.sub(phone_placeholder, conversation)

    return conversation, original_name, original_phone_numbers


# Prompt
client_openai = openai.OpenAI()
openai.api_key = os.environ["OPENAI_API_KEY"]


def prompt_openai(text, m13id):
    retries = 3
    backoff_factor = 2  # Backoff multiplier for exponential backoff
    delay = 1  # Initial delay in seconds
    for attempt in range(retries):
        try:
            prompt = [
                {
                    "role": "user",
                    "content": f"""
        You are a staff member of a non-profit mission agency. Please disregard previous knowledge and focus only on the given conversation between another staff member and a potential contact for evangelization. Extract the following data points in JSON format in Indonesian, with the specified keys:

        1. **name**: The name of the contact has been anonymized to 'Tian'. So Tian will be the name. 
        2. **occupation**: The contact's current job or profession.
        3. **education**: The highest level of education attained by the contact.
        4. **age**: The age of the contact.
        5. **handphone**: The contact's phone number.
        6. **marriage**: The contact's marital status. The options are:
            - **Lajang**: If the contact is single
            - **Menikah**: If the contact is married
            - **Janda/Duda**: If the contact is divorced or a widow/widower
        7. **persona**: A detailed JSON object containing the following:
        - **Initial problem**: The issue that first prompted the contact to reach out to the agency staff. This is typically found at the beginning of the conversation in the contact's first message.
        - **Initial theme**: The theme associated with the initial problem. Choose from the following categories:
            - **Spiritual (Rohani)**
            - **Economy/Work (Ekonomi/Keuangan)**
            - **Relationship/Family (Hubungan/Keluarga)**
            - **Personal/Lifestyle (Personal/Gaya hidup)**
            - **Health/Sickness (Kesehatan/Penyakit)**
        - **Pressing problem**: The most urgent issue currently facing the contact. This could be the same as the initial problem or a different one.
        - **Pressing theme**: The theme associated with the most pressing problem. Choose from the same categories as for the initial theme.
        8. **gender**: The gender of the contact.
        9. **address**: A breakdown of the contact's address, including:
            - **Province**: The province in which the contact resides.
            - **City**: The city or district (kota or kabupaten) where the contact lives.
            - **Kecamatan**: The subdistrict where the contact lives.
            - **Address**: Any additional specific details about the contact's location that can be inferred from the conversation.
        10. **suku**: The ethnic group or tribe the contact belongs to, if mentioned.
        11. **status hp**: How the contact's phone number can be contacted. The options are:
        - **WA**: Chosen when the contact gives his/her phone number to the agent when requested. This is the most common case.
        - **Both**: When the contact attempted to call the staff
        - **Telp**: When the contact doesn't have Whatsapp (wa) and only can be contacted through regular phone call. This is the least common case.
        12. **comments**: a short summary about the conversation. Please do not put any identifiable information in the summary. Please refer to the contact as 'COD'
        13. **comments (IDN)**: **comments** but translated in Indonesian.
        14. **attitude**: The general demeanor or attitude of the contact as inferred from the conversation. The options are:
            - **Open (Terbuka)**
            - **Not Open (Tidak Terbuka)**
            - **Group (Kelompok)**: If the contact's family member or friend/s are also interested to learn about the gospel.
        15. **recommendation**: A recommendation on how to approach or evangelize this person.
        16. **extra info**: Any other additional information that is important for a staff person to know such as when the contact is available to be contacted or to meet in person, or any other information that is unique to the contact.

        For each field, please provide the reasoning behind your answer, explaining why you believe it to be correct. Additionally, indicate your level of confidence in your answer, specifying a percentage or scale to represent the probability this answer might be correct based on the information you have at hand.

        Please return the data in the following JSON format:
        {{
            "name_result": "",
            "name_reasoning": "",
            "name_confidence": "",
            "occupation_result": "",
            "occupation_reasoning": "",
            "occupation_confidence": "",
            "education_result": "",
            "education_reasoning": "",
            "education_confidence": "",
            "age_result": "",
            "age_reasoning": "",
            "age_confidence": "",
            "handphone_result": "",
            "handphone_reasoning": "",
            "handphone_confidence": "",
            "marriage_result": "",
            "marriage_reasoning": "",
            "marriage_confidence": "",
            "persona_initial_problem": "",
            "persona_initial_theme": "",
            "persona_pressing_problem": "",
            "persona_pressing_theme": "",
            "gender_result": "",
            "gender_reasoning": "",
            "gender_confidence": "",
            "address_province_result": "",
            "address_province_reasoning": "",
            "address_province_confidence": "",
            "address_city_result": "",
            "address_city_reasoning": "",
            "address_city_confidence": "",
            "address_kecamatan_result": "",
            "address_kecamatan_reasoning": "",
            "address_kecamatan_confidence": "",
            "address_detail_result": "",
            "address_detail_reasoning": "",
            "address_detail_confidence": "",
            "suku_result": "",
            "suku_reasoning": "",
            "suku_confidence": "",
            "status_hp_result": "",
            "status_hp_reasoning": "",
            "status_hp_confidence": "",
            "attitude_result": "",
            "attitude_reasoning": "",
            "attitude_confidence": "",
            "comments": "",
            "comments_idn": "",
            "recommendation": "",
            "extra_info": ""
        }}

        Please make sure that the JSON formatting is valid. Do not include anything else than the valid JSON format.

        Text: {text}

        """,
                }
            ]
            completion = client_openai.chat.completions.create(
                model="gpt-4o",
                messages=prompt,
            )
            output = completion.choices[0].message.content
            logging.debug(output)
            return output
        except openai.APIError.InvalidRequestError as e:
            if "maximum context length" in str(
                e
            ):  # Check if the error is token-related
                print(
                    f"Error: Input text exceeds the token limit for conversation ID: {m13id}."
                )
                print("Please clean up the text and try again.")
                return None
            else:
                print(
                    f"An unexpected error occurred for conversation ID: {m13id}. Error: {e}"
                )
                return None
        except HTTPStatusError as e:
            if e.response.status_code == 429:
                logging.error(
                    f"Rate limit exceeded for conversation ID: {m13id}. Attempt {attempt + 1} of {retries}."
                )
                if attempt < retries - 1:
                    time.sleep(delay)  # Wait before retrying
                    delay *= backoff_factor  # Exponential backoff
                else:
                    logging.error(
                        f"All retry attempts failed for conversation ID: {m13id}. Please wait and try again later."
                    )
                    return None
            else:
                logging.error(
                    f"HTTP error for conversation ID: {m13id}. Status: {e.response.status_code}. Error: {e}"
                )
                return None
        except Exception as e:
            print(f"A general error occurred for conversation ID: {m13id}. Error: {e}")
        return None


if __name__ == "__main__":
    # Get input from console
    folder_path = input("Please enter folder path: ")
    excel_file = input("Please enter excel file for the output: ")
    excel_file = utility.validate_excel(filename=excel_file)

    # Initialize contacts
    contacts_list = []

    # Initialize counters for debugging
    total_files = len([f for f in os.listdir(folder_path) if f.endswith(".txt")])
    processed_files = 0

    # Process one folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            try:
                file_path = os.path.join(folder_path, file_name)
                m13id = utility.get_file_id(file_path)

                load_dotenv()
                db_config = {
                    "host": os.getenv("DB_HOST"),
                    "user": os.getenv("DB_USER"),
                    "password": os.getenv("DB_PASSWORD"),
                    "database": os.getenv("DB_NAME"),
                    "port": os.getenv("DB_PORT"),
                }

                # Get COD name
                db_manager = DatabaseManager(db_config=db_config)
                db_manager.connect()
                name_df = db_manager.fetch_name_by_m13(m13id=m13id)
                name = name_df.to_string(index=False, header=False)
                print(f"COD Name: {name}")

                with open(file_path, "r") as file:
                    original_conversation = file.read()
                    anonymized_text, original_name, original_phone = anonymize(
                        original_conversation, name
                    )
                    print(anonymized_text)
                    cleaned_text = utility.clean_html_styling(anonymized_text)
                    output = prompt_openai(cleaned_text, m13id)
                    print(output)

                    # Clean up JSON string
                    output = utility.clean_json(input_string=output)

                    # Convert the JSON into a Contact object
                    contact = utility.parse_json_to_contact(json_data=output)
                    if contact is None:
                        logging.error(f"Contact is None")

                    # Update the original name and phone number in the contact object
                    # Safeguard against errors if name/phone number not properly anonymized
                    if contact is not None:
                        contact.id = m13id
                        if contact.name == NAME_PLACEHOLDER:
                            logging.debug(
                                f"Changed {contact.name} into {original_name}"
                            )
                            contact.name = original_name
                        if contact.phone_number == PHONE_PLACEHOLDER:
                            logging.debug(
                                f"Changed {contact.phone_number} into {original_phone}"
                            )
                            contact.phone_number = original_phone

                    utility.contacts_to_excel(
                        contacts=[contact], excel_file_name=excel_file
                    )

                # Increment the counter and print progress
                processed_files += 1
                print(f"Processed {processed_files}/{total_files} files.")

            except Exception as e:
                logging.error(f"Error processing file {file_name}: {e}")

    print(f"Completed processing {processed_files} out of {total_files} files.")
