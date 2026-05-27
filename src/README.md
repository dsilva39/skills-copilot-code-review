# API de Atividades da Mergington High School

Uma aplicação FastAPI super simples que permite aos alunos visualizar e se inscrever em atividades extracurriculares.

## Funcionalidades

- Visualizar todas as atividades extracurriculares disponíveis
- Inscrever-se em atividades
- Exibir anuncios ativos de forma dinamica no topo da interface
- Gerenciar anuncios (criar, editar e excluir) para usuarios autenticados

## Como começar

1. Instale as dependências:

   ```
   pip install fastapi uvicorn
   ```

2. Execute a aplicação:

   ```
   python app.py
   ```

3. Abra seu navegador e acesse:
   - Documentação da API: http://localhost:8000/docs
   - Documentação alternativa: http://localhost:8000/redoc

## Endpoints da API

| Método | Endpoint                                                          | Descrição                                                            |
| ------ | ----------------------------------------------------------------- | -------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Obtém todas as atividades com detalhes e número atual de participantes |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Inscreve-se em uma atividade                                         |
| POST   | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Remove um aluno de uma atividade                                  |
| POST   | `/auth/login?username=<usuario>&password=<senha>`                | Autentica professor/gestor                                          |
| GET    | `/auth/check-session?username=<usuario>`                         | Valida sessão por usuário                                            |
| GET    | `/announcements/active`                                           | Lista anuncios ativos para exibicao publica                         |
| GET    | `/announcements?teacher_username=<usuario>`                      | Lista todos os anuncios (requer autenticacao)                       |
| POST   | `/announcements?teacher_username=<usuario>`                      | Cria anuncio (expiracao obrigatoria, inicio opcional)               |
| PUT    | `/announcements/{announcement_id}?teacher_username=<usuario>`    | Atualiza anuncio existente (requer autenticacao)                    |
| DELETE | `/announcements/{announcement_id}?teacher_username=<usuario>`    | Exclui anuncio existente (requer autenticacao)                      |

## Modelo de Dados

A aplicação usa um modelo de dados simples em MongoDB com identificadores significativos:

1. **Atividades** - Usa o nome da atividade como identificador:
   - Descrição
   - Horário
   - Número máximo de participantes permitidos
   - Lista de e-mails dos alunos inscritos

2. **Alunos** - Usa o e-mail como identificador:
   - Nome
   - Série

3. **Anuncios** - Usa identificador UUID como chave:
   - Mensagem do anuncio
   - Data de inicio (opcional)
   - Data de expiracao (obrigatoria)
   - Datas de criacao e atualizacao

Os dados sao persistidos no MongoDB configurado no projeto.
