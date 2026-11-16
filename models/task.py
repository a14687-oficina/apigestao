from con_sql_alchemy import bd


class TaskModel(bd.Model):
    __tablename__ = "tarefas"

    id = bd.Column(bd.Integer, primary_key=True, autoincrement=True)
    titulo = bd.Column(bd.String(150), nullable=False)
    descricao = bd.Column(bd.Text, nullable=False, default="")
    estado = bd.Column(bd.String(20), nullable=False, default="Pendente")
    utilizador_id = bd.Column(
        bd.Integer, bd.ForeignKey("utilizadores.id"), nullable=False, index=True
    )
    utilizador = bd.relationship("UserModel", back_populates="tarefas")

    def json(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "estado": self.estado,
            "utilizador_id": self.utilizador_id,
        }
