import re
import uuid
from itertools import permutations
from typing import Optional, Tuple
import time
import os
import pandas as pd
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

temp_stored = False


def extract_year(description):
    try:
        year_pattern = re.compile(r'(\d{4}|\d{2}[\'’])')
        match = year_pattern.search(description)

        extracted_year = None

        if match:
            year_str = match.group(1)

            if len(year_str) == 4:
                extracted_year = int(year_str)
            elif len(year_str) == 3 and year_str.endswith("'"):
                extracted_year = 1900 + int(year_str[:2])
            elif len(year_str) == 3 and year_str.endswith("’"):
                extracted_year = 1900 + int(year_str[:2])
            elif len(year_str) == 2:
                extracted_year = 1900 + int(year_str)

        extracted_description = description.replace(str(extracted_year), '') if extracted_year else description
        extracted_description = extracted_description.strip()
    except Exception as e:
        log.error(f"Error extracting year: {e}")
        extracted_year = None
        extracted_description = description

    return extracted_year, extracted_description


def __get_brand_within_year_range(brand_verification_data, brand_year) -> \
        tuple[Optional[str], Optional[str]]:
    for record_id, brand_name, start_year, end_year in brand_verification_data:
        if brand_year:
            if start_year and start_year <= brand_year <= end_year:
                return record_id, brand_name
            elif brand_year <= end_year:
                return record_id, brand_name
            else:
                print("BRAND YEAR AVAILABLE BUT IS NOT WITHIN RANGE. WHAT SHOULD WE DO NOW STEFAN?")
                return None, None
        else:
            return record_id, brand_name


def is_brand_name_replica(description):
    return any(keyword in description.lower() for keyword in ['clone', 'replica', 'handmade'])


def extract_brand(modified_description, brands, year, possible_brands: list):
    description_words = modified_description.split(' ')

    record_id, brand_name = None, None

    for word in description_words:
        word = word.lower()

        for possible_brand in possible_brands:
            if word == possible_brand.lower():
                record_id, brand_name = __get_brand_within_year_range(
                    brand_verification_data=brands[word], brand_year=year
                )

                if brand_name:
                    if is_brand_name_replica(modified_description):
                        brand_name_original = brand_name
                        brand_name = f"{brand_name}_replica"
                        modified_description = modified_description.replace(brand_name_original, '').strip()
                    else:
                        modified_description = modified_description.replace(brand_name, '').strip()

                return brand_name, record_id, modified_description

    return brand_name, record_id, modified_description


def __get_family_within_year_range(family_name, family_verification_data, family_year) -> tuple[
    Optional[str], Optional[str]]:
    record_id, start_year, end_year = family_verification_data

    if family_year:
        if start_year <= family_year <= end_year:
            return family_name, record_id
        elif family_year <= end_year:
            return family_name, record_id
        else:
            print(f"[ {record_id} ]FAMILY YEAR AVAILABLE BUT IS NOT WITHIN RANGE. WHAT SHOULD WE DO NOW STEFAN?")
            return None, None
    else:
        return family_name, record_id


