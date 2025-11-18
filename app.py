import os
import json
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    abort,
)

# -------------------------------------------------
# CONFIGURAZIONE DI BASE
# -------------------------------------------------
app = Flask(__name__)

# chiave per la sessione (puoi cambiarla)
app.secret_key = os.environ.get("SECRET_KEY", "pay4you-secret")

# file dove salviamo gli agenti (in JSON)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "static", "uploads")
AGENTS_FILE = os.path.join(DATA_DIR, "agents.json")

os.makedirs(DATA_DIR, exist_ok=True)


# -------------------------------------------------
# FUNZIONI DI SUPPORTO
# -------------------------------------------------
def load_agents():
    """Legge la lista agenti dal file JSON."""
    if not os.path.exists(AGENTS_FILE):
        return []
    try:
        with open(AGENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_agents(agents):
    """Salva la lista agenti nel file JSON."""
    with open(AGENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)


def require_admin(view_func):
    """Decorator per proteggere le pagine admin."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


# -------------------------------------------------
# ROUTE PUBBLICHE
# -------------------------------------------------
@app.route("/")
def index():
    # home = redirect verso login oppure in futuro verso la card pubblica
    return redirect(url_for("login"))


@app.route("/card/<int:agent_id>")
def public_card(agent_id):
    """Mostra la card pubblica dell'agente."""
    agents = load_agents()
    if agent_id < 0 or agent_id >= len(agents):
        abort(404)
    agent = agents[agent_id]
    return render_template("card.html", agent=agent, agent_id=agent_id)


# -------------------------------------------------
# LOGIN SEMPLICE PER ADMIN
# -------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login molto semplice.
    Password presa da variabile di ambiente ADMIN_PASSWORD
    oppure 'test' come default.
    """
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        real_password = os.environ.get("ADMIN_PASSWORD", "test")
        if password == real_password:
            session["is_admin"] = True
            return redirect(url_for("admin_list"))
        else:
            error = "Password errata"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------------------------------------------------
# AREA ADMIN: ELENCO / NUOVO / MODIFICA
# -------------------------------------------------
@app.route("/admin/agents")
@require_admin
def admin_list():
    """Elenco agenti (usa il template admin_list.html)."""
    agents = load_agents()
    return render_template("admin_list.html", agents=agents)


@app.route("/admin/agents/new", methods=["GET", "POST"])
@require_admin
def admin_new_agent():
    """Form per creare un nuovo agente (admin_agent_form.html)."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        company = request.form.get("company", "").strip()
        role = request.form.get("role", "").strip()
        photo = request.form.get("photo", "").strip()  # per ora solo URL

        agents = load_agents()
        agents.append(
            {
                "name": name,
                "phone": phone,
                "email": email,
                "company": company,
                "role": role,
                "photo": photo,
            }
        )
        save_agents(agents)
        return redirect(url_for("admin_list"))

    # GET: mostra il form vuoto
    return render_template("admin_agent_form.html", agent=None)


@app.route("/admin/agents/<int:agent_id>/edit", methods=["GET", "POST"])
@require_admin
def admin_edit_agent(agent_id):
    """Modifica di un agente esistente."""
    agents = load_agents()
    if agent_id < 0 or agent_id >= len(agents):
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        company = request.form.get("company", "").strip()
        role = request.form.get("role", "").strip()
        photo = request.form.get("photo", "").strip()

        agents[agent_id].update(
            {
                "name": name,
                "phone": phone,
                "email": email,
                "company": company,
                "role": role,
                "photo": photo,
            }
        )
        save_agents(agents)
        return redirect(url_for("admin_list"))

    # GET: mostra il form precompilato
    agent = agents[agent_id]
    return render_template("admin_agent_form.html", agent=agent, agent_id=agent_id)


# -------------------------------------------------
# ERROR HANDLER 404
# -------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# -------------------------------------------------
# AVVIO LOCALE (su Render gira con gunicorn app:app)
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

Inviato da iPhone
