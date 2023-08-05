# Barebones test implementation of cloudomate on Python2.x

## Prepare and uploade the package to PyPi (Optional)
You will need the PyPi user-id and password on twine upload
```
sudo apt install python-minimal
python get-pip.py
pip install twine
python setup.py sdist
twine upload dist/*
```
## Build the docker image (Optional)
Run the ./build.sh 

## Directly run app via docker-compose
docker-compose up -d

