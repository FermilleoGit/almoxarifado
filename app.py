from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime
import json
import os

app = Flask(__name__, static_folder='static')

DADOS_FILE = 'almoxarifado.json'

def carregar_dados():
    if os.path.exists(DADOS_FILE):
        with open(DADOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_dados(produtos):
    with open(DADOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

# Servir o frontend
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Listar todos os produtos
@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    return jsonify(carregar_dados())

# Adicionar produto
@app.route('/api/produtos', methods=['POST'])
def adicionar_produto():
    dados = request.json
    nome = dados.get('nome', '').strip()
    if not nome:
        return jsonify({'erro': 'Nome do produto é obrigatório'}), 400

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

# Retirar produto
@app.route('/api/produtos/<int:produto_id>/retirar', methods=['POST'])
def retirar_produto(produto_id):
    dados = request.json
    quem = dados.get('quem', '').strip()
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

# Devolver produto
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

# Remover produto
@app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
def remover_produto(produto_id):
    produtos = carregar_dados()
    nova_lista = [p for p in produtos if p['id'] != produto_id]
    if len(nova_lista) == len(produtos):
        return jsonify({'erro': 'Produto não encontrado'}), 404
    salvar_dados(nova_lista)
    return jsonify({'ok': True})

# Relatório em texto
@app.route('/api/relatorio', methods=['GET'])
def relatorio():
    produtos = carregar_dados()
    if not produtos:
        return jsonify({'erro': 'Nenhum produto cadastrado'}), 400

    disponiveis = [p for p in produtos if p['disponivel']]
    indisponiveis = [p for p in produtos if not p['disponivel']]

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
    # host='0.0.0.0' permite acesso pela rede local (celular no mesmo Wi-Fi)
    app.run(host='0.0.0.0', port=5000, debug=True)
