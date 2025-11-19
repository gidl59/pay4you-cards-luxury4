from flask import Flask, render_template, request, redirect, url_for, abort
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

DATA_FILE = "agents.json"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------
# UTILS
# --------------------

def load_agents():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_agents(agents):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, indent=2, ensure_ascii=False)



# --------------------
# HOME
# --------------------

@app.route("/")
def home():
    return render_template("login.html")



# --------------------
# LOGIN
# --------------------

ADMIN_PASSWORD = "test"

@app.route("/login", methods=["POST"])
def login():
    pwd = request.form.get("password")
    if pwd == ADMIN_PASSWORD:
        return redirect(url_for("admin_list"))
    return render_template("login.html", error="Password errata")



# --------------------
# LISTA AGENTI
# --------------------

@app.route("/admin")
def admin_list():
    agents = load_agents()
    return render_template("admin_list.html", agents=agents)



# --------------------
# NUOVO AGENTE
# --------------------

@app.route("/admin/new", methods=["GET", "POST"])
def admin_new_agent():
    if request.method == "POST":
        agents = load_agents()

        name = request.form.get("name")
        phone = request.form.get("phone")
        whatsapp = request.form.get("whatsapp")
        email = request.form.get("email")
        gallery = request.form.get("gallery", "")

        # foto
        photo_file = request.files.get("photo")
        photo_filename = None
        if photo_file and photo_file.filename:
            filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(UPLOAD_FOLDER, filename)
            photo_file.save(photo_path)
            photo_filename = filename

        new_agent = {
            "name": name,
            "phone": phone,
            "whatsapp": whatsapp,
            "email": email,
            "gallery": gallery,
            "photo": photo_filename
        }

        agents.append(new_agent)
        save_agents(agents)

        return redirect(url_for("admin_list"))

    return render_template("admin_agent_form.html", agent=None, agent_id=None)



# --------------------
# MODIFICA AGENTE
# --------------------

@app.route("/admin/edit/<int:agent_id>", methods=["GET", "POST"])
def admin_edit_agent(agent_id):
    agents = load_agents()

    if agent_id < 0 or agent_id >= len(agents):
        abort(404)

    agent = agents[agent_id]

    if request.method == "POST":
        agent["name"] = request.form.get("name")
        agent["phone"] = request.form.get("phone")
        agent["whatsapp"] = request.form.get("whatsapp")
        agent["email"] = request.form.get("email")
        agent["gallery"] = request.form.get("gallery", "")

        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(UPLOAD_FOLDER, filename)
            photo_file.save(photo_path)
            agent["photo"] = filename

        save_agents(agents)
        return redirect(url_for("admin_list"))

    return render_template("admin_agent_form.html", agent=agent, agent_id=agent_id)



# --------------------
# CARD PUBBLICA
# --------------------

@app.route("/card/<int:agent_id>")
def public_card(agent_id):
    agents = load_agents()

    if agent_id < 0 or agent_id >= len(agents):
        abort(404)

    agent = agents[agent_id]
    return render_template("card.html", agent=agent)



# --------------------
# 404
# --------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404



# --------------------
# RUN
# --------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
