# before running this file check file paths and also run the below command in terminal
# pip install pandas openpyxl

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, NamedStyle
import os
import re

# brand_df = pd.read_excel("./ProjectStefani-Data/ProjectStefani-Data/Brand.xlsx")
# family_df = pd.read_excel("./ProjectStefani-Data/ProjectStefani-Data/Family.xlsx")
# model_df = pd.read_excel("./ProjectStefani-Data/ProjectStefani-Data/Model.xlsx")
# porsche_df = pd.read_excel("./ProjectStefani-Data/ProjectStefani-Data/VehicleToOrganize_Porsche.xlsx")
brand_df = pd.read_excel("./ProjectStefani-Data/ProjectStefani-Data/Brand.xlsx")
family_df = pd.read_excel("./ProjectStefani-Data/ProjectStefani-Data/Family.xlsx")
model_df = pd.read_excel("./ProjectStefani-Data/ProjectStefani-Data/Model.xlsx")
porsche_df = pd.read_excel("./ProjectStefani-Data/ProjectStefani-Data/VehicleToOrganize_AlfaRomeo.xlsx")

print("Current Working Directory:", os.getcwd())

def extract_year(description):
        if isinstance(description, str):
            match = re.search(r"(\d{4}|\d{2}\')", description)

            if match:
                year_str = match.group(1)
                yearIndex = match.start()
                if len(year_str) == 2:
                    year = int(f"19{year_str}")
                else:
                    year = int(year_str)

                if year == 1600 :
                    match = re.findall(r"(\d{4}|\d{2}\')", description)
                    print(match)
                    if match and len(match)>1:
                        year_str = match[1]
                        if len(year_str) == 2:
                            year = int(f"19{year_str}")
                        else:
                            year = int(year_str)
                
                return year , yearIndex
        return None, ''

def find_family(rest, year, brand_name):
        filtered_df = family_df[
            (family_df['AnnoInizioCalcolato'] <= year) &
            (family_df['AnnoFineCalcolato'] >= year) &
            (family_df['Marca'] == brand_name)
        ]

        for index, row in filtered_df.iterrows():
            if row['Famiglia'].lower() in rest.lower():
                family_cod = row['ID_Record']
                return row['Famiglia'], family_cod
        return None, None  

def extract_family(description, year, brand_name, family):
        mod_famigliaA = ''
        mod_famigliaB = ''
        serie = ''
        stage = ''
        model_cod = ''

        if family:
            print("we have family")
            filtered_df = model_df[(model_df['AnnoInizioCalcolato'] <= year ) &
                                   (model_df['AnnoFineCalcolato']  >= year) &
                                 
                                   (model_df['Marca'] == brand_name) &
                                   (model_df['Mod_FamigliaA'] == family)]

            if not filtered_df.empty:
                print("yes")
                for index, row in filtered_df.iterrows():
                    pattern = re.compile(r'\b{}\b'.format(re.escape(row['Mod_FamigliaA'])), re.IGNORECASE)
                    if pattern.search(description):
                        mod_famigliaA = row['Mod_FamigliaA']
                        mod_famigliaB = description.replace(str(year), '').replace(str(brand_name), '').replace(str(mod_famigliaA), '')

                        serie = row['Serie']
                        stage = row['Stage']
                        model_cod = row['ID_Record']
                        return mod_famigliaA, mod_famigliaB, serie, stage, model_cod, family

            else:
                filtered_df = model_df[(model_df['AnnoInizioCalcolato'] <= year) &
                                       (model_df['AnnoFineCalcolato'] >= year) &
                                       (model_df['Marca'] == brand_name)]

#                 print(filtered_df)
                for index, row in filtered_df.iterrows():
                    pattern = re.compile(r'\b{}\b'.format(re.escape(row['Mod_FamigliaA'])), re.IGNORECASE)
                    if pattern.search(description):
                        mod_famigliaA = row['Mod_FamigliaA']
                        mod_famigliaB = description.replace(str(year), '').replace(str(brand_name), '').replace(str(mod_famigliaA), '')
                        serie = row['Serie']
                        stage = row['Stage']
                        model_cod = row['ID_Record'] 
                        if family is None:
                            family_cod = row['Famiglia::ID_Record']
                            familia_filtered_df = family_df[(family_df['Cod_Famiglia'] == family_cod)]
                            family = familia_filtered_df['Famiglia'].values[0]
                        return  mod_famigliaA, mod_famigliaB, serie, stage, model_cod, family
        return  mod_famigliaA, mod_famigliaB, serie, stage, model_cod, family

