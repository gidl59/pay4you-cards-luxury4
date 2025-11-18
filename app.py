from flask import Flask, render_template, send_from_directory
import os

app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)

########################################
# HOME → mostra la card (o reindirizza)
########################################
@app.route('/')
def home():
    return render_template("card.html")


########################################
# CARD AGENTE (se vuoi un indirizzo tipo /agente/nome)
########################################
@app.route('/card/<nome>')
def card(nome):
    return render_template("card.html", nome=nome)


########################################
# SERVE FILE STATICI (immagini, css)
########################################
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


########################################
# RUN PER RENDER
########################################
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
