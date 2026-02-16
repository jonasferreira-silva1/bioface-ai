# 📝 Cadastro e Consulta de Pessoas - BioFace AI

Este documento explica como cadastrar pessoas no sistema e verificar se estão cadastradas.

---

## 🆕 Cadastrar uma Nova Pessoa

### Comando

```bash
python scripts/register_face.py --name "Jonas Silva"
```

### Exemplos

```bash
# Cadastrar com nome
python scripts/register_face.py --name "João Silva"

# Cadastrar com nome composto (use aspas)
python scripts/register_face.py --name "Maria Santos"

# Cadastrar sem nome (anônimo)
python scripts/register_face.py
```

### Como Funciona

1. **Execute o comando** no terminal
2. **Uma janela da câmera abrirá**
3. **Posicione-se na frente da câmera**
4. **Aguarde a detecção** (aparecerá um retângulo verde ao redor da face)
5. **Pressione ESPAÇO** para capturar e cadastrar
6. **Pressione ESC** para cancelar

### O Que Acontece

- ✅ Face é detectada
- ✅ Embedding facial é gerado (128 dimensões)
- ✅ Usuário é criado no banco de dados
- ✅ Embedding é salvo associado ao usuário
- ✅ Mensagem de sucesso é exibida

### Saída Esperada

```
============================================================
Cadastro de Nova Face
============================================================
Posicione-se na frente da câmera...
Pressione ESPAÇO para capturar, ESC para cancelar
Gerando embedding...
Criando usuário no banco de dados...
Usuário criado: id=1, name=João Silva
============================================================
Face cadastrada com sucesso!
  Usuario ID: 1
  Nome: João Silva
  Confianca: 50%
============================================================
```

---

## 🔍 Verificar se uma Pessoa Está Cadastrada

### Método 1: Consultar Banco de Dados (SQLite)

#### Abrir o Banco de Dados

```bash
# Windows (PowerShell)
sqlite3 bioface.db

# Linux/Mac
sqlite3 bioface.db
```

#### Consultar Todos os Usuários

```sql
SELECT id, name, created_at, is_active FROM users;
```

**Exemplo de saída:**
```
id | name       | created_at          | is_active
---|------------|---------------------|----------
1  | João Silva | 2026-02-16 13:33:07 | 1
2  | Maria      | 2026-02-16 14:20:15 | 1
3  | NULL       | 2026-02-16 15:10:30 | 1
```

#### Consultar Embeddings de um Usuário

```sql
SELECT 
    fe.id, 
    fe.user_id, 
    u.name, 
    fe.confidence, 
    fe.created_at 
FROM face_embeddings fe
JOIN users u ON fe.user_id = u.id
WHERE u.name = 'João Silva';
```

#### Contar Quantos Embeddings Cada Usuário Tem

```sql
SELECT 
    u.id,
    u.name,
    COUNT(fe.id) as total_embeddings
FROM users u
LEFT JOIN face_embeddings fe ON u.id = fe.user_id
GROUP BY u.id, u.name;
```

#### Sair do SQLite

```sql
.quit
```

---

### Método 2: Script Python de Consulta

Crie um script para consultar o banco:

```python
# scripts/list_users.py
from src.database.repository import DatabaseRepository

db = DatabaseRepository()

print("=" * 60)
print("Usuários Cadastrados")
print("=" * 60)

users = db.get_all_users()

if not users:
    print("Nenhum usuário cadastrado.")
else:
    for user in users:
        embeddings = db.get_user_embeddings(user.id)
        print(f"\nID: {user.id}")
        print(f"  Nome: {user.name or '(Anônimo)'}")
        print(f"  Cadastrado em: {user.created_at}")
        print(f"  Embeddings: {len(embeddings)}")
        print(f"  Ativo: {'Sim' if user.is_active else 'Não'}")

print("\n" + "=" * 60)
```

**Executar:**
```bash
python scripts/list_users.py
```

---

### Método 3: Verificar Durante Execução do Sistema

