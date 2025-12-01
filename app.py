from flask import Flask, jsonify
import requests
import time
import datetime
import pytz
import os

app = Flask(__name__)

# --- CONFIGURATION ---
TRANSIT_API_KEY = "e087cc4f40c2af72891794bfa9347d5def4315d02bd01b272f9559e2e90147d6"  # <-- TA CLE ICI
STOP_ID = "STIVOFR:25614"               # L'ID trouvé (Cité Artisanale)

@app.route('/')
def home():
    return "Mode Espion Activé"

@app.route('/bus-matin')
def get_bus_schedule():
    tz_paris = pytz.timezone('Europe/Paris')
    now = datetime.datetime.now(tz_paris)
    
    # Mode Test : Actif 24h/24
    HEURE_DEBUT = 0
    HEURE_FIN = 24

    if not (HEURE_DEBUT <= now.hour < HEURE_FIN):
        return jsonify({"frames": [{"text": " ", "icon": "a236", "index": 0}]})

    try:
        # ATTENTION : Les lignes ci-dessous DOIVENT être décalées
        url = "https://external.transitapp.com/v3/public/stop_departures"
        headers = {'apiKey': TRANSIT_API_KEY}
        params = {'global_stop_id': STOP_ID}
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        prochains_bus = []
        current_time = time.time()

        if 'route_departures' in data:
            for route in data['route_departures']:
                # On récupère le nom de la ligne
                nom_ligne = str(route.get('route_short_name', 'Inconnu'))
                
                # Pas de filtre ici, on prend tout
                for depart in route['itineraries'][0]['schedule_items']:
                    ts_depart = depart['departure_time']
                    diff_seconds = ts_depart - current_time
                    minutes = int(diff_seconds / 60)
                    
                    if minutes >= 0:
                        prochains_bus.append({'ligne': nom_ligne, 'min': minutes})

        # Tri du plus rapide au plus lent
        prochains_bus.sort(key=lambda x: x['min'])

        if len(prochains_bus) > 0:
            premier = prochains_bus[0]
            # Affiche ex: "95-48: 5m"
            texte = f"{premier['ligne']}: {premier['min']}m"
            icone = "i2766"
        else:
            texte = "Aucun bus"
            icone = "a236"

        return jsonify({"frames": [{"text": texte, "icon": icone, "index": 0}]})

    except Exception as e:
        # En cas d'erreur technique
        return jsonify({"frames": [{"text": "Err", "icon": "i93", "index": 0}]})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
