from datetime import datetime
from flask import Flask, render_template, session, request, redirect, url_for, flash
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

def load_carros():
    with open('static/carros.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def es_fecha_disponible(date, carro, reservas):
    fecha_reserva = datetime.strptime(date, '%d-%m-%Y')
    for reserva in reservas:
        fecha_reserva_existente = datetime.strptime(reserva['date'], '%d-%m-%Y')
        if reserva['carro'] == carro and fecha_reserva == fecha_reserva_existente:
            return False
    return True

def es_fecha_en_rango(fecha, inicio, fin):
    fecha_reserva = datetime.strptime(fecha, '%d-%m-%Y')
    fecha_inicio = datetime.strptime(inicio, '%d-%m-%Y')
    fecha_fin = datetime.strptime(fin, '%d-%m-%Y')
    return fecha_inicio <= fecha_reserva <= fecha_fin

@app.route('/')
def index():
    carros = load_carros()
    return render_template('carros.html', carros=carros)

@app.route('/lista')
def lista():
    carros = load_carros()
    return render_template('carros.html', carros=carros)

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    carros = load_carros()
    
    if 'form' not in session:
        session['form'] = []
        
    list = session['form']
    
    if request.method == "POST":
        session['first_name'] = request.form['first-name']
        session['last_name'] = request.form['last-name']
        session['fecha'] = request.form['date']
        session['carro'] = request.form['carro']

        # Convertir la fecha de string a datetime
        fecha_reserva = datetime.strptime(session['fecha'], '%d-%m-%Y')
        fecha_actual = datetime.now()

        # Comparar si la fecha de reserva es anterior a la fecha actual
        if fecha_reserva < fecha_actual:
            flash('La fecha de reserva no puede ser anterior a la fecha actual.', 'error')
            return redirect(url_for('formulario'))
        
        # Verificar si la fecha y el carro están disponibles
        if not es_fecha_disponible(session['fecha'], session['carro'], session['form']):
            flash('El carro ya está reservado para esa fecha.', 'error')
            return redirect(url_for('formulario'))
        
        list.append({'name': session['first_name'], 'lastName': session['last_name'], 'date': session['fecha'], 'carro': session['carro']})
        session['form'] = list

        # Comprobar si la fecha está en el rango para la tabla avanzada
        if es_fecha_en_rango(session['fecha'], '04-12-2023', '08-12-2023'):
            pass
        
        next = request.args.get('next', None)
        if next:
            return redirect(next)
        return redirect(url_for('reservas'))
    return render_template('carros2.html', carros=carros)

@app.route('/reservas', methods=['GET', 'POST'])
def reservas():
    carros = load_carros()
    return render_template('carros3.html', carros=carros, Form=session['form'])

# Suponiendo que esta es la variable donde almacenas los datos de la sesión
datos_de_sesion = []

# Endpoint para borrar datos
@app.route('/borrar_datos', methods=['POST'])
def borrar_datos():
    # Almacenar los datos antes de borrarlos
    global datos_de_sesion
    datos_de_sesion = session.get('form', []).copy()

    # Borrar los datos de la sesión
    session['form'] = []
    return redirect(url_for('reservas'))

# Endpoint para recuperar datos
@app.route('/recuperar_datos', methods=['POST'])
def recuperar_datos():
    # Recuperar los datos almacenados
    global datos_de_sesion
    session['form'] = datos_de_sesion

    # Limpia la variable temporal para evitar recuperaciones futuras no deseadas
    datos_de_sesion = []
    return redirect(url_for('reservas'))


if __name__ == '__main__':
    app.run(debug=True)