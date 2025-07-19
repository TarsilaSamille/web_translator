# 🌍 Enhanced Edge NLP Translation System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow 2.15](https://img.shields.io/badge/tensorflow-2.15-orange.svg)](https://tensorflow.org/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema de tradução neural multilíngue otimizado para edge computing, especialmente projetado para funcionar em Raspberry Pi e ambientes de baixa conectividade.

## � Visão Geral

Este projeto estende o trabalho seminal de **Edge NLP for Efficient Machine Translation in Low Connectivity Areas** (Watt et al., 2023), introduzindo:

- **Suporte Multilíngue**: Tradução entre Hausa-Inglês e Inglês-Bidaio-Jagoi
- **Interface Web Moderna**: Dashboard responsivo com métricas em tempo real
- **Otimização para Edge**: Especificamente otimizado para Raspberry Pi
- **Monitoramento de Performance**: Coleta automática de métricas de sistema

## 🚀 Funcionalidades

### ✨ Características Principais
- 🔄 **Tradução em Tempo Real**: Interface web responsiva similar ao Google Translate
- 📊 **Métricas de Performance**: Monitoramento de CPU, memória, temperatura
- 🌐 **Suporte Multilíngue**: 3 pares de idiomas suportados
- 💾 **Histórico Local**: Armazenamento de traduções no navegador
- 🔧 **Correções Colaborativas**: Sistema de feedback para melhorar traduções
- 🍓 **Raspberry Pi Ready**: Otimizado para hardware ARM

### 🎨 Interface Web
- Design responsivo e moderno
- Contagem de caracteres em tempo real
- Troca rápida entre modelos
- Exportação de dados de performance
- Dashboard de métricas do sistema

## Arquitetura do Sistema

### Componentes Principais

## 🛠️ Instalação

### Pré-requisitos
- Python 3.8+
- pip
- Git

### Instalação Rápida

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/enhanced-edge-nlp-translation.git
cd enhanced-edge-nlp-translation

# Instalar dependências
pip install -r requirements.txt

# Iniciar o servidor
python app.py
```

### Instalação no Raspberry Pi

```bash
# Usar o script de configuração automática
chmod +x scripts/raspberry_pi_setup.sh
./scripts/raspberry_pi_setup.sh install
./scripts/raspberry_pi_setup.sh setup

# Verificar configuração
./scripts/raspberry_pi_setup.sh check
```

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Web Interface     │    │  Translation Engine │    │  Performance        │
│   (Flask + JS)      │───▶│   (Neural Models)   │───▶│   Monitor           │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
            │                         │                         │
            ▼                         ▼                         ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   User Interface    │    │  Model Management   │    │  System Metrics     │
│   - Translation     │    │  - LSTM Models      │    │  - CPU Usage        │
│   - History         │    │  - Tokenization     │    │  - Memory Usage     │
│   - Corrections     │    │  - Inference        │    │  - Temperature      │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 📊 Modelos Suportados

| Modelo | Idiomas | Tamanho | BLEU Score | Accuracy |
|--------|---------|---------|------------|----------|
| Hausa-English | Hausa ↔ Inglês | 24.3 MB | 73.5 | 91% |
| English-Bidaio-Jagoi | Inglês → Bidaio-Jagoi | 28.7 MB | 68.2 | 89% |
| Bidaio-Jagoi-English | Bidaio-Jagoi → Inglês | 28.1 MB | 71.8 | 90% |

## 🔧 Uso

### Interface Web
1. Acesse `http://localhost:5000`
2. Selecione o modelo de tradução
3. Digite o texto a ser traduzido
4. Clique em "Traduzir" ou pressione Ctrl+Enter

### API REST

```python
import requests

# Traduzir texto
response = requests.post('http://localhost:5000/api/translate', 
                        json={'text': 'Hello world', 'model': 'hausa-english-translator'})

# Obter métricas do sistema
metrics = requests.get('http://localhost:5000/api/system-metrics')
```

### Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/translate` | POST | Traduzir texto |
| `/api/system-metrics` | GET | Métricas do sistema |
| `/api/models` | GET | Lista de modelos disponíveis |

## 📈 Performance

