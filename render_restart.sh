#!/bin/bash
# Script para reiniciar e verificar o serviço no ambiente Render

echo "==== DIAGNOSTICANDO PROBLEMAS NO AMBIENTE RENDER ===="
echo "Data atual: $(date)"
echo "Diretório atual: $(pwd)"

echo -e "\n==== VERIFICANDO DIRETÓRIO DE MODELOS ===="
cd /opt/render/project/src || { echo "Erro ao acessar diretório do projeto"; exit 1; }
ls -la models/
echo -e "\n==== VERIFICANDO MODELO ESPECÍFICO ===="
ls -la models/english-snejag-translator/ || echo "Modelo não encontrado"

echo -e "\n==== EXECUTANDO DIAGNÓSTICO COMPLETO ===="
python render_debug.py

echo -e "\n==== TESTANDO CARREGAMENTO DO MODELO ===="
python test_model_load.py

echo -e "\n==== VERIFICANDO ARQUIVOS DE CONFIGURAÇÃO ===="
echo "Config do modelo english-snejag-translator:"
cat models/english-snejag-translator/config.json 2>/dev/null || echo "Arquivo não encontrado"
echo -e "\nConfig do modelo english_snejag_translator_2:"
cat models/english_snejag_translator_2/config.json 2>/dev/null || echo "Arquivo não encontrado"

echo -e "\n==== TESTE DE IMPORTAÇÃO DO TENSORFLOW/KERAS ===="
python -c "import tensorflow as tf; import keras; print(f'TensorFlow: {tf.__version__}, Keras: {keras.__version__}')" || echo "Erro ao importar TensorFlow/Keras"

echo -e "\n==== REINICIANDO SERVIDOR ===="
echo "Servidor reiniciado em: $(date)"
