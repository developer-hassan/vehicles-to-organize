# def handle_no_family_name_rows(
#         no_family_name_rows, no_family_name_descriptions, valid_family_names, brand_data, possible_brands,
#         df_family, model_df, agent_vehicles_organized, agent_ai_vehicles_organized
# ):
#     print("AGENT CALLED")
#     responses = []
#     try:
#         print(f"Total number of records to be handled by agent: {len(no_family_name_rows)}")
#
#         # Initialize the descriptions list with the original data
#         descriptions_list = no_family_name_descriptions
#         agent = LangchainAgent()
#
#         request_number = 1
#         while len(descriptions_list) > 300:
#             # Split the current descriptions into a chunk of 300 and the rest
#             descriptions_chunk = descriptions_list[:300]
#             descriptions_list = descriptions_list[300:]
#
#             # Get response from the agent for the current chunk
#             log.info(f"Making Groq request number: {request_number}")
#             chunk_response = agent.get_response(valid_names=valid_family_names, descriptions=descriptions_chunk)
#
#             start_index = chunk_response.find('{')
#             end_index = chunk_response.rfind('}')
#
#             json_data = chunk_response[start_index:end_index + 1]
#             json_data = re.split(r',\s*\n', json_data)
#
#             try:
#                 log.info(f"Got chunk response: {json_data}")
#             except Exception as e:
#                 log.error(f"Exception in printing the chunk response: {str(e)}")
#             else:
#                 # Add the response to the overall responses list
#                 responses.extend(json_data)
#                 request_number += 1
#
#         # Process any remaining descriptions (less than or equal to 300)
#         if descriptions_list:
#             log.info(f"Making Groq request number: {request_number}")
#             final_response = agent.get_response(valid_names=valid_family_names, descriptions=descriptions_list)
#             start_index = final_response.find('{')
#             end_index = final_response.rfind('}')
#             json_data = final_response[start_index:end_index + 1]
#             json_data = re.split(r',\s*\n', json_data)
#             responses.extend(json_data)
#     except Exception as e:
#         print(f"Exception during LLM Calls: {e}")
#
#     log.debug(f"Total number of 'no_family_name_rows' is: {len(no_family_name_rows)}")
#     log.debug(f"Total number of 'responses' is: {len(responses)}")
#
#     try:
#         for row, response in zip(no_family_name_rows, responses):
#             try:
#                 response = json.loads(response)
#                 # print(f"Decoded JSON response: {response}")
#             except json.JSONDecodeError as e:
#                 log.error(f"Error decoding JSON response: {response}, REASON: {str(e)}")
#                 try:
#                     response_corrected = re.sub(r'(?<=: )None(?=[,}])', '"None"', response)
#                     response = json.loads(response_corrected)
#                     log.debug(f"Corrected JSON response for None case: {response}")
#                 except Exception as e:
#                     log.error(f"Error decoding JSON response: INNER EXCEPTION, REASON: {str(e)}")
#                     continue
#             except Exception as e:
#                 log.error(f"Error decoding JSON response: {response}, REASON: {str(e)}")
#                 continue
#
#             family_name = 'None'
#             if 'extracted_name' in response:
#                 family_name = response['extracted_name']
#                 # Perform the action when 'extracted_name' is present
#                 row['Mod_Familigoa'] = family_name
#             else:
#                 # Handle the case where 'extracted_name' is not present
#                 row['Mod_Familigoa'] = 'Not Returned'
#             year = extract_year(row['Modello_Descriz_Originale'])
#             brand, brand_record_id = extract_brand(row['Modello_Descriz_Originale'], brand_data, year,
#                                                    possible_brands=possible_brands)
#
#             family_record_id = extract_family_id(family_name, year, df_family)
#             modello_a_serie, id_record_model, mod_stage, mod_serie = extract_modello_a_serie(
#                 family_name, model_df,
#                 year,
#                 row['Modello_Descriz_Originale'],
#                 brand
#             )
#             modello_b_versione = extract_model_part_b(
#                 row['Modello_Descriz_Originale'], year, brand, family_name,
#                 modello_a_serie, mod_serie, stage=mod_stage
#             )
#             accuracy = calculate_accuracy(
#                 brand, family_name, modello_a_serie, year, brand_record_id,
#                 family_record_id, id_record_model, mod_serie, mod_stage
#             )
#
#             append_to_vehicles(
#                 vehicles_list=agent_vehicles_organized, cod_veicolo=row['CodVeicolo'], year=year, brand=brand,
#                 modello_a_serie=modello_a_serie, modello_b_versione=modello_b_versione,
#                 mod_verificato=row['Mod_Verificato'], family_name=family_name, mod_versione=row['Mod_Versione'],
#                 mod_serie=mod_serie, mod_allestimento=row['Mod_Allestimento'], mod_stage=mod_stage,
#                 mod_potenza=row['Mod_Potenza'], description=row['Modello_Descriz_Originale'], is_ai="Yes"
#             )
#
#             additional_fields = get_ai_vehicles_organized_fields(
#                 brand_record_id=brand_record_id, family_record_id=family_record_id,
#                 id_record_model=id_record_model, accuracy=accuracy
#             )
#
#             append_to_vehicles(
#                 vehicles_list=agent_ai_vehicles_organized, cod_veicolo=row['CodVeicolo'], year=year, brand=brand,
#                 modello_a_serie=modello_a_serie, modello_b_versione=modello_b_versione,
#                 mod_verificato=row['Mod_Verificato'], family_name=family_name, mod_versione=row['Mod_Versione'],
#                 mod_serie=mod_serie, mod_allestimento=row['Mod_Allestimento'], mod_stage=mod_stage,
#                 mod_potenza=row['Mod_Potenza'], description=row['Modello_Descriz_Originale'], is_ai="Yes",
#                 additional_fields=additional_fields
#             )
#     except Exception as e:
#         print(f"Exception during zip loop: {str(e)}")