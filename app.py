from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# CARTELLE STATICHE ----------------------------------------------------------
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

AGENTS_FILE = "agents.json"

# FUNZIONI UTILI -------------------------------------------------------------
def load_agents():
    if not os.path.exists(AGENTS_FILE):
        return []
    with open(AGENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_agents(agents):
    with open(AGENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, indent=4, ensure_ascii=False)

# ROTTA LOGIN ---------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        if user == "admin" and pwd == "test":
            return redirect(url_for("admin_list"))

        return render_template("login.html", error="Credenziali errate")

    return render_template("login.html")

# LISTA AGENTI ---------------------------------------------------------------
@app.route("/admin")
def admin_list():
    agents = load_agents()
    return render_template("admin_list.html", agents=agents)

# FORM NUOVO AGENTE ----------------------------------------------------------
@app.route("/admin/new", methods=["GET", "POST"])
def admin_new_agent():
    if request.method == "POST":
        agents = load_agents()

        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        role = request.form.get("role")

        photo_file = request.files.get("photo")
        photo_filename = None

        if photo_file and photo_file.filename:
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_filename)
            photo_file.save(photo_path)

        new_agent = {
            "id": len(agents) + 1,
            "name": name,
            "phone": phone,
            "email": email,
            "role": role,
            "photo": photo_filename
        }

        agents.append(new_agent)
        save_agents(agents)

        return redirect(url_for("admin_list"))

    return render_template("admin_agent_form.html")

# MOSTRA CARD AGENTE ---------------------------------------------------------
@app.route("/agent/<int:agent_id>")
def show_agent(agent_id):
    agents = load_agents()
    agent = next((a for a in agents if a["id"] == agent_id), None)

    if not agent:
        return render_template("404.html"), 404

    return render_template("card.html", agent=agent)

# ROUTE PER IMMAGINI CARICATE ------------------------------------------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# HOME REDIRECT ---------------------------------------------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))

# ERRORE 404 ---------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# AVVIO LOCALE ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, d
