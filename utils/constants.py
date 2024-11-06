from pathlib import Path
import os

files = [
    "VehicleToOrganize_AlfaRomeo",
    "VehicleToOrganize_Bmw",
    "VehicleToOrganize_BritishGroup",
    "VehicleToOrganize_Chevrolet",
    "VehicleToOrganize_Ferrari",
    "VehicleToOrganize_Ford",
    "VehicleToOrganize_Honda",
    "VehicleToOrganize_Mercedes",
    "VehicleToOrganize_Porsche",
    "VehicleToOrganize_RollsRoyce"
]

brands = [
    "AlfaRomeo",
    "Bmw",
    "BritishGroup",
    "Chevrolet",
    "Ferrari",
    "Ford",
    "Honda",
    "Mercedes",
    "Porsche",
    "RollsRoyce"
]


project_dir = str(Path(__file__).resolve().parents[1])

BRAND_PATH = os.path.join(project_dir, "verification_data", "Brand.xlsx")
MODEL_PATH = os.path.join(project_dir, "verification_data", "Model.xlsx")
FAMILY_PATH = os.path.join(project_dir, "verification_data", "Family.xlsx")

INPUT_DIR = os.path.join(project_dir, "input")
OUTPUT_DIR = os.path.join(project_dir, "output")

ORGANIZED_DIR = os.path.join(OUTPUT_DIR, "Vehicles Organized")
AI_ORGANIZED_DIR = os.path.join(OUTPUT_DIR, "AI Vehicles Organized")