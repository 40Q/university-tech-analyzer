import subprocess
import re
import os
import json

wappalyzer_path = "wappalyzer/src/drivers/npm/cli.js"
sublist3r_path = "Sublist3r/sublist3r.py"
input_domains_file = "input_domains.txt"
output_subdomains_folder = "output_dir"
output_subdomains_file = "subdomains.txt"
output_valid_subdomains_file = "valid_subdomains.txt"
output_json_file = "output.json"

def run_sublist3r(domain):
    try:
        subprocess.check_call(['mkdir', '-p', output_subdomains_folder])
        output_filename = f"{output_subdomains_folder}/{domain.replace('.', '_')}.txt"

        if not os.path.exists(output_filename):
            output = subprocess.check_output(['python3', sublist3r_path, '-d', domain, '--ports=80,443', '-o', output_filename], stderr=subprocess.STDOUT)

        with open(output_filename, 'r') as file:
            subdomains = file.readlines()
        subdomains = [subdomain.strip() for subdomain in subdomains]

        print("Filtering subdomains...")
        not_allowed_keywords = ['mail', 'image', 'login', 'autodiscover', 'microsoft', 'googleapis', 'google', 'amazon', 'cdn', 'vpn', 'cisco', 'mx', 'spam', 'aws', 'idp', 'smtp', 'cloud', 'stage', 'dev', 'www']
        subdomains = [subdomain for subdomain in subdomains if not any(keyword in subdomain for keyword in not_allowed_keywords)]

        with open(output_subdomains_file, 'w') as file:
            file.write('\n'.join(subdomains))

        return subdomains
    except subprocess.CalledProcessError as e:
        print(f"Error running Sublist3r: {e.output}")
        return []

def run_puredns():
    try:
        subprocess.check_output(["puredns", "resolve", output_subdomains_file, '--write', output_valid_subdomains_file], stderr=subprocess.STDOUT)
        
        with open(output_valid_subdomains_file, 'r') as file:
            subdomains = file.readlines()
        subdomains = [subdomain.strip() for subdomain in subdomains]
        return subdomains
    except subprocess.CalledProcessError as e:
        print(f"Error running PureDNS: {e.output.decode()}")
        return []


def analize_tech(url):
    try:
        output = subprocess.check_output(["node", wappalyzer_path, url], stderr=subprocess.STDOUT)
        tech_data = json.loads(output.decode('utf-8'))
        
        if os.path.exists(output_json_file):
            with open(output_json_file, 'r') as file:
                try:
                    data_array = json.load(file)
                except json.JSONDecodeError:
                    data_array = []
        else:
            data_array = []
        
        data_array.append(tech_data)
        
        with open(output_json_file, 'w') as file:
            json.dump(data_array, file, indent=4)
            
        print(f"Analysis for {url} added to {output_json_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Error running Wappalyzer on {url}: {e.output.decode()}")
    except Exception as e:
        print(f"An error occurred: {e}")



def main():
    with open(input_domains_file, 'r') as file:
        domains = file.readlines()

    for domain in domains:
        if domain:
            print(f"Finding subdomains for: {domain}")
            subdomains = run_sublist3r(domain)
            print(f"Sublist3r found {len(subdomains)} subdomains.")


    print("Validating subdomains...")
    validated_subdomains = run_puredns()

    for subdomain in validated_subdomains:
        print(f"Analizing {subdomain}")
        url = f"http://{subdomain.strip()}"
        analize_tech(url)

if __name__ == "__main__":
    main()
