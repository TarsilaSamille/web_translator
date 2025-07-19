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

/**
 * Carrega e exibe métricas do navegador
 */
function loadBrowserMetrics() {
    if (!window.performanceMetrics) {
        document.getElementById('browser-metrics-full').innerHTML =
            `<span class="log-error">Sistema de métricas não inicializado.</span>`;
        return;
    }

    // Usar o relatório específico para o navegador
    const report = window.performanceMetrics.generateBrowserReport();

    if (!report || !report.metrics) {
        document.getElementById('browser-metrics-full').innerHTML =
            `<span class="log-warning">Nenhuma métrica do navegador disponível. O sistema de métricas está iniciado?</span>`;
        return;
    }

    const browserMetrics = report.metrics;

    // Exibir relatório completo
    document.getElementById('browser-metrics-full').textContent =
        JSON.stringify(report, null, 2);

    // Exibir estatísticas de memória JS
    if (browserMetrics.jsHeapMemory) {
        document.getElementById('js-memory-stats').innerHTML = `
            <ul>
                <li>Uso médio: ${browserMetrics.jsHeapMemory.averageMB.toFixed(2)} MB (${browserMetrics.jsHeapMemory.averagePercent.toFixed(1)}% do limite)</li>
                <li>Uso máximo: ${browserMetrics.jsHeapMemory.maxMB.toFixed(2)} MB</li>
                <li>Pico de uso: ${browserMetrics.jsHeapMemory.maxPercent.toFixed(1)}% do limite</li>
                <li>Pontuação: <strong>${report.performanceScore}</strong>/100</li>
            </ul>
        `;
    }

    // Exibir estatísticas de rede
    if (browserMetrics.networkConnection) {
        document.getElementById('network-stats').innerHTML = `
            <ul>
                <li>Tipo de conexão: ${browserMetrics.networkConnection.effectiveType}</li>
                <li>Velocidade: ${browserMetrics.networkConnection.downlinkMbps} Mbps</li>
                <li>Latência (RTT): ${browserMetrics.networkConnection.rttMs} ms</li>
                <li>Modo de economia de dados: ${browserMetrics.networkConnection.saveData ? 'Ativado' : 'Desativado'}</li>
            </ul>
        `;
    }

    // Exibir tempos de carregamento
    if (browserMetrics.pageLoad) {
        document.getElementById('page-load-stats').innerHTML = `
            <ul>
                <li>Tempo total: ${browserMetrics.pageLoad.totalLoadTime} ms</li>
                <li>DOM interativo: ${browserMetrics.pageLoad.domInteractiveTime} ms</li>
                <li>DOM completo: ${browserMetrics.pageLoad.domCompleteTime} ms</li>
                <li>Tempo de resposta do servidor: ${browserMetrics.pageLoad.responseTime} ms</li>
                <li>Tempo de DNS: ${browserMetrics.pageLoad.dnsLookupTime} ms</li>
            </ul>
        `;
    }

    // Exibir estatísticas de recursos
    if (browserMetrics.resources) {
        let resourceTypeHTML = '';

        if (browserMetrics.resources.byType) {
            const types = Object.keys(browserMetrics.resources.byType);
            if (types.length > 0) {
                resourceTypeHTML = '<br>Por tipo:<ul>';
                types.forEach(type => {
                    const typeInfo = browserMetrics.resources.byType[type];
                    resourceTypeHTML += `<li>${type}: ${typeInfo.count} recursos (${typeInfo.totalDuration.toFixed(2)} ms)</li>`;
                });
                resourceTypeHTML += '</ul>';
            }
        }

        document.getElementById('resource-stats').innerHTML = `
            <ul>
                <li>Total de recursos: ${browserMetrics.resources.count}</li>
                <li>Tempo médio: ${browserMetrics.resources.avgDuration.toFixed(2)} ms</li>
                <li>Tempo total: ${browserMetrics.resources.totalDuration.toFixed(2)} ms</li>
            </ul>
            ${resourceTypeHTML}
        `;
    }

    // Exibir estatísticas de interação
    if (browserMetrics.userInteractions) {
        const interactions = browserMetrics.userInteractions;
        const sessionCount = interactions.sessions ? interactions.sessions.length : 0;
        const activeSessions = interactions.sessions ?
            interactions.sessions.filter(s => !s.endTime).length : 0;

        document.getElementById('user-interaction-stats').innerHTML = `
            <ul>
                <li>Cliques: ${interactions.clicks}</li>
                <li>Teclas: ${interactions.keyPresses}</li>
                <li>Eventos de rolagem: ${interactions.scrollEvents}</li>
                <li>Envios de formulário: ${interactions.formSubmissions}</li>
                <li>Seleções de texto: ${interactions.textSelections}</li>
                <li>Sessões: ${sessionCount} (${activeSessions} ativa(s))</li>
            </ul>
        `;
    }
}

