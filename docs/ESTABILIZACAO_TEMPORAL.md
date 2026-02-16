# 🔧 Estabilização Temporal - Eliminar Oscilação

## 🐛 Problema

O sistema estava oscilando entre "Jonas Silva" e "Eliza", mostrando os nomes alternadamente mesmo quando a mesma pessoa estava na frente da câmera.

**Causa:** O sistema identificava frame por frame sem considerar o histórico, causando mudanças rápidas entre identificações.

---

## ✅ Solução Implementada

### **Sistema de Estabilização Temporal**

Implementado um sistema que:

1. ✅ **Mantém histórico** das últimas 10 identificações
2. ✅ **Requer consenso** de 7 frames antes de mudar a identificação
3. ✅ **Confiança mínima** de 60% para mostrar o nome
4. ✅ **Histerese** - evita mudanças rápidas entre nomes

### Como Funciona

```
Frame 1: Identifica "Jonas" → Adiciona ao histórico
Frame 2: Identifica "Jonas" → Adiciona ao histórico
Frame 3: Identifica "Eliza" → Adiciona ao histórico (mas não muda ainda)
...
Frame 7: Identifica "Eliza" → Agora há consenso (7 votos) → Muda para "Eliza"
```

**Resultado:** O nome só muda quando há consenso claro, eliminando oscilação.

---

## ⚙️ Parâmetros Configuráveis

No código (`src/main_light.py`):

```python
self.history_size = 10  # Quantos frames manter no histórico
self.consensus_threshold = 7  # Quantos frames precisam concordar para mudar
self.min_confidence_to_show = 0.6  # Confiança mínima para mostrar nome (60%)
```

### Ajustar Parâmetros

**Para ser mais restritivo (menos mudanças):**
- Aumente `consensus_threshold` para 8-9
- Aumente `min_confidence_to_show` para 0.7

**Para ser mais responsivo (mudanças mais rápidas):**
- Reduza `consensus_threshold` para 5-6
- Reduza `min_confidence_to_show` para 0.5

---

## 🎯 Comportamento Esperado

### Antes (com oscilação):
```
Frame 1: "Jonas Silva"
Frame 2: "Eliza"
Frame 3: "Jonas Silva"
Frame 4: "Eliza"
... (oscilando)
```

### Agora (estabilizado):
```
Frame 1-6: "Jonas Silva" (estabilizado)
Frame 7-13: "Eliza" aparece → Aguardando consenso
Frame 14: "Eliza" (consenso alcançado, muda)
Frame 15-20: "Eliza" (estabilizado)
```

---

## 📊 Vantagens

1. ✅ **Elimina oscilação** - Nome fica estável
2. ✅ **Mudanças confiáveis** - Só muda quando há consenso
3. ✅ **Melhor UX** - Interface mais estável e confiável
4. ✅ **Reduz falsos positivos** - Requer confiança mínima

---

## 🔍 Logs de Debug

O sistema agora loga mudanças de identificação:

```
INFO | Mudanca de identificacao: Eliza (conf=0.85, votos=7)
INFO | Nova identificacao: Jonas Silva (conf=0.92, votos=8)
```

Isso ajuda a entender quando e por que a identificação muda.

---

## ⚠️ Notas Importantes

1. **Primeiros frames:** Pode levar alguns frames para estabilizar na primeira identificação
2. **Mudanças de pessoa:** Quando uma pessoa sai e outra entra, pode levar 7-10 frames para mudar
3. **Confiança baixa:** Se a confiança estiver abaixo de 60%, mostra "DESCONHECIDO"

---

## 🚀 Teste

Execute o sistema:

```bash
python main-light.py
```

**Comportamento esperado:**
- ✅ Nome fica estável quando a mesma pessoa está na frente
- ✅ Só muda quando há consenso claro (7+ frames)
- ✅ Não oscila entre nomes diferentes

---

**Última atualização:** 2026-02-16

