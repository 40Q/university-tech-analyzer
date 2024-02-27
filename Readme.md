# University Tech Analyzer

## Installation
Run `init.sh` to get everything needed.

## Usage
1. Fill the `input_domains.txt` file with the domains you want to analyze. One per line. Make sure you don't include either protocols or subdomains.
```
Good: ucla.edu
Bad: www.ucla.edu
Bad: https://ucla.edu
```
2. Run:
```
python3 main.py
```

## Export CSV
Once your `output_json` folder has the exported data, your may run this command to merge them all into a csv file:
```
python3 make_csv.py
```