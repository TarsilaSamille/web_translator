#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
from pathlib import Path
from huggingface_hub import snapshot_download
from dotenv import load_dotenv
import shutil
import json


def load_env_variables():
    """Carrega as variáveis de ambiente do arquivo .env"""
    load_dotenv()
    
    # Carrega as variáveis de ambiente
    hf_username = os.getenv("HUGGINGFACE_USERNAME")
    hf_repo_name = os.getenv("HUGGINGFACE_REPO_NAME")
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    model_path = os.getenv("MODEL_PATH")
    
    # Verifica se as variáveis foram definidas
    if not all([hf_username, hf_repo_name, hf_token, model_path]):
        missing = []
        if not hf_username:
            missing.append("HUGGINGFACE_USERNAME")
        if not hf_repo_name:
            missing.append("HUGGINGFACE_REPO_NAME")
        if not hf_token:
            missing.append("HUGGINGFACE_TOKEN")
        if not model_path:
            missing.append("MODEL_PATH")
        
        raise ValueError(f"As seguintes variáveis de ambiente são obrigatórias: {', '.join(missing)}")
    
    return {
        "hf_username": hf_username,
        "hf_repo_name": hf_repo_name,
        "hf_token": hf_token,
        "model_path": model_path
    }


def download_model_from_huggingface(username, repo_name, token, local_dir):
    """
    Faz o download de um modelo do Hugging Face para um diretório local
    
    Args:
        username: Nome de usuário do Hugging Face
        repo_name: Nome do repositório
        token: Token de acesso ao Hugging Face
        local_dir: Diretório local para salvar o modelo
    """
    print(f"Fazendo download do modelo {username}/{repo_name} para {local_dir}")
    
    # Cria o diretório se não existir
    os.makedirs(local_dir, exist_ok=True)
    
    try:
        # Faz o download do modelo
        repo_id = f"{username}/{repo_name}"
        downloaded_path = snapshot_download(
            repo_id=repo_id,
            token=token,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        
        print(f"Download concluído com sucesso! Modelo salvo em: {downloaded_path}")
        return True
    except Exception as e:
        print(f"Erro ao fazer download do modelo: {e}")
        return False


def setup_model_for_inference(model_dir):
    """
    Configura o modelo para inferência, verificando e organizando os arquivos necessários
    
    Args:
        model_dir: Diretório onde o modelo foi baixado
    """
    # Verificar arquivos necessários
    required_files = {
        "model.keras": False,
        "config.json": False,
        "source_tokenizer.json": False,
        "target_tokenizer.json": False
    }
    
    # Verificar quais arquivos existem e quais precisam ser encontrados
    for root, _, files in os.walk(model_dir):
        for file in files:
            if file in required_files:
                required_files[file] = True
            
            # Se encontrar um modelo em formato .h5 ou .keras mas com nome diferente
            if file.endswith(".h5") or file.endswith(".keras"):
                if not required_files["model.keras"]:
                    # Copiar para model.keras
                    source = os.path.join(root, file)
                    target = os.path.join(model_dir, "model.keras")
                    print(f"Encontrado modelo: {file}, copiando para model.keras")
                    shutil.copy(source, target)
                    required_files["model.keras"] = True
                    
    # Verificar se todos os arquivos necessários foram encontrados
    missing_files = [file for file, found in required_files.items() if not found]
    
    if missing_files:
        print(f"ATENÇÃO: Os seguintes arquivos necessários não foram encontrados: {', '.join(missing_files)}")
        print("Você pode precisar renomeá-los manualmente ou fornecê-los.")
        return False
    else:
        print("Todos os arquivos necessários encontrados e organizados!")
        return True


def main():
    parser = argparse.ArgumentParser(description="Download de modelo do Hugging Face")
    parser.add_argument("--username", help="Nome de usuário do Hugging Face (sobrescreve .env)")
    parser.add_argument("--repo", help="Nome do repositório (sobrescreve .env)")
    parser.add_argument("--token", help="Token de acesso ao Hugging Face (sobrescreve .env)")
    parser.add_argument("--output", help="Diretório para salvar o modelo (sobrescreve .env)")
    
    args = parser.parse_args()
    
    try:
        # Carregar variáveis do .env
        env_vars = load_env_variables()
        
        # Sobrescrever com argumentos da linha de comando, se fornecidos
        username = args.username or env_vars["hf_username"]
        repo_name = args.repo or env_vars["hf_repo_name"]
        token = args.token or env_vars["hf_token"]
        output_dir = args.output or env_vars["model_path"]
        
        # Normalizar caminho
        output_dir = os.path.abspath(output_dir)
        
        # Fazer o download do modelo
        if download_model_from_huggingface(username, repo_name, token, output_dir):
            # Configurar para inferência
            if setup_model_for_inference(output_dir):
                print(f"\nModelo pronto para uso!")
                print(f"Para usar o modelo, execute:")
                print(f"python inference.py --model {output_dir} --interactive")
            else:
                print("\nDownload concluído, mas pode ser necessário configurar manualmente alguns arquivos.")
    
    except ValueError as e:
        print(f"Erro de configuração: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    main()
