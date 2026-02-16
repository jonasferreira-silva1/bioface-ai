# 🔧 Como Reconstruir a Imagem Docker

O erro `libGL.so.1: cannot open shared object file` indica que a imagem precisa ser reconstruída.

## ⚠️ IMPORTANTE: Rebuild Necessário

Após modificar o Dockerfile, você **DEVE** fazer rebuild:

```bash
# 1. Para o container atual
docker-compose down

# 2. Remove a imagem antiga (opcional, mas recomendado)
docker rmi bioface-ai:latest

# 3. Rebuild SEM cache (garante que tudo seja reconstruído)
docker-compose build --no-cache

# 4. Inicia novamente
docker-compose up
```

## 🚀 Comando Único (Recomendado)

```bash
docker-compose down && docker-compose build --no-cache && docker-compose up
```

## ✅ Verificar se Funcionou

Após o rebuild, você deve ver:
- ✅ Container iniciando sem erros
- ✅ Sem mensagens de `libGL.so.1`
- ✅ Sistema funcionando

## 🐛 Se Ainda Der Erro

1. Verifique se o Dockerfile foi salvo corretamente
2. Tente rebuild novamente com `--no-cache`
3. Verifique os logs: `docker-compose logs`

---

**Lembre-se**: Sempre faça rebuild após modificar o Dockerfile!

