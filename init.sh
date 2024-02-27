#/bin/bash

echo "Creating python env"
python3 -m venv env

echo "Activating python env"
source env/bin/activate

echo "Installing requirements"
pip install -r requirements.txt

echo "Installing Sublist3r"
git clone https://github.com/aboul3la/Sublist3r.git
cd Sublist3r
pip install -r requirements.txt

echo "Installing massdns"
brew install massdns

echo "Installing puredns"
go install github.com/d3mondev/puredns/v2@latest
echo -e "1.1.1.1\n8.8.8.8\n9.9.9.9" > ~/.config/puredns/resolvers.txt

echo "Installing Wappalyzer"
git clone git@github.com:tunetheweb/wappalyzer.git
cd wappalyzer
yarn install
yarn build

echo "Creating output directories"
mkdir sublist3r_output
mkdir filtered_sublist3r_output
mkdir puredns_output
mkdir json_output

echo "Creating files"
touch input_domains.txt

echo "Done!"

echo "You may now fill the input_domains.txt file with the domains you want to scan and run the script with the command 'python3 main.py'"