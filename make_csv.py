import os
import json
import pandas as pd

input_directory = 'json_output'
output_csv_path = 'data.csv'

def find_json_files(directory):
    json_files = []
    print(f"Reading JSON files from directory: {directory}")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files

def jsons_to_csv(json_files, output_csv_path):
    df_list = [] 
    print(f"Merging {len(json_files)} JSON files into {output_csv_path}")
    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)
            df_list.append(pd.DataFrame([data])) 
    
    if df_list:
        final_df = pd.concat(df_list, ignore_index=True)
        final_df.to_csv(output_csv_path, index=False)
        print(f"All JSON files have been successfully merged into {output_csv_path}")
    else:
        print("No JSON files found to merge.")


if __name__ == "__main__":
    json_files = find_json_files(input_directory)
    jsons_to_csv(json_files, output_csv_path)