### Raspberry Pi 4 (8GB RAM)
- **CPU Usage**: 45-60% durante tradução
- **Memory Usage**: 512MB pico
- **Temperature**: 45-65°C operacional
- **Response Time**: 245-698ms (dependendo do tamanho do texto)
- **Throughput**: Até 5 usuários simultâneos

### Tempos de Resposta
- **Texto curto** (1-10 palavras): 245-289ms
- **Texto médio** (11-25 palavras): 387-445ms
- **Texto longo** (26-50 palavras): 612-698ms


### Benchmark Customizado
```bash
# Executar benchmark Python
python scripts/raspberry_pi_benchmark.py

# Gerar relatório de performance
python scripts/raspberry_pi_benchmark.py --export-report
```

## 📁 Estrutura do Projeto

```
enhanced-edge-nlp-translation/
├── 📄 README.md                    # Este arquivo
├── 🐍 app.py                       # Servidor Flask principal
├── 🧠 inference.py                 # Engine de tradução neural
├── 📋 requirements.txt             # Dependências Python
├── 🔧 scripts/                     # Scripts de configuração
│   ├── raspberry_pi_setup.sh      # Configuração do Raspberry Pi
│   └── raspberry_pi_benchmark.py  # Sistema de benchmark
├── 📚 docs/                        # Documentação
│   ├── Enhanced_Edge_NLP_Translation_System.tex
│   └── TECHNICAL_DOCUMENTATION.md
├── 🤖 models/                      # Modelos de tradução
│   ├── hausa-english-translator/
│   ├── english-snejag-translator_3/
│   └── english_snejag_translator_2/
├── 🌐 templates/                   # Templates HTML
│   ├── index.html                  # Interface principal
│   ├── diagnostic.html             # Diagnósticos
│   └── models.html                 # Gerenciamento de modelos
├── 📊 static/                      # Recursos estáticos
│   ├── css/style.css
│   ├── js/app.js
│   └── js/performance-metrics.js
├── 📈 stats/                       # Estatísticas de uso
└── 🔍 corrections/                 # Correções de tradução
```

## 🌐 Deployment e Acesso

### 🚀 Sistema Online
O sistema está atualmente hospedado e acessível nos seguintes endereços:

- **URL Pública**: [https://web-translator.onrender.com](https://web-translator.onrender.com)
- **Plataforma**: Render Cloud Platform

### 📊 Especificações do Deployment
- **Plataforma**: Render Free Tier
- **Recursos**: 256MB RAM, Shared CPU
- **Runtime**: Python 3.11.11
- **Sistema**: Linux x86_64
- **Uptime**: 24/7 (com limitações free tier)

### 🎯 Funcionalidades Online
✅ Tradução Hausa-English  
✅ Tradução English-Snejag  
✅ Interface web responsiva  
✅ Métricas de performance em tempo real  
✅ Suporte desktop e mobile  
✅ Histórico de traduções  
✅ Sistema de correções  

### 🔗 GitHub Repository
- **Código Fonte**: [https://github.com/tarsilasamille/web_translator](https://github.com/tarsilasamille/web_translator)
- **Documentação**: Disponível no repositório
- **Issues e Suporte**: Via GitHub Issues

## 📱 Análise de Performance Cross-Platform

### 🖥️ Performance Desktop vs Mobile

Análise comparativa realizada em julho de 2025 demonstra variações significativas de performance entre plataformas:

| Métrica | Mac Desktop | Android Mobile | Diferença |
|---------|-------------|----------------|-----------|
| **Tempo de Resposta Médio** | 830.6ms | 5942.2ms | 7.15× mais lento |
| **Tempo Máximo** | 1125ms | 15122ms | 13.4× variação |
| **Throughput** | 1.38 trans/min | 1.93 trans/min | Mobile superior |

### 🔍 Fatores de Performance
- **Desktop (Mac + WiFi)**: Resposta quase em tempo real
- **Mobile (Android + 4G)**: Latência de rede (50ms base) impacta significativamente
- **Servidor**: Recursos consistentes (39-43% CPU) independente da plataforma
- **Browser**: Safari vs Chrome mostram diferenças de rendering

### 🎯 Otimizações Implementadas
✅ Design responsivo para mobile  
✅ Lazy loading de recursos  
✅ Cache inteligente no browser  
✅ Progressive web app features  
✅ Monitoramento de rede adaptativo  

