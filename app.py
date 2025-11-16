import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename
import json
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)

# =============== SETTINGS ===============
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "test")

DATA_FILE = "data.json"
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =============== LOAD / SAVE JSON ===============
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# =============== LOGIN ===============
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASSWORD:
            return redirect(url_for("admin_list"))
        return render_template("login.html", error="Credenziali errate")
    return render_template("login.html")

# =============== ADMIN – LISTA AGENTI ===============
@app.route("/admin")
def admin_list():
    data = load_data()
    return render_template("admin_list.html", agents=data)

# =============== ADMIN – CREA/MODIFICA AGENTE ===============
@app.route("/admin/edit/<slug>", methods=["GET", "POST"])
@app.route("/admin/new", methods=["GET", "POST"])
def admin_edit(slug=None):
    data = load_data()

    agent = data.get(slug, {}) if slug else {}

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]
        website = request.form["website"]

        new_slug = name.lower().replace(" ", "-")

        filename = agent.get("photo", None)
        if "photo" in request.files and request.files["photo"].filename != "":
            photo = request.files["photo"]
            filename = secure_filename(new_slug + ".jpg")
            photo.save(os.path.join(UPLOAD_FOLDER, filename))

        data[new_slug] = {
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "website": website,
            "photo": filename
        }

        save_data(data)

        return redirect(url_for("admin_list"))

    return render_template("admin_edit.html", agent=agent, slug=slug)

# =============== CARD – PUBBLICA ===============
@app.route("/card/<slug>")
def card(slug):
    data = load_data()
    agent = data.get(slug)

    if not agent:
        return render_template("404.html"), 404

    # QR CODE della stessa pagina
    qr = qrcode.make(request.url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render_template(
        "card.html",
        agent=agent,
        slug=slug,
        qr_code=qr_base64
    )

# =============== VCF – SALVA CONTATTO ===============
@app.route("/card/<slug>/vcf")
def vcf(slug):
    data = load_data()
    agent = data.get(slug)

    if not agent:
        abort(404)

    vcf_text = f"""BEGIN:VCARD
VERSION:3.0
FN:{agent['name']}
TEL:{agent['phone']}
EMAIL:{agent['email']}
END:VCARD"""

    return vcf_text, 200, {
        "Content-Type": "text/vcard",
        "Content-Disposition": f"attachment; filename={slug}.vcf"
    }

# =============== START ===============
if __name__ == "__main__":
    app.run()
