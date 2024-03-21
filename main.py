import subprocess
import os
import json

# Define paths
wappalyzer_path = "wappalyzer/src/drivers/npm/cli.js"
sublist3r_path = "Sublist3r/sublist3r.py"
input_domains_file = "input_domains.txt"
output_sublist3r_folder = "sublist3r_output"
output_filtered_sublist3r_folder = "filtered_sublist3r_output"
output_puredns_folder = "puredns_output"
output_json_folder = "json_output"

# Ensure all necessary directories exist
os.makedirs(output_sublist3r_folder, exist_ok=True)
os.makedirs(output_filtered_sublist3r_folder, exist_ok=True)
os.makedirs(output_puredns_folder, exist_ok=True)
os.makedirs(output_json_folder, exist_ok=True)

def run_sublist3r(domain):
    output_filename = f"{output_sublist3r_folder}/{domain.replace('.', '_')}.txt"
    filtered_output_filename = f"{output_filtered_sublist3r_folder}/{domain.replace('.', '_')}.txt"

    if not os.path.exists(output_filename):
        try:
            subprocess.check_output(['python3', sublist3r_path, '-d', domain, '--ports=80,443', '-o', output_filename], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(f"Error running Sublist3r: {e.output.decode(errors='ignore')}")
            return None

    if os.path.exists(filtered_output_filename):
        print("Subdomains already filtered, skipping.")
        return filtered_output_filename, domain.replace('.', '_')

    try:
        with open(output_filename, 'r', encoding='utf-8', errors='ignore') as file:
            subdomains = [subdomain.strip() for subdomain in file.readlines()]
    except FileNotFoundError:
        print(f"File not found: {output_filename}")
        return None

    not_allowed_keywords = ['mail', 'image', 'login', 'autodiscover', 'microsoft', 'googleapis', 'google', 'amazon', 'cdn', 'vpn', 'cisco', 'mx', 'spam', 'aws', 'idp', 'smtp', 'cloud', 'stage', 'dev', 'www', 'cpanel', 'webdisk']
    filtered_subdomains = [subdomain for subdomain in subdomains if not any(keyword in subdomain for keyword in not_allowed_keywords)]

    with open(filtered_output_filename, 'w', encoding='utf-8') as file:
        file.write('\n'.join(filtered_subdomains))

    return filtered_output_filename, domain.replace('.', '_')

def run_puredns(validated_output_filename, domain):
    output_filename = f"{output_puredns_folder}/{domain}.txt"

    if os.path.exists(output_filename):
        print("Subdomains already validated, skipping.")
        return

    try:
        subprocess.check_output(["puredns", "resolve", validated_output_filename, '--write', output_filename], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Error running PureDNS: {e.output.decode(errors='ignore')}")

def analyze_tech(subdomain, domain):
    url = f"http://{subdomain.strip()}"
    output_json_file = f"{output_json_folder}/{domain}/{subdomain}.json"

    os.makedirs(os.path.dirname(output_json_file), exist_ok=True)

    if os.path.exists(output_json_file):
        print(f"Analysis for {url} already exists, skipping.")
        return

    try:
        output = subprocess.check_output(["node", wappalyzer_path, url, '-w 2000'], stderr=subprocess.STDOUT)
        tech_data = json.loads(output.decode('utf-8', errors='ignore'))
        with open(output_json_file, 'w', encoding='utf-8') as file:
            json.dump(tech_data, file)
        print(f"Analysis for {url} added to {output_json_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Error running Wappalyzer on {url}: {e.output.decode(errors='ignore')}")
    except json.JSONDecodeError as e:
        print(f"JSON decoding error for {url}: {e}")

def main():
    if not os.path.exists(input_domains_file):
        print(f"Input file does not exist: {input_domains_file}")
        return

    with open(input_domains_file, 'r', encoding='utf-8', errors='ignore') as file:
        domains = [line.strip() for line in file if line.strip()]

    for domain in domains:
        if domain:
            print(f"Finding subdomains for: {domain}")
            filtered_output_filename, domain = run_sublist3r(domain.strip())
            print("Validating subdomains...")
            run_puredns(filtered_output_filename, domain)

    # Process validated subdomains and analyze tech with Wappalyzer
    for root, dirs, files in os.walk(output_puredns_folder):
        for file in sorted(files):  # Ensure alphabetical order
            file_path = os.path.join(root, file)
            domain = os.path.splitext(file)[0]
            print(f"Processing validated subdomains for: {domain}")
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    subdomains = [line.strip() for line in f if line.strip()]
                    for subdomain in subdomains:
                        print(f"Analyzing technology for: {subdomain}")
                        analyze_tech(subdomain, domain)
            except Exception as e:
                print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    main()