def extract_family(modified_description, brand_name, year, family_data):
    if not brand_name:
        return None, None, modified_description, None, None
    if not brand_name.lower() in family_data:
        print("Inside Brand name not found in family_data.")
        return None, None, modified_description, None, None

    brand_families = family_data[brand_name.lower()]
    description_words = modified_description.split(' ')
    for word in description_words:
        word_lower = word.lower()

        # for family_key in brand_families:
        if any(word_lower == brand_family.lower() for brand_family in brand_families):
            family_name, id_record = __get_family_within_year_range(
                family_name=word, family_verification_data=brand_families[word_lower], family_year=year
            )
            if family_name:
                modified_description = modified_description.replace(str(family_name), '').strip()

            return family_name, id_record, modified_description, word, None

        if not word_lower.isdigit() and re.match(r'^[a-zA-Z]+\d+$', word_lower):
            letters_part = ''.join(re.findall(r'[a-zA-Z]+', word))
            numbers_part = ''.join(re.findall(r'\d+', word))

            # print(f"Letters part: {letters_part}")
            # print(f"Numbers part: {numbers_part}")

            if any(letters_part.lower() == brand_family.lower() for brand_family in brand_families):
                family_name, id_record = __get_family_within_year_range(
                    family_name=letters_part,
                    family_verification_data=brand_families[letters_part.lower()],
                    family_year=year
                )
                if family_name:
                    modified_description = modified_description.replace(str(word), '').strip()
                return family_name, id_record, modified_description, word, numbers_part

            elif any(numbers_part.lower() == brand_family.lower() for brand_family in brand_families):
                family_name, id_record = __get_family_within_year_range(
                    family_name=numbers_part,
                    family_verification_data=brand_families[numbers_part.lower()],
                    family_year=year
                )
                if family_name:
                    modified_description = modified_description.replace(str(word), '').strip()
                return family_name, id_record, modified_description, word, None
            # else:
            #     print(f"Letters part letters/digits: {letters_part}")
            #     print(f"Numbers part letters/digits: {numbers_part}\n")

        if not word_lower.isdigit() and re.match(r'^\d+[a-zA-Z]+$', word_lower):
            letters_part = ''.join(re.findall(r'[a-zA-Z]+', word))
            numbers_part = ''.join(re.findall(r'\d+', word))

            # print(f"Letters part: {letters_part}")
            # print(f"Numbers part: {numbers_part}")

            if any(letters_part.lower() == brand_family.lower() for brand_family in brand_families):
                family_name, id_record = __get_family_within_year_range(
                    family_name=letters_part,
                    family_verification_data=brand_families[letters_part.lower()],
                    family_year=year
                )
                if family_name:
                    modified_description = modified_description.replace(str(word), '').strip()
                return family_name, id_record, modified_description, word, numbers_part

            elif any(numbers_part.lower() == brand_family.lower() for brand_family in brand_families):
                family_name, id_record = __get_family_within_year_range(
                    family_name=numbers_part,
                    family_verification_data=brand_families[numbers_part.lower()],
                    family_year=year
                )
                if family_name:
                    modified_description = modified_description.replace(str(word), '').strip()
                return family_name, id_record, modified_description, word, None
            # else:
            #     print(f"Letters part digit/letters: {letters_part}")
            #     print(f"Numbers part digit/letters: {numbers_part}\n")
                # print("Inside word not found in family_data.")
                # return None, None, modified_description, None, None

    return None, None, modified_description, None, None


def extract_family_names(family_df, brand_name):
    # Fill NaN values in 'Marca' column with empty strings to avoid indexing issues
    family_df['Marca'] = family_df['Marca'].fillna('')

    # Filter the family_df for rows containing the given brand_name (case-insensitive)
    filtered_df = family_df[family_df['Marca'].str.lower().str.contains(brand_name.lower())]

    # Extract unique family names from the filtered DataFrame
    family_names = filtered_df['Famiglia'].unique()

    # log.debug(f"Filtered Family names: {family_names}")

    return family_names


def extract_family_id(family_name, year, df_family):
    """
    Extracts the family_id if the family_name exists and the year is within the valid range.

    Parameters:
    family_name (str): The family name to validate.
    year (int): The year to validate.
    df_family (pd.DataFrame): The DataFrame containing family records with columns 'FamilyName', 'AnnoInizioCalcolato', 'AnnoFineCalcolato', and 'FamilyID'.

    Returns:
    int or None: The family_id if valid, otherwise None.
    """
    # Check if family_name exists in df_family
    family_record = df_family[df_family['Famiglia'].str.lower() == family_name.lower()]

    if not family_record.empty:
        # Extract the first record (assuming unique family names)
        record = family_record.iloc[0]
        start_year = record['AnnoInizioCalcolato']
        end_year = record['AnnoFineCalcolato']

        if pd.isna(end_year):
            if year is not None:  # Check for NaN in end_year
                if year >= start_year:
                    return record['ID_Record']
            # print("ID RECORD: ", record['ID_Record'])
            if pd.isna(year):
                if year is not None:
                    if start_year <= year <= end_year:
                        print("ID RECORD: ", record['ID_Record'])
                        return record['ID_Record']
                    return None
                return record['ID_Record']
    return None


def clean_model_df(model_data):
    model_data["Mod_FamigliaA"] = model_data["Mod_FamigliaA"].str.replace('-', ' ').str.lower()
    model_data["Marca"] = model_data["Marca"].str.replace('-', ' ').str.lower()
    model_data["AnnoInizioCalcolato"].fillna(0)
    model_data["AnnoFineCalcolato"].fillna(2024)

    return model_data


def __get_model_within_year_range(model_year: Optional[int], start_year: int, end_year: int, model_name: str,
                                  record_id: int, series: str, stage: str):
    if model_year:
        if start_year <= model_year <= end_year:
            return model_name, record_id, series, stage
        elif start_year == 0 and model_year <= end_year:
            return model_name, record_id, series, stage
        else:
            return None, None, None, None
    else:
        return model_name, record_id, series, stage