def extract_info_from_description(description, model_df,brand_name):
        mod_famigliaA = ''
        mod_famigliaB = ''
        serie = ''
        stage = ''
        model_cod = ''
        family = ''

        for index, row in family_df.iterrows():
            if not pd.isnull(row['Famiglia']):  

                mod_famigliaA_pattern = re.escape(str(row['Famiglia']))
                mod_famigliaA_pattern = re.escape(str(row['Famiglia']))
                pattern = re.compile(r'{}'.format(mod_famigliaA_pattern), re.IGNORECASE)

                if pattern.search(description) and row['Marca'] is not None and brand_name is not None and brand_name in str(row['Marca']):
                    family = row['Famiglia']
                    brand_name = row['Marca']
                    family_cod = row['ID_Record']
                    df = model_df[(model_df['Marca']==brand_name) & (model_df['Famiglia::ID_Record']==family_cod)]
                    for i, row in df.iterrows():
                        if i == 0:
                            mod_famigliaA = row['Mod_FamigliaA']
                            mod_famigliaB = description.replace(str(brand_name), '').replace(str(mod_famigliaA), '')
                            serie = row['Serie']
                            stage = row['Stage']
                            model_cod = row['ID_Record']
                    break

        return brand_name, mod_famigliaA, mod_famigliaB, serie, stage, model_cod,family
def find_family_in_Description(description, year, brand_name):
        if isinstance(description, str):
            rest = description.replace(str(year), '').replace(str(brand_name), '')
            family, family_cod = find_family(rest, year, brand_name)
            if family is None:
                filtered_df = family_df[(family_df['Marca'] == brand_name)]

                for index, row in filtered_df.iterrows():
                    pattern = re.compile(r'\b{}\b'.format(re.escape(row['Famiglia'])), re.IGNORECASE)
                    if pattern.search(description):
                        family = row['Famiglia']
                        family_cod = row['ID_Record']
            return family, family_cod
    #         if family is None:

        return None, None
def A_accuracy(description):
        marca_cod = ''
        year,yearIndex = extract_year(description)
    #     if yearIndex !='':

    #         if yearIndex > len(description) / 2:
    #             outputString = description[yearIndex:]
    #             description = outputString
    #         else:
    #             # If yearIndex is less than or equal to halfway through the description
    #             outputString = description[:yearIndex]
    #             description = outputString

        brand_name = extract_brand(description)
        if brand_name is not None:
            if 'Tractor' in description or 'Tractor-Sold' in description:
                brand_name += ' Diesel'

        brand_filtered_df = brand_df[brand_df['Marca'] == brand_name]
        if brand_name is not None and not brand_filtered_df.empty:
            marca_cod = brand_filtered_df['Record_ID'].values[0] 
            return brand_name,marca_cod,year
        else:
            columns_to_search = ['Marca', 'MarcaCompleto', 'MarcaCorto', 'NomeStoricoCostante']
            for column in columns_to_search:
                if not brand_name:
                    for index, row in brand_df.iterrows():
                        pattern = re.compile(r'\b{}\b'.format(re.escape(row['Marca'])), re.IGNORECASE)
                        if pattern.search(str(description)):
                            brand_name = row['Marca']
                            if 'Replica' in description and 'Replica' not in brand_name:
                                brand_name += ' Replica'
                            if 'Tractor' in description or 'Tractor-Sold' in description :
                                brand_name += ' Diesel'
                            brand_filtered_df = brand_df[brand_df['Marca'] == brand_name]
                            return brand_name, marca_cod, year
                else:
                    break
        return brand_name, marca_cod, year

