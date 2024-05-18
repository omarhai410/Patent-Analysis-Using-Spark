from bson import ObjectId
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itertools import chain


app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'  # Clé secrète pour la gestion de session

client = MongoClient('localhost', 27017)
db = client['spark']
db_users = client['spark']['users']
db_consultation = client['spark']['consultation']

# Charger les informations de configuration depuis config.json
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)

smtp_server = config_data["server"]
smtp_port = config_data["port"]
sender_email = config_data["email"]
sender_password = config_data["pwd"]



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('bigdata.html')

@app.route('/login2', methods=['GET', 'POST'])
def index2():
    return render_template('index.html')

@app.route('/login3', methods=['GET', 'POST'])
def index3():
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['pass']

    # Vérifier les informations d'identification dans la base de données
    user = db_users.find_one({'email': email, 'password': password})
    if user:
        # Connectez-vous avec succès, stockez le nom de l'utilisateur dans la session
        session['username'] = user['fullname']
        return redirect(url_for('recherche'))
    else:
        # Informez l'utilisateur que les informations d'identification sont incorrectes
        return render_template('index.html', error_message='Invalid email or password')

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        dob = request.form['dob']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['pass']

        data = {
            'fullname': fullname,
            'dob': dob,
            'phone': phone,
            'email': email,
            'password': password
        }

        db_users.insert_one(data)  # Insérer dans la collection 'users'

        return render_template('signup.html')

@app.route('/recherche', methods=['GET', 'POST'])
def recherche():
    if request.method == 'POST':
        selected_ids = request.form.getlist('selectedIds[]')
        search_term = request.form['search']
        selected_ids_str = request.form['selected_ids_str']

        username = session.get('username', None)

        if selected_ids_str == 'google':
            results, total_results = search_in_google_db(search_term, username)
        elif selected_ids_str == 'upsto':
            results, total_results = search_in_upsto_db(search_term, username)
        elif selected_ids_str == 'epo':
            results, total_results = search_in_epo_db(search_term, username)
        elif selected_ids_str == 'wipo':
            results, total_results = search_in_wipo_db(search_term, username)
        else:
            # If none of the specific databases are selected, search in all databases
            google_results, _ = search_in_google_db(search_term, username)
            epo_results, _ = search_in_epo_db(search_term, username)
            wipo_results, _ = search_in_wipo_db(search_term, username)

            # Aggregate results from all databases
            results = list(chain(google_results, epo_results, wipo_results))
            total_results = len(results)

        return render_template('recherche.html', results=results, total_results=total_results)
    return render_template('recherche.html', results=None, total_results=0)

def search_in_google_db(search_term, username=None):
    results = list(db.data.find({"title": {"$regex": search_term, "$options": "i"}}))
    total_results = len(results)
    if username:
        for result in results:
            consultation = db_consultation.find_one({"username": username, "patent_id": result["ID"]})
            if consultation:
                result["consultation_count"] = consultation.get("consultation_count", 0)
                result["last_consulted"] = consultation.get("last_consulted", None)
            else:
                result["consultation_count"] = 0
                result["last_consulted"] = None
    return results, total_results

def search_in_upsto_db(search_term,username=None):
    results = list(db.patentscope.find({"title": {"$regex": search_term, "$options": "i"}}))
    total_results = len(results)
    if username:
        for result in results:
            consultation = db_consultation.find_one({"username": username, "patent_id": result["ID"]})
            if consultation:
                result["consultation_count"] = consultation.get("consultation_count", 0)
                result["last_consulted"] = consultation.get("last_consulted", None)
            else:
                result["consultation_count"] = 0
                result["last_consulted"] = None
    return results, total_results

def search_in_epo_db(search_term,username=None):
    results = list(db.FPO.find({"title": {"$regex": search_term, "$options": "i"}}))
    total_results = len(results)
    if username:
        for result in results:
            consultation = db_consultation.find_one({"username": username, "patent_id": result["ID"]})
            if consultation:
                result["consultation_count"] = consultation.get("consultation_count", 0)
                result["last_consulted"] = consultation.get("last_consulted", None)
            else:
                result["consultation_count"] = 0
                result["last_consulted"] = None
    return results, total_results

def search_in_wipo_db(search_term,username=None):
    results = list(db.wip.find({"title": {"$regex": search_term, "$options": "i"}}))
    total_results = len(results)
    if username:
        for result in results:
            consultation = db_consultation.find_one({"username": username, "patent_id": result["ID"]})
            if consultation:
                result["consultation_count"] = consultation.get("consultation_count", 0)
                result["last_consulted"] = consultation.get("last_consulted", None)
            else:
                result["consultation_count"] = 0
                result["last_consulted"] = None
    return results, total_results

