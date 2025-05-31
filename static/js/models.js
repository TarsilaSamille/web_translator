
/**
 * Funções relacionadas ao gerenciamento de modelos
 */

// Verificar o status do modelo
function checkModelStatus(modelId) {
    return fetch(`/api/models/${modelId}/status`)
        .then(response => response.json())
        .catch(error => {
            console.error('Erro ao verificar status do modelo:', error);
            return { status: 'error', message: error.toString() };
        });
}

// Carregar um modelo específico
function loadModel(modelId) {
    document.getElementById(`load-${modelId}`).disabled = true;
    document.getElementById(`status-${modelId}`).innerHTML = 
        '<div class="flex items-center text-blue-600"><div class="spinner-border mr-2"></div> Carregando modelo...</div>';

    fetch(`/api/models/${modelId}/load`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`status-${modelId}`).innerHTML = 
                    '<span class="text-green-600 flex items-center"><i class="fas fa-check-circle mr-1"></i> Modelo carregado!</span>';
            } else {
                document.getElementById(`status-${modelId}`).innerHTML = 
                    `<span class="text-red-600 flex items-center"><i class="fas fa-exclamation-circle mr-1"></i> Erro: ${data.error}</span>`;
                document.getElementById(`load-${modelId}`).disabled = false;
            }
        })
        .catch(error => {
            document.getElementById(`status-${modelId}`).innerHTML = 
                `<span class="text-red-600 flex items-center"><i class="fas fa-exclamation-circle mr-1"></i> Erro de conexão</span>`;
            document.getElementById(`load-${modelId}`).disabled = false;
        });
}

// Descarregar um modelo específico
function unloadModel(modelId) {
    document.getElementById(`unload-${modelId}`).disabled = true;
    document.getElementById(`status-${modelId}`).innerHTML = 
        '<div class="flex items-center text-blue-600"><div class="spinner-border mr-2"></div> Descarregando modelo...</div>';

    fetch(`/api/models/${modelId}/unload`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`status-${modelId}`).innerHTML = 
                    '<span class="text-gray-600 flex items-center"><i class="fas fa-info-circle mr-1"></i> Modelo descarregado</span>';
                document.getElementById(`load-${modelId}`).disabled = false;
                document.getElementById(`unload-${modelId}`).disabled = true;
            } else {
                document.getElementById(`status-${modelId}`).innerHTML = 
                    `<span class="text-red-600 flex items-center"><i class="fas fa-exclamation-circle mr-1"></i> Erro: ${data.error}</span>`;
                document.getElementById(`unload-${modelId}`).disabled = false;
            }
        })
        .catch(error => {
            document.getElementById(`status-${modelId}`).innerHTML = 
                `<span class="text-red-600 flex items-center"><i class="fas fa-exclamation-circle mr-1"></i> Erro de conexão</span>`;
            document.getElementById(`unload-${modelId}`).disabled = false;
        });
}

// Baixar um novo modelo do Hugging Face
function downloadModel() {
    // Obter os valores do formulário
    const username = document.getElementById('hf-username').value.trim();
    const repo = document.getElementById('hf-repo').value.trim();
    const token = document.getElementById('hf-token').value.trim();
    const modelPath = document.getElementById('model-path').value.trim();
    
    // Validar entradas
    if (!username || !repo) {
        alert('Por favor, preencha o usuário e o repositório do Hugging Face.');
        return;
    }
    
    // Mostrar status de download
    const downloadStatus = document.getElementById('download-status');
    downloadStatus.classList.remove('hidden');
    downloadStatus.classList.add('bg-blue-50');
    downloadStatus.classList.add('text-blue-700');
    downloadStatus.classList.add('border');
    downloadStatus.classList.add('border-blue-200');
    downloadStatus.innerHTML = `
        <div class="flex items-center">
            <div class="spinner-border mr-2" role="status"></div>
            <div>Baixando modelo ${username}/${repo}... Este processo pode levar alguns minutos.</div>
        </div>
    `;
    
    // Enviar solicitação para o backend
    fetch('/api/models/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            repo: repo,
            token: token,
            path: modelPath
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            downloadStatus.classList.remove('bg-blue-50', 'text-blue-700', 'border-blue-200');
            downloadStatus.classList.add('bg-green-50', 'text-green-700', 'border-green-200');
            downloadStatus.innerHTML = `
                <div class="flex items-center">
                    <i class="fas fa-check-circle mr-2"></i> 
                    Modelo baixado com sucesso! 
                    <button class="bg-primary hover:bg-primaryDark text-white text-sm py-1 px-3 rounded transition-colors flex items-center ml-4" onclick="fetchModels()">
                        <i class="fas fa-sync mr-1"></i> Atualizar Lista
                    </button>
                </div>
            `;
        } else {
            downloadStatus.classList.remove('bg-blue-50', 'text-blue-700', 'border-blue-200');
            downloadStatus.classList.add('bg-red-50', 'text-red-700', 'border-red-200');
            downloadStatus.innerHTML = `
                <div class="flex items-center">
                    <i class="fas fa-exclamation-circle mr-2"></i> 
                    Erro ao baixar modelo: ${data.error}
                </div>
            `;
        }
    })
    .catch(error => {
        downloadStatus.classList.remove('bg-blue-50', 'text-blue-700', 'border-blue-200');
        downloadStatus.classList.add('bg-red-50', 'text-red-700', 'border-red-200');
        downloadStatus.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-circle mr-2"></i> 
                Erro de conexão: ${error.toString()}
            </div>
        `;
    });
}
