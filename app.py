import os
import json
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, send_from_directory, abort
)

# --- Config app ---
app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)

# Chiave per la sessione (login admin)
app.secret_key = os.environ.get("SECRET_KEY", "pay4you-dev-secret")

# File dove salviamo gli agenti (in JSON)
AGENTS_FILE = os.path.join(os.path.dirname(__file__), "agents.json")

# Cartella upload (per eventuali foto/pdf in futuro)
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------- FUNZIONI DI SUPPORTO ----------

def load_agents():
    """Carica gli agenti dal file JSON."""
    if not os.path.exists(AGENTS_FILE):
        return {}
    try:
        with open(AGENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # data è un dict {slug: {...}}
            return data
    except Exception:
        return {}


def save_agents(agents: dict):
    """Salva gli agenti nel file JSON."""
    with open(AGENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)


def get_admin_password():
    """Password admin presa da ENV, default 'test' se non impostata."""
    return os.environ.get("ADMIN_PASSWORD", "test")


# ---------- ROUTE PUBBLICHE ----------

@app.route("/health")
def health():
    return "ok", 200


@app.route("/")
def public_home():
    """
    Home pubblica:
    - se esiste almeno un agente, mostra il primo
    - altrimenti mostra la card 'vuota' (senza dati reali)
    """
    agents = load_agents()
    if agents:
        # Prende il primo agente del dict
        first_slug = next(iter(agents))
        agent = agents[first_slug]
        return render_template("card.html", agent=agent)
    # Nessun agente: card di esempio senza 'agent'
    return render_template("card.html")


@app.route("/<slug>")
def public_card(slug):
    """Card pubblica per uno specifico agente, es: /giuseppe."""
    agents = load_agents()
    agent = agents.get(slug)
    if not agent:
        return render_template("404.html"), 404
    return render_template("card.html", agent=agent)


# Per servire eventuali file caricati (foto/pdf)
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------- LOGIN / LOGOUT ADMIN ----------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd == get_admin_password():
            session["is_admin"] = True
            return redirect(url_for("admin_home"))
        else:
            error = "Password errata"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("public_home"))


def require_admin():
    if not session.get("is_admin"):
        return False
    return True


# ---------- AREA ADMIN ----------

@app.route("/admin")
def admin_home():
    if not require_admin():
        return redirect(url_for("login"))
    agents = load_agents()
    # Passo una lista ordinata per nome
    agents_list = sorted(agents.values(), key=lambda a: a.get("name", "").lower())
    return render_template("admin_list.html", agents=agents_list)


@app.route("/admin/new", methods=["GET", "POST"])
def admin_new():
    if not require_admin():
        return redirect(url_for("login"))

    if request.method == "POST":
        slug = request.form.get("slug", "").strip().lower()
        name = request.form.get("name", "").strip()

        if not slug or not name:
            error = "Slug e Nome sono obbligatori"
            return render_template("admin_agent_form.html", agent=None, error=error)

        agents = load_agents()
        if slug in agents:
            error = "Slug già esistente, scegline un altro"
            return render_template("admin_agent_form.html", agent=None, error=error)

        agent = {
            "slug": slug,
            "name": name,
            "role": request.form.get("role", "").strip(),
            "company": request.form.get("company", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "whatsapp": request.form.get("whatsapp", "").strip(),
            "email": request.form.get("email", "").strip(),
            "website": request.form.get("website", "").strip(),
            "facebook": request.form.get("facebook", "").strip(),
            "instagram": request.form.get("instagram", "").strip(),
            "linkedin": request.form.get("linkedin", "").strip(),
            # campi pdf / gallery vuoti per ora
            "pdf1": "",
            "pdf2": "",
            "pdf3": "",
            "pdf4": "",
            "gallery1": "",
            "gallery2": "",
            "gallery3": "",
            "gallery4": "",
            "photo": ""
        }
        agents[slug] = agent
        save_agents(agents)
        return redirect(url_for("admin_home"))

    # GET
    return render_template("admin_agent_form.html", agent=None, error=None)


@app.route("/admin/<slug>/edit", methods=["GET", "POST"])
def admin_edit(slug):
    if not require_admin():
        return redirect(url_for("login"))

    agents = load_agents()
    agent = agents.get(slug)
    if not agent:
        return render_template("404.html"), 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            error = "Il nome è obbligatorio"
            return render_template("admin_agent_form.html", agent=agent, error=error)

        # Aggiorno i campi base
        agent["name"] = name
        agent["role"] = request.form.get("role", "").strip()
        agent["company"] = request.form.get("company", "").strip()
        agent["phone"] = request.form.get("phone", "").strip()
        agent["whatsapp"] = request.form.get("whatsapp", "").strip()
        agent["email"] = request.form.get("email", "").strip()
        agent["website"] = request.form.get("website", "").strip()
        agent["facebook"] = request.form.get("facebook", "").strip()
        agent["instagram"] = request.form.get("instagram", "").strip()
        agent["linkedin"] = request.form.get("linkedin", "").strip()

        agents[slug] = agent
        save_agents(agents)
        return redirect(url_for("admin_home"))

    # GET
    return render_template("admin_agent_form.html", agent=agent, error=None)


@app.route("/admin/<slug>/delete", methods=["POST"])
def admin_delete(slug):
    if not require_admin():
        return redirect(url_for("login"))

    agents = load_agents()
    if slug in agents:
        agents.pop(slug)
        save_agents(agents)
    return redirect(url_for("admin_home"))


# ---------- 404 PERSONALIZZATA ----------

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# ---------- AVVIO LOCALE / RENDER ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", por
