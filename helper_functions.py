import json
import re
import pandas as pd
import os
from utils import (
    INPUT_DIR,
    OUTPUT_DIR,
    ORGANIZED_DIR,
    AI_ORGANIZED_DIR,
    BRAND_PATH,
    FAMILY_PATH,
    MODEL_PATH
)

from output_attributes import (
    extract_year,
    extract_brand,
    extract_family_names,
    extract_family,
    extract_family_id,
    extract_modello_a_serie,
    extract_model_part_b,
    calculate_accuracy,
    extract_modello_a_serie_and_stage,
    extract_family_from_model
)

from langchain_service.agent import LangchainAgent

import logging

log = logging.getLogger()
log.setLevel(logging.INFO)


def get_ai_vehicles_organized_fields(brand_record_id, family_record_id, id_record_model, accuracy):
    additional_fields = {
        'Cod_brand': brand_record_id,
        'Cod_family': family_record_id,
        'Cod_model': id_record_model,
        'Accuracy': accuracy
    }

    return additional_fields


def append_to_vehicles(vehicles_list, cod_veicolo, year, brand, modello_a_serie, modello_b_versione,
                       mod_verificato, family_name, mod_versione, mod_serie, mod_allestimento,
                       mod_stage, mod_potenza, description, is_ai, additional_fields=None):
    vehicle_data = {
        'CodVeicolo': cod_veicolo,
        'Anno': year,
        'Marca': brand,
        'Modello_A_Serie': modello_a_serie,
        'Model_B_Versisone': modello_b_versione,
        'Mod_Verificato': mod_verificato,
        'Mod_Familigoa': family_name,
        'Mod_Versione': mod_versione,
        'Mod_Serie': mod_serie,
        'Mod_Allestimento': mod_allestimento,
        'Mod_Stage': mod_stage,
        'Mod_Potenza': mod_potenza,
        'Modello_Descriz_Orignale': description,
        'AI': is_ai
    }

    if additional_fields:
        vehicle_data.update(additional_fields)

    vehicles_list.append(vehicle_data)


def get_customized_brand_information(df_brand: pd.DataFrame) -> dict:
    brand_dict = {}

    for _, row in df_brand.iterrows():
        brand_name = row['Brand Name']
        start_year = row['Year begin']
        end_year = row['Year End']

        # if pd.isna(start_year):
        #     start_year = ""
        if pd.isna(end_year):
            end_year = 2024

        aliases = [
            brand_name,
            row.get('Extended Brand Name', ''),
            row.get('Brand Name short', ''),
            row.get('Alias Brand Name', '')
        ]

        for alias in aliases:
            if pd.notna(alias) and alias:
                alias_lower = alias.lower()

                if "; " in alias_lower:
                    alias_list = alias_lower.split('; ')
                else:
                    alias_list = [alias_lower]

                for single_alias in alias_list:
                    if single_alias == "":
                        continue

                    single_alias = single_alias.replace(';', '') if ';' in single_alias else single_alias

                    if single_alias in brand_dict:
                        brand_dict[single_alias].append((row['Brand cod'], brand_name, start_year, end_year))
                    else:
                        brand_dict[single_alias] = [(row['Brand cod'], brand_name, start_year, end_year)]

    return brand_dict


def get_customized_family_information(df_family: pd.DataFrame) -> dict:
    family_dict = {}

    for _, row in df_family.iterrows():
        brand_name = row['Marca']
        if isinstance(brand_name, str):
            brand_name = brand_name.replace('-', ' ').lower()

        family_name = row['Famiglia']
        if isinstance(family_name, str):
            family_name = family_name.replace('-', ' ').lower()

        start_year = row['AnnoInizioCalcolato']
        end_year = row['AnnoFineCalcolato']

        if pd.isna(end_year):
            end_year = 2024

        if brand_name not in family_dict:
            family_dict[brand_name] = {}

        family_dict[brand_name][family_name] = (row['ID_Record'], start_year, end_year)
    return family_dict


def get_customized_model_information(df_model: pd.DataFrame) -> dict:
    model_dict = {}

    for _, row in df_model.iterrows():
        brand_name = row['Marca']
        if isinstance(brand_name, str):
            brand_name = brand_name.replace('-', ' ').lower()
        famiglia_a = row['Mod_FamigliaA']
        if isinstance(famiglia_a, str):
            famiglia_a = famiglia_a.replace('-', ' ').lower()

        famiglia_b = row['Mod_FamigliaB']
        # if isinstance(famiglia_b, str):
        # famiglia_b = famiglia_b.replace('-', ' ')

        year_begin = row['AnnoInizioCalcolato']
        year_end = row['AnnoFineCalcolato']

        # Assuming year_end being NaN means the range is open-ended up to 2024
        if pd.isna(year_end):
            year_end = 2024

        if brand_name not in model_dict:
            model_dict[brand_name] = {}

        model_dict[brand_name][famiglia_a] = (
        row['ID_Record'], row['Mod_FamigliaB'], row['Serie'], row['Stage'], year_begin, year_end)

    return model_dict


