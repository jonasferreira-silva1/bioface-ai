# 🎥 Como Usar o BioFace AI

## 🚀 Iniciar o Sistema

### No Windows (Recomendado)

```bash
python main-light.py
```

### No Docker (Linux/WSL2)

```bash
docker-compose up
```

## 📺 O Que Você Verá

Quando o sistema iniciar, uma **janela de vídeo** será aberta mostrando:

1. **Vídeo ao vivo** da sua câmera
2. **Retângulo verde** ao redor do rosto detectado
3. **Texto "FACE DETECTADA"** com a confiança (%)
4. **FPS** (frames por segundo) no canto superior esquerdo
5. **Contador de frames** processados
6. **Instruções** na parte inferior: "Pressione 'Q' para fechar"

## 🎯 Feedback Visual

### Quando uma face é detectada:

- ✅ **Retângulo verde** ao redor do rosto
- ✅ **Círculos verdes** nos cantos do retângulo
- ✅ **Texto verde** mostrando "FACE DETECTADA: XX%"
- ✅ **Logs no terminal** a cada 30 frames

### Informações na tela:

- **FPS**: Frames por segundo (canto superior esquerdo)
- **Frames**: Total de frames processados
- **LIGHT MODE**: Aviso de que não há detecção de emoções
- **Instruções**: Como fechar o sistema

## ❌ Como Fechar a Câmera

### Opção 1: Tecla Q (Recomendado)

1. **Clique na janela de vídeo** para focar nela
2. **Pressione a tecla 'Q'** (ou 'q')
3. O sistema fechará automaticamente

### Opção 2: Tecla ESC

1. **Clique na janela de vídeo** para focar nela
2. **Pressione a tecla ESC**
3. O sistema fechará automaticamente

### Opção 3: Ctrl+C no Terminal

1. **Clique no terminal** onde o programa está rodando
2. **Pressione Ctrl+C**
3. O sistema será interrompido

### Opção 4: Fechar a Janela

1. **Clique no X** da janela de vídeo
2. O sistema pode continuar rodando no terminal
3. Use Ctrl+C para garantir que pare completamente

## ⚠️ Problemas Comuns

### Janela não aparece?

1. Verifique se há outras janelas cobrindo ela
2. Olhe na barra de tarefas do Windows
3. Tente Alt+Tab para encontrar a janela
4. A janela pode estar minimizada

### Não detecta rosto?

1. Verifique se há luz suficiente
2. Certifique-se de que seu rosto está visível na câmera
3. Tente se aproximar ou se afastar da câmera
4. Verifique se a câmera não está bloqueada por outro programa

### Câmera não abre?

1. Feche outros programas que podem estar usando a câmera (Zoom, Teams, etc.)
2. Verifique as permissões da câmera no Windows
3. Tente reiniciar o programa

## 💡 Dicas

- **Foque a janela**: Clique nela antes de pressionar 'Q'
- **Terminal separado**: Mantenha o terminal visível para ver os logs
- **Performance**: Se estiver lento, aumente o `FRAME_SKIP` no `.env`
- **Memória**: Esta versão leve usa ~200-500MB (sem TensorFlow)

---

**Agora você sabe como usar o sistema! 🎉**

