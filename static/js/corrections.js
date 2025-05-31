/**
 * Funções para gerenciar correções de traduções
 */

/**
 * Salva uma correção de tradução
 * @param {Object} correction - Objeto com detalhes da correção
 */
function saveCorrection(correction) {
  // Obter o banco de dados de correções atual
  let corrections = JSON.parse(localStorage.getItem("translationCorrections")) || {};
  
  // Criar uma chave única baseada no texto de origem e no modelo
  const key = `${correction.modelId}:${correction.sourceText}`;
  
  // Salvar a correção
  corrections[key] = {
    sourceText: correction.sourceText,
    originalTranslation: correction.originalTranslation,
    correctedTranslation: correction.correctedTranslation,
    modelId: correction.modelId,
    sourceLang: correction.sourceLang,
    targetLang: correction.targetLang,
    timestamp: new Date().toISOString()
  };
  
  // Salvar no localStorage
  localStorage.setItem("translationCorrections", JSON.stringify(corrections));
  
  // Se estiver conectado ao backend, enviar a correção para o servidor
  if (window.navigator.onLine) {
    sendCorrectionToServer(correction);
  }
}

/**
 * Busca uma correção salva previamente
 * @param {string} modelId - ID do modelo usado
 * @param {string} sourceText - Texto original
 * @returns {Object|null} - Objeto com a correção ou null se não existir
 */
function getCorrection(modelId, sourceText) {
  const corrections = JSON.parse(localStorage.getItem("translationCorrections")) || {};
  const key = `${modelId}:${sourceText}`;
  return corrections[key] || null;
}

/**
 * Verifica se existe uma correção para uma tradução
 * @param {string} modelId - ID do modelo usado
 * @param {string} sourceText - Texto original
 * @returns {boolean} - Verdadeiro se existir uma correção
 */
function hasCorrectionFor(modelId, sourceText) {
  const corrections = JSON.parse(localStorage.getItem("translationCorrections")) || {};
  const key = `${modelId}:${sourceText}`;
  return key in corrections;
}

/**
 * Envia uma correção para o servidor
 * @param {Object} correction - A correção a ser enviada
 * @returns {Promise} - Promise com o resultado da operação
 */
function sendCorrectionToServer(correction) {
  return fetch('/api/corrections', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(correction)
  })
  .then(response => response.json())
  .then(data => {
    console.log("Correção enviada para o servidor:", data);
    return data;
  })
  .catch(error => {
    console.error("Erro ao enviar correção:", error);
    throw error;
  });
}

/**
 * Obtém todas as correções salvas localmente
 * @returns {Array} - Array de correções
 */
function getAllCorrections() {
  const correctionsObj = JSON.parse(localStorage.getItem("translationCorrections")) || {};
  return Object.values(correctionsObj);
}