def __get_model_in_year_range(model_year: Optional[int], start_year: int, end_year: int) -> bool:
    if model_year:
        if start_year <= model_year <= end_year:
            return True
        elif start_year == 0 and model_year <= end_year:
            return True
        else:
            return False
    else:
        return True


def extract_mode_stage(modified_description, model_data, brand_name, family_name, year):
    modello_a_serie = None
    id_record_model = None
    serie = None
    stage = None
    model_data = clean_model_df(model_data=model_data)
    if not brand_name or not family_name or not modified_description:
        return None, None, None, None

    filtered_data = model_data[
        (model_data["Marca"].str.lower() == brand_name.lower()) &
        (model_data["Mod_FamigliaA"].str.lower() == family_name.lower())
        ]

    for word in modified_description:
        word_lower = word.lower()

        for _, row in filtered_data.iterrows():
            if word_lower == row["Stage"].lower():
                modello_a_serie, id_record_model, serie, stage = __get_model_within_year_range(
                    model_year=year,
                    start_year=row['AnnoInizioCalcolato'],
                    end_year=row['AnnoFineCalcolato'],
                    model_name=row["Mod_FamigliaB"],
                    record_id=row["ID_Record"],
                    series=row["Serie"],
                    stage=row["Stage"]
                )
                if modello_a_serie:
                    break

        return modello_a_serie, id_record_model, serie, stage


def extract_modello_a_serie_and_stage(mod_digits, mod_strings, model_data: pd.DataFrame, extracted_year,
                                      extracted_brand, extracted_family):
    global temp_stored
    # 0. Initialize the to-returns with None
    modello_a_serie, mod_serie, mod_stage, mod_id_record = None, None, None, None

    # 1. Do not do any processing if brand or family is not found
    if not extracted_brand or not extracted_family:
        return modello_a_serie, mod_serie, mod_stage, mod_id_record

    # 2. Clean the model data
    model_data = clean_model_df(model_data=model_data)

    # 3. Filtered the records to get only the ones with extracted brand and family
    filtered_model_data = model_data[
        (model_data["Marca"].str.lower() == extracted_brand.lower()) &
        (model_data["Mod_FamigliaA"].str.lower() == extracted_family.lower())
        ]

    # 4. If single occurrence of filtered data, return the information
    if len(filtered_model_data) == 1:
        target_row = filtered_model_data.iloc[0]
        modello_a_serie = target_row["Mod_FamigliaA"]
        mod_serie = target_row["Serie"]
        mod_stage = target_row["Stage"]
        mod_id_record = target_row["ID_Record"]

    # 5. Iterate through the filtered data to get the desired output
    else:
        modello_a_serie_temp, mod_serie_temp, mod_stage_temp, mod_id_record_temp = None, None, None, None
        for _, row in filtered_model_data.iterrows():
            # 5.1. Check if model is within the year range
            is_model_within_range = __get_model_in_year_range(
                model_year=extracted_year,
                start_year=row['AnnoInizioCalcolato'],
                end_year=row['AnnoFineCalcolato']
            )

            if is_model_within_range:
                # 5.2. Check if extracted brand, and extracted mod_b_version are available in mod_famiglia_b
                mod_famiglia_b = row["Mod_FamigliaB"]

                if not temp_stored:
                    modello_a_serie_temp = mod_famiglia_b
                    mod_serie_temp = row["Serie"]
                    mod_stage_temp = row["Stage"]
                    mod_id_record_temp = row["ID_Record"]
                    temp_stored = True

                if (extracted_family.lower() in mod_famiglia_b.lower()) and any(
                        str(num) in mod_famiglia_b.lower() for num in mod_digits):
                    modello_a_serie = mod_famiglia_b
                    mod_serie = row["Serie"]
                    mod_stage = row["Stage"]
                    mod_id_record = row["ID_Record"]
                    break
                # else:
                #     if extracted_family == "SLK" and extracted_year == 2004:
                #         print(f"extracted_family lower: {extracted_family.lower()}")
                #         print(f"mod famiglia b: {mod_famiglia_b.lower()}")
                #         print(f"Mod digits: {mod_digits}")

                if extracted_family.lower() in mod_famiglia_b.lower() and any(
                        mod_string.lower() == word for word in mod_famiglia_b.lower().split() for mod_string in
                        mod_strings):
                    modello_a_serie = mod_famiglia_b
                    mod_serie = row["Serie"]
                    mod_stage = row["Stage"]
                    mod_id_record = row["ID_Record"]
                    break

                if extracted_family.lower() == mod_famiglia_b.lower():
                    modello_a_serie = mod_famiglia_b
                    mod_serie = row["Serie"]
                    mod_stage = row["Stage"]
                    mod_id_record = row["ID_Record"]
                    break

                if extracted_family.lower() in mod_famiglia_b.lower() and any(
                        str(mod_digit).lower() == word for word in mod_famiglia_b.lower().split() for mod_digit in
                        mod_digits):
                    modello_a_serie = mod_famiglia_b
                    mod_serie = row["Serie"]
                    mod_stage = row["Stage"]
                    mod_id_record = row["ID_Record"]
                    break

        if modello_a_serie_temp is not None and modello_a_serie is None:
            modello_a_serie = modello_a_serie_temp
            mod_serie = mod_serie_temp
            mod_stage = mod_stage_temp
            mod_id_record = mod_id_record_temp

        temp_stored = False

    return modello_a_serie, mod_serie, mod_stage, mod_id_record


