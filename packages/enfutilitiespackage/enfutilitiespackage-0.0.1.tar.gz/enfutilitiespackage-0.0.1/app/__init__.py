from flask import Flask

app = Flask(__name__)

# Register hooks, views, etc
from app import hooks
from app import main
