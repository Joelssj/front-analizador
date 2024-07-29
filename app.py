from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import requests
from lexer import analyze_lexical
from parser import analyze_syntactic
from semantic import analyze_semantic

# Obtener la ruta del directorio actual
current_directory = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=current_directory)
app.secret_key = 'your_secret_key'

# Configuración de conexión
db_config = {
    "host": "database-2.cwelf0i66mpp.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "93044699",
    "database": "registro"
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ""
    codigo = ""
    resultados_lexicos = []
    errores_de_sintaxis = ""
    errores_semanticos = ""
    total_resultados = {token: 0 for token in ['KEYWORD', 'IDENTIFIER', 'OPERATOR', 'SYMBOL', 'NUMERIC_CONSTANT', 'STRING_CONSTANT', 'COMMENT']}
    
    if request.method == 'POST':
        dbname = request.form['dbname']
        host = request.form['host']
        user = request.form['user']
        password = request.form['password']
        
        # Datos para la conexión
        data = {
            "host": host,
            "user": user,
            "password": password,
            "database": dbname
        }
        
        # URL para conectar a la base de datos
        url = "http://54.145.236.15:3011/aurora/conectar"
        
        # Realizar la solicitud POST
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # Esto arrojará una excepción si la solicitud falló
            mensaje = 'Conexión realizada con éxito'
            return redirect(url_for('home', mensaje=mensaje))
        except requests.exceptions.RequestException as e:
            mensaje = f'Error al conectar a la base de datos: {e}'
    
    return render_template('index.html', mensaje=mensaje, codigo=codigo, lexicos=resultados_lexicos, total=total_resultados, errores_de_sintaxis=errores_de_sintaxis, errores_semanticos=errores_semanticos)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    codigo = ""
    resultados_lexicos = []
    errores_de_sintaxis = ""
    errores_semanticos = ""
    total_resultados = {token: 0 for token in ['KEYWORD', 'IDENTIFIER', 'OPERATOR', 'SYMBOL', 'NUMERIC_CONSTANT', 'STRING_CONSTANT', 'COMMENT']}
    
    if request.method == 'POST':
        codigo = request.form['code']
        resultados_lexicos, total_resultados = analyze_lexical(codigo)
        errores_de_sintaxis = analyze_syntactic(codigo)
        errores_semanticos = analyze_semantic(codigo)

    mensaje = request.args.get('mensaje', '')

    return render_template('index.html', codigo=codigo, lexicos=resultados_lexicos, total=total_resultados, errores_de_sintaxis=errores_de_sintaxis, errores_semanticos=errores_semanticos, mensaje=mensaje)

@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json()
    codigo = data.get('query')

    # Validar el código SQL
    resultados_lexicos, total_resultados = analyze_lexical(codigo)
    errores_de_sintaxis = analyze_syntactic(codigo)
    errores_semanticos = analyze_semantic(codigo)

    # Mostrar resultados de análisis en la interfaz
    return jsonify({
        "lexicos": resultados_lexicos,
        "total": total_resultados,
        "errores_de_sintaxis": errores_de_sintaxis,
        "errores_semanticos": errores_semanticos
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
