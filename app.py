from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Produto, Entrada, Saida

app = Flask(__name__)
CORS(app)  # Permitir requisições do Streamlit

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///estoque.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    if request.method == "GET":
        # Listar os produtos
        produtos = Produto.query.all()
        return jsonify(
            [{"id": p.id, "nome": p.nome, "descricao": p.descricao, "quantidade_estoque": p.quantidade_estoque, "preco": p.preco} for p in produtos]
        )
    
    elif request.method == "POST":
        # Criar um novo produto
        data = request.json
        novo_produto = Produto(nome=data["nome"], descricao=data["descricao"], preco=data["preco"])
        
        db.session.add(novo_produto)
        db.session.commit()
        return jsonify({"message": "Produto criado com sucesso!"})

@app.route("/produto/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    produto = Produto.query.get(id)
    if not produto:
        return jsonify({"error": "Produto não encontrado!"}), 404
    data = request.json
    produto.nome = data["nome"]
    
    
    db.session.commit()
    return jsonify({"message": "Produto atualizado com sucesso!"})

@app.route("/produto/<int:id>", methods=["DELETE"])
def deletar_produto(id):
    produto = Produto.query.get(id)
    if not produto:
        return jsonify({"error": "Produto não encontrado!"}), 404
    db.session.delete(produto)
    db.session.commit()
    return jsonify({"message": "Produto deletado com sucesso!"})

# Rota para registrar e listar entrada de produto
@app.route('/entradas', methods=['GET','POST'])
def entrada():
    if request.method == "GET":
        entradas = Entrada.query.all()
        resultado = [{
            "id": e.id,
            "produto": e.produto.nome,
            "quantidade": e.quantidade,
            "data": e.data.strftime('%Y-%m-%d %H:%M:%S')
        } for e in entradas]
    
        return jsonify(resultado)
    elif request.method == "POST":    
        data = request.get_json()
        produto_id = data.get('produto_id')
        quantidade = data.get('quantidade')

        produto = Produto.query.get(produto_id)
        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 404
        
        produto.quantidade_estoque += quantidade  # Atualiza o estoque
        
        entrada = Entrada(produto_id=produto_id, quantidade=quantidade)
        

        db.session.add(entrada)
        db.session.commit()

    return jsonify({"mensagem": f"Entrada de {quantidade} unidades do produto {produto.nome} registrada com sucesso"}), 201

# Rota para registrar e listar saída de produto
@app.route('/saidas', methods=['GET','POST'])
def saida():
    if request.method == "GET":
        saidas = Saida.query.all()
        resultado = [{
            "id": s.id,
            "produto": s.produto.nome,
            "quantidade": s.quantidade,
            "data": s.data.strftime('%Y-%m-%d %H:%M:%S')
        } for s in saidas]
        
        return jsonify(resultado)
    elif request.method == "POST":
        data = request.get_json()
        produto_id = data.get('produto_id')
        quantidade = data.get('quantidade')

        produto = Produto.query.get(produto_id)
        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 404
        
        

        if produto.quantidade_estoque < quantidade:
            return jsonify({"erro": "Estoque insuficiente"}), 400
        
        saida = Saida(produto_id=produto_id, quantidade=quantidade)
        produto.quantidade_estoque -= quantidade  # Atualiza o estoque

        db.session.add(saida)
        db.session.commit()

    return jsonify({"mensagem": f"Saída de {quantidade} unidades do produto {produto.nome} registrada com sucesso"}), 201

if __name__ == "__main__":
    app.run(debug=True)