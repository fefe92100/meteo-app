from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import urllib.parse
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def chercher_ville(nom):
    nom_encode = urllib.parse.quote(nom)
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={nom_encode}&count=1&language=fr"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())
    if not data.get("results"):
        return None
    result = data["results"][0]
    return {
        "nom": result["name"],
        "pays": result.get("country", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"]
    }

@app.get("/meteo")
def meteo(ville: str = "Paris"):
    lieu = chercher_ville(ville)
    if not lieu:
        return {"erreur": "Ville introuvable"}

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lieu['latitude']}&longitude={lieu['longitude']}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        f"&timezone=auto"
    )
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

    jours = data["daily"]
    previsions = []
    for i in range(7):
        previsions.append({
            "date": jours["time"][i],
            "temp_max": jours["temperature_2m_max"][i],
            "temp_min": jours["temperature_2m_min"][i],
            "pluie_mm": jours["precipitation_sum"][i],
            "vent_kmh": jours["windspeed_10m_max"][i]
        })

    return {
        "ville": lieu["nom"],
        "pays": lieu["pays"],
        "previsions": previsions
    }