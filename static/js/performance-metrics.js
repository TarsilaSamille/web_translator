// Arquivo: /static/js/performance-metrics.js
// Sistema de coleta de métricas de desempenho para análise do artigo científico

class PerformanceMetrics {
    constructor() {
        this.metrics = {
            translationTimes: [],
            cpuUsage: [],
            memoryUsage: [],
            temperature: [],
            translationsCount: 0,
            errors: []
        };
        this.startTime = null;
        this.isCollecting = false;
    }

    // Iniciar coleta de métricas
    startCollection() {
        this.isCollecting = true;
        this.startTime = Date.now();
        console.log('🔄 Iniciando coleta de métricas de desempenho...');

        // Coletar métricas do sistema a cada 2 segundos
        this.systemMetricsInterval = setInterval(() => {
            this.collectSystemMetrics();
        }, 2000);

        // Coletar métricas de navegador a cada 5 segundos
        this.browserMetricsInterval = setInterval(() => {
            this.collectBrowserMetrics();
        }, 5000);
    }

    // Parar coleta de métricas
    stopCollection() {
        this.isCollecting = false;
        if (this.systemMetricsInterval) {
            clearInterval(this.systemMetricsInterval);
        }
        if (this.browserMetricsInterval) {
            clearInterval(this.browserMetricsInterval);
        }
        console.log('⏹️ Coleta de métricas interrompida');
    }

    // Coletar métricas do sistema (CPU, memória, temperatura)
    async collectSystemMetrics() {
        try {
            const response = await fetch('/api/system-metrics');
            const data = await response.json();

            if (data.success) {
                this.metrics.cpuUsage.push({
                    timestamp: Date.now(),
                    value: data.cpu_usage
                });

                this.metrics.memoryUsage.push({
                    timestamp: Date.now(),
                    value: data.memory_usage
                });

                this.metrics.temperature.push({
                    timestamp: Date.now(),
                    value: data.temperature
                });

                this.metrics.translationsCount = data.translations_today;

                // Manter apenas os últimos 100 pontos de dados
                if (this.metrics.cpuUsage.length > 100) {
                    this.metrics.cpuUsage.shift();
                    this.metrics.memoryUsage.shift();
                    this.metrics.temperature.shift();
                }
            }
        } catch (error) {
            console.error('Erro ao coletar métricas do sistema:', error);
            this.metrics.errors.push({
                timestamp: Date.now(),
                error: error.message,
                type: 'system_metrics'
            });
        }
    }

    // Coletar métricas do navegador
    collectBrowserMetrics() {
        try {
            // Métricas de performance do navegador
            if (performance.memory) {
                const memoryInfo = {
                    timestamp: Date.now(),
                    usedJSHeapSize: performance.memory.usedJSHeapSize,
                    totalJSHeapSize: performance.memory.totalJSHeapSize,
                    jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                };

                if (!this.metrics.browserMemory) {
                    this.metrics.browserMemory = [];
                }
                this.metrics.browserMemory.push(memoryInfo);

                // Manter apenas os últimos 50 pontos
                if (this.metrics.browserMemory.length > 50) {
                    this.metrics.browserMemory.shift();
                }
            }

            // Métricas de conexão de rede
            if (navigator.connection) {
                const connectionInfo = {
                    timestamp: Date.now(),
                    effectiveType: navigator.connection.effectiveType,
                    downlink: navigator.connection.downlink,
                    rtt: navigator.connection.rtt
                };

                if (!this.metrics.networkConnection) {
                    this.metrics.networkConnection = [];
                }
                this.metrics.networkConnection.push(connectionInfo);

                if (this.metrics.networkConnection.length > 50) {
                    this.metrics.networkConnection.shift();
                }
            }

        } catch (error) {
            console.error('Erro ao coletar métricas do navegador:', error);
            this.metrics.errors.push({
                timestamp: Date.now(),
                error: error.message,
                type: 'browser_metrics'
            });
        }
    }

    // Registrar tempo de tradução
    recordTranslationTime(startTime, endTime, sourceLength, targetLength, modelId) {
        const translationTime = endTime - startTime;

        this.metrics.translationTimes.push({
            timestamp: endTime,
            responseTime: translationTime,
            sourceLength: sourceLength,
            targetLength: targetLength,
            modelId: modelId,
            wordsPerSecond: sourceLength / (translationTime / 1000)
        });

        console.log(`📊 Tradução registrada: ${translationTime}ms para ${sourceLength} caracteres`);
    }

    // Gerar relatório de métricas
    generateReport() {
        const report = {
            collectionPeriod: {
                start: this.startTime,
                end: Date.now(),
                duration: Date.now() - this.startTime
            },
            translationMetrics: this.calculateTranslationMetrics(),
            systemMetrics: this.calculateSystemMetrics(),
            browserMetrics: this.calculateBrowserMetrics(),
            errors: this.metrics.errors
        };

        return report;
    }

