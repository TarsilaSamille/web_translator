#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para diagnóstico de problemas no ambiente Render
"""

import os
import sys
import glob
import json
import platform
import traceback

def diagnose():
    """Executa diagnósticos do ambiente e retorna informações"""
    results = {
        "sistema": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "cwd": os.getcwd(),
            "env_vars": {k: v for k, v in os.environ.items() if "PATH" in k or "RENDER" in k or "PYTHON" in k}
        },
        "diretorios": {},
        "modelos": {}
    }
    
    # Verificar diretórios principais
    dir_base = os.path.dirname(os.path.abspath(__file__))
    results["diretorios"]["base"] = {
        "path": dir_base,
        "exists": os.path.exists(dir_base),
        "is_dir": os.path.isdir(dir_base),
        "permissions": oct(os.stat(dir_base).st_mode)[-3:] if os.path.exists(dir_base) else "N/A"
    }
    
    # Verificar diretório de modelos
    models_dir = os.path.join(dir_base, "models")
    results["diretorios"]["models"] = {
        "path": models_dir,
        "exists": os.path.exists(models_dir),
        "is_dir": os.path.isdir(models_dir),
        "permissions": oct(os.stat(models_dir).st_mode)[-3:] if os.path.exists(models_dir) else "N/A",
        "subdiretórios": []
    }
    
    # Verificar modelos no diretório
    if os.path.exists(models_dir) and os.path.isdir(models_dir):
        try:
            subdirs = [d for d in glob.glob(os.path.join(models_dir, "*")) if os.path.isdir(d)]
            for model_dir in subdirs:
                model_name = os.path.basename(model_dir)
                model_info = {
                    "name": model_name,
                    "path": model_dir,
                    "permissions": oct(os.stat(model_dir).st_mode)[-3:] if os.path.exists(model_dir) else "N/A",
                    "files": {}
                }
                
                # Verificar arquivos do modelo
                for file in ["model.keras", "config.json", "source_tokenizer.json", "target_tokenizer.json"]:
                    file_path = os.path.join(model_dir, file)
                    file_exists = os.path.exists(file_path)
                    file_info = {
                        "exists": file_exists,
                        "is_file": os.path.isfile(file_path) if file_exists else False,
                        "size": os.path.getsize(file_path) if file_exists else 0,
                        "permissions": oct(os.stat(file_path).st_mode)[-3:] if file_exists else "N/A"
                    }
                    
                    model_info["files"][file] = file_info
                
                # Se o config.json existir, ler seu conteúdo
                config_path = os.path.join(model_dir, "config.json")
                if os.path.exists(config_path):
                    try:
                        with open(config_path, "r") as f:
                            model_info["config"] = json.load(f)
                    except Exception as e:
                        model_info["config_error"] = str(e)
                
                results["modelos"][model_name] = model_info
                results["diretorios"]["models"]["subdiretórios"].append(model_name)
        except Exception as e:
            results["error"] = {
                "message": str(e),
                "traceback": traceback.format_exc()
            }
    
    # Verificar caminhos absolutos para o modelo com problema
    problematic_model = "/opt/render/project/src/models/english-snejag-translator"
    results["modelo_problematico"] = {
        "path": problematic_model,
        "exists": os.path.exists(problematic_model),
        "is_dir": os.path.isdir(problematic_model) if os.path.exists(problematic_model) else False
    }
    
    if os.path.exists(problematic_model) and os.path.isdir(problematic_model):
        results["modelo_problematico"]["conteudo"] = os.listdir(problematic_model)
    
    # Verificar variáveis de ambiente relacionadas ao Python e TensorFlow
    try:
        import tensorflow as tf
        import keras
        results["bibliotecas"] = {
            "tensorflow_version": tf.__version__,
            "keras_version": keras.__version__,
            "tensorflow_path": tf.__file__
        }
    except ImportError as e:
        results["bibliotecas"] = {"error": str(e)}
    
    return results

if __name__ == "__main__":
    resultado = diagnose()
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    # Salvar resultado em arquivo
    with open("render_diagnostico.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print("\nDiagnóstico completo! Resultados salvos em 'render_diagnostico.json'")
