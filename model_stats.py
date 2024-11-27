import pandas as pd
import inquirer
import logging
import re
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def normalize_attitude(term):
    if str(term.lower()) == "open":
        term = "Open (Terbuka)"
    return term


# Function to normalize phone numbers
def normalize_phone_number(phone):
    phone = str(phone)
    # Remove non-numeric characters
    phone = re.sub(r"\D", "", phone)
    # Remove leading zeros and ensure it starts with the country code
    if phone.startswith("0"):
        phone = "62" + phone[1:]
    if phone.startswith("8"):
        phone = "62" + phone

    if phone == "":
        phone = "Not a phone number"
    return phone


def normalize_persona(term):
    normalized = term.replace("/", "&")
    return normalized.split(" ")[0]


def normalize_education(term):
    if pd.isna(term) or term == "Tidak Dikenal":
        term = "Tidak Diketahui"

    if "SMA" in str(term):
        term = "SMA"

    return term


def normalize_marriage(term):
    term = str(term).lower()
    if term == "married":
        return "menikah"
    elif term == "single":
        return "lajang"
    elif term == "cerai":
        return "janda/duda"
    elif "widow" in term:
        return "janda/duda"
    return term


# Function to get user selection
def get_user_selection(headers):
    questions = [
        inquirer.Checkbox(
            "headers",
            message="Select columns to compare",
            choices=headers,
        ),
    ]
    logging.info("Prompting user to select columns to compare...")
    answers = inquirer.prompt(questions)
    logging.info(f"User selected columns: {answers['headers']}")
    return answers["headers"]


# Function to compare columns
def compare_columns(df1, df2, headers):
    accuracy_per_category = {}

    # Compare row by row, column by column
    for header in headers:
        differences = 0
        total_comparisons = 0

        if header in df1.columns and header in df2.columns:
            for idx, (id1, id2, value1, value2) in enumerate(
                zip(df1["M13 ID"], df2["M13 ID"], df1[header], df2[header]), start=1
            ):
                # Normalize phone numbers if the column is 'handphone'
                if header.lower() == "handphone":
                    value1 = normalize_phone_number(value1)
                    value2 = normalize_phone_number(value2)

                if header.lower() == "persona":
                    value1 = normalize_persona(value1)
                    value2 = normalize_persona(value2)

                if header.lower() == "education":
                    value1 = normalize_education(value1)
                    value2 = normalize_education(value2)

                if header.lower() == "marriage":
                    value1 = normalize_marriage(value1)
                    value2 = normalize_marriage(value2)

                if header.lower() == "attitude":
                    value1 = normalize_attitude(value1)
                    value2 = normalize_attitude(value2)

                logging.debug(f"Inference: {value1}, Control: {value2}")

                # Increment the total comparisons counter
                total_comparisons += 1

                if (
                    (str(value1).lower() == str(value2).lower())
                    or (str(value1).lower() in str(value2).lower())
                    or (str(value2).lower() in str(value1).lower())
                ):
                    continue
                else:
                    logging.info(
                        f"Difference in {header} on file {id1} {id2} Inference: '{value1}' != Control: '{value2}'"
                    )
                    differences += 1

        else:
            logging.error(f"Column '{header}' is not found in one of the DataFrames")

        # Store the accuracy for this category
        if total_comparisons > 0:
            accuracy_per_category[header] = (
                total_comparisons - differences
            ) / total_comparisons
        else:
            accuracy_per_category[header] = None  # No comparisons made for this header

    return accuracy_per_category


def validate_excel(filename: str):
    if ".xlsx" not in filename:
        filename = filename + ".xlsx"

    return "output/" + filename


def main(args):
    # Paths to the Excel files
    inference_sheet_path = validate_excel(args.inference)
    control_sheet_path = validate_excel(args.control)

    # Read the data
    logging.info("Reading Excel files...")
    inference_df = pd.read_excel(inference_sheet_path)
    control_df = pd.read_excel(control_sheet_path)
    logging.info("Excel files read successfully.")

    # Headers in the data
    all_headers = list(inference_df.columns)
    logging.info(f"Headers found: {all_headers}")

    # Get user selection
    selected_headers = get_user_selection(all_headers)

    # Compare the data
    logging.info("Comparing selected columns...")
    accuracy_per_category = compare_columns(inference_df, control_df, selected_headers)

    # Log accuracy for each category
    for category, accuracy in accuracy_per_category.items():
        if accuracy is not None:
            logging.info(f"Accuracy for {category}: {accuracy:.2%}")
        else:
            logging.warning(f"No comparisons made for {category}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--control", type=str, help="Excel sheet of control data", required=True
    )
    parser.add_argument(
        "--inference",
        type=str,
        help="Excel sheet of inference result data",
        required=True,
    )
    args = parser.parse_args()
    main(args)
