from contact import Contact
import json
import logging
import os
import openpyxl
import re

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG to capture all messages
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app_debug.log"),  # Log file name
        logging.StreamHandler(),  # Continue to print to console as well
    ],
)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


def parse_json_to_contact(json_data):
    try:
        # json_data = validate_and_fix_json(json_data=json_data)
        data = json.loads(json_data)

        contact_info = {
            "name": data.get("name_result", ""),
            "phone_number": data.get("handphone_result", ""),
            "gender": data.get("gender_result", ""),
            "age": data.get("age_result", ""),
            "education": data.get("education_result", ""),
            "occupation": data.get("occupation_result", ""),
            "marriage": data.get("marriage_result", ""),
            "attitude": data.get("attitude_result", ""),
            "persona": data.get("persona_initial_theme", ""),
            "summary": data.get("comments_idn", ""),
            "extra_info": data.get("extra_info", ""),
            "status_hp": data.get("status_hp_result", ""),
            "suku": data.get("suku_result", ""),
            "province": data.get("address_province_result", ""),
            "city": data.get("address_city_result", ""),
            "kecamatan": data.get("address_kecamatan_result", ""),
            "address": data.get("address_detail_result", ""),
        }

        return Contact(**contact_info)
    except json.decoder.JSONDecodeError as e:
        logging.error(f"Encountered an error when parsing the JSON: {e}")
    except Exception as e:
        logging.error(f"Error parsing JSON to contact: {e}")
    return None  # This will cause error


EXCEL_HEADERS = [
    "M13 ID",
    "Name",
    "Attitude",
    "Handphone",
    "Persona",
    "Status HP",
    "Suku",
    "Gender",
    "Province",
    "Age (now)",
    "Level",
    "Education",
    "City",
    "Occupation",
    "Kecamatan",
    "Marriage",
    "Address",
    "Extra Info",
    "Comments",
]


def contacts_to_excel(contacts, excel_file_name):
    if os.path.exists(excel_file_name):
        wb = openpyxl.load_workbook(excel_file_name)
        ws = wb.active
        headers = [cell.value for cell in ws[1]]  # Read the first row as headers
    else:
        # Create a new Excel workbook and select the active worksheet
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Contacts"
        headers = EXCEL_HEADERS
        ws.append(headers)

    for contact in contacts:
        if contact is None:
            logging.error("Contact is None in contacts_to_excel. Skipping...")
            continue
        row_data = [
            str(contact._id),
            str(contact._name),
            str(contact._attitude),
            str(contact._phone_number),
            str(contact._persona),
            str(contact._status_hp),
            str(contact._suku),
            str(contact._gender),
            str(contact._province),
            str(contact._age),
            str(contact.level),
            str(contact._education),
            str(contact._city),
            str(contact._occupation),
            str(contact._kecamatan),
            str(contact._marriage),
            str(contact._address),
            str(contact._extra_info),
            str(contact._summary),
        ]
        ws.append(row_data)

    wb.save(excel_file_name)


# This function extracts and returns the ID in the format "<A-Z> <4 digit numbers>" from a file path
def get_file_id(file_path):
    pattern = r"([A-Z])\s(\d{4})"
    file_name = os.path.basename(file_path)
    logging.debug(f"Extracted file name: {file_name}")
    match = re.search(pattern, file_name)
    if match:
        logging.info(f"Match found: {match.group(0)}")
        return f"{match.group(1)} {match.group(2)}"
    else:
        logging.info("No match found.")
        return None


def clean_json(input_string):
    """
    Removes everything before the first `{` and after the last `}` in the given string.

    :param input_string: The string to clean.
    :return: The cleaned string or an empty string if `{` or `}` is missing.
    """
    try:
        start = input_string.index("{")
        end = input_string.rindex("}")
        return input_string[start : end + 1]
    except ValueError:
        # If `{` or `}` is not found, return an empty string
        return ""


# This function extracts and returns the ID in the format "<A-Z> <4 digit numbers>" from a file path
def get_file_id(file_path):
    pattern = r"([A-Z])\s(\d{4})"
    file_name = os.path.basename(file_path)
    logging.debug(f"Extracted file name: {file_name}")
    match = re.search(pattern, file_name)
    if match:
        logging.info(f"Match found: {match.group(0)}")
        return f"{match.group(1)} {match.group(2)}"
    else:
        logging.info("No match found.")
        return None


def validate_excel(filename: str):
    if ".xlsx" not in filename:
        return filename + ".xlsx"
    else:
        return filename
