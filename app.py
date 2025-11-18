from flask import Flask, render_template, request, redirect, url_for
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# CARTELLE --------------------------------------------------------------------
UPLOAD_FOLDER = "static/uploads"
DATA_FILE = "agents.json"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# CREA CARTELLA UPLOADS SE NON ESISTE ----------------------------------------
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# CREA FILE agents.json SE NON ESISTE ----------------------------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


# HOME → LOGIN ---------------------------------------------------------------
@app.route("/")
def home():
    return render_template("login.html")


# LOGIN FISSO ---------------------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    password = request.form.get("password")

    if password == "test":
        return redirect(url_for("dashboard"))
    else:
        return render_template("login.html", error="Password errata")


# DASHBOARD AGENTI -----------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    with open(DATA_FILE, "r") as f:
        agents = json.load(f)
    return render_template("dashboard.html", agents=agents)


# PAGINA NUOVO AGENTE --------------------------------------------------------
@app.route("/new")
def new_agent():
    return render_template("new_agent.html")


# SALVA NUOVO AGENTE ---------------------------------------------------------
@app.route("/save", methods=["POST"])
def save_agent():
    name = request.form.get("name")
    phone = request.form.get("phone")
    whatsapp = request.form.get("whatsapp")
    email = request.form.get("email")
    gallery = request.form.get("gallery")

    # FOTO PROFILO -------------------------------------------------------------
    photo = request.files.get("photo")
    photo_filename = None

    if photo:
        filename = secure_filename(photo.filename)
        photo_filename = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        photo.save(photo_filename)

    # CARICA DATI ESISTENTI ---------------------------------------------------
    with open(DATA_FILE, "r") as f:
        agents = json.load(f)

    # CREA NUOVO AGENTE --------------------------------------------------------
    new_agent = {
        "name": name,
        "phone": phone,
        "whatsapp": whatsapp,
        "email": email,
        "gallery": gallery,
        "photo": photo_filename.replace("static/", "") if photo_filename else None
    }

    agents.append(new_agent)

    # SALVA NUOVO FILE ---------------------------------------------------------
    with open(DATA_FILE, "w") as f:
        json.dump(agents, f, indent=4)

    return redirect(url_for("dashboard"))


# CARD PUBBLICA --------------------------------------------------------------
@app.route("/card/<int:agent_id>")
def card(agent_id):
    with open(DATA_FILE, "r") as f:
        agents = json.load(f)

    if agent_id >= len(agents):
        return "Agente inesistente"

    agent = agents[agent_id]
    return render_template("card.html", agent=agent)


# AVVIO ----------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
