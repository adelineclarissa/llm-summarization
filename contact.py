from enum import Enum
import pandas as pd
import json


class Category(Enum):
    PROVINCE = "province"
    CITY = "city"
    KECAMATAN = "kecamatan"
    DESA = "desa"


class Contact:
    def __init__(self, **kwargs):
        self._id = kwargs.get("id", "")
        self._name = kwargs.get("name", "")
        self._phone_number = kwargs.get("phone_number", "")
        self._gender = kwargs.get("gender", "")
        self._age = kwargs.get("age", "")
        self._education = kwargs.get("education", "")
        self._occupation = kwargs.get("occupation", "")
        self._marriage = kwargs.get("marriage", "")
        self._attitude = kwargs.get("attitude", "")
        self._persona = kwargs.get("persona", "")
        self._summary = kwargs.get("summary", "")
        self._extra_info = kwargs.get("extra_info", "")
        self._status_hp = kwargs.get("status_hp", "")
        self._suku = kwargs.get("suku", "")
        self._province = kwargs.get("province", "")
        self._city = kwargs.get("city", "")
        self._kecamatan = kwargs.get("kecamatan", "")
        self._address = kwargs.get("address", "")  # Specific address like desa
        self._level = None
        self._df_database = None
        self.init_level()

    def __repr__(self):
        return f"Contact(name={self._name}, phone_number={self._phone_number}, gender={self._gender})"

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def suku(self):
        return self._suku

    @suku.setter
    def suku(self, value):
        self._suku = value

    @property
    def status_hp(self):
        return self._status_hp

    @status_hp.setter
    def status_hp(self, value):
        self._status_hp = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def phone_number(self):
        return self._phone_number

    @phone_number.setter
    def phone_number(self, value):
        self._phone_number = value

    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, value):
        self._gender = value

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        self._age = value

    @property
    def education(self):
        return self._education

    @education.setter
    def education(self, value):
        self._education = value

    @property
    def occupation(self):
        return self._occupation

    @occupation.setter
    def occupation(self, value):
        self._occupation = value

    @property
    def marriage(self):
        return self._marriage

    @marriage.setter
    def marriage(self, value):
        self._marriage = value

    @property
    def attitude(self):
        return self._attitude

    @attitude.setter
    def attitude(self, value):
        self._attitude = value

    @property
    def persona(self):
        return self._persona

    @persona.setter
    def persona(self, value):
        self._persona = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        self._summary = value

    @property
    def extra_info(self):
        return self._extra_info

    @extra_info.setter
    def extra_info(self, value):
        self._extra_info = value

    @property
    def province(self):
        return self._province

    @province.setter
    def province(self, value):
        self._province = value

    @property
    def city(self):
        return self._city

    @city.setter
    def city(self, value):
        self._city = value

    @property
    def kecamatan(self):
        return self._kecamatan

    @kecamatan.setter
    def kecamatan(self, value):
        self._kecamatan = value

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

    @property
    def level(self):
        if self._level == None:
            self.init_level()  # finds the level and set self._level
        return self._level

    # Private methods
    def _find_level(self, city):
        # A helper function to find the level
        if city is None:
            return None
        # if variable district has 'kota'
        if city.lower().split()[0] == "kota":
            # remove the first word
            city = " ".join(city.split()[1:])
        df = pd.read_csv("kota_kab.csv")
        str_district = df["name"].str.upper()
        words = str_district.str.split()
        name = words.apply(lambda x: " ".join(x[1:]))
        match_index = name.str.lower() == city.lower()
        if match_index.any():  # Check if any match is found
            index = match_index.idxmax()
            district_level = words[index][0]
            # print(f"The level of district {district} is {district_level}")
            return district_level
        else:
            print(f"City {city} not found in the dataset.")
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
        if self._kecamatan == "" or self._kecamatan == None:
            # print("self._kecamatan is empty or None")
            return
        kecamatan_input = self._kecamatan

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
                        self._province = kecamatan_input
                    elif category == Category.CITY:
                        self._city = kecamatan_input
                    elif category == Category.KECAMATAN:
                        self._kecamatan = kecamatan_input
                    elif category == Category.DESA:
                        self._address = kecamatan_input

                    # Debug
                    print(f"Change field {category} to {kecamatan_input}")
                    break
            else:
                print("No match found in any category.")
                return

        self._level = level

    def print_info(self):
        print(f"ID: {self._id}")
        print(f"Name: {self._name}")
        print(f"Phone Number: {self._phone_number}")
        print(f"Gender: {self._gender}")
        print(f"Age: {self._age}")
        print(f"Education: {self._education}")
        print(f"Occupation: {self._occupation}")
        print(f"Marital Status: {self._marriage}")
        print(f"Attitude: {self._attitude}")
        print(f"Persona: {self._persona}")
        print(f"Summary: {self._summary}")
        print(f"Extra Info: {self._extra_info}")
        print(f"Status HP: {self._status_hp}")
        print(f"Suku: {self._suku}")
        print(f"Province: {self._province}")
        print(f"City: {self._city}")
        print(f"Kecamatan: {self._kecamatan}")
        print(f"Address: {self._address}")
        print(f"Level: {self._level}")
