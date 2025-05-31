#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('keep_alive')

# URL do servidor
BASE_URL = "https://web-translator.onrender.com"

def ping_server(target_url=None):
    """
    Faz uma requisição para o servidor para mantê-lo ativo.
    
    Args:
        target_url (str, opcional): URL específica para fazer ping.
                                     Se None, usa a URL base padrão.
    
    Returns:
        bool: True se o ping foi bem-sucedido, False caso contrário
    """
    url = target_url if target_url else f"{BASE_URL}/api/models"
    
    try:
        start_time = time.time()
        response = requests.get(url)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            logger.info(f"✅ Servidor online! URL: {url} - Tempo: {elapsed_time:.2f}s")
            return True
        else:
            logger.warning(f"⚠️ Servidor respondeu com código {response.status_code} para URL: {url}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro ao conectar com o servidor {url}: {e}")
        return False

def main(custom_url=None, interval=25):
    """
    Função principal que executa continuamente.
    
    Args:
        custom_url (str, opcional): URL personalizada para fazer ping
        interval (int, opcional): Intervalo em segundos entre pings
    """
    url = custom_url if custom_url else f"{BASE_URL}/api/status"
    logger.info(f"🚀 Iniciando keep-alive para {url}")
    
    try:
        while True:
            # Registra hora atual
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Faz ping no servidor
            success = ping_server(url)
            
            # Espera pelo intervalo especificado
            logger.info(f"⏳ Aguardando {interval} segundos até o próximo ping...")
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("🛑 Processo interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        
    return True

if __name__ == "__main__":
    import argparse
    
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Manter servidor ativo com auto-ping')
    parser.add_argument('--url', type=str, default=BASE_URL,
                        help='URL do servidor para fazer ping (padrão: %(default)s)')
    parser.add_argument('--interval', type=int, default=25,
                        help='Intervalo em segundos entre pings (padrão: %(default)s)')
    
    # Processar argumentos
    args = parser.parse_args()
    
    # Iniciar o loop principal
    main(args.url, args.interval)
