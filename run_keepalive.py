#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para iniciar manualmente um processo de manutenção do servidor.
Útil para ambientes como Render.com onde o servidor pode ser desligado por inatividade.

Uso:
    python run_keepalive.py 
"""

from keep_alive import main

if __name__ == "__main__":
    print("Iniciando processo de keep-alive para o servidor...")
    print("Pressione Ctrl+C para interromper.\n")
    main(interval=25)  # Um ping a cada 25 segundos (menos que o limite de 30s)