def calculate_accuracy(brand_name, family, model, year,marca_cod,family_cod,model_cod,serie,stage):
        accuracy_levels = {
            'A': 100,
            'B': 95,
            'C': 90,
            'D' : 85,
            'E': 80,
            'F': 60,
            'G': 40,
            'H': 20,
            'I': 0,
        }
        accuracy = 0
        if brand_name and family and model and year and family_cod and marca_cod and model_cod and serie and stage:
            accuracy = accuracy_levels['A']
        elif brand_name and family and year and ((marca_cod and family_cod) or(marca_cod and model_cod) or(family_cod and model_cod)) and serie and stage:
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
def is_brand_name_valid(brand_name):
        # Convert brand names to lowercase for case-insensitive comparison
        brand_df_lower = brand_df['Marca'].str.lower()

        # Check if the lowercase version of the brand name is in the DataFrame
        if brand_name.lower() in brand_df_lower.values:
            # Filter the DataFrame to get the rows with the specified brand name
            filtered_df = brand_df[brand_df['Marca'].str.lower() == brand_name.lower()]

            # Check if the filtered DataFrame is not empty
            if not filtered_df.empty:
                # Get the value from the 'ID_Record' column of the first row
                marca_cod = filtered_df.iloc[0]['Record_ID']
                return True
        else:
            # If brand name not found in DataFrame, return False and None for marca_cod
            return False
def extract_brand(description):
    brand_name = ''
    description = str(description).replace('No Reserve:','').replace('Modified','').replace('Black','').replace('Flat','').replace('Supercharged','').replace('-replica',' Replica').replace('-Royce',' Royce')
    if not isinstance(description, str) or description.lower() == 'nan':
          return None
    pattern = re.compile(r"([A-Za-z0-9]+\s)?([A-Za-z]+\s)+", re.IGNORECASE)
    if description :
        match = re.search(pattern, description)
#         print(match)

        if match:
            brand_name = match.group().strip()
            if 'Replica' in description:
                brand_name =  brand_name + ' Replica'
            if 'Diesel' in description:
                brand_name =  brand_name + ' Diesel'
            if is_brand_name_valid(brand_name):
                print('verified')
                return brand_name
            else:
                pattern =  re.compile(r"(([A-Za-z]+\s)+)",re.IGNORECASE)
                if description :
                    match = re.search(pattern, description)
#                     print(match)
                    if match:
                        brand_name = match.group().strip()
                        print(brand_name)
                    if 'Replica' in description:
                        brand_name =  brand_name + ' Replica'
                    if 'Diesel' in description:
                        brand_name =  brand_name + ' Diesel'    
                    if is_brand_name_valid(brand_name):
                        return brand_name
                    else:
                        pattern = re.compile(r"(\s([A-Za-z]+\s)+)", re.IGNORECASE)
                        if description :
                            match = re.search(pattern, description)
#                             print(match)
                            if match:
                                brand_name = match.group().strip()
#                                 print(brand_name)

                            if 'Replica' in description:
                                brand_name =  brand_name + ' Replica'
                            if 'Diesel' in description:
                                brand_name =  brand_name + ' Diesel'
                            if is_brand_name_valid(brand_name):
                                return brand_name
                            else:
                                return None
                
                
        else:
            pattern =  re.compile(r"(([A-Za-z]+\s)+)",re.IGNORECASE)
            if description :
                match = re.search(pattern, description)
                print(match)
                if match:
                    brand_name = match.group().strip()
                    print(brand_name)
                    if 'Replica' in description:
                        brand_name =  brand_name + ' Replica'
                    if 'Diesel' in description:
                        brand_name =  brand_name + ' Diesel'
                
                if is_brand_name_valid(brand_name):
                    return brand_name
                else :
                    pattern = re.compile(r"(\s([A-Za-z]+\s)+)", re.IGNORECASE)
                    if description :
                        match = re.search(pattern, description)
                        if match:
                            brand_name = match.group().strip()
                        if 'Replica' in description:
                            brand_name =  brand_name + ' Replica'
                        if 'Diesel' in description:
                            brand_name =  brand_name + ' Diesel'
                        if is_brand_name_valid(brand_name):
                            return brand_name
                        else:
                            return None
            return None
    else:
          return None



#-------------------------------------------------------------------------------------------------------------------------------
# insert data check