/**
 * Carrega e exibe o relatório comparativo servidor-cliente
 */
function loadComparativeReport() {
    if (!window.performanceMetrics) {
        document.getElementById('comparative-report').innerHTML =
            `<span class="log-error">Sistema de métricas não inicializado.</span>`;
        return;
    }

    // Usar o método cleanSpecialChars se disponível
    let report;
    if (typeof window.performanceMetrics.cleanSpecialChars === 'function') {
        report = window.performanceMetrics.cleanSpecialChars(
            window.performanceMetrics.generateComparativeReport()
        );
    } else {
        report = window.performanceMetrics.generateComparativeReport();
    }

    try {
        // Verificar e corrigir caracteres UTF-8 no relatório
        const fixedReport = JSON.parse(
            JSON.stringify(report)
                .replace(/\\u00c3\\u00a9/g, 'é')
                .replace(/\\u00c3\\u00a7/g, 'ç')
                .replace(/\\u00c3\\u00a3/g, 'ã')
                .replace(/\\u00c3\\u00a1/g, 'á')
                .replace(/\\u00c3\\u00a0/g, 'à')
                .replace(/\\u00c3\\u00a2/g, 'â')
                .replace(/\\u00c3\\u00b3/g, 'ó')
                .replace(/\\u00c3\\u00b5/g, 'õ')
                .replace(/\\u00c3\\u00ba/g, 'ú')
                .replace(/MÃ©tricas/g, 'Métricas')
                .replace(/traduÃ§Ã£o/g, 'tradução')
                .replace(/serviÃ§o/g, 'serviço')
                .replace(/memÃ³ria/g, 'memória')
                .replace(/disponÃ­vel/g, 'disponível')
                .replace(/ComparaÃ§Ã£o/g, 'Comparação')
                .replace(/traduÃ§Ãµes/g, 'traduções')
                .replace(/Â°C/g, '°C')
                .replace(/Â/g, '')
        );

        // Exibir relatório completo corrigido
        document.getElementById('comparative-report-full').textContent =
            JSON.stringify(fixedReport, null, 2);
    } catch (e) {
        console.error('Erro ao tentar corrigir caracteres UTF-8:', e);
        // Fallback para o relatório original se houver erro
        document.getElementById('comparative-report-full').textContent =
            JSON.stringify(report, null, 2);
    }

    // Criar tabela HTML com os dados do servidor
    let serverHtml = '<h4>Métricas do Servidor</h4>';
    if (typeof report.servidor.cpu === 'string') {
        serverHtml += `<p>${report.servidor.cpu}</p>`;
    } else {
        serverHtml += `
        <table class="metrics-table">
            <tr><th colspan="3">CPU</th></tr>
            <tr>
                <td><strong>Atual:</strong> ${report.servidor.cpu.utilizacaoAtual}</td>
                <td><strong>Média:</strong> ${report.servidor.cpu.utilizacaoMedia}</td>
                <td><strong>Pico:</strong> ${report.servidor.cpu.utilizacaoPico}</td>
            </tr>
            <tr><th colspan="3">Memória</th></tr>
            <tr>
                <td><strong>Atual:</strong> ${report.servidor.memoria.utilizacaoAtual}</td>
                <td><strong>Média:</strong> ${report.servidor.memoria.utilizacaoMedia}</td>
                <td><strong>Pico:</strong> ${report.servidor.memoria.utilizacaoPico}</td>
            </tr>
            <tr><th colspan="3">Temperatura</th></tr>
            <tr>
                <td><strong>Atual:</strong> ${report.servidor.temperatura.atual.replace('Â', '')}</td>
                <td><strong>Média:</strong> ${report.servidor.temperatura.media.replace('Â', '')}</td>
                <td><strong>Pico:</strong> ${report.servidor.temperatura.pico.replace('Â', '')}</td>
            </tr>
            <tr><th colspan="3">Sistema</th></tr>
            <tr>
                <td><strong>Tipo:</strong> ${report.servidor.sistema.tipo}</td>
                <td><strong>Plataforma:</strong> ${report.servidor.sistema.plataforma || 'N/A'}</td>
                <td><strong>Arquitetura:</strong> ${report.servidor.sistema.arquitetura || 'N/A'}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>Python Versão:</strong> ${report.servidor.sistema.pythonVersao || 'N/A'}</td>
            </tr>
            ${report.servidor.armazenamento && typeof report.servidor.armazenamento !== 'string' ? `
            <tr><th colspan="3">Armazenamento</th></tr>
            <tr>
                <td><strong>Total:</strong> ${report.servidor.armazenamento.total}</td>
                <td><strong>Usado:</strong> ${report.servidor.armazenamento.usado}</td>
                <td><strong>Livre:</strong> ${report.servidor.armazenamento.livre}</td>
            </tr>` : ''}
            ${report.servidor.detalhesRaspberryPi ? `
            <tr><th colspan="3">Detalhes do Raspberry Pi</th></tr>
            <tr>
                <td><strong>Modelo:</strong> ${report.servidor.detalhesRaspberryPi.modelo}</td>
                <td><strong>Temperatura:</strong> ${report.servidor.detalhesRaspberryPi.temperaturaAtual.replace('Â', '')}</td>
                <td><strong>Estado:</strong> <span class="${report.servidor.detalhesRaspberryPi.estadoTermico.includes('Alerta') ? 'log-error' : 'log-info'}">${report.servidor.detalhesRaspberryPi.estadoTermico}</span></td>
            </tr>` : ''}
            <tr><th colspan="3">Traduções</th></tr>
            <tr>
                <td colspan="3"><strong>Realizadas hoje:</strong> ${report.servidor.traducoesHoje}</td>
            </tr>
        </table>`;
    }

    // Criar tabela HTML com os dados do cliente
    let clientHtml = '<h4>Métricas do Cliente (Navegador)</h4>';
    if (typeof report.computadorLocal.navegador === 'string') {
        clientHtml += `<p>${report.computadorLocal.navegador}</p>`;
    } else {
        clientHtml += `
        <table class="metrics-table">
            <tr><th colspan="3">Navegador</th></tr>
            <tr>
                <td><strong>Plataforma:</strong> ${report.computadorLocal.navegador.plataforma}</td>
                <td><strong>CPU Cores:</strong> ${report.computadorLocal.navegador.nucleosCPU}</td>
                <td><strong>Memória:</strong> ${report.computadorLocal.navegador.memoriaDispositivo}</td>
            </tr>
            <tr>
                <td><strong>Resolução:</strong> ${report.computadorLocal.navegador.resolucao}</td>
                <td><strong>Viewport:</strong> ${report.computadorLocal.navegador.viewport}</td>
                <td><strong>Densidade:</strong> ${report.computadorLocal.navegador.densidadePixels}</td>
            </tr>`;

        if (typeof report.computadorLocal.memoria !== 'string') {
            clientHtml += `
            <tr><th colspan="3">Memória JavaScript</th></tr>
            <tr>
                <td><strong>Atual:</strong> ${report.computadorLocal.memoria.utilizacaoAtual}</td>
                <td><strong>Média:</strong> ${report.computadorLocal.memoria.utilizacaoMedia}</td>
                <td><strong>Pico:</strong> ${report.computadorLocal.memoria.utilizacaoPico}</td>
            </tr>`;
        }

        if (typeof report.computadorLocal.rede !== 'string') {
            clientHtml += `
            <tr><th colspan="3">Rede</th></tr>
            <tr>
                <td><strong>Tipo:</strong> ${report.computadorLocal.rede.tipoConexao}</td>
                <td><strong>Velocidade:</strong> ${report.computadorLocal.rede.velocidade}</td>
                <td><strong>Latência:</strong> ${report.computadorLocal.rede.latencia}</td>
            </tr>`;
        }

        if (typeof report.computadorLocal.desempenho !== 'string') {
            clientHtml += `
            <tr><th colspan="3">Desempenho</th></tr>
            <tr>
                <td><strong>Tempo total:</strong> ${report.computadorLocal.desempenho.tempoCarregamentoTotal}</td>
                <td><strong>Renderização:</strong> ${report.computadorLocal.desempenho.tempoRenderizacao}</td>
                <td><strong>Conexão:</strong> ${report.computadorLocal.desempenho.tempoConexao}</td>
            </tr>`;
        }

        clientHtml += `</table>`;
    }

    // Criar seção para dados comparativos
    let comparativeHtml = '<h4>Métricas Comparativas</h4>';
    if (typeof report.comparativo.traducao === 'string') {
        comparativeHtml += `<p>${report.comparativo.traducao}</p>`;
    } else {
        comparativeHtml += `
        <div class="comparative-box">
            <p><strong>Proporção de memória:</strong> ${report.comparativo.memoriaNavegadorVsServidor}</p>
            <p><strong>Tempo médio de resposta:</strong> ${report.comparativo.traducao.tempoMedioResposta}</p>
            <p><strong>Tempo mínimo de resposta:</strong> ${report.comparativo.traducao.tempoMinimoResposta}</p>
            <p><strong>Tempo máximo de resposta:</strong> ${report.comparativo.traducao.tempoMaximoResposta}</p>
            <p><strong>Throughput:</strong> ${report.comparativo.traducao.throughput}</p>
        </div>`;
    }

    // Atualizar elementos na página
    document.getElementById('server-metrics').innerHTML = serverHtml;
    document.getElementById('client-metrics').innerHTML = clientHtml;
    document.getElementById('comparative-metrics').innerHTML = comparativeHtml;
}

