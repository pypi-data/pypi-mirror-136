sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.7
sudo apt update
sudo apt install python3-pip
pip3 install twine
pip3 install --upgrade keyrings.alt
python3.7 setup.py sdist
python3 -m twine upload dist/*
