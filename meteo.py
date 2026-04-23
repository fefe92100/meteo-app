import urllib.request
import urllib.parse
import json
import csv
from datetime import datetime

def chercher_ville(nom):
    nom_encode = urllib.parse.quote(nom)
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={nom_encode}&count=1&language=fr"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())
    if not data.get("results"):
        print("❌ Ville introuvable.")
        return None
    result = data["results"][0]
    return {
        "nom": result["name"],
        "pays": result.get("country", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"]
    }

def afficher_et_sauvegarder(ville):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={ville['latitude']}&longitude={ville['longitude']}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        f"&timezone=auto"
    )
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

    jours = data["daily"]

    print(f"\n📅  Prévisions météo — {ville['nom']}, {ville['pays']}\n")
    print(f"{'Date':<12} {'Max':>6} {'Min':>6} {'Pluie':>8} {'Vent':>10}")
    print("-" * 46)

    # Sauvegarde CSV
    fichier = f"/home/{__import__('os').getenv('USER')}/projets/meteo_{ville['nom'].lower()}.csv"
    with open(fichier, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "temp_max", "temp_min", "pluie_mm", "vent_kmh"])

        for i in range(7):
            date = jours["time"][i]
            tmax = jours["temperature_2m_max"][i]
            tmin = jours["temperature_2m_min"][i]
            pluie = jours["precipitation_sum"][i]
            vent = jours["windspeed_10m_max"][i]
            print(f"{date:<12} {tmax:>5}°C {tmin:>5}°C {pluie:>6}mm {vent:>8}km/h")
            writer.writerow([date, tmax, tmin, pluie, vent])

    print(f"\n💾  Sauvegardé dans : {fichier}\n")

# Programme principal
nom = input("🌍 Entrez une ville : ")
ville = chercher_ville(nom)
if ville:
    afficher_et_sauvegarder(ville)