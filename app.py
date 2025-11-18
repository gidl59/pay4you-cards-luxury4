import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Cartella per upload immagini profilo
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Memoria in RAM degli agenti (lista di dizionari)
agents = []


# ---------------------------
# ROTTE DI BASE
# ---------------------------

@app.route("/")
def home():
    # reindirizza sempre alla pagina di login
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login molto semplice con una sola password.
    Password di default: "test"
    Puoi cambiarla mettendo ADMIN_PASSWORD nelle variabili di ambiente di Render.
    """
    if request.method == "POST":
        pwd = request.form.get("password", "")
        correct = os.getenv("ADMIN_PASSWORD", "test")

        if pwd == correct:
            return redirect(url_for("admin_list"))
        else:
            return render_template("login.html", error="Password errata")

    return render_template("login.html")


# ---------------------------
# AREA ADMIN - ELENCO
# ---------------------------

@app.route("/admin")
def admin_list():
    """
    Elenco di tutti gli agenti.
    Usa il template admin_list.html
    """
    return render_template("admin_list.html", agents=agents)


# ---------------------------
# AREA ADMIN - NUOVO AGENTE
# ---------------------------

@app.route("/admin/agent/new", methods=["GET", "POST"])
def admin_new_agent():
    """
    Crea un nuovo agente.
    GET  -> mostra il form vuoto
    POST -> salva i dati e torna alla lista
    """
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        whatsapp = request.form.get("whatsapp", "").strip()
        email = request.form.get("email", "").strip()
        gallery = request.form.get("gallery", "").strip()

        # upload foto
        photo_file = request.files.get("photo")
        photo_path = None
        if photo_file and photo_file.filename:
            filename = photo_file.filename
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            photo_file.save(save_path)
            photo_path = save_path

        agent = {
            "name": name,
            "phone": phone,
            "whatsapp": whatsapp,
            "email": email,
            "gallery": gallery,
            "photo": photo_path,
        }
        agents.append(agent)

        return redirect(url_for("admin_list"))

    # GET -> form vuoto
    return render_template(
        "admin_agent_form.html",
        agent=None,
        agent_id=None,
    )


# ---------------------------
# AREA ADMIN - MODIFICA AGENTE
# ---------------------------

@app.route("/admin/agent/<int:agent_id>/edit", methods=["GET", "POST"])
def admin_edit_agent(agent_id: int):
    """
    Modifica di un agente esistente (indice nella lista agents).
    """
    # Controllo rapido su indice
    if agent_id < 0 or agent_id >= len(agents):
        return render_template("404.html"), 404

    agent = agents[agent_id]

    if request.method == "POST":
        agent["name"] = request.form.get("name", "").strip()
        agent["phone"] = request.form.get("phone", "").strip()
        agent["whatsapp"] = request.form.get("whatsapp", "").strip()
        agent["email"] = request.form.get("email", "").strip()
        agent["gallery"] = request.form.get("gallery", "").strip()

        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            filename = photo_file.filename
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            photo_file.save(save_path)
            agent["photo"] = save_path

        return redirect(url_for("admin_list"))

    # GET -> mostra form con dati precompilati
    return render_template(
        "admin_agent_form.html",
        agent=agent,
        agent_id=agent_id,
    )


# ---------------------------
# CARD PUBBLICA
# ---------------------------

@app.route("/card/<int:agent_id>")
def public_card(agent_id: int):
    """
    Card pubblica di un agente specifico.
    """
    if agent_id < 0 or agent_id >= len(agents):
        return render_template("404.html"), 404

    agent = agents[agent_id]
    return render_template("card.html", agent=agent)


# ---------------------------
# ERRORE 404 PERSONALIZZATO
# ---------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# ---------------------------
# AVVIO LOCALE
# ---------------------------

if __name__ == "__main__":
    # Per sviluppo locale; su Render viene usato gunicorn app:app
    app.run(host="0.0.0.0", port=5000, debug=T
