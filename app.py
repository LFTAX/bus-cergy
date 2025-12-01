from flask import Flask, jsonify
import requests
import time
import datetime
import pytz
import os

app = Flask(__name__)

# --- TES INFOS ---
TRANSIT_API_KEY = "e087cc4f40c2af72891794bfa9347d5def4315d02bd01b272f9559e2e90147d6"  # <-- COLLE TA CLÉ ICI
STOP_ID = "STIVOFR:25614"               # L'ID que tu as trouvé (vers Préfecture)

@app.route('/')
def home():
    return "Mode Espion Activé !"

@app.route('/bus-matin')
def get_bus_schedule():
    # On règle l'heure
    tz_paris = pytz.timezone('Europe/Paris')
    now = datetime.datetime.now(tz_paris)
    
    # --- MODE TEST : ON ACTIVE 24H/24 ---
    # On force l'affichage quelle que soit l'heure
    HEURE_DEBUT = 0
    HEURE_FIN = 24

    if not (HEURE_DEBUT <= now.hour < HEURE_FIN):
         return jsonify({"frames": [{"text": " ", "icon": "a236", "index": 0}]})

    try:
