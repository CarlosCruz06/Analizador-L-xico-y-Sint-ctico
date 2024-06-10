from flask import Flask, request, jsonify, render_template
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Lista de palabras reservadas
reserved = {
    'package': 'PACKAGE',
    'import': 'IMPORT',
    'func': 'FUNC',
    'main': 'MAIN',
    'ftm': 'FTM',
    'fmt': 'FMT',
    'Println': 'PRINTLN'
}

# Lista de tokens
tokens = [
    'ID',          # Identificadores
    'STRING',      # Cadenas de texto
    'LPAREN',      # (
    'RPAREN',      # )
    'LBRACE',      # {
    'RBRACE',      # }
    'DOT',         # .
    'SEMICOLON',   # ;
] + list(reserved.values())

# Definición de los tokens con expresiones regulares
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_DOT = r'\.'
t_SEMICOLON = r';'
t_STRING = r'\".*?\"'

# Ignorar espacios en blanco y tabulaciones
t_ignore = ' \t'

# Regla para los identificadores y palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Verificar si es una palabra reservada
    if t.type == 'ID':
        print(f"Error léxico: '{t.value}' no es una palabra reservada válida.")
        t.lexer.skip(1)
    return t

# Regla para el manejo de nuevas líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Regla para errores
def t_error(t):
    print(f"Error léxico: carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

# Función para contar tokens y estructurar los resultados léxicos
def analizar_lexico(data):
    lexer.lineno = 1  # Reiniciar la cuenta de líneas
    lexer.input(data)
    tokens_contados = {
        'PACKAGE': 0,
        'IMPORT': 0,
        'FUNC': 0,
        'MAIN': 0,
        'FTM': 0,
        'FMT': 0,
        'PRINTLN': 0,
        'ID': 0,
        'STRING': 0,
        'LPAREN': 0,
        'RPAREN': 0,
        'LBRACE': 0,
        'RBRACE': 0,
        'DOT': 0,
        'SEMICOLON': 0,
    }
    
    analisis_lexico = []
    errors = []

    while True:
        tok = lexer.token()
        if not tok:
            break
        if tok.type == 'ID':
            errors.append(f"Error léxico en la línea {tok.lineno}: '{tok.value}' no es una palabra reservada válida.")
            continue
        tokens_contados[tok.type] += 1
        analisis_lexico.append({
            'line': tok.lineno,
            'token': tok.value,
            'type': tok.type
        })
    
    return tokens_contados, analisis_lexico, errors

# Definir la jerarquía de precedencia y asociatividad de los operadores
precedence = ()

# Definir la gramática
def p_program(p):
    '''program : package_decl import_decl func_decl'''

def p_package_decl(p):
    '''package_decl : PACKAGE MAIN'''

def p_import_decl(p):
    '''import_decl : IMPORT STRING'''

def p_func_decl(p):
    '''func_decl : FUNC MAIN LPAREN RPAREN LBRACE stmt RBRACE'''

def p_stmt(p):
    '''stmt : FMT DOT PRINTLN LPAREN STRING RPAREN'''

# Error rule for syntax errors
def p_error(p):
    print("Error en el análisis sintáctico!")

# Build the parser
parser = yacc.yacc()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    code = request.json.get('code')
    tokens_contados, analisis_lexico, errors = analizar_lexico(code)
    
    if errors:
        return jsonify({
            'lexical_errors': errors,
            'syntactic_analysis': 'La estructura es incorrecta.'
        })

    try:
        parser.parse(code)
        syntactic_analysis = 'El análisis sintáctico es correcto.'
    except:
        syntactic_analysis = 'Error en el análisis sintáctico.'

    return jsonify({
        'lexical_analysis': analisis_lexico,
        'syntactic_analysis': syntactic_analysis
    })

if __name__ == '__main__':
    app.run(debug=True)
