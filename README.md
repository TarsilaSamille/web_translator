# Tradutor Web Multilíngue

Este projeto implementa um sistema de tradução para múltiplas línguas, incluindo Hausa-Inglês, utilizando modelos de tradução neural desenvolvidos no Hugging Face. Além de uma interface de linha de comando, o projeto agora inclui uma interface web amigável similar ao Google Tradutor.

## Recursos

- Interface web interativa para tradução de textos
- API REST para integração com outros sistemas
- Suporte a múltiplos modelos de tradução
- Armazenamento do histórico de traduções no navegador
- Contagem de caracteres e limite de texto
- Interface para gerenciamento de modelos

## Configuração do ambiente

1. **Clone o repositório:**

   ```bash
   git clone <seu-repositorio>
   cd web_translator
   ```

2. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente:**
   Crie ou edite o arquivo `.env` na raiz do projeto com as seguintes variáveis:

   ```properties
   # Configuração do Hugging Face
   HUGGINGFACE_USERNAME="seu_usuario"
   HUGGINGFACE_REPO_NAME="nome_do_repositorio"
   HUGGINGFACE_TOKEN="seu_token"

   # Diretório para salvar o modelo localmente
   MODEL_PATH="models/nome_do_modelo"
   ```

## Download do modelo

Para baixar o modelo do Hugging Face:

```bash
# Usando as configurações do .env
python download_model.py

# Ou especificando manualmente os parâmetros
python download_model.py --username seu_usuario --repo nome_do_repositorio --token seu_token --output ./models/nome_do_modelo
```

## Usando o tradutor

Depois de baixar o modelo, você pode usá-lo de várias maneiras:

### Interface Web (Recomendado):

```bash
python app.py
```

Acesse o aplicativo em seu navegador em http://localhost:5000

### Modo interativo via CLI:

```bash
python inference.py --model ./models/nome_do_modelo --interactive
```

### Tradução de um texto específico via CLI:

```bash
python inference.py --model ./models/nome_do_modelo --text "Texto para traduzir"
```

## Estrutura do modelo

O modelo salvo deve conter os seguintes arquivos:

- `model.keras` - O modelo Keras de tradução
- `config.json` - Configuração do modelo (incluindo idiomas de origem/destino)
- `source_tokenizer.json` - Tokenizador para o idioma de origem
- `target_tokenizer.json` - Tokenizador para o idioma de destino

## API REST

O aplicativo web também fornece uma API REST que pode ser utilizada por outros sistemas:

### Obter modelos disponíveis

```
GET /api/models
```

Resposta:

```json
[
  {
    "id": "hausa_english_translator",
    "path": "/path/to/model",
    "source_language": "Hausa",
    "target_language": "English",
    "display_name": "Hausa → English"
  }
]
```

### Traduzir texto

```
POST /api/translate
```

Corpo da requisição:

```json
{
  "text": "Texto para traduzir",
  "model": "hausa_english_translator"
}
```

Resposta:

```json
{
  "success": true,
  "translated_text": "Translated text",
  "source_language": "Hausa",
  "target_language": "English"
}
```

## Como migrar o modelo Keras para uso com transformers.js

1. **Converter o modelo Keras para Hugging Face Transformers:**

   - Se o modelo for compatível, converta para PyTorch usando o script `transformers` ou exporte para ONNX.
   - Exemplo de conversão para ONNX:
     ```python
     import keras2onnx
     import onnx
     model = keras.models.load_model('model.keras')
     onnx_model = keras2onnx.convert_keras(model, model.name)
     onnx.save_model(onnx_model, 'model.onnx')
     ```
   - Ou, se for um modelo de tradução baseado em Transformers, treine/exporte usando a biblioteca `transformers` do Hugging Face.

2. **Suba o modelo convertido para o Hugging Face Hub:**

   - Crie um repositório no [Hugging Face Hub](https://huggingface.co/new).
   - Faça upload do arquivo `.onnx` ou do modelo PyTorch.

3. **Use o modelo no frontend com transformers.js:**
   - Instale o pacote:
     ```bash
     npm install @xenova/transformers
     ```
   - Exemplo de uso:
     ```js
     import { pipeline } from "@xenova/transformers";
     const translator = await pipeline("translation", "usuario/modelo-no-hub");
     const output = await translator("Texto em Hausa");
     console.log(output);
     ```

> **Observação:** Nem todos os modelos Keras são compatíveis diretamente com o Hugging Face ou transformers.js. Modelos baseados em arquitetura Transformer têm maior chance de compatibilidade.
