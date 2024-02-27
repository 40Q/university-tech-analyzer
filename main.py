import subprocess
import re
import os
import json

# Packages
wappalyzer_path = "wappalyzer/src/drivers/npm/cli.js"
sublist3r_path = "Sublist3r/sublist3r.py"

# User input
input_domains_file = "input_domains.txt"

# Checkpoints / Cache
output_sublist3r_folder = "sublist3r_output"
output_filetered_sublist3r_folder = "filtered_sublist3r_output"
output_puredns_folder = "puredns_output"

# Output
output_json_folder = "json_output"

def run_sublist3r(domain):
    try:
        subprocess.check_call(['mkdir', '-p', output_sublist3r_folder])
        subprocess.check_call(['mkdir', '-p', output_filetered_sublist3r_folder])
        output_filename = f"{output_sublist3r_folder}/{domain.replace('.', '_')}.txt"

        if not os.path.exists(output_filename):
            subprocess.check_output(['python3', sublist3r_path, '-d', domain, '--ports=80,443', '-o', output_filename], stderr=subprocess.STDOUT)

        print("Filtering subdomains...")
        filtered_output_filename = f"{output_filetered_sublist3r_folder}/{domain.replace('.', '_')}.txt"
        if os.path.exists(filtered_output_filename):
            print("Subdomains already filtered, skipping.")
            return (filtered_output_filename, domain.replace('.', '_'))

        with open(output_filename, 'r') as file:
            subdomains = file.readlines()
        subdomains = [subdomain.strip() for subdomain in subdomains]

        not_allowed_keywords = ['mail', 'image', 'login', 'autodiscover', 'microsoft', 'googleapis', 'google', 'amazon', 'cdn', 'vpn', 'cisco', 'mx', 'spam', 'aws', 'idp', 'smtp', 'cloud', 'stage', 'dev', 'www']
        subdomains = [subdomain for subdomain in subdomains if not any(keyword in subdomain for keyword in not_allowed_keywords)]

        with open(filtered_output_filename, 'w') as file:
            file.write('\n'.join(subdomains))

        return (filtered_output_filename, domain.replace('.', '_'))
    except subprocess.CalledProcessError as e:
        print(f"Error running Sublist3r: {e.output}")
        return []

def run_puredns(validated_output_filename, domain):
    try:
        subprocess.check_call(['mkdir', '-p', output_puredns_folder])
        output_filename = f"{output_puredns_folder}/{domain}.txt"

        if os.path.exists(output_filename):
            print("Subdomains already validated, skipping.")
            return []

        subprocess.check_output(["puredns", "resolve", validated_output_filename, '--write', output_filename], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Error running PureDNS: {e.output.decode()}")
        return []


def analize_tech(subdomain, domain):
    try:
        url = f"http://{subdomain.strip()}"

        if not os.path.exists(f"{output_json_folder}/{domain}"):
            os.makedirs(f"{output_json_folder}/{domain}")

        output_json_file = f"{output_json_folder}/{domain}/{subdomain}.json"

        if os.path.exists(output_json_file):
            print(f"Analysis for {url} already exists, skipping.")
            return

        output = subprocess.check_output(["node", wappalyzer_path, url, '-w 2000'], stderr=subprocess.STDOUT)
        tech_data = json.loads(output.decode('utf-8'))

        with open(output_json_file, 'w') as file:
            json.dump(tech_data, file)
            
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
            filtered_output_filename, domain = run_sublist3r(domain)
            print("Validating subdomains...")
            run_puredns(filtered_output_filename, domain)

    for root, dirs, files in os.walk(output_puredns_folder):
        for file in files:
            with open(os.path.join(root, file), 'r') as f:
                filename_without_extension = os.path.splitext(file)[0]
                validated_subdomains = f.readlines()
                for subdomain in validated_subdomains:
                    print(f"Analizing {subdomain}")
                    analize_tech(subdomain, filename_without_extension)

if __name__ == "__main__":
    main()
