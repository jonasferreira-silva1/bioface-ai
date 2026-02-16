# 🔧 Correção: Cadastro de Face Duplicada

## 🐛 Problema

Ao cadastrar uma nova pessoa, o sistema estava identificando como "Jonas Silva" ao invés de criar um novo usuário com o nome correto.

**Causa:** O script de cadastro não verificava se a face já estava cadastrada antes de criar um novo usuário. Isso permitia criar múltiplos usuários para a mesma pessoa.

---

## ✅ Solução Implementada

### 1. **Verificação Antes de Cadastrar**

O script `register_face.py` agora:

1. ✅ **Gera o embedding** da face
2. ✅ **Verifica se já existe** uma face similar no banco
3. ✅ **Pergunta ao usuário** o que fazer:
   - Adicionar embedding ao usuário existente
   - Criar novo usuário mesmo assim
   - Cancelar

### 2. **Threshold Mais Restritivo**

- **Threshold padrão:** Reduzido de `0.6` para `0.5`
- **Durante cadastro:** Usa `0.5` (mais restritivo) para evitar falsos positivos
- **Durante identificação:** Usa o threshold configurado (padrão `0.5`)

### 3. **Melhorias na Lógica de Identificação**

- Verifica se a distância está dentro do threshold antes de identificar
- Logs mais detalhados para debug
- Evita identificações com baixa confiança

---

## 🚀 Como Funciona Agora

### Cadastrar Nova Face

```bash
python scripts/register_face.py --name "Nova Pessoa"
```

**Fluxo:**

1. **Face detectada** → Gera embedding
2. **Verifica no banco** → Procura faces similares (threshold 0.5)
3. **Se encontrar face similar:**
   ```
   ============================================================
   ATENCAO: Face similar ja cadastrada!
     Usuario existente: Jonas Silva (ID: 2)
     Distancia: 0.4234
   ============================================================
   
   Esta face parece ser de: Jonas Silva
   O que deseja fazer?
     1 - Adicionar embedding ao usuario existente
     2 - Criar novo usuario mesmo assim
     3 - Cancelar
   
   Escolha (1/2/3):
   ```
4. **Se não encontrar:** Cria novo usuário automaticamente

---

## 📊 Configuração

### Ajustar Threshold

No arquivo `.env`:

```env
# Threshold de identificação (0.0-1.0)
# Valores menores = mais restritivo (menos falsos positivos)
# Valores maiores = mais permissivo (mais falsos positivos)
RECOGNITION_DISTANCE_THRESHOLD=0.5
```

**Recomendações:**
- `0.4-0.5`: Restritivo (recomendado para evitar confusões)
- `0.5-0.6`: Moderado
- `0.6-0.7`: Permissivo (pode confundir pessoas similares)

---

## 🔍 Verificar Usuários Cadastrados

```bash
python scripts/list_users.py
```

**Exemplo de saída:**
```
============================================================
Usuarios Cadastrados
============================================================

Total: 2 usuario(s)

ID: 1
  Nome: Teste
  Embeddings: 33
  Ativo: Sim
------------------------------------------------------------
ID: 2
  Nome: Jonas Silva
  Embeddings: 1
  Ativo: Sim
------------------------------------------------------------
```

---

## 🛠️ Corrigir Cadastros Duplicados

Se você já cadastrou a mesma pessoa duas vezes:

### Opção 1: Mesclar Usuários

```bash
# Mover embeddings do usuário 1 para o usuário 2
python scripts/merge_users.py --from 1 --to 2 --delete-old
```

### Opção 2: Deletar Usuário Duplicado

```bash
# Deletar usuário 1
python scripts/delete_user.py --id 1
```

Depois, cadastre novamente:

```bash
python scripts/register_face.py --name "Nome Correto"
```

---

## ⚠️ Avisos Importantes

1. **Threshold muito baixo (0.3-0.4):**
   - ✅ Menos falsos positivos
   - ❌ Pode não identificar a mesma pessoa em diferentes condições (iluminação, ângulo)

2. **Threshold muito alto (0.6-0.7):**
   - ✅ Identifica mesmo com variações
   - ❌ Pode confundir pessoas diferentes

3. **Recomendação:** Use `0.5` como padrão e ajuste conforme necessário.

---

## 📝 Exemplo Completo

### Situação: Cadastrar "Maria" mas sistema detecta como "Jonas Silva"

**Antes (com problema):**
```bash
python scripts/register_face.py --name "Maria"
# ❌ Cria novo usuário "Maria" mas sistema identifica como "Jonas Silva"
```

**Agora (corrigido):**
```bash
python scripts/register_face.py --name "Maria"
# ✅ Detecta que é similar a "Jonas Silva"
# ✅ Pergunta: "Adicionar ao existente ou criar novo?"
# ✅ Você escolhe: "2 - Criar novo usuario mesmo assim"
# ✅ Cria "Maria" corretamente
```

---

## ✅ Checklist

- [x] Script verifica faces existentes antes de cadastrar
- [x] Pergunta ao usuário o que fazer quando encontra face similar
- [x] Threshold padrão ajustado para 0.5 (mais restritivo)
- [x] Lógica de identificação melhorada
- [x] Logs mais detalhados

---

**Última atualização:** 2026-02-16

