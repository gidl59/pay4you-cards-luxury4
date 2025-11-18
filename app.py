from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

########################################
# HOME → REDIRECT AL LOGIN
########################################
@app.route('/')
def home():
    return redirect('/login')


########################################
# PAGINA LOGIN
########################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == "test":  # PUOI CAMBIARLA
            return redirect('/dashboard')
        else:
            return render_template("login.html", error="Password errata")
    return render_template("login.html")


########################################
# DASHBOARD (LISTA AGENTI)
########################################
@app.route('/dashboard')
def dashboard():
    # Esempio agenti – poi li prenderemo da JSON o Firebase
    agenti = [
        {"id": 1, "nome": "Mario Rossi"},
        {"id": 2, "nome": "Giuseppe Di Lisio"},
        {"id": 3, "nome": "Laura Bianchi"}
    ]
    return render_template("dashboard.html", agenti=agenti)


########################################
# CARD AGENTE
########################################
@app.route('/agente/<int:id>')
def agente(id):
    # Dati di esempio → poi collego al tuo database
    agente = {
        "id": id,
        "nome": "Nome Cognome",
        "telefono": "+39 333 0000000",
        "email": "email@example.com",
        "foto": "/static/img/default.jpg"
    }
    return render_template("card.html", agente=agente)


########################################
# DOWNLOAD VCF (BIGLIETTO DA VISITA)
########################################
@app.route('/download_vcf/<int:id>')
def download_vcf(id):
    file_path = os.path.join("static", "vcf", f"agente_{id}.vcf")
    if os.path.exists(file_path):
        return send_from_directory("static/vcf", f"agente_{id}.vcf", as_attachment=True)
    return "VCF non trovato", 404


########################################
# SERVE PER FAR PARTIRE CORRETTAMENTE SU RENDER
########################################
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
