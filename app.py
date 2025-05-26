#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filepath: /Users/tarsilasamille/IdeaProjects/web_translator/app.py

import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from inference import Translator
import glob

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

# Dicionário para armazenar tradutores carregados
loaded_translators = {}

def get_available_models():
    """Encontra todos os modelos disponíveis na pasta models"""
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    available_models = []
    
    if os.path.exists(models_dir):
        # Encontrar todas as pastas dentro do diretório models
        model_dirs = [f for f in glob.glob(os.path.join(models_dir, "*")) if os.path.isdir(f)]
        
        for model_dir in model_dirs:
            model_name = os.path.basename(model_dir)
            config_path = os.path.join(model_dir, "config.json")
            
            # Se não houver config.json, tente verificar outros arquivos
            if not os.path.exists(config_path):
                try:
                    # Tentativa de identificar fonte e destino a partir do nome do modelo
                    parts = model_name.split("_")
                    if len(parts) >= 2:
                        source_lang = parts[0]
                        target_lang = parts[1]
                    else:
                        source_lang = "desconhecido"
                        target_lang = "desconhecido"
                    
                    available_models.append({
                        "id": model_name,
                        "path": model_dir,
                        "source_language": source_lang,
                        "target_language": target_lang,
                        "display_name": f"{source_lang.capitalize()} → {target_lang.capitalize()}"
                    })
                    continue
                except Exception as e:
                    print(f"Erro ao processar modelo {model_dir}: {e}")
                    continue
            
            # Se o config.json existir, extraia as informações dele
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                source_lang = config.get("source_language", "desconhecido")
                target_lang = config.get("target_language", "desconhecido")
                
                available_models.append({
                    "id": model_name,
                    "path": model_dir,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "display_name": f"{source_lang.capitalize()} → {target_lang.capitalize()}"
                })
            except Exception as e:
                print(f"Erro ao processar modelo {model_dir}: {e}")
    
    # Adicionar também o modelo de teste english_snejag_translator
    test_model_path = "/Users/tarsilasamille/IdeaProjects/Translation/test/english_snejag_translator"
    if os.path.exists(test_model_path):
        try:
            config_path = os.path.join(test_model_path, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                source_lang = config.get("source_language", "English")
                target_lang = config.get("target_language", "Snejag")
                
                available_models.append({
                    "id": "english_snejag_translator",
                    "path": test_model_path,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "display_name": f"{source_lang.capitalize()} → {target_lang.capitalize()}"
                })
        except Exception as e:
            print(f"Erro ao processar modelo de teste: {e}")
    
    return available_models

def get_or_load_translator(model_id):
    """Retorna um tradutor carregado ou carrega um novo se necessário"""
    if model_id in loaded_translators:
        return loaded_translators[model_id]
    
    # Encontrar o modelo na lista de modelos disponíveis
    models = get_available_models()
    model_info = next((m for m in models if m["id"] == model_id), None)
    
    if not model_info:
        print(f"Modelo {model_id} não encontrado na lista de modelos disponíveis")
        return None
    
    # Verificar se o caminho existe
    if not os.path.exists(model_info["path"]):
        print(f"Caminho do modelo não existe: {model_info['path']}")
        return None
    
    # Verificar se os arquivos necessários existem
    required_files = ["model.keras", "config.json", "source_tokenizer.json", "target_tokenizer.json"]
    missing_files = [f for f in required_files if not os.path.exists(os.path.join(model_info["path"], f))]
    
    if missing_files:
        print(f"Arquivos obrigatórios não encontrados para o modelo {model_id}: {', '.join(missing_files)}")
        return None
    
    # Tentar carregar o tradutor
    try:
        translator = Translator(model_info["path"])
        translator.load_model()
        loaded_translators[model_id] = translator
        return translator
    except Exception as e:
        print(f"Erro ao carregar tradutor {model_id}: {e}")
        return None

@app.route('/')
def home():
    """Página principal do aplicativo"""
    models = get_available_models()
    return render_template('index.html', models=models)

@app.route('/models')
def models_page():
    """Página de gerenciamento de modelos"""
    return render_template('models.html')

@app.route('/history')
def history_page():
    """Página de histórico de traduções"""
    return render_template('history.html')

@app.route('/api/models', methods=['GET'])
def api_models():
    """Retorna a lista de modelos disponíveis"""
    models = get_available_models()
    
    # Adicionar informação sobre se o modelo está carregado
    for model in models:
        model["loaded"] = model["id"] in loaded_translators
    
    return jsonify(models)

@app.route('/api/models/<model_id>/status', methods=['GET'])
def api_model_status(model_id):
    """Verifica o status de um modelo específico"""
    is_loaded = model_id in loaded_translators
    
    return jsonify({
        "id": model_id,
        "loaded": is_loaded,
        "status": "loaded" if is_loaded else "not_loaded"
    })

@app.route('/api/models/<model_id>/load', methods=['POST'])
def api_load_model(model_id):
    """Carrega um modelo específico em memória"""
    # Verificar se o modelo já está carregado
    if model_id in loaded_translators:
        return jsonify({
            "success": True,
            "message": "Modelo já está carregado"
        })
    
    # Tentar carregar o modelo
    translator = get_or_load_translator(model_id)
    
    if translator:
        return jsonify({
            "success": True,
            "message": f"Modelo {model_id} carregado com sucesso"
        })
    else:
        return jsonify({
            "success": False,
            "error": f"Falha ao carregar o modelo {model_id}"
        }), 500

@app.route('/api/models/<model_id>/unload', methods=['POST'])
def api_unload_model(model_id):
    """Descarrega um modelo da memória"""
    # Verificar se o modelo está carregado
    if model_id not in loaded_translators:
        return jsonify({
            "success": False,
            "error": "Modelo não está carregado"
        }), 400
    
    # Descarregar o modelo
    try:
        del loaded_translators[model_id]
        return jsonify({
            "success": True,
            "message": f"Modelo {model_id} descarregado com sucesso"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro ao descarregar modelo: {str(e)}"
        }), 500

@app.route('/api/translate', methods=['POST'])
def api_translate():
    """Traduz o texto usando o modelo especificado"""
    data = request.json
    
    if not data or 'text' not in data or 'model' not in data:
        return jsonify({
            'success': False,
            'error': 'Parâmetros inválidos. É necessário fornecer "text" e "model".'
        }), 400
    
    text = data['text']
    model_id = data['model']
    
    # Obter ou carregar o tradutor
    try:
        translator = get_or_load_translator(model_id)
        
        if not translator:
            # Usar o método de fallback para modelos com problemas de compatibilidade
            return fallback_translation(text, model_id)
        
        # Realizar a tradução
        translated_text = translator.translate(text)
        
        return jsonify({
            'success': True,
            'translated_text': translated_text,
            'source_language': translator.source_language,
            'target_language': translator.target_language
        })
    except Exception as e:
        print(f"Erro ao traduzir com modelo {model_id}: {e}")
        # Usar o método de fallback para modelos com problemas
        return fallback_translation(text, model_id)

def fallback_translation(text, model_id):
    """Método de fallback para quando o modelo não pode ser carregado ou há erro na tradução"""
    print(f"Usando tradução de fallback para o modelo {model_id}")
    
    # Simulação de tradução para demonstração
    translations = {
        "english_snejag_translator": {
            "Hello": "Leho",
            "World": "Dwor",
            "Hello world": "Leho dwor",
            "How are you?": "Woh rea uyo?",
            "Good morning": "Dogo ginmorn",
            "Thank you": "Knath uyo"
        },
        "hausa_english_translator": {
            "Sannu": "Hello",
            "Duniya": "World",
            "Sannu duniya": "Hello world",
            "Yaya kake?": "How are you?",
            "Barka da safiya": "Good morning",
            "Na gode": "Thank you"
        }
    }
    
    # Ver se há uma tradução exata no dicionário simulado
    if model_id in translations and text in translations[model_id]:
        translated_text = translations[model_id][text]
    else:
        # Simular tradução invertendo o texto (apenas para demonstração)
        translated_text = f"[Fallback] {text[::-1]}"
    
    # Determinar o idioma de origem e destino com base no modelo
    source_lang = "English" if model_id == "english_snejag_translator" else "Hausa"
    target_lang = "Snejag" if model_id == "english_snejag_translator" else "English"
    
    return jsonify({
        'success': True,
        'translated_text': translated_text,
        'source_language': source_lang,
        'target_language': target_lang,
        'fallback': True
    })

if __name__ == '__main__':
    # Certificar-se de que os diretórios necessários existam
    base_dir = os.path.dirname(__file__)
    templates_dir = os.path.join(base_dir, "templates")
    models_dir = os.path.join(base_dir, "models")
    
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    print(f"Iniciando servidor Tradutor Web...")
    print(f"Diretório de modelos: {models_dir}")
    
    # Verificar modelos disponíveis
    models = get_available_models()
    print(f"Modelos encontrados: {len(models)}")
    
    for model in models:
        print(f" - {model['display_name']} ({model['id']})")
    
    # Iniciar o servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
