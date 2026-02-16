# 🤝 Guia de Contribuição - BioFace AI

Obrigado por considerar contribuir com o BioFace AI! Este documento fornece diretrizes para contribuições.

## 📋 Como Contribuir

### Reportar Bugs

1. Verifique se o bug já não foi reportado nas [Issues](https://github.com/seu-usuario/bioface-ai/issues)
2. Crie uma nova issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. atual
   - Logs relevantes (se houver)
   - Ambiente (OS, Python, versões)

### Sugerir Melhorias

1. Abra uma issue com tag "enhancement"
2. Descreva a melhoria proposta
3. Explique por que seria útil
4. Se possível, forneça exemplos de uso

### Contribuir com Código

1. **Fork** o repositório
2. **Crie uma branch** para sua feature:
   ```bash
   git checkout -b feature/nova-feature
   ```
3. **Faça suas alterações** seguindo as convenções:
   - Código bem comentado
   - Documentação atualizada
   - Testes (se aplicável)
4. **Commit** com mensagens claras:
   ```bash
   git commit -m "Adiciona feature X"
   ```
5. **Push** para sua branch:
   ```bash
   git push origin feature/nova-feature
   ```
6. Abra um **Pull Request**

## 📝 Convenções de Código

### Estilo Python

- Siga [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints quando possível
- Docstrings em todas as funções/classes
- Máximo 100 caracteres por linha

### Comentários

- Comente código complexo
- Explique "por quê", não "o quê"
- Use português para comentários (projeto em PT-BR)

### Estrutura

- Um arquivo = uma responsabilidade
- Funções pequenas e focadas
- Evite código duplicado

## 🧪 Testes

- Adicione testes para novas features
- Mantenha cobertura de testes
- Execute testes antes de fazer PR:
  ```bash
  pytest tests/
  ```

## 📚 Documentação

- Atualize README se necessário
- Adicione docstrings
- Documente decisões arquiteturais importantes

## ✅ Checklist para PR

Antes de submeter um Pull Request, verifique:

- [ ] Código segue convenções do projeto
- [ ] Testes passam
- [ ] Documentação atualizada
- [ ] Sem erros de lint
- [ ] Commits com mensagens claras
- [ ] Branch atualizada com main/master

## 🎯 Áreas que Precisam de Ajuda

- Testes unitários e de integração
- Modelos de IA pré-treinados
- Documentação e exemplos
- Otimizações de performance
- Suporte a mais plataformas
- Traduções

## 📞 Contato

- Abra uma issue para discussões
- Use Discussions para perguntas gerais

---

**Obrigado por contribuir! 🎉**


