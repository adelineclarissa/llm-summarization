from enum import Enum
import pandas as pd
from dataclasses import dataclass, field
import logging


class Category(Enum):
    PROVINCE = "province"
    CITY = "city"
    KECAMATAN = "kecamatan"
    DESA = "desa"


@dataclass
class Contact:
    id: str = ""
    name: str = ""
    phone_number: str = ""
    gender: str = ""
    age: str = ""
    education: str = ""
    occupation: str = ""
    marriage: str = ""
    attitude: str = ""
    persona: str = ""
    summary: str = ""
    extra_info: str = ""
    status_hp: str = ""
    suku: str = ""
    province: str = ""
    city: str = ""
    kecamatan: str = ""
    address: str = ""
    _df_database: pd.DataFrame = field(init=False, default=None)

    _level = None  # Initialize level

    @property
    def level(self):
        if not hasattr(self, "_level"):  # Check if `_level` exists
            self.init_level()
        return self._level

    @level.setter
    def level(self, value):
        self._level = value

    _kota_kab_df = None

    @staticmethod
    def load_districts():
        if Contact._kota_kab_df is None:
            Contact._kota_kab_df = pd.read_csv("kota_kab.csv")
        return Contact._kota_kab_df

    # Private methods
    def _find_level(self, kota_kab_result):
        """A helper function to determine the level of a district (kota or kabupaten) based on the provided city name"""

        if kota_kab_result is None:
            return None

        # Normalize the name if variable district has 'kota'
        # logging.debug(f"Before normalization: {city}")
        # if city.lower().split()[0] == "kota":
        #     city = " ".join(city.split()[1:])
        # logging.debug(f"After normalization: {city}")

        # BYPASS: if kota_kab_result has "kota", return the level as kota
        if kota_kab_result.lower().split()[0] == "kota":
            return "KOTA"

        # Read the dataset
        df = self.load_districts()

        # Extract district names and levels
        str_district = df["name"].str.upper()
        words = str_district.str.split()
        name = words.apply(lambda x: " ".join(x[1:]))

        # Find the match in the dataset
        match_index = name.str.lower() == kota_kab_result.lower()
        if match_index.any():  # Check if any match is found
            index = match_index.idxmax()
            district_level = words[index][0]
            # print(f"The level of district {district} is {district_level}")
            logging.info(f"Match found: {kota_kab_result} is a {district_level}")
            return district_level
        else:
            logging.warning(f"City {kota_kab_result} not found in the dataset.")
            return None

    def _validate(self, addr_input, category: Category):
        """Validate an address input based on the specified category.

        Args:
            addr_input (str): The address input to validate.
            category (Category): The category of the address input.

        Raises:
            ValueError: If an invalid category is provided.

        Returns:
            tuple: A tuple containing a boolean indicating whether the address input is valid for the given category and a DataFrame of the filtered results.
        """
        if self._df_database is None:
            self.init_db()
        all_df = self._df_database

        categories = {
            Category.PROVINCE: "admin1Name_en",
            Category.CITY: "admin2Name_en",
            Category.KECAMATAN: "admin3Name_en",
            Category.DESA: "admin4Name_en",
        }

        if category in categories:
            filtered_df = all_df[
                all_df[categories[category]].str.lower() == addr_input.lower()
            ]
            if not filtered_df.empty:
                print(f"LOG: {addr_input} is a {category}")
                return (True, filtered_df)
            else:
                return (False, None)
        else:
            raise ValueError(f"Invalid category provided: {category}.")

    # Public methods
    def get_db(self):
        return self._df_database

    def init_db(self):
        database1 = "idn_admin4boundaries_tabulardata.xlsx"
        ADMIN1 = "admin1Name_en"  # province
        ADMIN2 = "admin2Name_en"  # kota/kabupaten
        ADMIN3 = "admin3Name_en"  # kecamatan
        ADMIN4 = "admin4Name_en"  # desa

        excel_book = pd.ExcelFile(database1)
        all_sheets = {}
        for sheet_name in excel_book.sheet_names:
            all_sheets[sheet_name] = excel_book.parse(sheet_name)

        df = pd.concat(all_sheets.values(), ignore_index=True)
        all_df = df[[ADMIN4, ADMIN3, ADMIN2, ADMIN1]]

        self._df_database = all_df

    # For testing
    def validate(self, addr_input, category):
        return self._validate(addr_input, category)

    def find_level(self, district):
        return self._find_level(district)

    def init_level(self):
        if self.kecamatan == "" or self.kecamatan == None:
            logging.warning("self.kecamatan is empty or None")
            return
        kecamatan_input = self.kecamatan

        if self._df_database is None:
            self.init_db()

        kota_kab_result = ""
        kecamatan_result = ""
        desa_result = ""

        try:
            # check if the kecamatan_input is actually a kecamatan
            isValid, district_df = self._validate(
                addr_input=kecamatan_input, category=Category.KECAMATAN
            )
        except (TypeError, AttributeError, ValueError) as e:
            if isinstance(e, TypeError):
                print("TypeError occurred:", e)
            elif isinstance(e, AttributeError):
                print("AttributeError occurred:", e)
            elif isinstance(e, ValueError):  # if category is invalid
                print("ValueError occured:", e)

        # if district_df is empty, we need to check if it's the other category
        if isValid:
            # find level
            kota_kab_result = district_df.iloc[0]["admin2Name_en"]
            logging.info(f"Mencari level dari kota/kab {str(kota_kab_result)}")
            level = self._find_level(kota_kab_result)
        else:
            level = None
            print("No match found in kecamatan. Checking other categories.")
            for category in [Category.DESA, Category.CITY, Category.PROVINCE]:
                is_valid, district_df = self._validate(
                    addr_input=kecamatan_input, category=category
                )
                if is_valid:
                    print(f"Found match in category: {category}")
                    if category == Category.PROVINCE:
                        self.province = kecamatan_input
                    elif category == Category.CITY:
                        self.city = kecamatan_input
                    elif category == Category.KECAMATAN:
                        self.kecamatan = kecamatan_input
                    elif category == Category.DESA:
                        self.address = kecamatan_input

                    # Debug
                    print(f"Change field {category} to {kecamatan_input}")
                    break
            else:
                print("No match found in any category.")
                return

        self._level = level
