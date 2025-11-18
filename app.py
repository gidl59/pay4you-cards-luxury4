import os
import json
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Percorsi base ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
DATA_FILE = os.path.join(BASE_DIR, "agents.json")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Crea cartella uploads e file json se non esistono ---------------------------
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)


def load_agents():
    """Legge la lista agenti dal file JSON."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_agents(agents):
    """Salva la lista agenti nel file JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=4)


# LOGIN (home) ----------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        password = request.form.get("password", "")

        # password amministratore (per ora fissa)
        if password == "test":
            return redirect(url_for("admin_list"))
        else:
            error = "Password errata"

    return render_template("login.html", error=error)


# LISTA AGENTI ---------------------------------------------------------------
@app.route("/admin/agents")
def admin_list():
    agents = load_agents()
    return render_template("admin_list.html", agents=agents)


# NUOVO AGENTE ---------------------------------------------------------------
@app.route("/admin/agents/new")
def admin_new_agent():
    return render_template("admin_agent_form.html", agent=None, agent_id=None)


# MODIFICA AGENTE ------------------------------------------------------------
@app.route("/admin/agents/<int:agent_id>/edit")
def admin_edit_agent(agent_id):
    agents = load_agents()
    if agent_id < 0 or agent_id >= len(agents):
        return render_template("404.html"), 404

    agent = agents[agent_id]
    return render_template("admin_agent_form.html", agent=agent, agent_id=agent_id)


# SALVA (NUOVO O MODIFICA) ---------------------------------------------------
@app.route("/admin/agents/save", methods=["POST"])
def admin_save_agent():
    agents = load_agents()

    # se c'è agent_id facciamo modifica, altrimenti nuovo
    agent_id_raw = request.form.get("agent_id")
    agent_id = int(agent_id_raw) if agent_id_raw not in (None, "", "None") else None

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    whatsapp = request.form.get("whatsapp", "").strip()
    email = request.form.get("email", "").strip()
    gallery = request.form.get("gallery", "").strip()

    # Upload foto -------------------------------------------------------------
    photo = request.files.get("photo")
    photo_path = None

    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        abs_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        photo.save(abs_path)
        # percorso relativo usato in url_for('static', filename=...)
        photo_path = f"uploads/{filename}"

    # Se stiamo modificando, partiamo dai dati esistenti
    if agent_id is not None and 0 <= agent_id < len(agents):
        agent = agents[agent_id]
    else:
        agent = {}

    agent["name"] = name
    agent["phone"] = phone
    agent["whatsapp"] = whatsapp
    agent["email"] = email
    agent["gallery"] = gallery

    if photo_path:
        agent["photo"] = photo_path

    if agent_id is None:
        agents.append(agent)
    else:
        agents[agent_id] = agent

    save_agents(agents)

    return redirect(url_for("admin_list"))


# CARD PUBBLICA --------------------------------------------------------------
@app.route("/card/<int:agent_id>")
def public_card(agent_id):
    agents = load_agents()
    if agent_id < 0 or agent_id >= len(agents):
        return render_template("404.html"), 404

    agent = agents[agent_id]
    return render_template("card.html", agent=agent, agent_id=agent_id)


# 404 PERSONALIZZATA ---------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Per esecuzione locale ------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=100