Quando você executa o sistema principal:

```bash
python main-light.py
```

O sistema **automaticamente identifica** pessoas cadastradas e mostra o nome na tela:

- ✅ **Se identificar**: Mostra "Nome da Pessoa: XX%" na tela
- ❌ **Se não identificar**: Mostra "DESCONHECIDO: XX%" e cria usuário anônimo automaticamente

**Logs no terminal:**
```
Frame 30: 1 face(s) detectada(s)
  -> Face detectada com confiança: 50%
  -> Novo usuário criado: ID 2
```

ou

```
Face identificada: João Silva (ID: 1, conf: 0.85)
```

---

## 📊 Estrutura do Banco de Dados

### Tabela `users`

| Coluna      | Tipo    | Descrição                    |
|-------------|---------|------------------------------|
| id          | INTEGER | ID único do usuário          |
| name        | TEXT    | Nome (pode ser NULL)         |
| created_at  | DATETIME| Data de cadastro             |
| updated_at  | DATETIME| Última atualização           |
| is_active   | BOOLEAN | Se o usuário está ativo      |

### Tabela `face_embeddings`

| Coluna      | Tipo    | Descrição                    |
|-------------|---------|------------------------------|
| id          | INTEGER | ID único do embedding       |
| user_id     | INTEGER | ID do usuário (FK)          |
| embedding   | TEXT    | JSON com array de floats     |
| confidence  | FLOAT   | Confiança da detecção       |
| face_size   | INTEGER | Tamanho da face             |
| created_at  | DATETIME| Data de criação             |

---

## 🔧 Comandos Úteis

### Ver Localização do Banco de Dados

O banco de dados SQLite é criado automaticamente no diretório raiz do projeto:

```
rec-facial/
  └── bioface.db  ← Banco de dados aqui
```

### Backup do Banco de Dados

```bash
# Windows
copy bioface.db bioface_backup.db

# Linux/Mac
cp bioface.db bioface_backup.db
```

### Limpar Banco de Dados (CUIDADO!)

```bash
# Remove o banco (todos os dados serão perdidos)
del bioface.db  # Windows
rm bioface.db   # Linux/Mac
```

O banco será recriado automaticamente na próxima execução.

---

## ❓ Perguntas Frequentes

### Q: Posso cadastrar a mesma pessoa várias vezes?

**R:** Sim! Cada cadastro cria um novo embedding. Isso **melhora a precisão** da identificação, pois o sistema terá mais exemplos da mesma pessoa.

### Q: Quantos embeddings cada pessoa precisa?

**R:** Recomendamos **3-5 embeddings** por pessoa para melhor precisão. Você pode cadastrar a mesma pessoa várias vezes em diferentes ângulos/iluminações.

### Q: O que acontece se não der nome?

**R:** O usuário será criado como **anônimo** (`name = NULL`). O sistema ainda consegue identificar, mas mostrará "Usuario X" ao invés do nome.

### Q: Como renomear um usuário?

**R:** Use SQL diretamente:

```sql
UPDATE users SET name = 'Novo Nome' WHERE id = 1;
```

### Q: Como deletar um usuário?

**R:** Use SQL:

```sql
-- Deletar usuário e todos os seus embeddings
DELETE FROM users WHERE id = 1;
```

---

## 📝 Exemplo Completo

### 1. Cadastrar João Silva

```bash
python scripts/register_face.py --name "João Silva"
```

### 2. Verificar se foi cadastrado

```bash
sqlite3 bioface.db "SELECT * FROM users WHERE name = 'João Silva';"
```

### 3. Testar identificação

```bash
python main-light.py
```

O sistema deve identificar e mostrar "João Silva: XX%" na tela.

---

## ✅ Checklist

- [ ] Câmera funcionando
- [ ] Banco de dados criado (`bioface.db` existe)
- [ ] Pessoa cadastrada com sucesso
- [ ] Embedding salvo no banco
- [ ] Sistema identifica a pessoa em tempo real

---

**Última atualização:** 2026-02-16

