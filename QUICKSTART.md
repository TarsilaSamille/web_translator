# 🚀 Guia de Início Rápido - Enhanced Edge NLP Translation System

## ⚡ Início Rápido (5 minutos)

### 1. Instalação Básica
```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/enhanced-edge-nlp-translation.git
cd enhanced-edge-nlp-translation

# Instalar dependências
pip install -r requirements.txt

# Iniciar o servidor
python app.py
```

Acesse: http://localhost:5000

### 2. Instalação com Docker
```bash
# Build e executar com Docker
docker-compose up --build

# Ou apenas build
docker build -t edge-nlp-translator .
docker run -p 5000:5000 edge-nlp-translator
```

### 3. Instalação no Raspberry Pi
```bash
# Configuração automática
chmod +x scripts/raspberry_pi_setup.sh
./scripts/raspberry_pi_setup.sh install
./scripts/raspberry_pi_setup.sh setup
```

## 🎯 Principais Recursos

### ✅ O que funciona imediatamente:
- ✅ Interface web de tradução
- ✅ API REST para traduções
- ✅ Monitoramento de métricas em tempo real
- ✅ Histórico de traduções
- ✅ Sistema de correções
- ✅ Diagnósticos de sistema

### 🔧 Configurações Opcionais:
- 🔧 Benchmark de performance
- 🔧 Monitoramento avançado
- 🔧 Otimizações para Raspberry Pi
- 🔧 Exportação de dados científicos

## 📊 Modelos Disponíveis

| Modelo | Status | Tamanho | Qualidade |
|--------|--------|---------|-----------|
| Hausa-English | ✅ Pronto | 24.3 MB | BLEU 73.5 |
| English-Bidaio-Jagoi | ✅ Pronto | 28.7 MB | BLEU 68.2 |
| Bidaio-Jagoi-English | ✅ Pronto | 28.1 MB | BLEU 71.8 |

## 🛠️ Comandos Úteis

### Desenvolvimento
```bash
# Executar em modo desenvolvimento
python app.py

# Executar testes
python -m pytest tests/

# Verificar código
flake8 app.py inference.py
```

### Raspberry Pi
```bash
# Verificar sistema
./scripts/raspberry_pi_setup.sh check

# Executar benchmark
./scripts/raspberry_pi_setup.sh benchmark

# Monitorar recursos
./scripts/raspberry_pi_setup.sh monitor
```

### Docker
```bash
# Executar com docker-compose
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

## 🔍 Solução de Problemas

### Problema: Servidor não inicia
```bash
# Verificar dependências
pip check

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Problema: Modelos não carregam
```bash
# Verificar estrutura dos modelos
python -c "from app import get_available_models; print(get_available_models())"

# Verificar permissões
ls -la models/
```

### Problema: Performance baixa
```bash
# Executar diagnóstico
python scripts/raspberry_pi_benchmark.py

# Verificar uso de recursos
htop
```

## 📈 Métricas de Performance

### Tempo de Resposta Esperado:
- **Texto curto**: < 300ms
- **Texto médio**: < 500ms
- **Texto longo**: < 700ms

### Recursos do Sistema:
- **CPU**: < 60% (média)
- **RAM**: < 512MB (pico)
- **Temperatura**: < 70°C (Raspberry Pi)

## 🎨 Personalização

### Modificar Interface:
- `templates/index.html` - Interface principal
- `static/css/style.css` - Estilos
- `static/js/app.js` - Funcionalidade JavaScript

### Adicionar Novos Modelos:
1. Adicionar na pasta `models/`
2. Seguir estrutura: `model.keras`, `config.json`, `*_tokenizer.json`
3. Reiniciar servidor

### Configurar Métricas:
- Modificar `static/js/performance-metrics.js`
- Ajustar frequência de coleta
- Personalizar exports

## 🔗 Links Úteis

- [Documentação Técnica](docs/TECHNICAL_DOCUMENTATION.md)
- [Artigo Científico](docs/Enhanced_Edge_NLP_Translation_System.tex)
- [Issues no GitHub](https://github.com/seu-usuario/enhanced-edge-nlp-translation/issues)
- [Raspberry Pi Setup](scripts/raspberry_pi_setup.sh)

## 🚨 Avisos Importantes

### ⚠️ Antes de usar em produção:
1. Configurar variáveis de ambiente (`.env`)
2. Configurar logs adequados
3. Implementar backup dos modelos
4. Configurar monitoramento de saúde

### ⚠️ Raspberry Pi:
1. Configurar swap adequado
2. Monitorar temperatura
3. Usar fonte de alimentação adequada
4. Considerar cooling ativo

## 📞 Suporte

### Problemas Comuns:
- [FAQ](https://github.com/seu-usuario/enhanced-edge-nlp-translation/wiki/FAQ)
- [Troubleshooting](https://github.com/seu-usuario/enhanced-edge-nlp-translation/wiki/Troubleshooting)

### Contato:
- 📧 Email: [seu.email@exemplo.com]
- 🐙 GitHub: [https://github.com/seu-usuario]
- 💬 Discord: [link do servidor]

---

**🎉 Pronto para começar!** O sistema está configurado e funcionando. Acesse http://localhost:5000 e comece a traduzir!