def create_output_directories():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(ORGANIZED_DIR):
        os.makedirs(ORGANIZED_DIR)
    if not os.path.exists(AI_ORGANIZED_DIR):
        os.makedirs(AI_ORGANIZED_DIR)

    return True


def load_brand_data() -> pd.DataFrame:
    brand_data = pd.read_excel(BRAND_PATH)
    return brand_data


def load_family_data() -> pd.DataFrame:
    family_data = pd.read_excel(FAMILY_PATH)
    return family_data


def load_model_data() -> pd.DataFrame:
    model_data = pd.read_excel(MODEL_PATH)
    return model_data


def load_input_data(brand_name: str) -> pd.DataFrame:
    file_path = os.path.join(INPUT_DIR, f'VehicleToOrganize_{brand_name}.xlsx')
    df = pd.read_excel(file_path)
    # df = df.head(500)
    return df


def extract_digits_from_modello_b_versione(input_string) -> tuple:
    digits_list = []  # Initialize an empty list to store extracted numbers
    strings_list = []  # Initialize an empty list to store purely string words

    if input_string:  # Check if the string is not empty
        words = input_string.split()  # Split the string into words

        for word in words:
            word_lower = word.lower()  # Convert word to lowercase

            # Check if the word contains only digits
            if word.isdigit():
                digits_list.append(int(word))  # Append the digit as an integer

            # Check if the word has the pattern: letters followed by numbers (e.g., G550)
            elif re.match(r'^[a-zA-Z]+\d+$', word_lower):
                # Extract the numeric part from the word and append it to the list
                numbers_part = ''.join(re.findall(r'\d+', word))
                digits_list.append(int(numbers_part))

            # Check if the word contains only letters (pure string)
            elif word.isalpha():
                strings_list.append(word)  # Append the word to the strings_list
    if "AMG" in strings_list and "GT" in strings_list:
        strings_list.remove("AMG")

    return digits_list, strings_list  # Return both lists as a tuple


def extract_strings_and_digits_for_family(input_string):
    digits_list = []
    strings_list = []

    if input_string:
        words = input_string.split()

        for word in words:
            word_lower = word.lower()

            # Check if the word contains only digits
            if word.isdigit():
                digits_list.append(int(word))

            # Check if the word contains only letters (pure string)
            elif word.isalpha():
                strings_list.append(word)  # Append the word to the strings_list

            # Check if the word has the pattern: letters followed by numbers (e.g., G550)
            elif re.match(r'^[a-zA-Z]+\d+$', word_lower):
                # Extract the numeric part from the word and append it to the list
                numbers_part = ''.join(re.findall(r'\d+', word))
                digits_list.append(int(numbers_part))

    if "AMG" in strings_list and "GT" in strings_list:
        strings_list.remove("AMG")

    return digits_list, strings_list  # Return both lists as a tuple


