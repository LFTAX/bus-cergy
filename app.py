from flask import Flask, jsonify
import requests
import time
import datetime
import pytz
import os

app = Flask(__name__)

# --- CONFIGURATION ---
TRANSIT_API_KEY = "e087cc4f40c2af72891794bfa9347d5def4315d02bd01b272f9559e2e90147d6"
STOP_ID = "STIVOFR:23904"        # L'ID confirmé (Cité Artisanale -> Préfecture)
LIGNES_VOULUES = ["1242", "1224"] 

@app.route('/')
def home():
    return "Serveur Bus Optimisé (Filtre > 10min)"

@app.route('/bus-matin')
def get_bus_schedule():
    tz_paris = pytz.timezone('Europe/Paris')
    now = datetime.datetime.now(tz_paris)
    
    # --- HORAIRES DU MATIN ---
    # Réglé pour demain matin (7h00 - 9h00)
    # Si tu veux tester maintenant, mets HEURE_FIN = 23
    HEURE_DEBUT = 7
    HEURE_FIN = 9 

    # Hors horaires : écran vide pour dormir
    if not (HEURE_DEBUT <= now.hour < HEURE_FIN):
         return jsonify({"frames": [{"text": " ", "icon": "a236", "index": 0}]})

    try:
        url = "https://external.transitapp.com/v3/public/stop_departures"
        headers = {'apiKey': TRANSIT_API_KEY}
        params = {'global_stop_id': STOP_ID}
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        bus_trouves = []
        current_time = time.time()

        if 'route_departures' in data:
            for route in data['route_departures']:
                nom_ligne = str(route.get('route_short_name', 'Inconnu'))
                
                # On filtre tes lignes
                if nom_ligne in LIGNES_VOULUES:
                    for depart in route['itineraries'][0]['schedule_items']:
                        ts_depart = depart['departure_time']
                        diff_seconds = ts_depart - current_time
                        minutes = int(diff_seconds / 60)
                        
                        # --- LE FILTRE "MARCHE A PIED" ---
                        # On ne garde que les bus qui sont à au moins 5 min
                        if minutes >= 5:
                            bus_trouves.append({'ligne': nom_ligne, 'min': minutes})

        # On trie pour afficher le prochain bus "prenable"
        bus_trouves.sort(key=lambda x: x['min'])

        # --- CONSTRUCTION DE L'AFFICHAGE ---
        frames = []

        if len(bus_trouves) > 0:
            # On prend les 2 prochains bus maximum
            prochains = bus_trouves[:2]
            
            idx = 0
            for bus in prochains:
                # ÉCRAN A : Numéro (Fixe)
                frames.append({
                    "text": bus['ligne'],
                    "icon": "i2766", # Icône Bus
                    "index": idx
                })
                idx += 1
                
                # ÉCRAN B : Temps (Fixe)
                frames.append({
                    "text": f"{bus['min']} min",
                    "icon": "a236", # Icône Horloge
                    "index": idx
                })
                idx += 1
        else:
            # Si aucun bus n'est > 10 min (ou s'il n'y en a pas du tout)
            frames.append({"text": "Pas de bus", "icon": "a236", "index": 0})

        return jsonify({"frames": frames})

    except Exception as e:
        return jsonify({"frames": [{"text": "Err", "icon": "i93", "index": 0}]})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
