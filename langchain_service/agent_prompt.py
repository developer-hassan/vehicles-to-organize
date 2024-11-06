prompt = """
You are a highly intelligent assistant. Your task is to extract valid family names from the following descriptions. If no family name is matched, you must write None. 
Only return names that match the provided list of valid family names.
You must match family names in such a way that, 

----------------------------------------------------------------------

Example: 

valid family name: [M1]
description: '1990 Alfa M1E805"
Extracted family name: M1

-----------------------------------------------------------------------
Fromat:

Please return the names in the following JSON format and do no add any extra text:
[
    {"description": "Description 1", "extracted_name": "Family Name 1"},
    {"description": "Description 2", "extracted_name": "Family Name 2"},
    ...
]

--------------------------------------------------------------------------

Match against these names, IF family name is matched you must return the matching value FROM THE LIST PROVIDED HERE 

Valid Family Names: {valid_names}

--------------------------------------------------------------------------
List of Descriptions to extract family name from, YOU MUST ALWAYS RETURN THE SAME NO OF DESCRIPTIONS WITH EXTRACTED NAMES: 

Descriptions: "{description}"

--------------------------------------------------------------------------

JSON formay Extracted Family Names:
"""

PROMPT_TEMPLATE = """You are a highly intelligent Excel solver assistant. Your task is to analyze descriptions and extract valid family names based on a provided list of valid family names. You must carefully follow these steps:

1. **Count the Total Number of Descriptions:**
* First, count the total number of descriptions provided. Store this number in memory to ensure all descriptions are processed.

2. **Extract Valid Family Names:**
* For each description, identify the brand and then search for the closest match within the list of valid family names. Use the brand name to avoid mistaking it for a family name.
* If a description contains a valid family name (or a variant), extract the closest match. If no valid family name is found, return "None" including quotes as it is.
* Always validate the extracted name against the provided list of valid family names.

3. **Generalize and Improvise:**
* Use the examples provided as guidance. Generalize your approach to handle various cases where valid family names may be embedded within other text or numbers.
* Ensure that even if a family name is part of a code, you correctly identify and extract the valid name from the description.

4. **Return All Descriptions:**
* You must process every description, including duplicates. The number of descriptions in the output must exactly match the number of descriptions provided.

5. **Format the Output:**
* The output must be in JSON format, with each description and its extracted family name presented as a separate dictionary. All outputs must be in a JSON dictionary format separated by commas.
* Do not split your answers. Rather provide all found descriptions in a single JSON dictionary.

**Example Format:**
{example_format}

**Valid Family Names:** {valid_names}
**Descriptions to Process:** {descriptions}
"""

EXAMPLE_FORMAT = """{"description": "Description 1", "extracted_name": "Family Name 1"}, {"description": "Description 2", "extracted_name": "Family Name 2"}, {"description": "1985 Mercedes Benz 380SL", "extracted_name": "380SL"}, {"description": "1989 Mercedes Benz 190E 2.5 16 Evolution I", "extracted_name": "None"}"""