def process_xlsx_files(df, brand_data, df_family, model_data: pd.DataFrame, possible_brands: list, family_data):
    no_family_name_rows = []
    no_family_name_descriptions = []

    vehicles_organized, ai_vehicles_organized, agent_vehicles_organized, agent_ai_vehicles_organized = [], [], [], []

    df['Modello_Descriz_Originale'] = df['Modello_Descriz_Originale'].fillna('')
    df.dropna(subset=['Modello_Descriz_Originale'], inplace=True)
    df = df[df['Modello_Descriz_Originale'].str.strip() != '']

    df['Modello_Descriz_Originale'] = (
        df['Modello_Descriz_Originale']
        .str.replace('-replica', ' Replica')
        .str.replace('Rolls-Royce', 'Rolls Royce')
        .str.replace('Mercedes-Benz', 'Mercedes Benz')
        .str.replace('-', ' ')
        .str.replace('Original Owner', '')
        .str.replace('No reserve:', '')
        .str.replace('No Reserve:', '')
        .str.replace("’", " ")
    )

    valid_family_names = []

    # try:
    for index, row in df.iterrows():
        description = row.get('Modello_Descriz_Originale', '')
        cod_veicolo = row.get('CodVeicolo', '')
        mod_potenza = row.get('Mod_Potenza', '')
        mod_allestimento = row.get('Mod_Allestimento', '')
        mod_verificato = row.get('Mod_Verificato', '')
        mod_versione = row.get('Mod_Versione', '')

        # print(f"Original Description: {description}")

        year, modified_description = extract_year(description)
        # print(f"Extracted Year: {year}")

        brand, brand_record_id, modified_description = extract_brand(
            modified_description=modified_description, brands=brand_data,
            year=year, possible_brands=possible_brands
        )
        # print(f"Extracted Brand: {brand}")

        # TODO: CHECKPOINT DONE TILL BRAND EXTRACTION

        family_name, family_record_id, modified_description, family_word, number_part = extract_family(
            modified_description=modified_description, brand_name=brand, year=year, family_data=family_data
        )

        # TODO: CHECKPOINT till initial working family extraction

        # mod_digits, mod_strings = extract_strings_and_digits_for_family(input_string=description)
        model_version_string = extract_model_part_b(
            description=description, subtraction_list=[year, brand, family_name]
        )

        modello_b_versione_digits, modello_b_versione_strings = extract_digits_from_modello_b_versione(
            input_string=model_version_string)

        if family_name is None:
            family_name, family_record_id = extract_family_from_model(
                mod_digits=modello_b_versione_digits,
                mod_strings=modello_b_versione_strings,
                model_data=model_data,
                extracted_year=year,
                extracted_brand=brand
            )
            family_word = family_name

        if family_name is None:
            print(f"Original description: {description}")
            print(f"Mod Digits: {modello_b_versione_digits}")
            print(f"Mod Strings: {modello_b_versione_strings}")

        modello_a_serie, mod_serie, mod_stage, mod_id_record = extract_modello_a_serie_and_stage(
            mod_digits=modello_b_versione_digits, mod_strings=modello_b_versione_strings, model_data=model_data,
            extracted_year=year, extracted_brand=brand, extracted_family=family_name
        )

        modello_b_versione = extract_model_part_b(
            description=description, subtraction_list=[year, brand, family_word, modello_a_serie]
        )

        accuracy = calculate_accuracy(brand, family_name, modello_a_serie, year, brand_record_id, family_record_id,
                                      mod_id_record, mod_serie, mod_stage)

        append_to_vehicles(
            vehicles_list=vehicles_organized, cod_veicolo=cod_veicolo, year=year, brand=brand,
            modello_a_serie=modello_a_serie, modello_b_versione=modello_b_versione, mod_verificato=mod_verificato,
            family_name=family_name, mod_versione=mod_versione, mod_serie=mod_serie,
            mod_allestimento=mod_allestimento, mod_stage=mod_stage, mod_potenza=mod_potenza,
            description=description, is_ai="No"
        )

        additional_fields = get_ai_vehicles_organized_fields(
            brand_record_id=brand_record_id, family_record_id=family_record_id,
            id_record_model=mod_id_record, accuracy=accuracy
        )
        append_to_vehicles(
            vehicles_list=ai_vehicles_organized, cod_veicolo=cod_veicolo, year=year, brand=brand,
            modello_a_serie=modello_a_serie, modello_b_versione=modello_b_versione, mod_verificato=mod_verificato,
            family_name=family_name, mod_versione=mod_versione, mod_serie=mod_serie,
            mod_allestimento=mod_allestimento, mod_stage=mod_stage, mod_potenza=mod_potenza,
            description=description, is_ai="No", additional_fields=additional_fields
        )

    if no_family_name_descriptions:
        pass
        # handle_no_family_name_rows(
        #     no_family_name_rows, no_family_name_descriptions, valid_family_names, brand_data, possible_brands,
        #     df_family, model_df, agent_vehicles_organized, agent_ai_vehicles_organized
        # )

    # except Exception as e:
    #     print(f"Exception occurred here: {str(e)}")

    log.debug(f"Total records: {len(df)}")

    log.debug(f"Total vehicles organized: {len(vehicles_organized)}")
    log.debug(f"Total AI vehicles organized: {len(ai_vehicles_organized)}")

    log.debug(f"Total agent vehicles organized: {len(agent_vehicles_organized)}")
    log.debug(f"Total agent AI vehicles organized: {len(agent_ai_vehicles_organized)}")

    log.debug(f"Total output records: {len(vehicles_organized) + len(agent_vehicles_organized)}")
    results = vehicles_organized + agent_vehicles_organized
    ai_results = ai_vehicles_organized + agent_ai_vehicles_organized

    result_df = pd.DataFrame(results)
    ai_results_df = pd.DataFrame(ai_results)
    return result_df, ai_results_df


def write_data_to_excel(data: pd.DataFrame, file_path: str):
    data.to_excel(file_path, index=False)
    print(f"Data written to {file_path}")


def get_clean_aliases(alias_string) -> list:
    alias_string = alias_string.strip().rstrip(';')
    aliases = [alias.strip() for alias in alias_string.split(';')]
    aliases = [alias for alias in aliases if alias]

    return aliases


def get_possible_brands_by_name(input_brand_name: str, brand_data: pd.DataFrame) -> list:
    possible_brands_list = []

    brand_names = brand_data["Brand Name"].tolist()

    for brand_name in brand_names:
        if input_brand_name.lower() in brand_name.lower():
            alias_brand_name = brand_data.loc[brand_data["Brand Name"] == brand_name, "Alias Brand Name"].values[0]
            possible_brands_list.append(brand_name)

            if alias_brand_name and not pd.isna(alias_brand_name):
                clean_aliases = get_clean_aliases(alias_string=alias_brand_name)
                possible_brands_list.extend(clean_aliases)

    return possible_brands_list
