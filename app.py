import os
from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager, get_jwt, jwt_required
from flask_restful import Api, Resource

from con_sql_alchemy import bd
from blocklist import BLOCKLIST
from models.task import TaskModel
from models.user import UserModel
from resources.task import Task, Tasks, UserLogin, UserRegister

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///tarefas.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY", "chave-local-para-desenvolvimento-altere-antes-de-publicar"
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

bd.init_app(app)
api = Api(app)
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def verifica_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.revoked_token_loader
def token_revogado(jwt_header, jwt_payload):
    return {"mensagem": "Token revogado. Faça login novamente."}, 401


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        BLOCKLIST.add(get_jwt()["jti"])
        return {"mensagem": "Logout efetuado com sucesso."}, 200


api.add_resource(UserRegister, "/registo")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(Tasks, "/tarefas")
api.add_resource(Task, "/tarefas/<int:task_id>")


def inicializar_base_de_dados():
    bd.create_all()
    email = os.getenv("ADMIN_EMAIL", "admin@tarefas.local").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "Admin123!")
    if UserModel.find_by_email(email) is None:
        admin = UserModel(
            username=os.getenv("ADMIN_USERNAME", "Administrador"),
            email=email,
            password=password,
            tipo="admin",
        )
        bd.session.add(admin)
        bd.session.commit()


if __name__ == "__main__":
    with app.app_context():
        inicializar_base_de_dados()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