model_df1 = pd.read_excel("./PulisciDescrizioniOrignalFiles/VehicleToOrganize_AlfaRomeo.xlsx")
model_df2 = pd.read_excel("./PulisciDescrizioniOrignalFiles/VehicleToOrganize_Bmw.xlsx")
model_df4 = pd.read_excel("./PulisciDescrizioniOrignalFiles/VehicleToOrganize_Chevrolet.xlsx")
model_df5 = pd.read_excel("./PulisciDescrizioniOrignalFiles/VehicleToOrganize_Ferrari.xlsx")
model_df6 = pd.read_excel("./PulisciDescrizioniOrignalFiles/VehicleToOrganize_Ford.xlsx")
model_df7 = pd.read_excel("./PulisciDescrizioniOrignalFiles/VehicleToOrganize_Honda.xlsx")
model_df8 = pd.read_excel("./PulisciDescrizioniOrignalFiles/VehicleToOrganize_Mercedes.xlsx")
model_df9 = pd.read_excel("./PulisciDescrizioniOrignalFiles/VehicleToOrganize_RollsRoyce.xlsx")
model_df3 = pd.read_excel("./PulisciDescrizioniOrignalFiles/VehicleToOrganize_BritishGroup.xlsx")



import pandas as pd
import re
import time
# List of DataFrames to process add and remove
dfs = [
     (porsche_df, 'porsche'),
     (model_df1, 'alfaromeo'),
     (model_df7, 'honda'),
     (model_df2, 'bmw'),
     (model_df4, 'chevrolet'),
     (model_df5, 'ferrari'),
     (model_df6, 'ford'),
     (model_df8, 'mercedes'),
     (model_df9, 'rollsroyce'),
     (model_df3, 'britishmg')
]

