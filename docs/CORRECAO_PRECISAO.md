# 🔧 Correção de Precisão - Identificação Incorreta

## 🐛 Problema

Quando Eliza se aproxima da câmera, o sistema identifica incorretamente como "Jonas Silva", mesmo sendo Eliza.

**Causas identificadas:**
1. Threshold muito permissivo (0.5) permitia confusão entre pessoas
2. Falta de validação de ambiguidade (dois matches muito próximos)
3. Confiança mínima muito baixa (60%)
4. Embeddings podem variar com distância da câmera

---

## ✅ Soluções Implementadas

### 1. **Threshold Mais Restritivo**

- **Antes:** `0.5` (muito permissivo)
- **Agora:** `0.4` (mais restritivo)
- **Para mostrar nome:** `0.35` (ainda mais restritivo)

**Resultado:** Reduz falsos positivos significativamente.

### 2. **Validação de Ambiguidade**

Novo parâmetro `RECOGNITION_AMBIGUITY_THRESHOLD` (padrão: 0.1):

- Se dois usuários tiverem distâncias muito próximas (< 0.1 de diferença)
- O sistema **não identifica** para evitar confusão
- Retorna `None` quando há ambiguidade

**Exemplo:**
```
Melhor match: Jonas Silva (distância: 0.38)
Segundo melhor: Eliza (distância: 0.42)
Diferença: 0.04 < 0.1 (ambiguidade!) → Não identifica
```

### 3. **Confiança Mínima Aumentada**

- **Antes:** 60% de confiança mínima
- **Agora:** 70% de confiança mínima

**Resultado:** Só mostra nome quando realmente confiável.

### 4. **Validação Dupla de Distância**

O sistema agora valida:
1. Distância <= threshold (0.4) para considerar match
2. Distância <= min_distance_to_show (0.35) para mostrar nome

**Resultado:** Dupla validação garante maior precisão.

---

## ⚙️ Configuração

No arquivo `.env`:

```env
# Threshold de identificação (mais restritivo)
RECOGNITION_DISTANCE_THRESHOLD=0.4

# Threshold de ambiguidade (diferença mínima entre matches)
RECOGNITION_AMBIGUITY_THRESHOLD=0.1
```

### Ajustar Parâmetros

**Para ser ainda mais restritivo:**
```env
RECOGNITION_DISTANCE_THRESHOLD=0.35
RECOGNITION_AMBIGUITY_THRESHOLD=0.15
```

**Para ser mais permissivo (se necessário):**
```env
RECOGNITION_DISTANCE_THRESHOLD=0.45
RECOGNITION_AMBIGUITY_THRESHOLD=0.08
```

---

## 🚀 Melhorias Adicionais Recomendadas

### 1. **Adicionar Mais Embeddings para Eliza**

Cadastre Eliza em diferentes distâncias da câmera:

```bash
# Adicionar embeddings próximos da câmera
python scripts/add_embeddings.py --user-id 3 --count 10
```

**Dica:** Peça para Eliza se aproximar e se afastar da câmera durante o cadastro.

### 2. **Cadastrar em Diferentes Condições**

- Diferentes distâncias (perto/longe)
- Diferentes ângulos
- Diferentes iluminações
- Diferentes expressões

---

## 📊 Como Funciona Agora

### Fluxo de Identificação:

1. **Gera embedding** da face detectada
2. **Busca no banco** com threshold 0.4
3. **Valida ambiguidade:**
   - Se diferença entre melhor e segundo melhor < 0.1 → Não identifica
4. **Valida distância:**
   - Se distância > 0.35 → Não mostra nome
5. **Valida confiança:**
   - Se confiança < 70% → Não mostra nome
6. **Aplica estabilização temporal:**
   - Requer consenso de 7 frames

**Resultado:** Muito mais preciso e confiável.

---

## 🔍 Logs de Debug

O sistema agora loga:

```
DEBUG | Ambiguidade detectada: melhor=2 (dist=0.38), segundo=3 (dist=0.42), diff=0.04 < 0.1
DEBUG | Distancia muito alta para mostrar (0.42 > 0.35), nao identificando
DEBUG | Face identificada: Eliza (ID: 3, dist=0.32, conf=0.68)
```

Isso ajuda a entender por que uma identificação foi rejeitada.

---

## ✅ Teste

Execute o sistema:

```bash
python main-light.py
```

**Comportamento esperado:**
- ✅ Eliza identificada corretamente quando está perto
- ✅ Eliza identificada corretamente quando está longe
- ✅ Não confunde Eliza com Jonas
- ✅ Mostra "DESCONHECIDO" quando há ambiguidade ou baixa confiança

---

## ⚠️ Se Ainda Não Funcionar

1. **Adicione mais embeddings para Eliza:**
   ```bash
   python scripts/add_embeddings.py --user-id 3 --count 20
   ```

2. **Reduza ainda mais o threshold:**
   ```env
   RECOGNITION_DISTANCE_THRESHOLD=0.35
   ```

3. **Aumente o threshold de ambiguidade:**
   ```env
   RECOGNITION_AMBIGUITY_THRESHOLD=0.15
   ```

---

**Última atualização:** 2026-02-16

