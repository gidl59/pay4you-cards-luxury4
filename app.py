import os
import json
import io
from functools import wraps

import qrcode
from flask import (
    Flask,
    render_template,
    abort,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file,
)

app = Flask(__name__)

# Chiave di sessione per login admin
app.secret_key = os.environ.get("SECRET_KEY", "cambia-questa-chiave-super-segreta")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_PATH = os.path.join(BASE_DIR, "agents.json")


# -------------------------
#  FUNZIONI DI SUPPORTO
# -------------------------
def load_agents():
    """Legge agents.json e ritorna una lista di agenti."""
    if not os.path.exists(AGENTS_PATH):
        return []
    try:
        with open(AGENTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        print("ERRORE: formato JSON non valido in agents.json")
        return []


def save_agents(agents):
    """Salva la lista agenti su agents.json."""
    with open(AGENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)


AGENTS = load_agents()


def refresh_agents():
    """Ricarica la lista agenti in memoria."""
    global AGENTS
    AGENTS = load_agents()


def get_agent_by_slug(slug):
    for a in AGENTS:
        if a.get("slug") == slug:
            return a
    return None


def admin_logged_in():
    return session.get("admin_logged_in") is True


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not admin_logged_in():
            return redirect(url_for("admin_login", next=request.path))
        return view_func(*args, **kwargs)

    return wrapped


# -------------------------
#  ROTTE PUBBLICHE
# -------------------------
@app.route("/")
def index():
    """Elenco pubblico degli agenti (lista card)."""
    return render_template("index.html", agents=AGENTS)


@app.route("/card/<slug>")
def card(slug):
    """Card pubblica dell'agente (vista da QR / link)."""
    agent = get_agent_by_slug(slug)
    if not agent:
        abort(404)
    return render_template("card.html", agent=agent)


@app.route("/qr/<slug>.png")
def qr_code(slug):
    """Genera al volo il QR code per la card dell'agente."""
    agent = get_agent_by_slug(slug)
    if not agent:
        abort(404)

    # URL completo della card (es: https://pay4you-cards-luxury4.onrender.com/card/giuseppe)
    card_url = url_for("card", slug=slug, _external=True)

    img = qrcode.make(card_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")


@app.route("/health")
def health():
    return "OK", 200


# -------------------------
#  LOGIN ADMIN
# -------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """
    Login semplice con password fissa.
    Password attuale: test  (puoi cambiarla qui sotto).
    """
    if request.method == "POST":
        password = request.form.get("password", "").strip()
        if password == "test":  # <--- CAMBIA QUI LA PASSWORD
            session["admin_logged_in"] = True
            flash("Login effettuato", "success")
            next_url = request.args.get("next") or url_for("admin_agents")
            return redirect(next_url)
        else:
            flash("Password errata", "error")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Disconnesso", "success")
    return redirect(url_for("admin_login"))


# -------------------------
#  PANNELLO ADMIN
# -------------------------
@app.route("/admin")
@login_required
def admin_agents():
    """Lista agenti in admin."""
    return render_template("admin_agents.html", agents=AGENTS)


@app.route("/admin/agent/new", methods=["GET", "POST"])
@login_required
def admin_new_agent():
    """Crea nuovo agente."""
    if request.method == "POST":
        slug = request.form.get("slug", "").strip().lower()
        if not slug:
            flash("Lo slug è obbligatorio.", "error")
            return redirect(url_for("admin_new_agent"))

        if get_agent_by_slug(slug):
            flash("Esiste già un agente con questo slug.", "error")
            return redirect(url_for("admin_new_agent"))

        new_agent = {
            "slug": slug,
            "nome": request.form.get("nome", "").strip(),
            "titolo_breve": request.form.get("titolo_breve", "").strip(),
            "ruolo_principale": request.form.get("ruolo_principale", "").strip(),
            "ruolo_secondario": request.form.get("ruolo_secondario", "").strip(),
            "mobile": request.form.get("mobile", "").strip(),
            "ufficio": request.form.get("ufficio", "").strip(),
            "email_personale": request.form.get("email_personale", "").strip(),
            "email_aziendale": request.form.get("email_aziendale", "").strip(),
            "sito_web": request.form.get("sito_web", "").strip(),
            "indirizzo_1_label": request.form.get("indirizzo_1_label", "").strip(),
            "indirizzo_1": request.form.get("indirizzo_1", "").strip(),
            "indirizzo_2_label": request.form.get("indirizzo_2_label", "").strip(),
            "indirizzo_2": request.form.get("indirizzo_2", "").strip(),
            "whatsapp": request.form.get("whatsapp", "").strip(),
            "foto_profilo": request.form.get("foto_profilo", "").strip(),
            "foto_cover": request.form.get("foto_cover", "").strip(),
            "vcard_file": request.form.get("vcard_file", "").strip(),
            # il QR ora è generato al volo, non serve salvare file path
        }

        agents = load_agents()
        agents.append(new_agent)
        save_agents(agents)
        refresh_agents()
        flash("Agente creato.", "success")
        return redirect(url_for("admin_agents"))

    return render_template("admin_edit_agent.html", agent=None)


@app.route("/admin/agent/<slug>/edit", methods=["GET", "POST"])
@login_required
def admin_edit_agent(slug):
    """Modifica un agente esistente."""
    agent = get_agent_by_slug(slug)
    if not agent:
        abort(404)

    if request.method == "POST":
        agents = load_agents()
        for a in agents:
            if a.get("slug") == slug:
                a["nome"] = request.form.get("nome", "").strip()
                a["titolo_breve"] = request.form.get("titolo_breve", "").strip()
                a["ruolo_principale"] = request.form.get("ruolo_principale", "").strip()
                a["ruolo_secondario"] = request.form.get("ruolo_secondario", "").strip()
                a["mobile"] = request.form.get("mobile", "").strip()
                a["ufficio"] = request.form.get("ufficio", "").strip()
                a["email_personale"] = request.form.get("email_personale", "").strip()
                a["email_aziendale"] = request.form.get("email_aziendale", "").strip()
                a["sito_web"] = request.form.get("sito_web", "").strip()
                a["indirizzo_1_label"] = request.form.get("indirizzo_1_label", "").strip()
                a["indirizzo_1"] = request.form.get("indirizzo_1", "").strip()
                a["indirizzo_2_label"] = request.form.get("indirizzo_2_label", "").strip()
                a["indirizzo_2"] = request.form.get("indirizzo_2", "").strip()
                a["whatsapp"] = request.form.get("whatsapp", "").strip()
                a["foto_profilo"] = request.form.get("foto_profilo", "").strip()
                a["foto_cover"] = request.form.get("foto_cover", "").strip()
                a["vcard_file"] = request.form.get("vcard_file", "").strip()
                break

        save_agents(agents)
        refresh_agents()
        flash("Agente aggiornato.", "success")
        return redirect(url_for("admin_agents"))

    return render_template("admin_edit_agent.html", agent=agent)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
