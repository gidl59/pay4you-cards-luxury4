import os
import json
from flask import Flask, render_template, abort

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_PATH = os.path.join(BASE_DIR, "agents.json")


def load_agents():
    """Carica la lista degli agenti da agents.json."""
    try:
        with open(AGENTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except FileNotFoundError:
        print("ATTENZIONE: agents.json non trovato.")
        return []
    except json.JSONDecodeError:
        print("ATTENZIONE: errore di formato in agents.json.")
        return []


AGENTS = load_agents()


def get_agent_by_slug(slug: str):
    """Ritorna l'agente con lo slug richiesto, oppure None."""
    for agent in AGENTS:
        if agent.get("slug") == slug:
            return agent
    return None


@app.route("/")
def index():
    """
    Elenco agenti.
    Pagina semplice da cui apri la card.
    """
    return render_template("index.html", agents=AGENTS)


@app.route("/card/<slug>")
def card(slug):
    """
    Card singola dell'agente, vista finale (quella da aprire con QR).
    """
    agent = get_agent_by_slug(slug)
    if not agent:
        abort(404)
    return render_template("card.html", agent=agent)


@app.route("/health")
def health():
    """Rotta di test per Render."""
    return "OK", 200


if __name__ == "__main__":
    # Per sviluppo locale
    app.run(host="0.0.0.0", port=5000, debug=True)
