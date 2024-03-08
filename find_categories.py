import os
import json

def map_unique_categories_with_id(directory):
    categories = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for tech in data.get("technologies", []):
                        for category in tech.get("categories", []):
                            cat_id = category["id"]
                            cat_name = category["name"]
                            categories[cat_id] = cat_name
    # Sort categories by ID and convert to list of tuples [(id, name)]
    sorted_categories = sorted(categories.items(), key=lambda x: x[0])
    return sorted_categories

directory = 'json_output'  # Update this path
unique_categories_with_id = map_unique_categories_with_id(directory)
print(unique_categories_with_id)