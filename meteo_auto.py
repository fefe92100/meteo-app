import urllib.request
import json
import csv

# Changez ici votre ville
VILLE_NOM = "Boulogne-Billancourt"
LATITUDE = 48.8352
LONGITUDE = 2.2408

def afficher_et_sauvegarder():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        f"&timezone=auto"
    )
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

    jours = data["daily"]
    fichier = f"/home/fefe/projets/meteo_auto.csv"

    with open(fichier, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "temp_max", "temp_min", "pluie_mm", "vent_kmh"])
        for i in range(7):
            writer.writerow([
                jours["time"][i],
                jours["temperature_2m_max"][i],
                jours["temperature_2m_min"][i],
                jours["precipitation_sum"][i],
                jours["windspeed_10m_max"][i]
            ])

    print(f"✅ Météo sauvegardée pour {VILLE_NOM}")

afficher_et_sauvegarder()
