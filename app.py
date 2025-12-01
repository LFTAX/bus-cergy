from flask import Flask, jsonify
import requests
import time
import datetime
import pytz
import os

app = Flask(__name__)

# --- CONFIGURATION FINALE ---
TRANSIT_API_KEY = "e087cc4f40c2af72891794bfa9347d5def4315d02bd01b272f9559e2e90147d6"  # <-- REMETS TA CLÉ ICI
STOP_ID = "STIVOFR:25614"               # <-- METS LE BON ID QUE TU VIENS DE CHOISIR
LIGNES_VOULUES = ["1242", "1224"]       # On ne veut voir que ceux-là

@app.route('/')
def home():
    return "Serveur Bus Cergy Actif !"

@app.route('/bus-matin')
def get_bus_schedule():
    tz_paris = pytz.timezone('Europe/Paris')
    now = datetime.datetime.now(tz_paris)
    
    # --- HORAIRES ---
    # Pour ce soir : on laisse jusqu'à 23h.
    # Demain, tu pourras remettre HEURE_FIN = 9
    HEURE_DEBUT = 7
    HEURE_FIN = 23

    # Si on est hors horaires, on dort
    if not (HEURE_DEBUT <= now.hour < HEURE_FIN):
         return jsonify({"frames": [{"text": " ", "icon": "a236", "index": 0}]})

    try:
        url = "https://external.transitapp.com/v3/public/stop_departures"
        headers = {'apiKey': TRANSIT_API_KEY}
        params = {'global_stop_id': STOP_ID}
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        prochains_bus = []
        current_time = time.time()

        if 'route_departures' in data:
            for route in data['route_departures']:
                nom_ligne = route.get('route_short_name', '')
                
                # --- LE FILTRE EST ACTIVÉ ICI ---
                if nom_ligne in LIGNES_VOULUES:
                    for depart in route['itineraries'][0]['schedule_items']:
                        ts_depart = depart['departure_time']
                        diff_seconds = ts_depart - current_time
                        minutes = int(diff_seconds / 60)
                        
                        # On garde les bus qui arrivent (>= 0 min)
                        if minutes >= 0:
                            prochains_bus.append({'ligne': nom_ligne, 'min': minutes})

        # On trie pour avoir le plus rapide en premier
        prochains_bus.sort(key=lambda x: x['min'])

        if len(prochains_bus) > 0:
            premier_bus = prochains_bus[0]
            # Affichage : "1242: 4m"
            texte = f"{premier_bus['ligne']}: {premier_bus['min']}m"
            icone = "i2766"
        else:
            # Si aucun 1242/1224 n'est prévu
            texte = "Pas de bus"
            icone = "a236"

        return jsonify({"frames": [{"text": texte, "icon": icone, "index": 0}]})

    except Exception as e:
        return jsonify({"frames": [{"text": "Err", "icon": "i93", "index": 0}]})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
