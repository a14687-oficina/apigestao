from werkzeug.security import check_password_hash, generate_password_hash

from con_sql_alchemy import bd


class UserModel(bd.Model):
    __tablename__ = "utilizadores"

    id = bd.Column(bd.Integer, primary_key=True)
    username = bd.Column(bd.String(80), nullable=False)
    email = bd.Column(bd.String(255), unique=True, nullable=False, index=True)
    password_hash = bd.Column(bd.String(255), nullable=False)
    tipo = bd.Column(bd.String(20), nullable=False, default="utilizador")
    tarefas = bd.relationship(
        "TaskModel", back_populates="utilizador", cascade="all, delete-orphan"
    )

    def __init__(self, username, email, password, tipo="utilizador"):
        self.username = username.strip()
        self.email = email.strip().lower()
        self.set_password(password)
        self.tipo = tipo

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verifica_password(self, password):
        return check_password_hash(self.password_hash, password)

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "tipo": self.tipo,
        }

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email.strip().lower()).first()

    @classmethod
    def find_by_id(cls, user_id):
        return cls.query.get(user_id)

    def save(self):
        bd.session.add(self)
        bd.session.commit()

    def delete(self):
        bd.session.delete(self)
        bd.session.commit()
