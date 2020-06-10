#! /bin/bash

file=bin/activate
if [[ -f "$file" ]]; then
    echo "'$file' exists. Setup already performed. Aborting."
    exit 1
fi

virtualenv -p python3 .
source bin/activate

mkdir flit
cd flit
git clone https://github.com/ipfs/py-ipfs-http-client.git
cd py-ipfs-http-client
pip install flit
flit install --pth-file
cd ../../

pip install -r requirements.txt

python src/manage.py migrate

echo "Creating administrator user account..."
python src/manage.py createsuperuser

chmod +x run.sh
