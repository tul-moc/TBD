import json

json_file_path = 'articles-small.json'
try:
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    if isinstance(data, list):
        print(f"Počet položek v JSON souboru: {len(data)}")
    else:
        print("JSON neobsahuje seznam na nejvyšší úrovni.")
except FileNotFoundError:
    print(f"Soubor {json_file_path} nebyl nalezen.")
except json.JSONDecodeError as e:
    print(f"Chyba při zpracování JSON: {e}")
