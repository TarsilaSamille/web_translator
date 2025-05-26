import os
import json
import argparse
import numpy as np
import string

# Usando importações do Keras diretamente ao invés de via TensorFlow
from keras.models import load_model
from keras.preprocessing.text import tokenizer_from_json
from keras.preprocessing.sequence import pad_sequences

def clean_sentence(sentence):
    """Limpa a sentença removendo pontuações e convertendo para minúsculas"""
    lower_case_sent = sentence.lower()
    string_punctuation = string.punctuation + "!" + '?'
    clean_sentence = lower_case_sent.translate(str.maketrans('', '', string_punctuation))
    return clean_sentence

def logits_to_sentence(logits, tokenizer):
    """Converte logits para texto usando o tokenizador"""
    index_to_words = {idx: word for word, idx in tokenizer.word_index.items()}
    index_to_words[0] = '' 
    return ' '.join([index_to_words[prediction] for prediction in np.argmax(logits, 1)])

class Translator:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        self.source_tokenizer = None
        self.target_tokenizer = None
        self.config = {}
        self.max_source_len = 0
        self.max_target_len = 0

    def load_model(self):
        # Carregar modelo
        print(f"Carregando modelo de: {self.model_path}")
        model_file = os.path.join(self.model_path, "model.keras")
        
        # Verificar se o arquivo existe
        if not os.path.exists(model_file):
            raise FileNotFoundError(f"O arquivo do modelo não foi encontrado em: {model_file}")
            
        self.model = load_model(model_file)
        
        # Carregar configuração
        config_file = os.path.join(self.model_path, "config.json")
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"O arquivo de configuração não foi encontrado em: {config_file}")
            
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        # Extrair informações do config
        self.max_source_len = self.config.get("max_source_len", 0)
        self.max_target_len = self.config.get("max_target_len", 0)
        self.source_language = self.config.get("source_language", "")
        self.target_language = self.config.get("target_language", "")
        
        # Carregar tokenizadores
        source_tokenizer_file = os.path.join(self.model_path, "source_tokenizer.json")
        target_tokenizer_file = os.path.join(self.model_path, "target_tokenizer.json")
        
        # Verificar se os arquivos de tokenizador existem
        if not os.path.exists(source_tokenizer_file):
            raise FileNotFoundError(f"O arquivo do tokenizador de origem não foi encontrado em: {source_tokenizer_file}")
            
        if not os.path.exists(target_tokenizer_file):
            raise FileNotFoundError(f"O arquivo do tokenizador de destino não foi encontrado em: {target_tokenizer_file}")
        
        # Carregar e corrigir tokenizadores (se necessário)
        with open(source_tokenizer_file, 'r') as f:
            source_tokenizer_data = json.load(f)
            # Verificar se o JSON está dentro de outro JSON (correção para casos especiais)
            if isinstance(source_tokenizer_data, str):
                source_tokenizer_data = json.loads(source_tokenizer_data)
            self.source_tokenizer = tokenizer_from_json(json.dumps(source_tokenizer_data))
        
        with open(target_tokenizer_file, 'r') as f:
            target_tokenizer_data = json.load(f)
            # Verificar se o JSON está dentro de outro JSON (correção para casos especiais)
            if isinstance(target_tokenizer_data, str):
                target_tokenizer_data = json.loads(target_tokenizer_data)
            self.target_tokenizer = tokenizer_from_json(json.dumps(target_tokenizer_data))
        
        print(f"Modelo carregado com sucesso!")
        print(f"Tradutor: {self.source_language} -> {self.target_language}")
        return True

    def translate(self, text):
        if not self.model:
            raise ValueError("Modelo não carregado. Por favor, carregue o modelo primeiro.")
        
        # Limpar e tokenizar o texto
        cleaned_text = clean_sentence(text)
        tokenized = self.source_tokenizer.texts_to_sequences([cleaned_text])
        
        # Padding
        padded = pad_sequences(tokenized, self.max_source_len, padding="post")
        padded = padded.reshape(*padded.shape, 1)
        
        # Previsão
        prediction = self.model.predict(padded)
        
        # Converter para texto
        translated_text = logits_to_sentence(prediction[0], self.target_tokenizer)
        
        return translated_text

def main():
    parser = argparse.ArgumentParser(description="Ferramenta de tradução")
    parser.add_argument("--model", default="models/english_snejag_translator", help="Caminho para o diretório do modelo")
    parser.add_argument("--interactive", action="store_true", help="Iniciar modo interativo")
    parser.add_argument("--text", help="Texto para traduzir")
    
    args = parser.parse_args()
    
    # Criar e carregar tradutor
    translator = Translator(args.model)
    translator.load_model()
    
    # Modo interativo ou tradução única
    if args.interactive:
        print(f"\nTradutor {translator.source_language} -> {translator.target_language}")
        print("-" * 40)
        
        while True:
            text = input(f"\nDigite o texto em {translator.source_language} (ou 'sair' para encerrar): ").strip()
            
            if text.lower() == "sair":
                print("Encerrando o tradutor...")
                break
                
            if text:
                translated = translator.translate(text)
                print(f"\nTexto original ({translator.source_language}): {text}")
                print(f"Tradução ({translator.target_language}): {translated}")
    
    elif args.text:
        translated = translator.translate(args.text)
        print(f"Texto original: {args.text}")
        print(f"Tradução: {translated}")
    
    else:
        print("Por favor, forneça um texto para traduzir com --text ou use o modo interativo com --interactive")
        print(f"Exemplo: python inference.py --model {args.model} --text 'Hello world'")
        print(f"Exemplo: python inference.py --model {args.model} --interactive")

if __name__ == "__main__":
    main()