    // Calcular métricas de tradução
    calculateTranslationMetrics() {
        if (this.metrics.translationTimes.length === 0) {
            return null;
        }

        const times = this.metrics.translationTimes.map(t => t.responseTime);
        const lengths = this.metrics.translationTimes.map(t => t.sourceLength);

        return {
            totalTranslations: this.metrics.translationTimes.length,
            averageResponseTime: times.reduce((a, b) => a + b, 0) / times.length,
            minResponseTime: Math.min(...times),
            maxResponseTime: Math.max(...times),
            medianResponseTime: this.calculateMedian(times),
            averageTextLength: lengths.reduce((a, b) => a + b, 0) / lengths.length,
            throughput: this.metrics.translationTimes.length / ((Date.now() - this.startTime) / 1000 / 60) // traduções por minuto
        };
    }

    // Calcular métricas do sistema
    calculateSystemMetrics() {
        if (this.metrics.cpuUsage.length === 0) {
            return null;
        }

        const cpuValues = this.metrics.cpuUsage.map(c => c.value);
        const memoryValues = this.metrics.memoryUsage.map(m => m.value);
        const tempValues = this.metrics.temperature.map(t => t.value);

        return {
            cpu: {
                average: cpuValues.reduce((a, b) => a + b, 0) / cpuValues.length,
                min: Math.min(...cpuValues),
                max: Math.max(...cpuValues),
                median: this.calculateMedian(cpuValues)
            },
            memory: {
                average: memoryValues.reduce((a, b) => a + b, 0) / memoryValues.length,
                min: Math.min(...memoryValues),
                max: Math.max(...memoryValues),
                median: this.calculateMedian(memoryValues)
            },
            temperature: {
                average: tempValues.reduce((a, b) => a + b, 0) / tempValues.length,
                min: Math.min(...tempValues),
                max: Math.max(...tempValues),
                median: this.calculateMedian(tempValues)
            }
        };
    }

    // Calcular métricas do navegador
    calculateBrowserMetrics() {
        if (!this.metrics.browserMemory || this.metrics.browserMemory.length === 0) {
            return null;
        }

        const jsHeapSizes = this.metrics.browserMemory.map(m => m.usedJSHeapSize);

        return {
            jsHeapMemory: {
                average: jsHeapSizes.reduce((a, b) => a + b, 0) / jsHeapSizes.length,
                min: Math.min(...jsHeapSizes),
                max: Math.max(...jsHeapSizes),
                median: this.calculateMedian(jsHeapSizes)
            },
            networkConnection: this.metrics.networkConnection
        };
    }

    // Calcular mediana
    calculateMedian(values) {
        const sorted = values.slice().sort((a, b) => a - b);
        const middle = Math.floor(sorted.length / 2);

        if (sorted.length % 2 === 0) {
            return (sorted[middle - 1] + sorted[middle]) / 2;
        } else {
            return sorted[middle];
        }
    }

    // Exportar dados para análise
    exportData() {
        const report = this.generateReport();
        const dataStr = JSON.stringify(report, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });

        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `performance-metrics-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        console.log('📁 Métricas exportadas para arquivo JSON');
    }

    // Exibir relatório no console
    logReport() {
        const report = this.generateReport();
        console.log('📊 RELATÓRIO DE MÉTRICAS DE DESEMPENHO');
        console.log('=====================================');
        console.log(report);

        if (report.translationMetrics) {
            console.log(`✅ Traduções realizadas: ${report.translationMetrics.totalTranslations}`);
            console.log(`⏱️ Tempo médio de resposta: ${report.translationMetrics.averageResponseTime.toFixed(2)}ms`);
            console.log(`🔄 Throughput: ${report.translationMetrics.throughput.toFixed(2)} traduções/minuto`);
        }

        if (report.systemMetrics) {
            console.log(`💻 CPU médio: ${report.systemMetrics.cpu.average.toFixed(2)}%`);
            console.log(`🧠 Memória média: ${report.systemMetrics.memory.average.toFixed(2)}MB`);
            console.log(`🌡️ Temperatura média: ${report.systemMetrics.temperature.average.toFixed(2)}°C`);
        }
    }
}

// Instância global para coleta de métricas
window.performanceMetrics = new PerformanceMetrics();

// Eventos do documento
document.addEventListener('DOMContentLoaded', function () {
    // Iniciar coleta automaticamente
    window.performanceMetrics.startCollection();

    // Adicionar botões para controle das métricas
    const metricsControls = document.createElement('div');
    metricsControls.innerHTML = `
        <div class="mt-4 text-center">
            <button id="export-metrics" class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors mr-2">
                <i class="fas fa-download mr-2"></i>Exportar Métricas
            </button>
            <button id="log-report" class="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                <i class="fas fa-chart-line mr-2"></i>Ver Relatório
            </button>
        </div>
    `;

    const metricsSection = document.querySelector('.mt-8.bg-gray-50');
    if (metricsSection) {
        metricsSection.appendChild(metricsControls);

        // Event listeners para os botões
        document.getElementById('export-metrics').addEventListener('click', () => {
            window.performanceMetrics.exportData();
        });

        document.getElementById('log-report').addEventListener('click', () => {
            window.performanceMetrics.logReport();
        });
    }
});

// Integração com o sistema de tradução existente
window.addEventListener('beforeunload', function () {
    window.performanceMetrics.stopCollection();
});
