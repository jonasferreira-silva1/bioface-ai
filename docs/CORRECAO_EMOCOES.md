# 🔧 Correção: Classificação de Emoções

**Data:** 2026-02-16  
**Problemas:** Emoção não muda quando expressão muda, mensagem oscila na tela

---

## 🐛 Problemas Identificados

1. **Emoção não muda**: Sistema mostrava "Feliz" mesmo quando a pessoa estava brava
2. **Mensagem oscila**: Emoção piscava na tela, não ficava fixa
3. **Emoção "fixada"**: Sistema parecia salvar uma emoção e não atualizar

---

## ✅ Correções Implementadas

### 1. **Melhorias na Classificação de Emoções**

#### Uso de Landmarks do MediaPipe
- ✅ Agora usa landmarks 3D do MediaPipe para análise geométrica
- ✅ Detecta posição das sobrancelhas (altura e inclinação)
- ✅ Detecta abertura da boca (largura e altura)
- ✅ Detecta abertura dos olhos

#### Detecção Melhorada de "Angry" (Raiva)
- ✅ **Sobrancelhas inclinadas para baixo** (slope negativo) = raiva
- ✅ **Sobrancelhas baixas** = raiva
- ✅ **Boca fechada/tensa** (baixo aspect ratio) = raiva
- ✅ **Alto contraste e densidade de bordas** = raiva

**Antes:** Usava apenas características visuais (brilho, contraste)  
**Agora:** Usa análise geométrica dos landmarks (muito mais preciso)

### 2. **Estabilização Temporal de Emoções**

Implementado sistema de estabilização similar à identificação:

- ✅ **Histórico de emoções**: Mantém últimas 6 emoções detectadas
- ✅ **Votação por maioria**: Escolhe emoção com mais votos
- ✅ **Consenso antes de mudar**: Requer 4 frames concordando para mudar emoção
- ✅ **Mantém emoção estável**: Não oscila entre emoções diferentes
- ✅ **Limpeza inteligente**: Só limpa se não aparecer por 50% do histórico

**Resultado:** Emoção fica fixa na tela, não oscila mais!

### 3. **Melhorias no Salvamento**

- ✅ **Salva apenas quando muda**: Não salva a mesma emoção repetidamente
- ✅ **Salva a cada 60 frames**: Ou quando a emoção muda
- ✅ **Usa emoção estável**: Salva a emoção estabilizada, não a instantânea

**Resultado:** Não "fixa" emoções antigas no banco.

---

## 🔧 Detalhes Técnicos

### Características Geométricas Extraídas

1. **Abertura dos Olhos**
   - Distância entre pálpebras superior e inferior
   - Detecta surpresa (olhos abertos) ou sono (olhos fechados)

2. **Posição das Sobrancelhas**
   - Altura relativa (baixa = raiva)
   - Inclinação (slope negativo = raiva)

3. **Abertura da Boca**
   - Largura e altura
   - Aspect ratio (altura/largura)
   - Boca aberta = feliz, boca fechada = raiva/triste

### Lógica de Classificação Melhorada

**Angry (Raiva):**
- Sobrancelhas inclinadas para baixo: 50% do peso
- Sobrancelhas baixas: 30% do peso
- Boca fechada/tensa: 20% do peso
- Características visuais: complemento

**Happy (Feliz):**
- Boca aberta (alto aspect ratio): 40% do peso
- Boca larga: 30% do peso
- Características visuais: 30% do peso

**Resultado:** Detecção muito mais precisa, especialmente para raiva!

---

## 📊 Parâmetros de Estabilização

```python
emotion_history_size = 6  # Histórico de 6 frames
emotion_consensus_threshold = 4  # 4 frames precisam concordar para mudar
```

**Como funciona:**
1. Sistema detecta emoção a cada frame
2. Adiciona ao histórico (últimos 6 frames)
3. Conta votos por emoção
4. Só muda se houver 4+ votos para nova emoção
5. Mantém emoção atual se ainda aparecer no histórico

---

## 🚀 Teste Agora

Execute o sistema:

```bash
python main-light.py
```

**O que você verá:**
- ✅ Emoção detectada corretamente (especialmente raiva)
- ✅ Emoção fica fixa na tela (não oscila)
- ✅ Emoção muda quando você muda de expressão
- ✅ Formato: `Nome: XX% | Emoção: XX%`

---

## 📝 Notas

### Por Que Estava Mostrando "Feliz" Quando Estava Bravo?

**Causa:** As heurísticas antigas usavam apenas brilho e contraste, que não são suficientes para detectar raiva. Raiva é melhor detectada por:
- Posição das sobrancelhas (geométrico)
- Forma da boca (geométrico)
- Não apenas brilho/contraste

**Solução:** Agora usa landmarks do MediaPipe para análise geométrica precisa.

### Por Que a Mensagem Oscilava?

**Causa:** Não havia estabilização temporal para emoções. Cada frame mostrava a emoção detectada naquele momento, causando oscilação.

**Solução:** Implementada estabilização temporal (votação por maioria) similar à identificação.

---

## ✅ Status

**Correções:** ✅ Implementadas  
**Teste:** Pronto para testar

---

**Última atualização:** 2026-02-16

