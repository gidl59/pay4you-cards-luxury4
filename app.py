import os
import json
from flask import Flask, render_template, abort

app = Flask(__name__)

# Percorso base del progetto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_PATH = os.path.join(BASE_DIR, "agents.json")


def load_agents():
    """Carica la lista agenti da agents.json."""
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


def get_agent_by_slug(slug):
    """Ritorna l'agente con quello slug oppure None."""
    for agent in AGENTS:
        if agent.get("slug") == slug:
            return agent
    return None


@app.context_processor
def inject_brand():
    """Variabili globali per i template (se ti servono)."""
    return {
        "brand_name": "PAY4YOU",
        "brand_subtitle": "Agenzia di Promozione Servizi POS",
    }


@app.route("/")
def index():
    """
    Pagina elenco agenti.
    Usa templates/index.html
    e riceve la lista AGENTS.
    """
    return render_template("index.html", agents=AGENTS)


@app.route("/card/<slug>")
def card(slug):
    """
    Pagina card singola agente.
    Usa templates/card.html
    e riceve un singolo 'agent'.
    """
    agent = get_agent_by_slug(slug)
    if not agent:
        abort(404)
    return render_template("card.html", agent=agent)


# (Opzionale) rotta di test per Render/health check
@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    # Per sviluppo locale
    app.run(host="0.0.0.0", port=5000, debug=True)