/**
 * Verifica o status do Raspberry Pi e exibe se disponível
 */
function checkRaspberryPiStatus() {
    if (!window.performanceMetrics || !window.performanceMetrics.metrics.serverInfo) {
        return;
    }

    const serverInfo = window.performanceMetrics.metrics.serverInfo;

    // Verificar se é um Raspberry Pi
    if (serverInfo.isRaspberryPi) {
        // Criar ou atualizar seção do Raspberry Pi
        let raspberrySection = document.getElementById('raspberry-pi-status');
        if (!raspberrySection) {
            // Criar nova seção se não existir
            raspberrySection = document.createElement('div');
            raspberrySection.id = 'raspberry-pi-status';
            raspberrySection.className = 'mb-6 p-4 bg-red-50 border border-red-200 rounded-lg';

            // Inserir antes da seção de métricas do sistema
            const systemMetricsSection = document.querySelector('.mt-8.bg-gray-50');
            if (systemMetricsSection) {
                systemMetricsSection.parentNode.insertBefore(raspberrySection, systemMetricsSection);
            } else {
                // Fallback para inserir no final da página
                document.body.appendChild(raspberrySection);
            }
        }

        // Obter temperatura atual
        const temperature = window.performanceMetrics.metrics.temperature &&
            window.performanceMetrics.metrics.temperature.length > 0 ?
            window.performanceMetrics.metrics.temperature[window.performanceMetrics.metrics.temperature.length - 1].value.toFixed(1) :
            null;

        // Calcular estado térmico
        let thermalState = "Normal";
        let stateClass = "text-green-600";

        if (temperature) {
            if (temperature > 75) {
                thermalState = "Crítico - Resfriamento necessário!";
                stateClass = "text-red-600 font-bold";
            } else if (temperature > 65) {
                thermalState = "Alta - Monitorar";
                stateClass = "text-orange-600 font-bold";
            } else if (temperature > 55) {
                thermalState = "Elevada";
                stateClass = "text-yellow-600";
            }
        }

        // Atualizar conteúdo
        raspberrySection.innerHTML = `
            <div class="flex items-start gap-4">
                <div class="text-3xl text-red-600">🍓</div>
                <div class="flex-1">
                    <h3 class="text-lg font-medium mb-2">Raspberry Pi Detectado</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                        <div><strong>Modelo:</strong> ${serverInfo.raspberryPiModel || "Não identificado"}</div>
                        <div><strong>Arquitetura:</strong> ${serverInfo.architecture || "Desconhecida"}</div>
                        <div><strong>Python:</strong> ${serverInfo.pythonVersion || "Versão desconhecida"}</div>
                        <div>
                            <strong>Temperatura:</strong> 
                            ${temperature ? `${temperature}°C <span class="${stateClass}">(${thermalState})</span>` : "Indisponível"}
                        </div>
                    </div>
                    ${window.performanceMetrics.metrics.serverInfo.diskUsage ? `
                    <div class="mt-2">
                        <strong>Armazenamento:</strong> 
                        ${window.performanceMetrics.metrics.serverInfo.diskUsage.used} GB de 
                        ${window.performanceMetrics.metrics.serverInfo.diskUsage.total} GB usado 
                        (${window.performanceMetrics.metrics.serverInfo.diskUsage.percent}%)
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    } else {
        // Remover seção se existir mas não for mais Raspberry Pi
        const raspberrySection = document.getElementById('raspberry-pi-status');
        if (raspberrySection) {
            raspberrySection.remove();
        }
    }
}