def extract_modello_a_serie(modified_description, brand_name, family_name, year, model_data, number_part):
    if modified_description:
        modified_description = modified_description.replace("(", "").replace(")", "")
    # call the mod stage function
    modello_a_serie, id_record_model, serie, stage = extract_mode_stage(modified_description=modified_description,
                                                                        model_data=model_data, brand_name=brand_name,
                                                                        family_name=family_name, year=year)
    if modello_a_serie:
        return modello_a_serie, id_record_model, serie, stage
    else:
        model_data = clean_model_df(model_data=model_data)

        if not brand_name or not family_name:
            return None, None, None, None

        filtered_data = model_data[
            (model_data["Marca"].str.lower() == brand_name.lower()) &
            (model_data["Mod_FamigliaA"].str.lower() == family_name.lower())
            ]

        if filtered_data.empty:
            return None, None, None, None

        matching_rows = filtered_data[filtered_data["Mod_FamigliaA"].str.lower() == family_name.lower()]

        if len(matching_rows) == 1:
            row = matching_rows.iloc[0]
            modello_a_serie = row['Mod_FamigliaA']
            id_record_model = row["ID_Record"]
            serie = row["Serie"]
            stage = row["Stage"]

        for _, row in matching_rows.iterrows():
            modello_a_serie, id_record_model, serie, stage = __get_model_within_year_range(
                model_year=year,
                start_year=row['AnnoInizioCalcolato'],
                end_year=row['AnnoFineCalcolato'],
                model_name=row["Mod_FamigliaB"],
                record_id=row["ID_Record"],
                series=row["Serie"],
                stage=row["Stage"]
            )
            if number_part:
                if modello_a_serie and str(number_part) in modello_a_serie:
                    break

            else:
                if modello_a_serie:
                    break

        return modello_a_serie, id_record_model, serie, stage


def extract_model_part_b(description: str, subtraction_list: list):
    model_part_b = description

    for subtraction in subtraction_list:
        if subtraction is not None:
            model_part_b = model_part_b.replace(str(subtraction), '')

    return model_part_b.strip()


def calculate_accuracy(brand_name, family, model, year, marca_cod, family_cod, model_cod, serie, stage):
    accuracy_levels = {
        'A': 100,
        'B': 95,
        'C': 90,
        'D': 85,
        'E': 80,
        'F': 60,
        'G': 40,
        'H': 20,
        'I': 0,
    }
    accuracy = 0
    if brand_name and family and model and year and family_cod and marca_cod and model_cod and serie and stage:
        accuracy = accuracy_levels['A']
    elif brand_name and family and year and (
            (marca_cod and family_cod) or (marca_cod and model_cod) or (family_cod and model_cod)) and serie and stage:
        accuracy = accuracy_levels['B']
    elif brand_name and family and year and serie and stage:
        accuracy = accuracy_levels['C']
    elif brand_name and family and model and (serie or stage) and year:
        accuracy = accuracy_levels['D']
    elif brand_name and family and model and year:
        accuracy = accuracy_levels['E']
    elif brand_name and family and year:
        accuracy = accuracy_levels['F']
    elif brand_name and year:
        accuracy = accuracy_levels['G']
    elif brand_name or year:
        accuracy = accuracy_levels['H']
    else:
        accuracy = accuracy_levels['I']
    return accuracy
