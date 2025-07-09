#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste rápido para verificar se o sistema está funcionando
"""

import sys
import os

def test_imports():
    """Testa se todas as importações estão funcionando"""
    print("🔍 Testando importações...")
    
    try:
        import flask
        print("✅ Flask importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Flask: {e}")
        return False
    
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow {tf.__version__} importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar TensorFlow: {e}")
        return False
    
    try:
        import keras
        print(f"✅ Keras {keras.__version__} importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Keras: {e}")
        return False
    
    try:
        import psutil
        print(f"✅ psutil {psutil.__version__} importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar psutil: {e}")
        return False
    
    return True

def test_models():
    """Testa se os modelos estão disponíveis"""
    print("\n🤖 Testando modelos...")
    
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    
    if not os.path.exists(models_dir):
        print("❌ Diretório de modelos não encontrado")
        return False
    
    models = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
    
    if not models:
        print("❌ Nenhum modelo encontrado")
        return False
    
    print(f"✅ {len(models)} modelos encontrados:")
    for model in models:
        model_path = os.path.join(models_dir, model)
        required_files = ["model.keras", "config.json", "source_tokenizer.json", "target_tokenizer.json"]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join(model_path, file)):
                missing_files.append(file)
        
        if missing_files:
            print(f"  ⚠️  {model} (arquivos faltando: {', '.join(missing_files)})")
        else:
            print(f"  ✅ {model} (completo)")
    
    return True

def test_app_structure():
    """Testa se a estrutura do app está correta"""
    print("\n🏗️ Testando estrutura do app...")
    
    required_files = [
        "app.py",
        "inference.py",
        "requirements.txt",
        "templates/index.html",
        "static/css/style.css",
        "static/js/app.js"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Arquivos faltando: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Todos os arquivos principais encontrados")
        return True

def test_app_import():
    """Testa se o app pode ser importado"""
    print("\n🐍 Testando importação do app...")
    
    try:
        # Adicionar o diretório atual ao path
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Tentar importar as funções principais
        from inference import Translator
        print("✅ Translator importado com sucesso")
        
        # Tentar importar app (apenas as partes que não iniciam o servidor)
        import app
        print("✅ App importado com sucesso")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao importar: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes do sistema...")
    print("=" * 50)
    
    tests = [
        ("Importações", test_imports),
        ("Modelos", test_models),
        ("Estrutura", test_app_structure),
        ("App", test_app_import)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! O sistema está pronto para uso.")
        print("\nPara iniciar o servidor:")
        print("python app.py")
        print("\nAcesse: http://localhost:5000")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
