import json
import os
import dotenv
dotenv.load_dotenv()

parser_data_out = {}

def load_test_data():
    global parser_data_out
    with open(os.getenv("EXPORT_JSON"), "r", encoding='utf-8') as file:
        parser_data_out = json.load(file)