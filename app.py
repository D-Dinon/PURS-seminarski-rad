from flask import Flask, request, session, redirect, url_for, render_template, jsonify
from flask_cors import CORS
import sqlite3
import threading
import serial

app = Flask(__name__)
CORS(app)

temp_list = []

app.secret_key = '_5#y2L"F4Q8z-n-xec]/'

def create_db():
    conn = sqlite3.connect('ventilator.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS VentilatorLog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datum TEXT NOT NULL,
        vrijeme TEXT NOT NULL,
        temperatura REAL NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

create_db()

temperature = None

def read_from_serial():
    global temperature
    ser = serial.Serial('COM6', 9600)
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(f"Pročitano sa serijskog porta: {line}")
            if "Temperatura:" in line:
                temperature_str = line.split(': ')[1].split(' ')[0]
                try:
                    temperature = float(temperature_str)
                    print(f"Temperatura: {temperature}")
                except ValueError:
                    print("Error converting temperature to float")

serial_thread = threading.Thread(target=read_from_serial)
serial_thread.daemon = True
serial_thread.start()


@app.before_request
def before_request_func():
    if request.path == '/login':
        return
    if session.get('username') is None:
        return redirect(url_for('login'))




@app.get('/login')
def login():
    response = render_template('login.html')
    return response, 200


@app.get('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('login'))


@app.post('/login')
def provjera():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'PURS' and password == '1234':
        session['username'] = username
        return redirect(url_for('index'))
    else:
        session['poruka'] = 'Uneseni su pogrešni podatci'
        return redirect(url_for('login'))

@app.route('/')
def index():
    conn = sqlite3.connect('ventilator.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM VentilatorLog')
    entries = cursor.fetchall()
    conn.close()
    return render_template('index.html', entries=entries)

@app.route('/add_entry', methods=['POST'])
def add_entry():
    datum = request.form['datum']
    vrijeme = request.form['vrijeme']
    temperatura = request.form['temperatura']
    
    conn = sqlite3.connect('ventilator.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO VentilatorLog (datum, vrijeme, temperatura) VALUES (?, ?, ?)', (datum, vrijeme, temperatura))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    conn = sqlite3.connect('ventilator.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM VentilatorLog WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/get_temperature')
def get_temperature():
    global temperature
    return jsonify({'temperature': temperature})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)