#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filepath: /Users/tarsilasamille/IdeaProjects/web_translator/static/js/models.js

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
