#!/usr/bin/env bash

# change into directory the script is located in
pushd `dirname ${BASH_SOURCE[0]}` > /dev/null

# does a virtual environment exist?
if [ ! -d "venv" ]; then
  # does not exist, create it
  echo "Creating virtual environment ..."
  python3 -m venv venv/

  echo "Activating virtual environment ..."
  source ./venv/bin/activate

  # install requirements
  echo "Installing python requirements in virtual environment ..."
  pip3 install -r requirements.txt
else
  # virtual environment exists, activate it
  source venv/bin/activate
fi

# call python script
python3 cloudflare_dyndns.py

# deactivate virtual environment
deactivate

# change back into original directory
popd > /dev/null

