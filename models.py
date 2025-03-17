from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    quantidade_estoque = db.Column(db.Integer, default=0)
    preco = db.Column(db.Float, nullable=False)
    entradas = db.relationship('Entrada', backref='produto', lazy=True)
    saidas = db.relationship('Saida', backref='produto', lazy=True)

    def __repr__(self):
        return f'<Produto {self.nome} - Estoque: {self.quantidade_estoque}>'

class Entrada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Entrada {self.quantidade} de {self.produto.nome} em {self.data}>'

class Saida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Saida {self.quantidade} de {self.produto.nome} em {self.data}>'