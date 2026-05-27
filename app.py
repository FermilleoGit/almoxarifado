from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime
import json
import os
import secrets
import html

app = Flask(__name__, static_folder='static')

# Configurações de segurança
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # 1MB

DADOS_FILE = 'almoxarifado.json'
SENHA_ADMIN = os.environ.get('SENHA_ADMIN', 'mudar123')  # Configure no Railway!

def sanitizar(texto):
    if not texto:
        return texto
    texto = ''.join(char for char in texto if ord(char) >= 32 or char in '\n\r')
    return html.escape(texto)[:200]

def carregar_dados():
    if os.path.exists(DADOS_FILE):
        with open(DADOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_dados(produtos):
    with open(DADOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    return jsonify(carregar_dados())

@app.route('/api/produtos', methods=['POST'])
def adicionar_produto():
    dados = request.json
    nome = sanitizar(dados.get('nome', '').strip())
    if not nome:
        return jsonify({'erro': 'Nome do produto é obrigatório'}), 400
    if len(nome) > 200:
        return jsonify({'erro': 'Nome muito longo (máx 200 caracteres)'}), 400

    produtos = carregar_dados()
    produto = {
        'id': int(datetime.now().timestamp() * 1000),
        'nome': nome,
        'disponivel': True,
        'data_retirada': None,
        'quem_retirou': ''
    }
    produtos.append(produto)
    salvar_dados(produtos)
    return jsonify(produto), 201

@app.route('/api/produtos/<int:produto_id>/retirar', methods=['POST'])
def retirar_produto(produto_id):
    dados = request.json
    senha = dados.get('senha', '')
    if senha != SENHA_ADMIN:
        return jsonify({'erro': 'Senha incorreta'}), 401
    
    quem = sanitizar(dados.get('quem', '').strip())
    if not quem:
        return jsonify({'erro': 'Informe quem está retirando'}), 400

    produtos = carregar_dados()
    for p in produtos:
        if p['id'] == produto_id:
            p['disponivel'] = False
            p['data_retirada'] = datetime.now().strftime('%d/%m/%Y %H:%M')
            p['quem_retirou'] = quem
            salvar_dados(produtos)
            return jsonify(p)

    return jsonify({'erro': 'Produto não encontrado'}), 404

@app.route('/api/produtos/<int:produto_id>/devolver', methods=['POST'])
def devolver_produto(produto_id):
    produtos = carregar_dados()
    for p in produtos:
        if p['id'] == produto_id:
            p['disponivel'] = True
            p['data_retirada'] = None
            p['quem_retirou'] = ''
            salvar_dados(produtos)
            return jsonify(p)
    return jsonify({'erro': 'Produto não encontrado'}), 404

@app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
def remover_produto(produto_id):
    produtos = carregar_dados()
    nova_lista = [p for p in produtos if p['id'] != produto_id]
    if len(nova_lista) == len(produtos):
        return jsonify({'erro': 'Produto não encontrado'}), 404
    salvar_dados(nova_lista)
    return jsonify({'ok': True})

@app.route('/api/relatorio', methods=['GET'])
def relatorio():
    produtos = carregar_dados()
    if not produtos:
        return jsonify({'erro': 'Nenhum produto cadastrado'}), 400

    disponiveis = [p for p in produtos if p['permitido']]
    indisponiveis = [p for p in produtos if not p['permitido']]

    linhas = [
        '=== RELATÓRIO DO ALMOXARIFADO ===',
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Total de produtos: {len(produtos)}",
        '',
        f"✅ PRODUTOS DISPONÍVEIS ({len(disponiveis)}):",
    ]
    for p in disponiveis:
        linhas.append(f"  - {p['nome']}")

    linhas += ['', f"❌ PRODUTOS INDISPONÍVEIS ({len(indisponiveis)}):"]
    for p in indisponiveis:
        linhas.append(f"  - {p['nome']}")
        linhas.append(f"    Retirado por: {p['quem_retirou']}")
        linhas.append(f"    Data: {p['data_retirada']}")

    return jsonify({'relatorio': '\n'.join(linhas)})

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    # Em desenvolvimento local apenas
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Em produção (Railway) - apenas log
    print(f"SERVIDOR INICIADO EM MODO PRODUÇÃO")
    print(f"SECRET_KEY configurada: {'✓' if os.environ.get('SECRET_KEY') else '⚠️ NÃO CONFIGURADA!'}")
    print(f"SENHA_ADMIN configurada: {'✓' if os.environ.get('SENHA_ADMIN') else '⚠️ USANDO PADRÃO!'}")