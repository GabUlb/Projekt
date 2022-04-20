#!/bin/fish

python3 -m venv venv
source venv/bin/activate.fish
pip install Flask
pip install --upgrade Pillow

export FLASK_APP=main.py
flask run
