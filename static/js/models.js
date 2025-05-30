
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
        '<div class="spinner-border spinner-border-sm text-primary" role="status">' +
        '<span class="visually-hidden">Carregando...</span></div> Carregando modelo...';

    fetch(`/api/models/${modelId}/load`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`status-${modelId}`).innerHTML = 
                    '<span class="text-success"><i class="fas fa-check-circle"></i> Modelo carregado!</span>';
            } else {
                document.getElementById(`status-${modelId}`).innerHTML = 
                    `<span class="text-danger"><i class="fas fa-exclamation-circle"></i> Erro: ${data.error}</span>`;
                document.getElementById(`load-${modelId}`).disabled = false;
            }
        })
        .catch(error => {
            document.getElementById(`status-${modelId}`).innerHTML = 
                `<span class="text-danger"><i class="fas fa-exclamation-circle"></i> Erro de conexão</span>`;
            document.getElementById(`load-${modelId}`).disabled = false;
        });
}

// Descarregar um modelo específico
function unloadModel(modelId) {
    document.getElementById(`unload-${modelId}`).disabled = true;
    document.getElementById(`status-${modelId}`).innerHTML = 
        '<div class="spinner-border spinner-border-sm text-primary" role="status">' +
        '<span class="visually-hidden">Descarregando...</span></div> Descarregando modelo...';

    fetch(`/api/models/${modelId}/unload`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`status-${modelId}`).innerHTML = 
                    '<span class="text-secondary"><i class="fas fa-info-circle"></i> Modelo descarregado</span>';
                document.getElementById(`load-${modelId}`).disabled = false;
                document.getElementById(`unload-${modelId}`).disabled = true;
            } else {
                document.getElementById(`status-${modelId}`).innerHTML = 
                    `<span class="text-danger"><i class="fas fa-exclamation-circle"></i> Erro: ${data.error}</span>`;
                document.getElementById(`unload-${modelId}`).disabled = false;
            }
        })
        .catch(error => {
            document.getElementById(`status-${modelId}`).innerHTML = 
                `<span class="text-danger"><i class="fas fa-exclamation-circle"></i> Erro de conexão</span>`;
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
    downloadStatus.classList.remove('d-none');
    downloadStatus.classList.add('alert-info');
    downloadStatus.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Baixando...</span>
            </div>
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
            downloadStatus.classList.remove('alert-info');
            downloadStatus.classList.add('alert-success');
            downloadStatus.innerHTML = `
                <div>
                    <i class="fas fa-check-circle"></i> 
                    Modelo baixado com sucesso! 
                    <button class="btn btn-sm btn-primary ms-2" onclick="fetchModels()">
                        <i class="fas fa-sync"></i> Atualizar Lista
                    </button>
                </div>
            `;
        } else {
            downloadStatus.classList.remove('alert-info');
            downloadStatus.classList.add('alert-danger');
            downloadStatus.innerHTML = `
                <div>
                    <i class="fas fa-exclamation-circle"></i> 
                    Erro ao baixar modelo: ${data.error}
                </div>
            `;
        }
    })
    .catch(error => {
        downloadStatus.classList.remove('alert-info');
        downloadStatus.classList.add('alert-danger');
        downloadStatus.innerHTML = `
            <div>
                <i class="fas fa-exclamation-circle"></i> 
                Erro de conexão: ${error.toString()}
            </div>
        `;
    });
}
