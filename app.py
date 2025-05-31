#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filepath: /Users/tarsilasamille/IdeaProjects/web_translator/app.py

import os
import json
import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from inference import Translator
import glob

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

# Diretório para armazenar as correções
CORRECTIONS_DIR = os.path.join(os.path.dirname(__file__), "corrections")

def find_correction(text, model_id):
    """Encontra uma correção para um texto e modelo específicos"""
    # Certificar-se de que o diretório de correções existe
    os.makedirs(CORRECTIONS_DIR, exist_ok=True)
    
    # Normalizar o texto para comparação
    text = text.strip()
    
    # Procurar em todos os arquivos de correção
    for filename in os.listdir(CORRECTIONS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(CORRECTIONS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    correction = json.load(f)
                    
                    # Verificar se a correção se aplica
                    if correction.get('modelId') == model_id and correction.get('sourceText', '').strip() == text:
                        return correction
            except Exception as e:
                print(f"Erro ao ler correção {filepath}: {e}")
    
    return None

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
    
    # Verificar também se há modelo english_snejag_translator baixado pelo download_model.py
    downloaded_model_path = os.path.join(os.path.dirname(__file__), "models", "english_snejag_translator")
    if os.path.exists(downloaded_model_path):
        try:
            config_path = os.path.join(downloaded_model_path, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                source_lang = config.get("source_language", "English")
                target_lang = config.get("target_language", "Snejag")
                
                available_models.append({
                    "id": "english_snejag_translator",
                    "path": downloaded_model_path,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "display_name": f"{source_lang.capitalize()} → {target_lang.capitalize()}"
                })
                print(f"Modelo english_snejag_translator encontrado em: {downloaded_model_path}")
        except Exception as e:
            print(f"Erro ao processar modelo baixado: {e}")
    
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
    
@app.route('/corrections')
def corrections_page():
    """Página de correções de traduções"""
    return render_template('corrections.html')

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
        
@app.route('/api/models/download', methods=['POST'])
def api_download_model():
    """Faz o download de um modelo do Hugging Face"""
    data = request.json
    
    if not data:
        return jsonify({"success": False, "error": "Dados JSON não fornecidos"}), 400
    
    username = data.get('username')
    repo = data.get('repo')
    token = data.get('token')
    path = data.get('path')
    
    if not username or not repo:
        return jsonify({"success": False, "error": "Usuário e repositório são obrigatórios"}), 400
    
    if not path:
        path = os.path.join('models', f"{username}_{repo}")
    
    # Verificar se o diretório models existe, criar se não
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # Verificar se o caminho é relativo e converter para absoluto se necessário
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)
    
    try:
        # Importar o módulo de download e executar
        import sys
        from download_model import download_model_from_huggingface, setup_model_for_inference
        
        # Fazer download
        success = download_model_from_huggingface(username, repo, token, path)
        
        if success:
            # Configurar para inferência
            setup_success = setup_model_for_inference(path)
            return jsonify({
                "success": True,
                "message": "Modelo baixado com sucesso",
                "path": path,
                "setup_success": setup_success
            })
        else:
            return jsonify({
                "success": False,
                "error": "Erro ao baixar o modelo. Verifique as credenciais e o repositório."
            }), 500
    
    except Exception as e:
        import traceback
        print(f"Erro ao baixar modelo: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": f"Erro ao baixar modelo: {str(e)}"
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
    use_corrections = data.get('use_corrections', True)  # Por padrão, usa correções se disponíveis
    
    # Verificar primeiro se existe uma correção para este texto e modelo
    if use_corrections:
        correction = find_correction(text, model_id)
        if correction:
            return jsonify({
                'success': True,
                'translated_text': correction['correctedTranslation'],
                'source_language': correction.get('sourceLang', 'desconhecido'),
                'target_language': correction.get('targetLang', 'desconhecido'),
                'from_correction': True,
                'original_translation': correction.get('originalTranslation', '')
            })
    
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
            'target_language': translator.target_language,
            'from_correction': False
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

@app.route('/api/corrections', methods=['POST'])
def save_correction():
    """Salva uma correção de tradução"""
    data = request.json
    
    if not data or 'sourceText' not in data or 'correctedTranslation' not in data:
        return jsonify({
            'success': False,
            'error': 'Parâmetros inválidos. É necessário fornecer "sourceText" e "correctedTranslation".'
        }), 400
    
    # Criar uma estrutura para a correção
    correction = {
        'sourceText': data['sourceText'],
        'originalTranslation': data.get('originalTranslation', ''),
        'correctedTranslation': data['correctedTranslation'],
        'modelId': data.get('modelId', ''),
        'sourceLang': data.get('sourceLang', ''),
        'targetLang': data.get('targetLang', ''),
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    # Certificar-se de que o diretório de correções existe
    os.makedirs(CORRECTIONS_DIR, exist_ok=True)
    
    # Criar um nome de arquivo baseado no timestamp
    filename = f"{correction['timestamp'].replace(':', '-').replace('.', '-')}.json"
    filepath = os.path.join(CORRECTIONS_DIR, filename)
    
    try:
        # Salvar a correção no arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(correction, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Correção salva com sucesso',
            'correction': correction
        })
    except Exception as e:
        print(f"Erro ao salvar correção: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao salvar correção: {str(e)}'
        }), 500

@app.route('/api/corrections', methods=['GET'])
def get_corrections():
    """Obtém todas as correções salvas"""
    try:
        # Certificar-se de que o diretório de correções existe
        os.makedirs(CORRECTIONS_DIR, exist_ok=True)
        
        # Verificar se há filtros
        model_id = request.args.get('model_id')
        source_lang = request.args.get('source_lang')
        target_lang = request.args.get('target_lang')
        since_time = request.args.get('since')  # Timestamp ISO para filtrar por data
        
        # Obter todos os arquivos de correção
        corrections = []
        for filename in os.listdir(CORRECTIONS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CORRECTIONS_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        correction = json.load(f)
                        
                        # Adicionar ID para facilitar rastreamento
                        if 'id' not in correction:
                            correction['id'] = os.path.splitext(filename)[0]
                        
                        # Aplicar filtros, se houver
                        if model_id and correction.get('modelId') != model_id:
                            continue
                        if source_lang and correction.get('sourceLang') != source_lang:
                            continue
                        if target_lang and correction.get('targetLang') != target_lang:
                            continue
                        # Filtrar por timestamp, se fornecido
                        if since_time and correction.get('timestamp', '') <= since_time:
                            continue
                            
                        corrections.append(correction)
                except Exception as e:
                    print(f"Erro ao ler correção {filepath}: {e}")
        
        # Ordenar por timestamp, do mais recente para o mais antigo
        corrections.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Obter estatísticas das correções
        stats = {
            'total': len(corrections),
            'models': {},
            'languages': {}
        }
        
        for correction in corrections:
            # Estatísticas por modelo
            model_id = correction.get('modelId', 'desconhecido')
            if model_id not in stats['models']:
                stats['models'][model_id] = 0
            stats['models'][model_id] += 1
            
            # Estatísticas por idioma
            lang_pair = f"{correction.get('sourceLang', '?')} → {correction.get('targetLang', '?')}"
            if lang_pair not in stats['languages']:
                stats['languages'][lang_pair] = 0
            stats['languages'][lang_pair] += 1
        
        return jsonify({
            'success': True,
            'corrections': corrections,
            'stats': stats
        })
    except Exception as e:
        print(f"Erro ao obter correções: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao obter correções: {str(e)}'
        }), 500

import threading
import time
from keep_alive import ping_server

# Variável global para controlar o thread de auto-ping
keep_alive_thread = None

# Registrar o tempo de início do aplicativo
app.start_time = datetime.datetime.now()

@app.route('/api/status', methods=['GET'])
def api_status():
    """Endpoint para verificar o status do serviço"""
    uptime = datetime.datetime.now() - app.start_time
    
    return jsonify({
        'status': 'online',
        'time': datetime.datetime.now().isoformat(),
        'uptime_seconds': uptime.total_seconds(),
        'uptime_human': str(uptime).split('.')[0],  # Remove microssegundos
        'models_loaded': len(loaded_translators),
        'auto_ping': keep_alive_thread is not None and keep_alive_thread.is_alive(),
        'server': 'Render.com' if os.environ.get('RENDER') else 'Local'
    })

def start_auto_ping():
    """Inicia um thread para fazer auto-ping e manter o servidor ativo"""
    def run_ping_loop():
        print("🔄 Iniciando thread de auto-ping para evitar inatividade")
        while True:
            try:
                # Usar o endpoint de status para ping interno
                ping_server("http://localhost:5000/api/status")
                time.sleep(25)  # Intervalo de 25 segundos (menor que o limite de 30s)
            except Exception as e:
                print(f"Erro no auto-ping: {e}")
                time.sleep(5)  # Em caso de erro, tenta novamente após 5 segundos
    
    global keep_alive_thread
    keep_alive_thread = threading.Thread(target=run_ping_loop, daemon=True)
    keep_alive_thread.start()
    print("✅ Thread de auto-ping iniciada com sucesso!")

if __name__ == '__main__':
    # Certificar-se de que os diretórios necessários existam
    base_dir = os.path.dirname(__file__)
    templates_dir = os.path.join(base_dir, "templates")
    models_dir = os.path.join(base_dir, "models")
    corrections_dir = os.path.join(base_dir, "corrections")
    
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(corrections_dir, exist_ok=True)
    
    print(f"Iniciando servidor Tradutor Web...")
    print(f"Diretório de modelos: {models_dir}")
    
    # Verificar modelos disponíveis
    models = get_available_models()
    print(f"Modelos encontrados: {len(models)}")
    
    for model in models:
        print(f" - {model['display_name']} ({model['id']})")
    
    # Iniciar thread de auto-ping se estiver no ambiente de produção (Render)
    is_render = (os.environ.get('RENDER') == 'true' or 
                 os.environ.get('RUNNING_ON_RENDER') or
                 os.environ.get('IS_RENDER') or
                 'render.com' in os.environ.get('HOST', '') or
                 'onrender.com' in os.environ.get('HOSTNAME', ''))
    
    # Também pode ser ativado manualmente se necessário
    if is_render or os.environ.get('ENABLE_AUTO_PING') == 'true':
        print("🔄 Ambiente de produção detectado, ativando auto-ping...")
        start_auto_ping()
    
    # Iniciar o servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
