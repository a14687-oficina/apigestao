# API de Gestão de Tarefas

API REST em Flask para registo/autenticação de utilizadores e gestão de tarefas com SQLite, SQLAlchemy e JWT. O primeiro arranque cria as tabelas e um administrador caso ainda não exista.

## Instalação e execução

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

A API fica disponível em `http://localhost:5000`. Por omissão, a base de dados `tarefas.db` é criada na pasta `instance/` pelo Flask-SQLAlchemy.

## Administrador inicial

Para facilitar a avaliação, por omissão é criado:

- Email: `admin@tarefas.local`
- Password: `Admin123!`

É possível configurar antes de iniciar a aplicação: `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_USERNAME` e `JWT_SECRET_KEY`. Em qualquer ambiente real, defina uma chave JWT e uma password de administrador fortes através de variáveis de ambiente. A password é guardada apenas como hash. O endpoint de registo não aceita nem define o campo `tipo` enviado pelo cliente.

## Endpoints

| Método | Endpoint | Acesso | Descrição |
|---|---|---|---|
| POST | `/registo` | Público | Regista utilizador comum |
| POST | `/login` | Público | Devolve token JWT |
| POST | `/logout` | JWT | Revoga o token em memória |
| POST | `/tarefas` | JWT | Cria tarefa para o utilizador autenticado |
| GET | `/tarefas` | JWT | Lista tarefas próprias; admin lista todas |
| GET | `/tarefas/<id>` | JWT | Consulta uma tarefa |
| PUT | `/tarefas/<id>` | JWT | Atualiza uma tarefa |
| DELETE | `/tarefas/<id>` | JWT | Elimina uma tarefa |

Os utilizadores comuns recebem `403` ao tentar consultar, alterar ou apagar tarefas de outras pessoas. Os estados aceites são `Pendente`, `Em curso` e `Concluída`.

## Exemplos

Registo (JSON):

```json
{"username":"Ana","email":"ana@example.com","password":"UmaPasswordSegura1"}
```

Login (JSON):

```json
{"email":"ana@example.com","password":"UmaPasswordSegura1"}
```

Enviar o token devolvido nos restantes pedidos através do cabeçalho:

```text
Authorization: Bearer <access_token>
```

Criar tarefa (JSON):

```json
{"titulo":"Preparar relatório","descricao":"Rever os dados do mês","estado":"Pendente"}
```

Atualizar tarefa: enviar em `PUT /tarefas/<id>` os campos a alterar (pode ser apenas um subconjunto dos três campos). O proprietário não pode ser alterado pelo pedido.

## Estrutura

```text
3I-main/
├── app.py
├── con_sql_alchemy.py
├── blocklist.py
├── models/
│   ├── user.py
│   └── task.py
├── resources/
│   └── task.py
├── requirements.txt
└── instance/             # criada automaticamente; contém a base de dados local
```