from flask import request

@app.route('/detail/<patent_id>')
def detail(patent_id):
    collection = request.args.get('collection')  # Récupérer la valeur de la collection de l'URL
    if collection == 'data':
        patent_details = db.data.find_one({"ID": patent_id})
    elif collection == 'FPO':
        patent_details = db.FPO.find_one({"ID": patent_id})
    elif collection == 'wip':
        patent_details = db.wip.find_one({"ID": patent_id})
    else:
        patent_details = db.data.find_one({"ID": patent_id})

    current_time = datetime.now()

    if 'username' in session:
        username = session['username']
        db_consultation = db['consultation']  # Assurez-vous d'avoir une collection de consultation
        db_consultation.update_one(
            {"username": username, "patent_id": patent_id},
            {"$inc": {"consultation_count": 1}, "$set": {"last_consulted": current_time}},
            upsert=True
        )

    return render_template('detail.html', patent_details=patent_details)


@app.route('/historique')
def historique():
    if 'username' in session:
        username = session['username']
        consultations = db_consultation.find({"username": username}, {"patent_id": 1, "last_consulted": 1}).sort("last_consulted", -1)
        consultations_dict = {str(consultation["patent_id"]): consultation["last_consulted"] for consultation in consultations}
        return jsonify(consultations_dict)
    else:
        return jsonify({})

@app.route('/historique/delete/<patent_id>', methods=['DELETE'])
def delete_from_historique(patent_id):
    if 'username' in session:
        username = session['username']
        db_consultation.delete_one({"username": username, "patent_id": patent_id})
        return jsonify({"message": "L'élément a été supprimé avec succès"})
    else:
        return jsonify({"error": "Vous devez être connecté pour effectuer cette action"}), 401

@app.route('/user_info', methods=['GET'])
def user_info():
    if 'username' in session:
        username = session['username']
        user_data = db_users.find_one({'fullname': username})
        if user_data:
            html = f'<div>'
            html += f'<h5>Nom complet:</h5><p class="lead">{user_data["fullname"]}</p>'
            html += f'<h5>Date de naissance:</h5><p class="lead">{user_data["dob"]}</p>'
            html += f'<h5>Téléphone:</h5><p class="lead">{user_data["phone"]}</p>'
            html += f'<h5>Email:</h5><p class="lead">{user_data["email"]}</p>'
            html += '</div>'
            return html
        else:
            return '<div class="container">Informations utilisateur non disponibles</div>'
    else:
        return '<div class="container">Utilisateur non connecté</div>'

@app.route('/send_email', methods=['GET'])
def send_email():
    if 'username' in session:
        username = session['username']
        user_data = db_users.find_one({'fullname': username})
        if user_data:
            random_patent = db.data.aggregate([{'$sample': {'size': 1}}]).next()
            patent_detail_link = f"http://127.0.0.1:5000/detail/{random_patent['ID']}"
            email_content = f"""
            Bonjour {user_data['fullname']},

            Voici les informations d'un brevet aléatoire :

            Titre : {random_patent['title']}
            ID : {random_patent['ID']}
            {'Inventeurs : ' + ', '.join(random_patent['inventors']) if 'inventors' in random_patent else ''}
            {'Date de publication : ' + random_patent['publication_date'] if 'publication_date' in random_patent else ''}
            {'Pays : ' + random_patent['country'] if 'country' in random_patent else ''}
            {'Assignataires actuels : ' + ', '.join(random_patent['current_assignees']) if 'current_assignees' in random_patent else ''}
            {'Date de priorité : ' + random_patent['priority_date'] if 'priority_date' in random_patent else ''}
            {'Langue : ' + random_patent['other_language'] if 'other_language' in random_patent else ''}

            Vous pouvez consulter ce brevet en détail sur notre site : {patent_detail_link}.

            Cordialement,
            Votre équipe AGROPA
            """

            user_email = user_data['email']

            send_email(user_email, "Nouvelle alerte de brevet", email_content)

            return jsonify({'message': 'L\'e-mail a été envoyé avec succès'})
        else:
            return jsonify({'error': 'Informations utilisateur non disponibles'}), 400
    else:
        return jsonify({'error': 'Utilisateur non connecté'}), 401


def send_email(recipient, subject, body):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, message.as_string())

if __name__ == '__main__':
    app.run(debug=True)
