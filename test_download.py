#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
from pathlib import Path
import sys

# Adicionando o diretório atual ao caminho de pesquisa
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from download_model import download_model_from_huggingface, setup_model_for_inference

def main():
    # Valores padrão para teste
    username = "tarsssss"
    repo = "hausa-english-translator"
    token = None  # Token não é obrigatório para modelos públicos
    output_dir = "./models/hausa_english_translator"
    
    print(f"Testando download do modelo {username}/{repo} para {output_dir}")
    
    try:
        # Normalizar caminho
        output_dir = os.path.abspath(output_dir)
        
        # Criar diretório models se não existir
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        
        # Fazer o download do modelo
        if download_model_from_huggingface(username, repo, token, output_dir):
            # Configurar para inferência
            if setup_model_for_inference(output_dir):
                print(f"\nModelo pronto para uso!")
                print(f"Para usar o modelo, execute:")
                print(f"python inference.py --model {output_dir} --interactive")
            else:
                print("\nDownload concluído, mas pode ser necessário configurar manualmente alguns arquivos.")
        else:
            print("\nFalha no download do modelo.")
    
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
