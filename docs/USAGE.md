# 🎥 Como Usar - BioFace AI

Guia completo de uso do sistema.

---

## 🚀 Iniciar o Sistema

### Windows (Recomendado)

```bash
python main-light.py
```

### Linux/Mac

```bash
python3 main-light.py
```

---

## 📺 Interface Visual

Quando o sistema iniciar, uma **janela de vídeo** será aberta mostrando:

1. **Vídeo ao vivo** da sua câmera
2. **Retângulo verde** ao redor do rosto detectado
3. **Nome da pessoa** identificada (se cadastrada)
4. **Emoção detectada** (se habilitado)
5. **FPS** (frames por segundo) no canto superior esquerdo
6. **Contador de frames** processados

### Feedback Visual

**Quando uma face é detectada:**
- ✅ **Retângulo verde** ao redor do rosto
- ✅ **Nome da pessoa** (se identificada) ou "DESCONHECIDO"
- ✅ **Emoção** (se habilitado)
- ✅ **Confiança** da identificação (%)

---

## 🆕 Cadastrar uma Nova Pessoa

### Comando

```bash
python scripts/register_face.py --name "Jonas Silva"
```

### Passo a Passo

1. **Execute o comando** no terminal
2. **Uma janela da câmera abrirá**
3. **Posicione-se na frente da câmera**
4. **Aguarde a detecção** (aparecerá um retângulo verde)
5. **Pressione ESPAÇO** para capturar e cadastrar
6. **Pressione ESC** para cancelar

### Exemplos

```bash
# Cadastrar com nome
python scripts/register_face.py --name "João Silva"

# Cadastrar com nome composto (use aspas)
python scripts/register_face.py --name "Maria Santos"

# Cadastrar sem nome (anônimo)
python scripts/register_face.py
```

**⚠️ Importante:** O sistema impede cadastros duplicados. Se a pessoa já estiver cadastrada, uma mensagem será exibida.

Para mais detalhes, consulte [CADASTRO_E_CONSULTA.md](CADASTRO_E_CONSULTA.md).

---

## 🔍 Consultar Pessoas Cadastradas

### Listar Todos os Usuários

```bash
python scripts/list_all_users.py
```

### Verificar se Pessoa Está Cadastrada

```bash
# Lista todos e procure pelo nome
python scripts/list_all_users.py | findstr "Jonas"  # Windows
python scripts/list_all_users.py | grep "Jonas"      # Linux/Mac
```

---

## ⌨️ Controles

### Fechar o Sistema

**Opção 1: Tecla Q (Recomendado)**
1. Clique na janela de vídeo para focar nela
2. Pressione a tecla `Q` (ou `q`)
3. O sistema fechará automaticamente

**Opção 2: Tecla ESC**
1. Clique na janela de vídeo
2. Pressione `ESC`
3. O sistema fechará

**Opção 3: Ctrl+C no Terminal**
1. Clique no terminal
2. Pressione `Ctrl+C`
3. O sistema será interrompido

---

## ⚠️ Problemas Comuns

### Janela não aparece?

1. Verifique se há outras janelas cobrindo ela
2. Olhe na barra de tarefas
3. Tente `Alt+Tab` para encontrar a janela
4. A janela pode estar minimizada

### Não detecta rosto?

1. Verifique se há luz suficiente
2. Certifique-se de que seu rosto está visível
3. Tente se aproximar ou se afastar da câmera
4. Verifique se a câmera não está bloqueada

### Câmera não abre?

1. Feche outros programas usando a câmera (Zoom, Teams, etc.)
2. Verifique as permissões da câmera
3. Tente reiniciar o programa

### Identifica como "DESCONHECIDO"?

1. Certifique-se de que você está cadastrado
2. Verifique se há luz suficiente
3. Tente se aproximar mais da câmera
4. Re-cadastre-se se necessário

---

## 💡 Dicas

- **Foque a janela**: Clique nela antes de pressionar 'Q'
- **Terminal separado**: Mantenha o terminal visível para ver os logs
- **Performance**: Se estiver lento, aumente o `FRAME_SKIP` no `.env`
- **Iluminação**: Boa iluminação melhora muito a detecção
- **Estabilização**: O sistema usa estabilização temporal para evitar oscilação

---

## 📚 Mais Informações

- **[CADASTRO_E_CONSULTA.md](CADASTRO_E_CONSULTA.md)** - Detalhes sobre cadastro
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solução de problemas
- **[STATUS.md](STATUS.md)** - Estado atual do projeto

---

**Última atualização:** 2026-02-17

