# FastAPI - Framework Web Moderno

## Visão Geral

FastAPI é um framework web moderno e rápido para construção de APIs com Python 3.8+ baseado em type hints padrão do Python.

## Características Principais

### 🚀 Alta Performance
- Uma das frameworks Python mais rápidas disponíveis
- Comparável ao NodeJS e Go
- Baseado em Starlette e Pydantic

### 🛠️ Fácil de Usar
- Redução de ~200-300% no tempo de desenvolvimento
- Menos bugs (redução de ~40% de erros humanos)
- Suporte inteligente do editor com autocompletar

### 🎯 Pronto para Produção
- Documentação automática interativa (Swagger UI + ReDoc)
- Baseado em padrões abertos (OpenAPI + JSON Schema)
- Segurança integrada (OAuth2, JWT)

### 📝 Baseado em Padrões
- OpenAPI para documentação de APIs
- JSON Schema para validação de dados
- Type hints do Python para validação automática

## Instalação

```bash
pip install "fastapi[standard]"
```

O grupo `[standard]` inclui:
- `uvicorn` - servidor ASGI
- `httpx` - cliente HTTP para testes
- `jinja2` - templates
- `python-multipart` - upload de arquivos

## Exemplo Básico

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

## Executando

```bash
fastapi dev main.py
```

## Documentação Automática

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Recursos Avançados

### Validação de Dados
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None

@app.post("/items/")
def create_item(item: Item):
    return item
```

### Dependências
```python
from fastapi import Depends

def get_current_user(token: str = Depends(oauth2_scheme)):
    return fake_decode_token(token)

@app.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### Segurança
```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}
```

## Uso no Video Genius

O Video Genius utiliza FastAPI para:

- **API RESTful** para processamento de vídeos
- **Validação automática** de dados de entrada
- **Documentação interativa** para desenvolvedores
- **Autenticação e autorização** via JWT
- **Streaming de vídeo** com responses assíncronas

## Performance

- **Benchmarks**: Um dos frameworks Python mais rápidos
- **Escalabilidade**: Suporte nativo a async/await
- **Otimizações**: Uvicorn com uvloop para máxima performance

## Comparação com Outros Frameworks

| Framework | Performance | Facilidade | Documentação |
|-----------|-------------|------------|--------------|
| FastAPI   | ⭐⭐⭐⭐⭐    | ⭐⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐     |
| Flask     | ⭐⭐⭐       | ⭐⭐⭐⭐     | ⭐⭐⭐⭐       |
| Django    | ⭐⭐⭐⭐      | ⭐⭐⭐      | ⭐⭐⭐⭐⭐     |
| Bottle    | ⭐⭐⭐       | ⭐⭐⭐⭐⭐   | ⭐⭐⭐        |

## Links Úteis

- **Documentação Oficial**: https://fastapi.tiangolo.com/
- **Repositório GitHub**: https://github.com/tiangolo/fastapi
- **Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **Exemplos Avançados**: https://fastapi.tiangolo.com/advanced/

## Dicas para Video Genius

1. Use `async def` para operações I/O bound (upload/download de vídeos)
2. Configure CORS adequadamente para aplicações web
3. Use Pydantic models para validação de metadados de vídeo
4. Implemente paginação para listas grandes de vídeos
5. Use dependências para injeção de serviços (BigQuery, Cloud Storage)

---

*Documentação criada para o projeto Video Genius - Outubro 2025*