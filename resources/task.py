import re

from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from con_sql_alchemy import bd
from models.task import TaskModel
from models.user import UserModel

ESTADOS = {"Pendente", "Em curso", "Concluída"}
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def payload_json():
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else None


class UserRegister(Resource):
    def post(self):
        dados = payload_json()
        if not dados:
            return {"mensagem": "O corpo do pedido deve ser um objeto JSON."}, 400
        username = dados.get("username")
        email = dados.get("email")
        password = dados.get("password")
        if not all(isinstance(v, str) and v.strip() for v in (username, email, password)):
            return {"mensagem": "username, email e password são obrigatórios."}, 400
        if not EMAIL_RE.match(email.strip()):
            return {"mensagem": "O email indicado não é válido."}, 400
        if len(password) < 8:
            return {"mensagem": "A password deve ter pelo menos 8 caracteres."}, 400
        if UserModel.find_by_email(email):
            return {"mensagem": "Já existe um utilizador com este email."}, 400

        user = UserModel(username=username, email=email, password=password)
        try:
            bd.session.add(user)
            bd.session.commit()
        except IntegrityError:
            bd.session.rollback()
            return {"mensagem": "Já existe um utilizador com este email."}, 400
        return {"mensagem": "Utilizador registado com sucesso.", "utilizador": user.json()}, 201


class UserLogin(Resource):
    def post(self):
        dados = payload_json()
        if not dados or not isinstance(dados.get("email"), str) or not isinstance(dados.get("password"), str):
            return {"mensagem": "email e password são obrigatórios."}, 400
        user = UserModel.find_by_email(dados["email"])
        if not user or not user.verifica_password(dados["password"]):
            return {"mensagem": "Email ou password incorretos."}, 401
        token = create_access_token(
            identity=str(user.id),
            additional_claims={"tipo": user.tipo},
        )
        return {"access_token": token, "utilizador": user.json()}, 200


class Tasks(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()
        query = TaskModel.query
        if claims.get("tipo") != "admin":
            query = query.filter_by(utilizador_id=int(get_jwt_identity()))
        return {"tarefas": [t.json() for t in query.order_by(TaskModel.id).all()]}, 200

    @jwt_required()
    def post(self):
        dados = payload_json()
        if not dados:
            return {"mensagem": "O corpo do pedido deve ser um objeto JSON."}, 400
        titulo = dados.get("titulo")
        descricao = dados.get("descricao", "")
        estado = dados.get("estado", "Pendente")
        if not isinstance(titulo, str) or not titulo.strip():
            return {"mensagem": "O título é obrigatório."}, 400
        if not isinstance(descricao, str):
            return {"mensagem": "A descrição deve ser texto."}, 400
        if estado not in ESTADOS:
            return {"mensagem": "Estado inválido. Use Pendente, Em curso ou Concluída."}, 400
        tarefa = TaskModel(
            titulo=titulo.strip(), descricao=descricao.strip(), estado=estado,
            utilizador_id=int(get_jwt_identity()),
        )
        bd.session.add(tarefa)
        bd.session.commit()
        return tarefa.json(), 201


class Task(Resource):
    @jwt_required()
    def get(self, task_id):
        tarefa = TaskModel.query.get(task_id)
        if tarefa is None:
            return {"mensagem": "Tarefa não encontrada."}, 404
        if get_jwt().get("tipo") != "admin" and tarefa.utilizador_id != int(get_jwt_identity()):
            return {"mensagem": "Não tem permissão para consultar esta tarefa."}, 403
        return tarefa.json(), 200

    @jwt_required()
    def put(self, task_id):
        tarefa = TaskModel.query.get(task_id)
        if tarefa is None:
            return {"mensagem": "Tarefa não encontrada."}, 404
        if get_jwt().get("tipo") != "admin" and tarefa.utilizador_id != int(get_jwt_identity()):
            return {"mensagem": "Não tem permissão para alterar esta tarefa."}, 403
        dados = payload_json()
        if not dados:
            return {"mensagem": "O corpo do pedido deve ser um objeto JSON."}, 400
        if "utilizador_id" in dados:
            return {"mensagem": "Não é permitido alterar o proprietário da tarefa."}, 400
        titulo = dados.get("titulo", tarefa.titulo)
        descricao = dados.get("descricao", tarefa.descricao)
        estado = dados.get("estado", tarefa.estado)
        if not isinstance(titulo, str) or not titulo.strip():
            return {"mensagem": "O título deve ser texto não vazio."}, 400
        if not isinstance(descricao, str):
            return {"mensagem": "A descrição deve ser texto."}, 400
        if estado not in ESTADOS:
            return {"mensagem": "Estado inválido. Use Pendente, Em curso ou Concluída."}, 400
        tarefa.titulo = titulo.strip()
        tarefa.descricao = descricao.strip()
        tarefa.estado = estado
        bd.session.commit()
        return tarefa.json(), 200

    @jwt_required()
    def delete(self, task_id):
        tarefa = TaskModel.query.get(task_id)
        if tarefa is None:
            return {"mensagem": "Tarefa não encontrada."}, 404
        if get_jwt().get("tipo") != "admin" and tarefa.utilizador_id != int(get_jwt_identity()):
            return {"mensagem": "Não tem permissão para eliminar esta tarefa."}, 403
        bd.session.delete(tarefa)
        bd.session.commit()
        return {"mensagem": "Tarefa eliminada com sucesso."}, 200
