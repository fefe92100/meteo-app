from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import urllib.request
import urllib.parse
import json

from database import get_db, init_db
from auth import verify_password, create_token, verify_token, get_user, create_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Initialiser la base de données au démarrage
@app.on_event("startup")
def startup():
    init_db()

# Modèles
class RegisterData(BaseModel):
    username: str
    email: str
    password: str

# Routes auth
@app.post("/register")
def register(data: RegisterData, db: Session = Depends(get_db)):
    if get_user(db, data.username):
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")
    user = create_user(db, data.username, data.email, data.password)
    return {"message": f"Compte créé pour {user.username}"}

@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    token = create_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Token invalide")
    user = get_user(db, username)
    return {"username": user.username, "email": user.email}

# Route météo protégée
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
def meteo(ville: str = "Paris", token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Connectez-vous pour accéder à la météo")

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