#!/bin/bash
# Script para verificar se OpenCV está funcionando corretamente

echo "Verificando dependências do OpenCV..."

# Verifica libGL.so.1
if [ -f /usr/lib/x86_64-linux-gnu/libGL.so.1 ] || [ -f /usr/lib/libGL.so.1 ]; then
    echo "✓ libGL.so.1 encontrado"
else
    echo "✗ libGL.so.1 NÃO encontrado"
    echo "  Tentando localizar..."
    find /usr -name "libGL.so*" 2>/dev/null || echo "  Nenhum libGL encontrado"
fi

# Verifica outras dependências
for lib in libglib-2.0.so.0 libsm.so.6 libxext.so.6; do
    if ldconfig -p | grep -q "$lib"; then
        echo "✓ $lib encontrado"
    else
        echo "✗ $lib NÃO encontrado"
    fi
done

# Tenta importar OpenCV
echo ""
echo "Testando importação do OpenCV..."
python3 -c "import cv2; print(f'✓ OpenCV {cv2.__version__} importado com sucesso')" 2>&1

