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


def setup_logging():
    # instantiate logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Change this

    # formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # file handler
    file_handler = logging.FileHandler("app_debug.log")
    file_handler.setFormatter(formatter)

    # add handlers to logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)


# Anonymizes a full name in a conversation, accounting for first, middle (if any), and last names.
def anonymize(
    conversation,
    original_name,
    name_placeholder=NAME_PLACEHOLDER,
    phone_placeholder=PHONE_PLACEHOLDER,
):

    original_name = original_name.replace("(", "").replace(")", "")
    name_parts = original_name.split()
    name_pattern = (
        r"\b("
        + r"|".join(
            [re.escape(part) for part in name_parts]
            + [r"\s+".join(map(re.escape, name_parts))]
        )
        + r")\b"
    )
    name_with_parentheses_pattern = (
        r"(" + r"\s+".join(map(re.escape, name_parts)) + r")\s*\(([^)]+)\)"
    )
    name_regex = re.compile(name_pattern, re.IGNORECASE)
    name_with_parentheses_regex = re.compile(
        name_with_parentheses_pattern, re.IGNORECASE
    )
    conversation = name_regex.sub(name_placeholder, conversation)
    conversation = name_with_parentheses_regex.sub(
        lambda match: f"{name_placeholder} ({name_placeholder})", conversation
    )

    # Anonymize phone numbers
    phone_pattern = r"(?<!\d)(?:\+62|08)\d{9,}\b"

    phone_regex = re.compile(phone_pattern)
    original_phone_numbers = phone_regex.findall(conversation)
    conversation = phone_regex.sub(phone_placeholder, conversation)

    return conversation, original_name, original_phone_numbers


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
                model="gpt-4o-mini",
                messages=prompt,
            )
            output = completion.choices[0].message.content
            logger.debug(output)
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
                logger.error(
                    f"Rate limit exceeded for conversation ID: {m13id}. Attempt {attempt + 1} of {retries}."
                )
                if attempt < retries - 1:
                    time.sleep(delay)  # Wait before retrying
                    delay *= backoff_factor  # Exponential backoff
                else:
                    logger.error(
                        f"All retry attempts failed for conversation ID: {m13id}. Please wait and try again later."
                    )
                    return None
            else:
                logger.error(
                    f"HTTP error for conversation ID: {m13id}. Status: {e.response.status_code}. Error: {e}"
                )
                return None
        except Exception as e:
            print(f"A general error occurred for conversation ID: {m13id}. Error: {e}")
        return None


def prompt_summary(text, m13id):
    prompt = [
        {
            "role": "user",
            "content": f"""
    You are a staff member of a non-profit mission agency. Please disregard previous knowledge and focus only on the given conversation between another staff member and a potential contact for evangelization. Extract the following data points in JSON format in Indonesian, with the specified keys:
    Your task is to extract the following information and present it as a paragraph in Indonesian:
    1. The name of the agent or mediator that was last to speak with the contact.
    2. The contact’s initial felt need, what he/she asked or talked about in the beginning of the conversation.
    3. Summarize the Agent’s expalnation about Isa Al-Masih (refer to Isa Al-Masih as IAM).  This explanation is aimed to console or give advice to the contact after they talk about their felt need.
    4. Extract the contact's opinion about Isa Al-Masih according to the Gospel (IAM versi Injil)

    Here is the conversation:

    {text}

    """,
        }
    ]
    completion = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=prompt,
    )
    output = completion.choices[0].message.content
    logger.debug(output)
    return output


# This function cleans the HTML formatting and anonymize the text
def anonymize_and_clean(file_path: str, m13id: str):
    load_dotenv()
    db_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": os.getenv("DB_PORT"),
    }

    # get the contact's name from database
    db_manager = DatabaseManager(db_config=db_config)
    db_manager.connect()
    name_df = db_manager.fetch_name_by_m13(m13id=m13id)
    name = name_df.to_string(index=False, header=False)

    with open(file_path, "r") as file:
        conversation = file.read()
        conversation = utility.clean_html_styling(conversation)
        clean_conversation, original_name, original_phone = anonymize(
            conversation, name
        )
    db_manager.disconnect()
    # Dump the clean conversation
    with open(f"test-dump-2/{m13id}_clean.txt", "w") as f:
        f.write(clean_conversation)

    return clean_conversation, original_name, original_phone


def main(folder_path: str, excel_file: str):
    total_files = len([f for f in os.listdir(folder_path) if f.endswith(".txt")])
    processed_files = 0
    skipped_ids = []

    # process one folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            try:
                file_path = os.path.join(folder_path, file_name)
                m13id = utility.get_file_id(file_path)
                cleaned_text, original_name, original_phone = anonymize_and_clean(
                    file_path, m13id
                )

                output = prompt_openai(cleaned_text, m13id)
                output = utility.clean_json(input_string=output)
                contact = utility.parse_json_to_contact(json_data=output)

                # prevent exceptions in the next block if contact is None
                if contact is not None:
                    contact.id = m13id  # IMPORTANT
                    contact.init_level()  # IMPORTANT: Initialize level
                    if contact.name == NAME_PLACEHOLDER:
                        logger.debug(f"Changed {contact.name} into {original_name}")
                        contact.name = original_name
                    if contact.phone_number == PHONE_PLACEHOLDER:
                        logger.debug(
                            f"Changed {contact.phone_number} into {original_phone}"
                        )
                        contact.phone_number = original_phone
                    # parse contact and output it in excel
                    success = utility.contact_to_excel(contact, excel_file)

                else:
                    logger.error(
                        f"Contact is None. Appending ID '{m13id}' to the skipped_id list."
                    )
                    skipped_ids.append(m13id)

                # LOG - output json dump into a txt file
                dumpfile = f"test-output-dump/{m13id}-dump.txt"
                with open(dumpfile, "w") as f:
                    f.write(output)

                # increment the counter and log the progress
                processed_files += 1
                logger.info(f"Processed {processed_files}/{total_files} files.")

            except Exception as e:
                # TODO: give more explanation about the exception
                logger.error(f"Error processing file {file_name}: {e}")

    # finally
    if skipped_ids:
        logger.warning(
            f"Processed {processed_files}/{total_files} files. Skipped {len(skipped_ids)} files with IDs: {', '.join(skipped_ids)}"
        )
    else:
        logger.info(
            f"Successfully processed all files in the folder."
        )  # see if this works lol


if __name__ == "__main__":
    client_openai = openai.OpenAI()
    openai.api_key = os.environ["OPENAI_API_KEY"]
    setup_logging()
    logger = logging.getLogger(__name__)

    folder_path = input("Please enter folder path: ")
    excel_file = input("Please enter excel file for the output: ")
    excel_file = utility.validate_excel(filename=excel_file)

    main(folder_path, excel_file)
