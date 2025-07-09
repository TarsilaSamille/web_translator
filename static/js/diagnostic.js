// Funções de diagnóstico

/**
 * Formata uma linha de log com cores para destacar informações importantes
 * @param {string} line - A linha de log a ser formatada
 * @returns {string} - HTML formatado com cores
 */
function formatLogLine(line) {
    if (!line) return '';

    return line
        .replace(/\[ERROR\]|\[ERRO\]|ERRO|\bERROR\b/gi, '<span class="log-error">$&</span>')
        .replace(/\[WARNING\]|\[AVISO\]|AVISO|\bWARNING\b/gi, '<span class="log-warning">$&</span>')
        .replace(/\[INFO\]|INFO/gi, '<span class="log-info">$&</span>')
        .replace(/\[DEBUG\]|DEBUG/gi, '<span class="log-debug">$&</span>')
        .replace(/\[DIAGNÓSTICO\]/gi, '<span class="log-info">$&</span>')
        .replace(/english-snejag-translator/gi, '<span class="log-error">$&</span>')
        .replace(/\b500\b/g, '<span class="log-error">$&</span>')
        .replace(/modelo problemático/gi, '<span class="log-error">$&</span>')
        .replace(/Error|Exception/gi, '<span class="log-error">$&</span>')
        .replace(/Traceback/gi, '<span class="log-warning">$&</span>');
}

// Função para criar um indicador visual de saúde
function createHealthIndicator(status) {
    return `<span class="health-indicator health-${status}"></span>`;
}

// Exportar funções
if (typeof module !== 'undefined') {
    module.exports = {
        formatLogLine,
        createHealthIndicator
    };
}