# Load data from Excel files
for df,df_name in dfs:
    organized_df_b = pd.DataFrame(
        columns=[
            "ID_Record",
            "CodVeicolo",
            "anno",
            "Marca",
            "Modello_A_Serie",
            "Modello_B_Versisone",
            "Mod_Famiglia",
            "Mod_Serie",
            "Mod_Stage",
            "Modello_Descriz_Originale",
            "Cod_brand",
            "Cod_family",
            "Cod_model",
            "Accuracy",
            "No Reserve",
            "EX Property"
        ]
    )

    marca_cod = ''
    model_cod =''
    family_cod =''
    yearIndex = ''
    # Helper function to extract year from the description

    
    # Load data from Excel files
    # Assuming model_df, brand_df, family_df, porsche_df are already loaded

    # Assuming the rest of the code remains the same...

    start_time = time.time()

    for index, row in df.iterrows():
        print(index)

        cod_veicolo = row["CodVeicolo"]
        description = row["Modello_Descriz_Originale"]
        description = str(description).replace('No Reserve:','').replace('Modified','').replace("Mercedes-Benz","Mercedes Benz").replace("Rolls-Royce","Rolls Royce")

            
        if  'CAYENNE DIESEL'  in description or 'PANAMERA DIESEL'in description:
            description =  str(description).replace('DIESEL','') 
    #     console.log(description)
        brand_name, marca_cod, year = A_accuracy(description)
        family, family_cod = find_family_in_Description(description, year, brand_name)
        print(family,brand_name, marca_cod, year,"dev")

        numbers = []

        mod_famigliaA, mod_famigliaB, serie, stage, model_cod, family = extract_family(description, year, brand_name, family)

        print(mod_famigliaA, mod_famigliaB, serie, stage, model_cod, family,"fff")
        if family == None:
            rest = description.replace(str(year), '')
            brand_name, mod_famigliaA, mod_famigliaB, serie, stage, model_cod,family = extract_info_from_description(rest, model_df,brand_name)

        rest = description.replace(str(year), '').replace(str(brand_name),"").replace(str(family),'')
        pattern = r'\((\d+)\)'
        matches = re.findall(pattern,rest)
        if matches :

            for match in matches:

                for index,row in model_df.iterrows():
                    if row['Stage'] == match and row['Marca']==brand_name:
                        print(row['Serie'])
                        stage = row['Stage']
                        serie = row['Serie']
                        mod_famigliaA = row['Mod_FamigliaB']
                        mod_famigliaB = description.replace(str(year), '').replace(str(brand_name),"").replace(str(family),'').replace(str(mod_famigliaA),'').replace(str(serie),'').replace(str(stage),'').replace('()','')
                        break

        if family == None or family=='':

            rest = description.replace(str(year), '').replace(str(brand_name),"").replace(str(family),'')
            pattern = r'\b\d{3}\b'
            matches = re.findall(pattern,rest)
            if matches :

                for match in matches:

                    for index,row in model_df.iterrows():
                        if row['Stage'] == match and row['Marca']==brand_name:
                            print(row['Serie'])
                            stage = row['Stage']
                            serie = row['Serie']
                            model_cod = row['ID_Record']
                            family_cod = row['Famiglia::ID_Record']
                            mod_famigliaA = row['Mod_FamigliaB']
                            family_filtered_df = family_df[(family_df['ID_Record']==row['Famiglia::ID_Record'])]
                            for index,row in family_filtered_df.iterrows():
                                family = row['Famiglia']
                            mod_famigliaB = description.replace(str(year), '').replace(str(brand_name),"").replace(str(family),'').replace(str(mod_famigliaA),'').replace(str(serie),'').replace(str(stage),'').replace('()','')
                            break

        if family is not None:
            if family_cod is None:
                family_df_filtered = family_df[
                                 (family_df['Marca'] == brand_name) & 
                                 (family_df['Famiglia']==family)]
                if not family_df_filtered.empty :
                    family_cod = family_df_filtered['ID_Record'].values[0]

            print(mod_famigliaB , mod_famigliaA , stage , serie ,year,family_cod )
            if mod_famigliaB == '' and mod_famigliaA == '' and stage == '' and serie == '' and year is not None and family_cod is not None:
                model_df_filtered = model_df[(model_df['Famiglia::ID_Record'] == int(family_cod)) & 
                             (model_df['Marca'] == brand_name) & 
                             (model_df['AnnoInizioCalcolato'] <= year) & 
                             (model_df['AnnoFineCalcolato'] >= year)]


                if not model_df_filtered.empty:
                    mod_famigliaA = model_df_filtered['Mod_FamigliaA'].values[0]
                    stage = model_df_filtered['Stage'].values[0]
                    serie = model_df_filtered['Serie'].values[0]
                    model_cod = model_df_filtered['ID_Record'].values[0]
                
                
        if family == "718"  and year is not None and int(year) <= 2023 and int(year) >= 2016:
            family = "BOXSTER"
            family_cod =48290
            mod_famigliaA = "BOXSTER"
            stage = "718"
            serie = "IV"
            model_cod = 143647
       
            
        if family and year is None or year == "":
            mod_famigliaA = family
        if family == "911" and mod_famigliaA  == "" and serie == "" and stage == "":
            print(year)
            model_filtered_df = model_df[ (model_df['Marca'] == brand_name) &  (model_df['Mod_FamigliaA']==family)]
            for index,row in model_filtered_df.iterrows():
                if row['Stage'] in description.replace(brand_name,'').replace(family,"") :
                    mod_famigliaA = row['Mod_FamigliaA']
                    stage = row['Stage']
                    serie = row['Serie']
                    model_cod = row['ID_Record']
                    mod_famigliaB =  description

                    # test gffghf



        mod_famigliaB =  description
        if family  == "912" and mod_famigliaA == "912" and "912 E" in description:
            mod_famigliaA = mod_famigliaA + " E"
            mod_famigliaB = mod_famigliaB.replace("E","")
        elif "914-4" in description :
            mod_famigliaA  = mod_famigliaA + "-4"
            mod_famigliaB = mod_famigliaB.replace("-4","")
        elif "914-6" in description :
            print("hello")
            mod_famigliaA  = mod_famigliaA + "-6"
            mod_famigliaB = mod_famigliaB.replace("-6","")
            
        elif brand_name != None and brand_name.lower() =="porsche" and str(family) == str("356") and stage is not None and stage != "":
            mod_famigliaA = mod_famigliaA + " - " + stage
            print(mod_famigliaA)
        elif serie is not None and mod_famigliaA is not None and serie not in mod_famigliaA and serie != "I":      
            print("new this")
            print(mod_famigliaA)
            mod_famigliaA = mod_famigliaA + " - " + serie
        if family != None and family!='' and brand_name and mod_famigliaA != '914' and mod_famigliaA !='912' :
            family_filtered_data = family_df[(family_df['Famiglia'] == str(family)) & (family_df['Marca'] == str(brand_name))]
            print(family_filtered_data,"ffgb")
            if not family_filtered_data.empty :
                value = family_filtered_data.iloc[0]['Conta_Modelli']
                print(value,"rrrrrr")
                if value:
                    if int(value) > 1 and serie=='I':
                        model_filter = model_df[(model_df['Marca'] == str(brand_name)) & (model_df['Mod_FamigliaA'] == str(mod_famigliaA))  & (model_df['Mod_FamigliaA'] != model_df['Mod_FamigliaB'] )]
                        if not model_filter.empty and serie not in mod_famigliaA:

                           
                            mod_famigliaA = mod_famigliaA  + " - " + serie
        accuracy = calculate_accuracy(brand_name, family, model_cod, year,marca_cod,family_cod,model_cod,serie,stage)
        patterns_to_remove = [
        r'\b\d+-Mile\b',
        r'\b\d+-Kilometer\b',
        r'\b\d+-Powered\b',
        r'\b\d+-Years-Owned\b',
        r'\b\d+-Years-Family-Owned\b',
        r'\b\d+-Style\b',
        r'Modified',
        r'Original-Owner',
        r'RoW',
        r'One-Family-Owned',
        r'One-Owner'
    ]


        combined_pattern = '|'.join(patterns_to_remove)

        mod_famigliaB = re.sub(combined_pattern, '', mod_famigliaB)
        # Tokenize brand_name into individual words
        if brand_name is not None :
            brand_words = brand_name.split()

            # Iterate over each word and replace it in mod_famigliaB
            for word in brand_words:
                mod_famigliaB = mod_famigliaB.replace(word, '')

        # Perform other replacements
        mod_famigliaB = mod_famigliaB.replace(str(year), '').replace(str(family), '').replace(str(mod_famigliaA), '').replace(str(serie), '').replace(str(stage), '').replace('()', '').replace("No reserve", "").replace("No Reserve", "").replace('""', "").strip()

        mod_famigliaB =mod_famigliaB.replace(str(year), '').replace(str(brand_name),"").replace(str(family),'').replace(str(mod_famigliaA),'').replace(str(serie),'').replace(str(stage),'').replace('()','').replace("No reserve","").replace("No Reserve","").replace('""',"").strip()
        
                    

        print(description,brand_name, family, stage, model_cod, year,marca_cod,family_cod,model_cod,accuracy)
        organized_row = {
            "ID_Record": index + 1,
            "CodVeicolo": cod_veicolo,
            "anno": year,
            "Marca": brand_name,
            "Modello_A_Serie": mod_famigliaA.upper(),
            "Modello_B_Versisone": mod_famigliaB,
            "Mod_Famiglia": family.upper(),
            "Mod_Serie": serie,

            "Mod_Stage": stage,
            "Modello_Descriz_Originale": description,
            "Cod_brand": marca_cod,
            "Cod_family": family_cod,
            "Cod_model": model_cod,
            "Accuracy": accuracy,
            "No Reserve" :True if "No Reserve" in description  else False,
            "EX Property" : re.findall(r'Ex–(\w+\s+\w+)', description)[0] if re.findall(r'Ex–(\w+\s+\w+)', description) else ""
        }

        organized_df_b = pd.concat(
            [organized_df_b, pd.DataFrame([organized_row])], ignore_index=True
        )

    end_time = time.time()
    total_time = end_time - start_time
    print("Total time taken for {}:".format(df_name), total_time, "seconds")
    output_file_name = "./organized_result_{}.xlsx".format(df_name)  # Name the output file based on the DataFrame name
    organized_df_b.to_excel(output_file_name, index=False)
    print("Results saved to:", output_file_name)
