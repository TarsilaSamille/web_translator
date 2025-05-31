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

# Verificar versão do TensorFlow e Keras
try:
    import tensorflow as tf
    import keras
    print(f"[INFO] TensorFlow versão: {tf.__version__}")
    print(f"[INFO] Keras versão: {keras.__version__}")
    
    # Verificar se estamos no ambiente Render
    render_env = os.environ.get('RENDER') == 'true' or '/opt/render' in os.getcwd()
    print(f"[INFO] Ambiente Render detectado: {render_env}")
    
    # Definir função de fallback para tradução
    global fallback_translation
    def fallback_translation(text, model_id):
        """Função de fallback para tradução quando o carregamento do modelo falha"""
        print(f"[DEBUG] Usando função de fallback para tradução com modelo {model_id}")
        
        # Obter informações do modelo da lista de modelos disponíveis
        models = get_available_models()
        model_info = next((m for m in models if m["id"] == model_id), None)
        
        if not model_info:
            return jsonify({
                'success': False,
                'error': f'Modelo {model_id} não encontrado'
            }), 404
            
        # Informar que estamos usando o fallback
        return jsonify({
            'success': True,
            'translated_text': f"[FALLBACK] Tradução para '{text}' não disponível. Serviço de tradução em manutenção.",
            'source_language': model_info.get('source_language', 'desconhecido'),
            'target_language': model_info.get('target_language', 'desconhecido'),
            'from_correction': False,
            'is_fallback': True
        })
except Exception as e:
    print(f"[AVISO] Não foi possível determinar as versões de TensorFlow/Keras: {e}")

# Verificar estrutura da pasta de modelos no início
def check_models_directory():
    """Verifica e registra informações sobre a estrutura da pasta de modelos na inicialização"""
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    
    print("\n[DEBUG] ===== VERIFICAÇÃO DE DIRETÓRIOS DE MODELOS NA INICIALIZAÇÃO =====")
    
    if not os.path.exists(models_dir):
        print(f"[DEBUG] ALERTA: Diretório de modelos não existe: {models_dir}")
        try:
            os.makedirs(models_dir, exist_ok=True)
            print(f"[DEBUG] Diretório de modelos criado: {models_dir}")
        except Exception as e:
            print(f"[DEBUG] Erro ao criar diretório de modelos: {e}")
        return
    
    print(f"[DEBUG] Diretório de modelos encontrado: {models_dir}")
    
    try:
        # Listar todos os subdiretórios
        subdirs = [os.path.join(models_dir, d) for d in os.listdir(models_dir) 
                  if os.path.isdir(os.path.join(models_dir, d))]
        
        print(f"[DEBUG] Subdiretórios encontrados: {len(subdirs)}")
        
        for subdir in subdirs:
            model_name = os.path.basename(subdir)
            print(f"\n[DEBUG] Verificando modelo: {model_name}")
            print(f"[DEBUG] Caminho completo: {subdir}")
            
            try:
                files = os.listdir(subdir)
                print(f"[DEBUG] Arquivos encontrados: {files}")
                
                # Verificar arquivos importantes
                for file in ["model.keras", "config.json", "source_tokenizer.json", "target_tokenizer.json"]:
                    file_path = os.path.join(subdir, file)
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        print(f"[DEBUG] {file}: Existe, tamanho: {size} bytes")
                    else:
                        print(f"[DEBUG] {file}: NÃO EXISTE")
                
                # Se tiver config.json, exibir conteúdo
                config_path = os.path.join(subdir, "config.json")
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                            print(f"[DEBUG] Conteúdo do config.json: {config}")
                    except Exception as e:
                        print(f"[DEBUG] Erro ao ler config.json: {e}")
            except Exception as e:
                print(f"[DEBUG] Erro ao verificar modelo {model_name}: {e}")
    except Exception as e:
        print(f"[DEBUG] Erro ao verificar diretório de modelos: {e}")
    
    print("[DEBUG] ===== FIM DA VERIFICAÇÃO DE DIRETÓRIOS DE MODELOS =====\n")