// Exportar funções
if (typeof module !== 'undefined') {
    module.exports = {
        formatLogLine,
        createHealthIndicator,
        loadBrowserMetrics,
        loadComparativeReport
    };
}

// Inicializar diagnóstico do navegador quando o documento estiver carregado
document.addEventListener('DOMContentLoaded', function () {
    // Adicionar event listener para o botão de métricas do navegador
    const refreshBrowserMetricsBtn = document.getElementById('refresh-browser-metrics');
    if (refreshBrowserMetricsBtn) {
        refreshBrowserMetricsBtn.addEventListener('click', loadBrowserMetrics);
    }

    // Adicionar event listener para o botão de cópia de métricas
    const copyBrowserMetricsBtn = document.getElementById('copy-browser-metrics');
    if (copyBrowserMetricsBtn) {
        copyBrowserMetricsBtn.addEventListener('click', () => {
            const metricsText = document.getElementById('browser-metrics-full').innerText;
            navigator.clipboard.writeText(metricsText)
                .then(() => alert('Métricas copiadas para a área de transferência!'))
                .catch(err => alert('Erro ao copiar métricas: ' + err));
        });
    }

    // Adicionar event listener para o botão de exportação
    const exportBrowserMetricsBtn = document.getElementById('export-browser-metrics');
    if (exportBrowserMetricsBtn && window.performanceMetrics) {
        exportBrowserMetricsBtn.addEventListener('click', () => {
            window.performanceMetrics.exportBrowserMetrics();
        });
    }

    // Configurar aba de relatório comparativo
    const refreshComparativeBtn = document.getElementById('refresh-comparative');
    if (refreshComparativeBtn) {
        refreshComparativeBtn.addEventListener('click', loadComparativeReport);
    }

    const copyComparativeBtn = document.getElementById('copy-comparative');
    if (copyComparativeBtn) {
        copyComparativeBtn.addEventListener('click', () => {
            const metricsText = document.getElementById('comparative-report-full').innerText;
            navigator.clipboard.writeText(metricsText)
                .then(() => alert('Relatório comparativo copiado para a área de transferência!'))
                .catch(err => alert('Erro ao copiar relatório: ' + err));
        });
    }

    const exportComparativeBtn = document.getElementById('export-comparative-json');
    if (exportComparativeBtn && window.performanceMetrics) {
        exportComparativeBtn.addEventListener('click', () => {
            window.performanceMetrics.exportComparativeReport();
        });
    }

    // Carregar métricas do navegador inicialmente
    setTimeout(loadBrowserMetrics, 1000);

    // Carregar relatório comparativo inicialmente
    setTimeout(loadComparativeReport, 1000);

    // Verificar status do Raspberry Pi na inicialização
    setTimeout(checkRaspberryPiStatus, 1000); // Dar tempo para métricas inicializarem
});

// Verificar status do Raspberry Pi a cada 10 segundos
setInterval(checkRaspberryPiStatus, 10000);
