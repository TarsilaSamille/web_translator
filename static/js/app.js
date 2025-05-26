// Funções auxiliares para o aplicativo de tradução

/**
 * Salva o último modelo utilizado
 * @param {string} modelId - ID do modelo selecionado
 */
function saveLastUsedModel(modelId) {
  localStorage.setItem("lastModelId", modelId);
}

/**
 * Recupera o último modelo utilizado
 * @returns {string|null} - ID do último modelo usado ou null
 */
function getLastUsedModel() {
  return localStorage.getItem("lastModelId");
}

/**
 * Salva o histórico de traduções
 * @param {Object} translation - Objeto com detalhes da tradução
 */
function saveTranslationHistory(translation) {
  let history = JSON.parse(localStorage.getItem("translationHistory")) || [];

  // Adicionar tradução ao histórico, mantendo apenas as 10 últimas
  history.unshift({
    sourceText: translation.sourceText,
    translatedText: translation.translatedText,
    modelId: translation.modelId,
    sourceLang: translation.sourceLang,
    targetLang: translation.targetLang,
    timestamp: new Date().toISOString(),
  });

  // Limitar a 10 entradas
  if (history.length > 10) {
    history = history.slice(0, 10);
  }

  localStorage.setItem("translationHistory", JSON.stringify(history));
}
