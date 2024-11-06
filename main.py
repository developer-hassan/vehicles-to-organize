import os

import logging
import sys

from utils import (
    ORGANIZED_DIR,
    AI_ORGANIZED_DIR
)

from helper_functions import (
    get_customized_brand_information,
    get_customized_family_information,
    get_customized_model_information,
    create_output_directories,
    load_brand_data,
    load_model_data,
    load_family_data,
    load_input_data,
    process_xlsx_files,
    write_data_to_excel,
    get_possible_brands_by_name
)

logging.basicConfig(stream=sys.stdout, level="DEBUG")
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Change the name according to the brand
BRAND_NAME: str = "Mercedes"
processed_df_filepath: str = os.path.join(ORGANIZED_DIR, f"VehicleOrganized_{BRAND_NAME}.xlsx")
ai_processed_df_filepath: str = os.path.join(AI_ORGANIZED_DIR, f"AI_VehicleOrganized_{BRAND_NAME}.xlsx")

if __name__ == "__main__":
    create_output_directories()

    # Load Verification Data
    brand_df = load_brand_data()
    family_df = load_family_data()
    model_df = load_model_data()

    # Load Input Data of car brand
    input_df = load_input_data(brand_name=BRAND_NAME)

    possible_brands = get_possible_brands_by_name(input_brand_name=BRAND_NAME, brand_data=brand_df)
    log.info(f"Possible brands: {possible_brands}")

    customized_brand_information = get_customized_brand_information(df_brand=brand_df)
    customized_family_information = get_customized_family_information(df_family=family_df)
    # customized_model_information = get_customized_model_information(df_model=model_df)

    # TODO: Need to replace this with a proper function when all fields completed
    # process_xlsx_files(
    #     df=input_df, brand_data=customized_brand_information, df_family=family_df,
    #     model_data=model_df, possible_brands=possible_brands, family_data=customized_family_information
    # )

    processed_df, ai_processed_df = process_xlsx_files(
        df=input_df, brand_data=customized_brand_information, df_family=family_df,
        model_data=model_df, possible_brands=possible_brands, family_data=customized_family_information
    )

    write_data_to_excel(data=processed_df, file_path=processed_df_filepath)
    write_data_to_excel(data=ai_processed_df, file_path=ai_processed_df_filepath)
