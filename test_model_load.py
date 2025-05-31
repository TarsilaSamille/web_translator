#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar o carregamento de modelo específico no ambiente Render
"""

import os
import sys
import json
import traceback

# Adicionar diretório atual ao PATH para importar módulos locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inference import Translator

def test_model_loading(model_path):
    """Testa o carregamento específico de um modelo"""
    print(f"Testando carregamento do modelo em: {model_path}")
    print(f"Diretório do modelo existe: {os.path.exists(model_path)}")
    
    try:
        if os.path.exists(model_path):
            print(f"Conteúdo do diretório do modelo:")
            for item in os.listdir(model_path):
                item_path = os.path.join(model_path, item)
                size = os.path.getsize(item_path) if os.path.isfile(item_path) else "diretório"
                print(f" - {item}: {size} bytes" if isinstance(size, int) else f" - {item}: {size}")
        
        # Tentar criar e carregar o tradutor
        translator = Translator(model_path)
        result = translator.load_model()
        
        if result:
            print(f"SUCESSO: Modelo carregado com êxito!")
            print(f"Fonte: {translator.source_language}")
            print(f"Alvo: {translator.target_language}")
            
            # Testar a tradução
            test_texts = ["Hello world", "Good morning", "How are you"]
            
            print("\nTestando algumas traduções:")
            for text in test_texts:
                try:
                    translated = translator.translate(text)
                    print(f" - '{text}' => '{translated}'")
                except Exception as e:
                    print(f" - '{text}' => ERRO: {str(e)}")
            
            return True
        else:
            print(f"ERRO: O método load_model() retornou False")
            return False
            
    except Exception as e:
        print(f"ERRO ao carregar modelo: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    else:
        # Testar o modelo problemático por padrão
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "models", "english-snejag-translator")
    
    print(f"==== TESTE DE CARREGAMENTO DE MODELO ====")
    print(f"Caminho: {model_path}")
    
    # Verificar ambiente Render
    is_render = '/opt/render' in os.getcwd()
    print(f"Ambiente Render: {is_render}")
    print(f"Diretório atual: {os.getcwd()}")
    
    # Importações para verificar versões
    try:
        import tensorflow as tf
        print(f"TensorFlow versão: {tf.__version__}")
    except ImportError:
        print("TensorFlow não está instalado")
    
    try:
        import keras
        print(f"Keras versão: {keras.__version__}")
    except ImportError:
        print("Keras não está instalado")
    
    # Testar carregamento
    success = test_model_loading(model_path)
    
    print("\n==== RESULTADO DO TESTE ====")
    if success:
        print("✅ SUCESSO: O modelo foi carregado corretamente!")
        sys.exit(0)
    else:
        print("❌ FALHA: Não foi possível carregar o modelo!")
        
        # Tentar modelos alternativos
        print("\nTentando modelos alternativos...")
        alt_models = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "english_snejag_translator_2"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "english-snejag-translator_3")
        ]
        
        for alt_model in alt_models:
            print(f"\nTestando modelo alternativo: {alt_model}")
            if test_model_loading(alt_model):
                print(f"✅ MODELO ALTERNATIVO CARREGADO COM SUCESSO: {alt_model}")
                print(f"Considere usar este modelo em vez do original.")
                sys.exit(0)
        
        print("\n❌ NENHUM MODELO ALTERNATIVO FUNCIONOU")
        sys.exit(1)
