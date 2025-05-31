#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import json
import csv
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('fetch_corrections')

# URLs e caminhos
BASE_URL = "https://web-translator.onrender.com"
API_ENDPOINT = f"{BASE_URL}/api/corrections"
CSV_PATH = "data/corrections.csv"
JSON_PATH = "data/corrections.json"
LAST_FETCH_FILE = "data/last_fetch.txt"

def ensure_data_directory():
    """Garante que o diretório de dados existe."""
    os.makedirs("data", exist_ok=True)

def get_last_fetch_time():
    """Obtém o timestamp da última busca."""
    try:
        if os.path.exists(LAST_FETCH_FILE):
            with open(LAST_FETCH_FILE, 'r') as f:
                return f.read().strip()
        return None
    except Exception as e:
        logger.error(f"Erro ao ler o último timestamp: {e}")
        return None

def save_last_fetch_time():
    """Salva o timestamp atual como última busca."""
    try:
        with open(LAST_FETCH_FILE, 'w') as f:
            f.write(datetime.utcnow().isoformat())
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar o último timestamp: {e}")
        return False

def fetch_corrections():
    """Busca as correções do servidor."""
    last_fetch = get_last_fetch_time()
    params = {}
    
    if last_fetch:
        params["since"] = last_fetch
    
    try:
        logger.info("Buscando correções do servidor...")
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro HTTP ao buscar correções: {e}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao conectar com o servidor: {e}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao processar resposta JSON: {e}")
        return []

def update_json_file(corrections):
    """Atualiza o arquivo JSON com as novas correções."""
    try:
        # Carrega o arquivo existente se disponível
        existing_data = []
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("Arquivo JSON existente está corrompido. Criando novo.")
        
        # Adiciona novos dados (evitando duplicatas por ID)
        existing_ids = {item.get('id') for item in existing_data}
        
        for correction in corrections:
            if correction.get('id') not in existing_ids:
                existing_data.append(correction)
                existing_ids.add(correction.get('id'))
        
        # Salva o arquivo JSON atualizado
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Arquivo JSON atualizado com {len(corrections)} novas correções.")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar arquivo JSON: {e}")
        return False

def update_csv_file(corrections):
    """Atualiza o arquivo CSV com as novas correções."""
    try:
        file_exists = os.path.exists(CSV_PATH)
        
        with open(CSV_PATH, 'a', encoding='utf-8', newline='') as f:
            # Definindo os campos do CSV
            fieldnames = [
                'id', 'timestamp', 'model_id', 'source_text', 
                'original_translation', 'corrected_translation', 
                'source_lang', 'target_lang'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Escreve o cabeçalho se o arquivo não existir
            if not file_exists:
                writer.writeheader()
            
            # Escreve as novas correções
            for correction in corrections:
                writer.writerow({
                    'id': correction.get('id', ''),
                    'timestamp': correction.get('timestamp', ''),
                    'model_id': correction.get('modelId', ''),
                    'source_text': correction.get('sourceText', ''),
                    'original_translation': correction.get('originalTranslation', ''),
                    'corrected_translation': correction.get('correctedTranslation', ''),
                    'source_lang': correction.get('sourceLang', ''),
                    'target_lang': correction.get('targetLang', '')
                })
        
        logger.info(f"Arquivo CSV atualizado com {len(corrections)} novas correções.")
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar arquivo CSV: {e}")
        return False

def main():
    """Função principal."""
    try:
        ensure_data_directory()
        corrections = fetch_corrections()
        
        if not corrections:
            logger.info("Nenhuma nova correção encontrada.")
            return
        
        logger.info(f"Recebidas {len(corrections)} correções do servidor.")
        
        # Atualiza os arquivos
        json_updated = update_json_file(corrections)
        csv_updated = update_csv_file(corrections)
        
        if json_updated and csv_updated:
            # Só salva o último timestamp se tudo foi salvo com sucesso
            save_last_fetch_time()
            logger.info("Processo concluído com sucesso!")
        else:
            logger.warning("Houve problemas ao salvar alguns arquivos.")
    
    except Exception as e:
        logger.error(f"Erro não esperado: {e}")

if __name__ == "__main__":
    main()