# Executar verificação na inicialização
check_models_directory()

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
    print(f"[DEBUG] Solicitado carregamento do modelo: {model_id}")
    
    if model_id in loaded_translators:
        print(f"[DEBUG] Modelo {model_id} já está carregado, retornando instância existente")
        return loaded_translators[model_id]
    
    # Encontrar o modelo na lista de modelos disponíveis
    print(f"[DEBUG] Buscando informações do modelo {model_id} na lista de modelos disponíveis")
    models = get_available_models()
    print(f"[DEBUG] Modelos disponíveis: {[m['id'] for m in models]}")
    model_info = next((m for m in models if m["id"] == model_id), None)
    
    if not model_info:
        print(f"[DEBUG] ERRO: Modelo {model_id} não encontrado na lista de modelos disponíveis")
        return None
    else:
        print(f"[DEBUG] Modelo {model_id} encontrado: {model_info}")
    
    # Verificar se o caminho existe
    print(f"[DEBUG] Verificando se o caminho do modelo existe: {model_info['path']}")
    if not os.path.exists(model_info["path"]):
        print(f"[DEBUG] ERRO: Caminho do modelo não existe: {model_info['path']}")
        return None
    else:
        print(f"[DEBUG] Caminho do modelo existe: {model_info['path']}")
        print(f"[DEBUG] Conteúdo do diretório: {os.listdir(model_info['path'])}")
    
    # Verificar se os arquivos necessários existem
    required_files = ["model.keras", "config.json", "source_tokenizer.json", "target_tokenizer.json"]
    print(f"[DEBUG] Verificando arquivos necessários: {required_files}")
    
    for file in required_files:
        file_path = os.path.join(model_info["path"], file)
        exists = os.path.exists(file_path)
        if exists:
            try:
                size = os.path.getsize(file_path)
                print(f"[DEBUG] Arquivo {file} - Existe: {exists}, Tamanho: {size} bytes")
            except Exception as e:
                print(f"[DEBUG] Arquivo {file} - Existe: {exists}, Erro ao obter tamanho: {e}")
        else:
            print(f"[DEBUG] Arquivo {file} - Existe: {exists}")
    
    missing_files = [f for f in required_files if not os.path.exists(os.path.join(model_info["path"], f))]
    
    if missing_files:
        print(f"[DEBUG] ERRO: Arquivos obrigatórios não encontrados para o modelo {model_id}: {', '.join(missing_files)}")
        return None
    else:
        print(f"[DEBUG] Todos os arquivos obrigatórios encontrados para o modelo {model_id}")
    
    # Tentar carregar o tradutor
    print(f"[DEBUG] Tentando carregar o tradutor para o modelo {model_id}...")
    try:
        print(f"[DEBUG] Criando instância do Translator com caminho: {model_info['path']}")
        
        # Verificar se estamos no ambiente Render
        is_render = '/opt/render' in model_info['path']
        print(f"[DEBUG] Executando no ambiente Render: {is_render}")
        
        # Tratamento especial para o modelo english-snejag-translator no Render
        if is_render and model_id == "english-snejag-translator":
            print(f"[DEBUG] Tratamento especial para o modelo {model_id} no Render")
            
            # Verificar permissões da pasta do modelo
            try:
                perm = oct(os.stat(model_info['path']).st_mode)[-3:]
                print(f"[DEBUG] Permissões da pasta do modelo: {perm}")
                
                # Listar todos os arquivos e suas permissões
                for file in os.listdir(model_info['path']):
                    file_path = os.path.join(model_info['path'], file)
                    file_perm = oct(os.stat(file_path).st_mode)[-3:]
                    file_size = os.path.getsize(file_path)
                    print(f"[DEBUG] Arquivo {file}: permissões={file_perm}, tamanho={file_size} bytes")
            except Exception as e:
                print(f"[DEBUG] Erro ao verificar permissões: {str(e)}")
        
        # Garantir que o caminho existe no Render
        if is_render and not os.path.exists(model_info['path']):
            print(f"[DEBUG] Tentando criar diretório do modelo no Render: {model_info['path']}")
            try:
                os.makedirs(model_info['path'], exist_ok=True)
            except Exception as e:
                print(f"[DEBUG] Erro ao criar diretório: {str(e)}")
        
        # Verificar os links simbólicos que podem estar incorretos no Render
        if is_render and model_id == "english-snejag-translator":
            print(f"[DEBUG] Verificando e corrigindo possíveis problemas de links no modelo {model_id}")
            try:
                # Tentar usar caminhos alternativos se necessário
                alt_paths = [
                    "/opt/render/project/src/models/english_snejag_translator_2",  # Tenta usando o modelo 2
                    "/opt/render/project/src/models/english-snejag-translator_3"    # Tenta usando o modelo 3
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        print(f"[DEBUG] Encontrado caminho alternativo para o modelo: {alt_path}")
                        # Verificar se o modelo alternativo tem os arquivos necessários
                        if all(os.path.exists(os.path.join(alt_path, f)) for f in ["model.keras", "config.json", "source_tokenizer.json", "target_tokenizer.json"]):
                            print(f"[DEBUG] Usando caminho alternativo para o modelo: {alt_path}")
                            model_info['path'] = alt_path
                            break
            except Exception as e:
                print(f"[DEBUG] Erro ao tentar usar caminhos alternativos: {str(e)}")
        
        translator = Translator(model_info["path"])
        
        print(f"[DEBUG] Chamando método load_model()...")
        success = translator.load_model()
        
        if success:
            print(f"[DEBUG] Modelo {model_id} carregado com sucesso!")
            loaded_translators[model_id] = translator
            return translator
        else:
            print(f"[DEBUG] ERRO: Falha ao carregar modelo {model_id} - método load_model() retornou False")
            return None
    except Exception as e:
        import traceback
        print(f"[DEBUG] ERRO: Exceção ao carregar tradutor {model_id}: {e}")
        print(f"[DEBUG] Traceback completo: {traceback.format_exc()}")
        
        # Tratamento especial para erros no ambiente Render
        if '/opt/render' in model_info['path']:
            print(f"[DEBUG] Detectado erro no ambiente Render. Tentando procedimento alternativo...")
            try:
                # Verificar se é um problema de versão do TensorFlow/Keras
                import tensorflow as tf
                import keras
                print(f"[DEBUG] Versões no Render: TensorFlow {tf.__version__}, Keras {keras.__version__}")
                
                # Tentar usar um modelo alternativo se o original falhou
                if model_id == "english-snejag-translator":
                    print(f"[DEBUG] Tentando carregamento automático de um modelo alternativo...")
                    
                    # Tentar modelos alternativos
                    for alt_model_id in ["english_snejag_translator_2", "english-snejag-translator_3"]:
                        print(f"[DEBUG] Tentando modelo alternativo: {alt_model_id}")
                        alt_model = next((m for m in get_available_models() if m["id"] == alt_model_id), None)
                        
                        if alt_model:
                            print(f"[DEBUG] Modelo alternativo {alt_model_id} encontrado, tentando carregar...")
                            try:
                                alt_translator = Translator(alt_model["path"])
                                alt_success = alt_translator.load_model()
                                
                                if alt_success:
                                    print(f"[DEBUG] Modelo alternativo {alt_model_id} carregado com sucesso!")
                                    # Guardar o tradutor alternativo sob o ID original para manter compatibilidade
                                    loaded_translators[model_id] = alt_translator
                                    return alt_translator
                            except Exception as alt_e:
                                print(f"[DEBUG] Erro ao carregar modelo alternativo {alt_model_id}: {alt_e}")
                
                print(f"[DEBUG] Tentando abordagem alternativa de carregamento...")
                return None
            except Exception as render_error:
                print(f"[DEBUG] Falha no procedimento alternativo: {render_error}")
        
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
    print(f"[DEBUG] ===== NOVA SOLICITAÇÃO DE TRADUÇÃO =====")
    data = request.json
    
    if not data or 'text' not in data or 'model' not in data:
        print(f"[DEBUG] ERRO: Parâmetros inválidos: {data}")
        return jsonify({
            'success': False,
            'error': 'Parâmetros inválidos. É necessário fornecer "text" e "model".'
        }), 400
    
    text = data['text']
    model_id = data['model']
    use_corrections = data.get('use_corrections', True)  # Por padrão, usa correções se disponíveis
    
    print(f"[DEBUG] Solicitação de tradução recebida:")
    print(f"[DEBUG] - Texto: '{text}'")
    print(f"[DEBUG] - Modelo: {model_id}")
    print(f"[DEBUG] - Usar correções: {use_corrections}")
    
    # Verificar primeiro se existe uma correção para este texto e modelo
    if use_corrections:
        print(f"[DEBUG] Verificando se existe correção para este texto e modelo...")
        correction = find_correction(text, model_id)
        if correction:
            print(f"[DEBUG] Correção encontrada! Retornando tradução corrigida.")
            return jsonify({
                'success': True,
                'translated_text': correction['correctedTranslation'],
                'source_language': correction.get('sourceLang', 'desconhecido'),
                'target_language': correction.get('targetLang', 'desconhecido'),
                'from_correction': True,
                'original_translation': correction.get('originalTranslation', '')
            })
        print(f"[DEBUG] Nenhuma correção encontrada para este texto e modelo.")
    
    # Obter ou carregar o tradutor
    try:
        print(f"[DEBUG] Tentando obter ou carregar o tradutor para o modelo: {model_id}")
        translator = get_or_load_translator(model_id)
        
        if not translator:
            print(f"[DEBUG] ERRO: Não foi possível carregar o tradutor para o modelo {model_id}. Usando fallback.")
            # Verificar se o método de fallback existe
            if 'fallback_translation' not in globals():
                print(f"[DEBUG] ERRO: Método fallback_translation não está definido!")
                return jsonify({
                    'success': False,
                    'error': f'Erro ao carregar modelo {model_id} e método de fallback não está disponível.'
                }), 500
                
            # Usar o método de fallback para modelos com problemas de compatibilidade
            return fallback_translation(text, model_id)
        
        # Realizar a tradução
        print(f"[DEBUG] Tradutor carregado com sucesso. Realizando tradução...")
        try:
            translated_text = translator.translate(text)
            print(f"[DEBUG] Tradução realizada com sucesso: '{translated_text}'")
            
            return jsonify({
                'success': True,
                'translated_text': translated_text,
                'source_language': translator.source_language,
                'target_language': translator.target_language,
                'from_correction': False
            })
        except Exception as e:
            print(f"[DEBUG] ERRO durante a tradução: {e}")
            import traceback
            print(f"[DEBUG] Traceback da tradução: {traceback.format_exc()}")
            raise
            
    except Exception as e:
        import traceback
        print(f"[DEBUG] ERRO ao traduzir com modelo {model_id}: {e}")
        print(f"[DEBUG] Traceback completo: {traceback.format_exc()}")
        
        # Verificar se o método de fallback existe
        if 'fallback_translation' not in globals():
            print(f"[DEBUG] ERRO: Método fallback_translation não está definido!")
            return jsonify({
                'success': False,
                'error': f'Erro ao traduzir com modelo {model_id}: {str(e)}'
            }), 500
            
        # Usar o método de fallback para modelos com problemas
        print(f"[DEBUG] Tentando usar método de fallback para a tradução...")
        return fallback_translation(text, model_id)

def fallback_translation(text, model_id):
    """Método de fallback para quando o modelo não pode ser carregado ou há erro na tradução"""
    print(f"[DEBUG] Ativando tradução de fallback para o modelo {model_id}")
    
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
        },
        "english-snejag-translator": {
            "Hello": "Leho",
            "World": "Dwor",
            "Hello world": "Leho dwor",
            "How are you?": "Woh rea uyo?",
            "Good morning": "Dogo ginmorn",
            "Thank you": "Knath uyo"
        }
    }
    
    print(f"[DEBUG] Verificando se existe tradução exata para '{text}' no fallback do modelo {model_id}")
    
    # Ver se há uma tradução exata no dicionário simulado
    if model_id in translations and text in translations[model_id]:
        translated_text = translations[model_id][text]
        print(f"[DEBUG] Tradução exata encontrada no fallback: '{translated_text}'")
    else:
        # Simular tradução invertendo o texto (apenas para demonstração)
        translated_text = f"[Fallback] {text[::-1]}"
        print(f"[DEBUG] Usando tradução reversa como fallback: '{translated_text}'")
    
    # Determinar o idioma de origem e destino com base no modelo
    if model_id == "english_snejag_translator" or model_id == "english-snejag-translator":
        source_lang = "English"
        target_lang = "Snejag"
    elif model_id == "hausa_english_translator":
        source_lang = "Hausa"
        target_lang = "English"
    else:
        source_lang = "Desconhecido"
        target_lang = "Desconhecido"
    
    print(f"[DEBUG] Retornando tradução de fallback: '{translated_text}' ({source_lang} → {target_lang})")
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
    
    # Verificar ambiente Render específico
    is_render = os.environ.get('RENDER') == 'true' or '/opt/render' in os.getcwd()
    
    return jsonify({
        'status': 'online',
        'time': datetime.datetime.now().isoformat(),
        'uptime_seconds': uptime.total_seconds(),
        'uptime_human': str(uptime).split('.')[0],  # Remove microssegundos
        'models_loaded': len(loaded_translators),
        'auto_ping': keep_alive_thread is not None and keep_alive_thread.is_alive(),
        'server': 'Render.com' if is_render else 'Local',
        'working_directory': os.getcwd(),
        'models_directory': os.path.join(os.path.dirname(__file__), "models")
    })

@app.route('/api/debug/render', methods=['GET'])
def render_debug():
    """Endpoint para diagnóstico específico do ambiente Render"""
    from render_debug import diagnose
    
    # Verificar se há senha na query string
    auth_key = request.args.get('key', '')
    if not auth_key or auth_key != 'debug-render-2025':
        return jsonify({
            'error': 'Acesso não autorizado. Forneça a chave de autenticação.'
        }), 401
    
    # Executar diagnóstico
    try:
        diagnostico = diagnose()
        return jsonify({
            'success': True,
            'diagnostico': diagnostico
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

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
