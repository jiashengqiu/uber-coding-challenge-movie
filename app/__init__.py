import os
from flask import Flask
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), './templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=TEMPLATE_DIR)

from app import views