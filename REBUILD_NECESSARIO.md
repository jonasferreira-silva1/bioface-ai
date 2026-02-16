# ⚠️ REBUILD OBRIGATÓRIO - Correção libGL.so.1

## 🔴 AÇÃO NECESSÁRIA

O Dockerfile foi corrigido, mas você **DEVE** fazer rebuild completo da imagem.

## 🚀 Comandos para Executar

### Opção 1: Rebuild Completo (Recomendado)

```bash
# Para tudo
docker-compose down

# Remove imagem antiga
docker rmi bioface-ai:latest

# Rebuild SEM cache (OBRIGATÓRIO!)
docker-compose build --no-cache

# Inicia
docker-compose up
```

### Opção 2: Comando Único

```bash
docker-compose down && \
docker rmi bioface-ai:latest 2>/dev/null || true && \
docker-compose build --no-cache && \
docker-compose up
```

## ✅ O Que Foi Corrigido

1. ✅ **Todas as dependências OpenGL** adicionadas
2. ✅ **ldconfig** executado para atualizar cache
3. ✅ **Verificação durante build** para detectar problemas
4. ✅ **Variáveis de ambiente** para modo headless
5. ✅ **Teste de importação** do OpenCV durante build

## 📋 Dependências Adicionadas

- `libgl1-mesa-glx` - Biblioteca principal libGL.so.1
- `libglx-mesa0` - Extensões OpenGL
- `libglu1-mesa` - Utilitários OpenGL
- `ldconfig` - Atualiza cache de bibliotecas

## ⚠️ IMPORTANTE

- **NÃO pule o `--no-cache`** - É essencial!
- **NÃO use imagem antiga** - Remova antes de rebuild
- **Aguarde o build completar** - Pode demorar alguns minutos

## 🎯 Resultado Esperado

Após rebuild, você verá:

```
OpenCV 4.8.1.78 instalado com sucesso
```

E o sistema iniciará sem erros de `libGL.so.1`.

---

**Execute os comandos acima AGORA para aplicar a correção!**

