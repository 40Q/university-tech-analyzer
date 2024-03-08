import os
import json
import csv

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
    sorted_categories = sorted(categories.items(), key=lambda x: x[0])
    return sorted_categories

def find_last_status_200_url(urls):
    for url, info in reversed(list(urls.items())):
        if info.get("status") == 200:
            return url
    return None

def process_json_files(directory, csv_file_path):
    categories_with_id = map_unique_categories_with_id(directory)
    fieldnames = ['url'] + [f'{name}_{cid}' for cid, name in categories_with_id]
    processed_urls = set()

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        last_url = find_last_status_200_url(data.get("urls", {}))
                        
                        if last_url in processed_urls:
                            continue
                        processed_urls.add(last_url)
                        
                        row = {fieldname: '' for fieldname in fieldnames}
                        row['url'] = last_url

                        for tech in data.get("technologies", []):
                            for category in tech.get("categories", []):
                                cat_id = category["id"]
                                cat_name = category["name"]
                                column_name = f'{cat_name}_{cat_id}'
                                if column_name in row:
                                    row[column_name] += f'{tech["name"]}; '

                        for key, value in row.items():
                            if value and value.endswith('; '):
                                row[key] = value[:-2]

                        writer.writerow(row)

directory = 'json_output'  # Update this path
csv_file_path = 'multicolumn-csv.csv'  # Update this path
process_json_files(directory, csv_file_path)
