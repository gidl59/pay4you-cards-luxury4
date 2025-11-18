import os
from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ---------------------------------------------------------
# CONFIGURAZIONE STORAGE FILE
# ---------------------------------------------------------
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# =========================================================
# DATABASE SEMPLICE (MEMORIA) – SOSTITUIBILE CON FIREBASE
# =========================================================
AGENTS = {}

def get_agent(agent_id):
    return AGENTS.get(agent_id)

# =========================================================
# PAGINA LOGIN ADMIN
# =========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "test":  # ← CAMBIA PASSWORD QUI
            return redirect("/admin")
        return render_template("login.html", error="Password errata")
    return render_template("login.html")

# =========================================================
# DASHBOARD ADMIN
# =========================================================
@app.route("/admin")
def admin_home():
    return render_template("admin_list.html", agents=AGENTS)

# =========================================================
# AGGIUNGI / MODIFICA AGENTE
# =========================================================
@app.route("/admin/agent", methods=["GET", "POST"])
def admin_agent_form():
    agent_id = request.args.get("id")

    if request.method == "POST":
        # --- lettura dati modulo ---
        agent_id = request.form.get("agent_id").strip()
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        whatsapp = request.form.get("whatsapp")
        facebook = request.form.get("facebook")
        instagram = request.form.get("instagram")
        website = request.form.get("website")
        pdf1 = request.form.get("pdf1")
        pdf2 = request.form.get("pdf2")
        pdf3 = request.form.get("pdf3")
        pdf4 = request.form.get("pdf4")

        # ------------------------------
        # FOTO
        # ------------------------------
        photo_file = request.files.get("photo")
        photo_filename = None

        if photo_file and photo_file.filename != "":
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_filename)
            photo_file.save(photo_path)

        # ------------------------------
        # SALVATAGGIO AGENTE
        # ------------------------------
        AGENTS[agent_id] = {
            "id": agent_id,
            "name": name,
            "phone": phone,
            "email": email,
            "whatsapp": whatsapp,
            "facebook": facebook,
            "instagram": instagram,
            "website": website,
            "pdf1": pdf1,
            "pdf2": pdf2,
            "pdf3": pdf3,
            "pdf4": pdf4,
            "photo": photo_filename,
        }

        return redirect("/admin")

    # SE È MODIFICA, PRERCHÈ HO ID
    agent_data = None
    if agent_id:
        agent_data = get_agent(agent_id)
        if not agent_data:
            abort(404)

    return render_template("admin_agent_form.html", agent=agent_data)

# =========================================================
# PAGINA CARD /biglietto da visita
# =========================================================
@app.route("/card/<agent_id>")
def card_page(agent_id):
    agent = get_agent(agent_id)
    if not agent:
        abort(404)
    return render_template("card.html", agent=agent)

# =========================================================
# HOME → REDIRECT A LOGIN
# =========================================================
@app.route("/")
def home():
    return redirect("/login")

# =========================================================
# PAGINA 404 PERSONALIZZATA
# =========================================================
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

# =========================================================
# AVVIO SERVER (PER RENDER)
# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
