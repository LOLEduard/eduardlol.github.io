from flask import Flask, render_template, redirect, request, session, url_for, jsonify
import json
import uuid
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with a real secret key in production

# Path to the keys file
keys_file_path = 'keys.json'

# Predefined owner key
OWNER_KEY = 'your_owner_key'  # Replace this with your actual owner key

# Load or initialize keys
if os.path.exists(keys_file_path) and os.path.getsize(keys_file_path) > 0:
    with open(keys_file_path, 'r') as file:
        keys = json.load(file)
else:
    keys = {}

# Save keys
def save_keys():
    with open(keys_file_path, 'w') as file:
        json.dump(keys, file)

# Generate a key for a given IP address
def generate_key(ip):
    key = str(uuid.uuid4())
    expiration = datetime.now() + timedelta(hours=24)
    keys[ip] = {'key': key, 'expiration': expiration.isoformat(), 'ip': ip, 'created_at': datetime.now().isoformat()}
    save_keys()
    return key

# Get the client's IP address
def get_client_ip():
    if 'X-Forwarded-For' in request.headers:
        # The X-Forwarded-For header can contain a list of IPs, take the first one
        ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    elif 'X-Real-IP' in request.headers:
        ip = request.headers['X-Real-IP']
    else:
        ip = request.remote_addr
    return ip

# Authentication check
def check_auth():
    return session.get('authenticated')

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/step/<int:step>')
def step(step):
    ip = get_client_ip()
    if step == 1:
        return render_template('step.html', step=step)
    elif 1 < step <= 3:
        # Simulate ad interaction
        return redirect(url_for('ad_interaction', step=step))
    elif step == 4:
        if ip in keys and datetime.fromisoformat(keys[ip]['expiration']) > datetime.now():
            key = keys[ip]['key']
        else:
            key = generate_key(ip)
        return render_template('complete.html', key=key)
    else:
        return redirect(url_for('index'))

@app.route('/ad/<int:step>')
def ad_interaction(step):
    # Simulate an ad interaction
    return redirect(url_for('step', step=step+1))

@app.route('/api/verify_key', methods=['POST'])
def verify_key():
    data = request.json
    key = data.get('key')
    ip = get_client_ip()
    if ip in keys and keys[ip]['key'] == key and datetime.fromisoformat(keys[ip]['expiration']) > datetime.now():
        return jsonify({"status": "valid"})
    return jsonify({"status": "invalid"}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['key'] == OWNER_KEY:  # Check the entered key against the owner key
            session['authenticated'] = True  # Set session to authenticated
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('dashboard.html', keys=keys)

@app.route('/delete_key/<ip>', methods=['POST'])
def delete_key(ip):
    if not check_auth():
        return redirect(url_for('login'))
    if ip in keys:
        del keys[ip]
        save_keys()
    return redirect(url_for('dashboard'))

@app.route('/edit_key/<ip>', methods=['GET', 'POST'])
def edit_key(ip):
    if not check_auth():
        return redirect(url_for('login'))
    if request.method == 'POST':
        if request.form['owner_key'] == OWNER_KEY:  # Check owner key
            new_key = request.form['key']
            new_expiration = request.form['expiration']
            keys[ip]['key'] = new_key
            keys[ip]['expiration'] = new_expiration
            save_keys()
            return redirect(url_for('dashboard'))
        else:
            return "Unauthorized", 403
    return render_template('edit_key.html', ip=ip, key_data=keys[ip])

if __name__ == '__main__':
    app.run(debug=True)
