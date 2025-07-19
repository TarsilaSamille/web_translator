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

        // Inicializar rastreamento de interações do usuário
        this.setupUserInteractionTracking();
    }

    // Configurar rastreamento de interações do usuário
    setupUserInteractionTracking() {
        // Inicializar métricas de interação do usuário
        if (!this.metrics.userInteractions) {
            this.metrics.userInteractions = {
                clicks: 0,
                keyPresses: 0,
                scrollEvents: 0,
                formSubmissions: 0,
                textSelections: 0,
                inputEvents: 0,
                lastActivity: Date.now(),
                sessions: [{
                    startTime: Date.now(),
                    endTime: null
                }]
            };
        }

        // Rastrear cliques
        document.addEventListener('click', () => {
            if (this.isCollecting) {
                this.metrics.userInteractions.clicks++;
                this.updateUserActivity();
            }
        });

        // Rastrear teclas pressionadas
        document.addEventListener('keydown', () => {
            if (this.isCollecting) {
                this.metrics.userInteractions.keyPresses++;
                this.updateUserActivity();
            }
        });

        // Rastrear eventos de rolagem
        document.addEventListener('scroll', () => {
            if (this.isCollecting) {
                this.metrics.userInteractions.scrollEvents++;
                this.updateUserActivity();
            }
        }, { passive: true });

        // Rastrear envios de formulário
        document.addEventListener('submit', () => {
            if (this.isCollecting) {
                this.metrics.userInteractions.formSubmissions++;
                this.updateUserActivity();
            }
        });

        // Rastrear seleções de texto
        document.addEventListener('selectionchange', () => {
            if (this.isCollecting && document.getSelection().toString().length > 0) {
                this.metrics.userInteractions.textSelections++;
                this.updateUserActivity();
            }
        });

        // Rastrear eventos de entrada
        document.addEventListener('input', () => {
            if (this.isCollecting) {
                this.metrics.userInteractions.inputEvents++;
                this.updateUserActivity();
            }
        });

        // Verificar inatividade a cada 30 segundos
        this.inactivityCheckInterval = setInterval(() => {
            if (this.isCollecting) {
                const inactiveThreshold = 60000; // 60 segundos
                const now = Date.now();

                if (now - this.metrics.userInteractions.lastActivity > inactiveThreshold) {
                    // Fechar a sessão atual e iniciar uma nova quando o usuário retornar
                    const currentSession = this.metrics.userInteractions.sessions[
                        this.metrics.userInteractions.sessions.length - 1
                    ];

                    if (currentSession && !currentSession.endTime) {
                        currentSession.endTime = this.metrics.userInteractions.lastActivity;
                    }
                }
            }
        }, 30000);
    }

    // Atualizar timestamp da última atividade do usuário
    updateUserActivity() {
        const now = Date.now();
        const lastActivity = this.metrics.userInteractions.lastActivity;
        const inactiveThreshold = 60000; // 60 segundos

        this.metrics.userInteractions.lastActivity = now;

        // Se estava inativo, inicie nova sessão
        if (now - lastActivity > inactiveThreshold) {
            this.metrics.userInteractions.sessions.push({
                startTime: now,
                endTime: null
            });
        }
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
        if (this.inactivityCheckInterval) {
            clearInterval(this.inactivityCheckInterval);
        }

        // Fechar sessão atual
        if (this.metrics.userInteractions) {
            const currentSession = this.metrics.userInteractions.sessions[
                this.metrics.userInteractions.sessions.length - 1
            ];
            if (currentSession && !currentSession.endTime) {
                currentSession.endTime = Date.now();
            }
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

                // Salvar informações do servidor
                if (!this.metrics.serverInfo) {
                    this.metrics.serverInfo = {};
                }

                // Atualizar informações do servidor
                this.metrics.serverInfo = {
                    platform: data.platform || "Desconhecido",
                    architecture: data.architecture || "Desconhecido",
                    isRaspberryPi: !!data.is_raspberry_pi,
                    raspberryPiModel: data.raspberry_pi_model || null,
                    pythonVersion: data.python_version || "Desconhecido",
                    encoding: data.encoding || "utf-8",
                    timestamp: Date.now()
                };

                // Adicionar informações de disco se disponíveis
                if (data.disk_usage) {
                    this.metrics.serverInfo.diskUsage = data.disk_usage;
                }

                // Atualizar os botões de métricas na interface
                this.updateMetricsButtons();

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
            // Métricas de memória do navegador
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
                    rtt: navigator.connection.rtt,
                    saveData: navigator.connection.saveData
                };

                if (!this.metrics.networkConnection) {
                    this.metrics.networkConnection = [];
                }
                this.metrics.networkConnection.push(connectionInfo);

                if (this.metrics.networkConnection.length > 50) {
                    this.metrics.networkConnection.shift();
                }
            }

            // Métricas de performance do navegador
            if (window.performance && window.performance.timing) {
                if (!this.metrics.pagePerformance) {
                    const timing = performance.timing;
                    this.metrics.pagePerformance = {
                        navigationStart: timing.navigationStart,
                        loadEventEnd: timing.loadEventEnd,
                        domComplete: timing.domComplete,
                        domInteractive: timing.domInteractive,
                        responseEnd: timing.responseEnd,
                        responseStart: timing.responseStart,
                        connectEnd: timing.connectEnd,
                        connectStart: timing.connectStart,
                        domainLookupEnd: timing.domainLookupEnd,
                        domainLookupStart: timing.domainLookupStart,
                        redirectEnd: timing.redirectEnd,
                        redirectStart: timing.redirectStart
                    };
                }
            }

            // Coletar dados do cliente
            if (!this.metrics.clientInfo) {
                this.metrics.clientInfo = {
                    userAgent: navigator.userAgent,
                    platform: navigator.platform,
                    language: navigator.language,
                    cookiesEnabled: navigator.cookieEnabled,
                    devicePixelRatio: window.devicePixelRatio,
                    screenWidth: window.screen.width,
                    screenHeight: window.screen.height,
                    viewportWidth: window.innerWidth,
                    viewportHeight: window.innerHeight
                };
            }

            // Coletar métricas de recursos
            if (performance.getEntriesByType) {
                const resources = performance.getEntriesByType('resource');

                if (!this.metrics.resourceMetrics) {
                    this.metrics.resourceMetrics = {
                        count: 0,
                        totalSize: 0,
                        totalDuration: 0,
                        byType: {}
                    };
                }

                // Analisar recursos carregados recentemente
                const newResources = resources.slice(this.metrics.resourceMetrics.count);

                for (const resource of newResources) {
                    this.metrics.resourceMetrics.count++;
                    this.metrics.resourceMetrics.totalDuration += resource.duration;

                    // Categorizar por tipo
                    const type = resource.initiatorType;
                    if (!this.metrics.resourceMetrics.byType[type]) {
                        this.metrics.resourceMetrics.byType[type] = {
                            count: 0,
                            totalDuration: 0
                        };
                    }

                    this.metrics.resourceMetrics.byType[type].count++;
                    this.metrics.resourceMetrics.byType[type].totalDuration += resource.duration;
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

    // Gerar relatório comparativo detalhado entre servidor e cliente
    generateComparativeReport() {
        const report = {
            timestamp: new Date().toISOString(),
            collectionPeriod: {
                start: new Date(this.startTime).toISOString(),
                end: new Date().toISOString(),
                durationMs: Date.now() - this.startTime
            },
            servidor: {
                descricao: "Métricas do servidor que executa os modelos de tradução",
                cpu: this.metrics.cpuUsage.length > 0 ? {
                    utilizacaoAtual: this.metrics.cpuUsage[this.metrics.cpuUsage.length - 1].value + "%",
                    utilizacaoMedia: this.calculateSystemMetrics()?.cpu.average.toFixed(1) + "%",
                    utilizacaoPico: this.calculateSystemMetrics()?.cpu.max.toFixed(1) + "%"
                } : "Dados não disponíveis",
                memoria: this.metrics.memoryUsage.length > 0 ? {
                    utilizacaoAtual: (this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1].value).toFixed(1) + " MB",
                    utilizacaoMedia: this.calculateSystemMetrics()?.memory.average.toFixed(1) + " MB",
                    utilizacaoPico: this.calculateSystemMetrics()?.memory.max.toFixed(1) + " MB"
                } : "Dados não disponíveis",
                temperatura: this.metrics.temperature.length > 0 ? {
                    atual: this.metrics.temperature[this.metrics.temperature.length - 1].value.toFixed(1) + "°C",
                    media: this.calculateSystemMetrics()?.temperature.average.toFixed(1) + "°C",
                    pico: this.calculateSystemMetrics()?.temperature.max.toFixed(1) + "°C"
                } : "Dados não disponíveis",
                traducoesHoje: this.metrics.translationsCount || 0,
                sistema: {
                    tipo: this.metrics.serverInfo?.isRaspberryPi ?
                        `Servidor Backend (Raspberry Pi ${this.metrics.serverInfo.raspberryPiModel || ""})` :
                        "Servidor Backend",
                    plataforma: this.metrics.serverInfo?.platform || "Desconhecido",
                    arquitetura: this.metrics.serverInfo?.architecture || "Desconhecida",
                    pythonVersao: this.metrics.serverInfo?.pythonVersion || "Desconhecida",
                    encoding: this.metrics.serverInfo?.encoding || "utf-8",
                    processamento: "Dedicado para inferência de modelos"
                },
                armazenamento: this.metrics.serverInfo?.diskUsage ? {
                    total: `${this.metrics.serverInfo.diskUsage.total} GB`,
                    usado: `${this.metrics.serverInfo.diskUsage.used} GB (${this.metrics.serverInfo.diskUsage.percent}%)`,
                    livre: `${this.metrics.serverInfo.diskUsage.free} GB`
                } : "Dados de armazenamento não disponíveis",
                detalhesRaspberryPi: this.metrics.serverInfo?.isRaspberryPi ? {
                    modelo: this.metrics.serverInfo.raspberryPiModel || "Modelo não detectado",
                    temperaturaAtual: this.metrics.temperature.length > 0 ?
                        this.metrics.temperature[this.metrics.temperature.length - 1].value.toFixed(1) + "°C" : "N/A",
                    estadoTermico: this.metrics.temperature.length > 0 ?
                        (this.metrics.temperature[this.metrics.temperature.length - 1].value > 70 ?
                            "Alerta: Alta temperatura!" : "Normal") : "N/A"
                } : null
            },
            computadorLocal: {
                descricao: "Métricas do navegador do cliente que acessa o serviço",
                navegador: this.metrics.clientInfo ? {
                    userAgent: this.metrics.clientInfo.userAgent,
                    plataforma: this.metrics.clientInfo.platform,
                    idioma: this.metrics.clientInfo.language,
                    resolucao: `${this.metrics.clientInfo.screenWidth}x${this.metrics.clientInfo.screenHeight}`,
                    viewport: `${this.metrics.clientInfo.viewportWidth}x${this.metrics.clientInfo.viewportHeight}`,
                    densidadePixels: this.metrics.clientInfo.devicePixelRatio,
                    nucleosCPU: navigator.hardwareConcurrency || "N/A",
                    memoriaDispositivo: navigator.deviceMemory ?
                        `${navigator.deviceMemory} GB` : "Não disponível",
                    sistema: {
                        tipo: "Cliente (Navegador)",
                        arquitetura: "JavaScript frontend",
                        processamento: "Interface de usuário e comunicação com API"
                    }
                } : "Dados do navegador não disponíveis",
                memoria: this.metrics.browserMemory && this.metrics.browserMemory.length > 0 ? {
                    utilizacaoAtual: (this.metrics.browserMemory[this.metrics.browserMemory.length - 1].usedJSHeapSize / 1024 / 1024).toFixed(1) + " MB",
                    utilizacaoMedia: this.calculateBrowserMetrics()?.jsHeapMemory.averageMB.toFixed(1) + " MB",
                    utilizacaoPico: this.calculateBrowserMetrics()?.jsHeapMemory.maxMB.toFixed(1) + " MB",
                    percentualUtilizado: this.calculateBrowserMetrics()?.jsHeapMemory.averagePercent.toFixed(1) + "%"
                } : "Dados de memória do navegador não disponíveis",
                rede: this.metrics.networkConnection && this.metrics.networkConnection.length > 0 ? {
                    tipoConexao: this.metrics.networkConnection[this.metrics.networkConnection.length - 1].effectiveType,
                    velocidade: this.metrics.networkConnection[this.metrics.networkConnection.length - 1].downlink + " Mbps",
                    latencia: this.metrics.networkConnection[this.metrics.networkConnection.length - 1].rtt + " ms",
                    economizadorDados: this.metrics.networkConnection[this.metrics.networkConnection.length - 1].saveData ? "Ativado" : "Desativado"
                } : "Dados de rede não disponíveis",
                desempenho: this.metrics.pagePerformance ? {
                    tempoCarregamentoTotal: (this.metrics.pagePerformance.loadEventEnd - this.metrics.pagePerformance.navigationStart) + " ms",
                    tempoRenderizacao: (this.metrics.pagePerformance.domComplete - this.metrics.pagePerformance.responseEnd) + " ms",
                    tempoConexao: (this.metrics.pagePerformance.connectEnd - this.metrics.pagePerformance.connectStart) + " ms"
                } : "Dados de desempenho não disponíveis",
                interacao: this.metrics.userInteractions ? {
                    cliques: this.metrics.userInteractions.clicks,
                    teclasPressionadas: this.metrics.userInteractions.keyPresses,
                    eventosRolagem: this.metrics.userInteractions.scrollEvents,
                    enviosFormulario: this.metrics.userInteractions.formSubmissions,
                    numSessoes: this.metrics.userInteractions.sessions ? this.metrics.userInteractions.sessions.length : 0
                } : "Dados de interação não disponíveis",
                recursos: this.metrics.resourceMetrics ? {
                    totalRecursosCarregados: this.metrics.resourceMetrics.count,
                    tempoMedioCarregamento: (this.metrics.resourceMetrics.totalDuration / Math.max(1, this.metrics.resourceMetrics.count)).toFixed(1) + " ms"
                } : "Dados de recursos não disponíveis"
            },
            comparativo: {
                traducao: this.metrics.translationTimes && this.metrics.translationTimes.length > 0 ? {
                    tempoMedioResposta: this.calculateTranslationMetrics()?.averageResponseTime.toFixed(1) + " ms",
                    tempoMinimoResposta: this.calculateTranslationMetrics()?.minResponseTime + " ms",
                    tempoMaximoResposta: this.calculateTranslationMetrics()?.maxResponseTime + " ms",
                    throughput: this.calculateTranslationMetrics()?.throughput.toFixed(2) + " traduções/minuto"
                } : "Dados de tradução não disponíveis",
                memoriaNavegadorVsServidor: this.metrics.browserMemory && this.metrics.browserMemory.length > 0 &&
                    this.metrics.memoryUsage && this.metrics.memoryUsage.length > 0 ?
                    `O navegador está usando aproximadamente ${((this.calculateBrowserMetrics().jsHeapMemory.averageMB * 1024 * 1024) /
                        this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1].value * 100).toFixed(2)}% 
                     da memória que o servidor está usando` : "Comparação não disponível",
                resumo: {
                    titulo: "Distribuição de Processamento",
                    descricao: "O servidor realiza o processamento intensivo dos modelos neurais de tradução, consumindo " +
                        "mais recursos computacionais, enquanto o navegador (cliente) é responsável pela interface de " +
                        "usuário e comunicação com a API, utilizando menos recursos.",
                    conclusao: "Este é um modelo de processamento cliente-servidor típico, onde o processamento pesado " +
                        "dos modelos de tradução é feito no servidor, economizando recursos do dispositivo do cliente."
                }
            }
        };

        return report;
    }

    // Gerar relatório específico do navegador para exportação
    generateBrowserReport() {
        const browserMetrics = this.calculateBrowserMetrics();

        if (!browserMetrics) {
            return {
                error: "Nenhuma métrica do navegador disponível",
                collectionStatus: this.isCollecting ? "Ativo" : "Inativo",
                timestamp: new Date().toISOString()
            };
        }

        // Adicionar informações do sistema operacional
        if (!browserMetrics.clientInfo) {
            browserMetrics.clientInfo = {};
        }

        browserMetrics.clientInfo.cpuCores = navigator.hardwareConcurrency || "N/A";
        browserMetrics.clientInfo.deviceMemory = navigator.deviceMemory ?
            `${navigator.deviceMemory} GB` : "N/A";
        browserMetrics.clientInfo.pdfViewerEnabled = navigator.pdfViewerEnabled || "N/A";

        // Adicionar indicadores de performance
        const performance_score = this.calculatePerformanceScore(browserMetrics);

        return {
            collectionPeriod: {
                start: this.startTime,
                end: Date.now(),
                duration: Date.now() - this.startTime
            },
            metrics: browserMetrics,
            performanceScore: performance_score,
            timestamp: new Date().toISOString(),
            comparedToServer: {
                memoryRatio: browserMetrics.jsHeapMemory ?
                    (this.metrics.memoryUsage.length > 0 ?
                        (browserMetrics.jsHeapMemory.averageMB * 1024 * 1024) / this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1].value :
                        "N/A") :
                    "N/A",
                description: "Proporção entre uso de memória no navegador e no servidor"
            }
        };
    }

    // Calcular pontuação de performance do navegador (0-100)
    calculatePerformanceScore(browserMetrics) {
        let score = 0;
        let components = 0;

        // Pontuação para memória (menor é melhor)
        if (browserMetrics.jsHeapMemory) {
            // Uso máximo de memória como % do limite (menor é melhor)
            const memoryScore = Math.max(0, 100 - browserMetrics.jsHeapMemory.maxPercent);
            score += memoryScore;
            components++;
        }

        // Pontuação para rede (maior é melhor)
        if (browserMetrics.networkConnection) {
            // Classificação de conexão
            let networkScore = 0;
            switch (browserMetrics.networkConnection.effectiveType) {
                case 'slow-2g':
                    networkScore = 25;
                    break;
                case '2g':
                    networkScore = 50;
                    break;
                case '3g':
                    networkScore = 75;
                    break;
                case '4g':
                    networkScore = 100;
                    break;
                default:
                    networkScore = 50;
            }

            // Ajustar baseado na latência (menor é melhor)
            if (browserMetrics.networkConnection.rttMs) {
                const rttScore = Math.max(0, 100 - (browserMetrics.networkConnection.rttMs / 10));
                networkScore = (networkScore + rttScore) / 2;
            }

            score += networkScore;
            components++;
        }

        // Pontuação para tempo de carregamento (menor é melhor)
        if (browserMetrics.pageLoad) {
            // Tempo total de carregamento (escala: 0-5000ms)
            const loadTimeScore = Math.max(0, 100 - (browserMetrics.pageLoad.totalLoadTime / 50));
            score += loadTimeScore;
            components++;
        }

        // Pontuação para recursos (menor é melhor)
        if (browserMetrics.resources && browserMetrics.resources.avgDuration) {
            // Tempo médio de carregamento dos recursos (escala: 0-500ms)
            const resourceScore = Math.max(0, 100 - (browserMetrics.resources.avgDuration / 5));
            score += resourceScore;
            components++;
        }

        // Calcular média das pontuações
        return components > 0 ? Math.round(score / components) : 0;
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
        const jsHeapPercents = this.metrics.browserMemory.map(m =>
            (m.usedJSHeapSize / m.jsHeapSizeLimit) * 100);

        const browserMetrics = {
            jsHeapMemory: {
                // Valores em MB para melhor legibilidade
                averageMB: (jsHeapSizes.reduce((a, b) => a + b, 0) / jsHeapSizes.length) / (1024 * 1024),
                minMB: Math.min(...jsHeapSizes) / (1024 * 1024),
                maxMB: Math.max(...jsHeapSizes) / (1024 * 1024),
                medianMB: this.calculateMedian(jsHeapSizes) / (1024 * 1024),
                // Porcentagem de uso em relação ao limite
                averagePercent: jsHeapPercents.reduce((a, b) => a + b, 0) / jsHeapPercents.length,
                maxPercent: Math.max(...jsHeapPercents)
            }
        };

        // Adicionar métricas de rede se disponíveis
        if (this.metrics.networkConnection && this.metrics.networkConnection.length > 0) {
            const latestConnection = this.metrics.networkConnection[this.metrics.networkConnection.length - 1];

            browserMetrics.networkConnection = {
                effectiveType: latestConnection.effectiveType,
                downlinkMbps: latestConnection.downlink,
                rttMs: latestConnection.rtt,
                saveData: latestConnection.saveData
            };
        }

        // Adicionar métricas de performance da página se disponíveis
        if (this.metrics.pagePerformance) {
            const timing = this.metrics.pagePerformance;

            browserMetrics.pageLoad = {
                totalLoadTime: timing.loadEventEnd - timing.navigationStart,
                domInteractiveTime: timing.domInteractive - timing.navigationStart,
                domCompleteTime: timing.domComplete - timing.navigationStart,
                dnsLookupTime: timing.domainLookupEnd - timing.domainLookupStart,
                tcpConnectTime: timing.connectEnd - timing.connectStart,
                responseTime: timing.responseEnd - timing.responseStart,
                processingTime: timing.domComplete - timing.responseEnd,
                redirectTime: timing.redirectEnd - timing.redirectStart
            };
        }

        // Adicionar informações do cliente
        if (this.metrics.clientInfo) {
            browserMetrics.clientInfo = this.metrics.clientInfo;
        }

        // Adicionar métricas de recursos
        if (this.metrics.resourceMetrics) {
            browserMetrics.resources = {
                count: this.metrics.resourceMetrics.count,
                totalDuration: this.metrics.resourceMetrics.totalDuration,
                avgDuration: this.metrics.resourceMetrics.totalDuration /
                    Math.max(1, this.metrics.resourceMetrics.count),
                byType: this.metrics.resourceMetrics.byType
            };
        }

        // Informações de interação do usuário
        if (this.metrics.userInteractions) {
            browserMetrics.userInteractions = this.metrics.userInteractions;
        }

        return browserMetrics;
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
        // Limpar caracteres especiais
        const cleanReport = this.cleanSpecialChars(report);

        // Adicionar BOM (Byte Order Mark) para garantir que o arquivo seja reconhecido como UTF-8
        const BOM = new Uint8Array([0xEF, 0xBB, 0xBF]);
        const dataStr = JSON.stringify(cleanReport, null, 2);
        const dataBlob = new Blob([BOM, dataStr], { type: 'application/json;charset=utf-8' });

        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `performance-metrics-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        console.log('📁 Métricas exportadas para arquivo JSON com codificação UTF-8');
    }

    // Exportar apenas métricas do navegador
    exportBrowserMetrics() {
        const report = this.generateBrowserReport();
        // Limpar caracteres especiais
        const cleanReport = this.cleanSpecialChars(report);

        // Adicionar BOM (Byte Order Mark) para garantir que o arquivo seja reconhecido como UTF-8
        const BOM = new Uint8Array([0xEF, 0xBB, 0xBF]);
        const dataStr = JSON.stringify(cleanReport, null, 2);
        const dataBlob = new Blob([BOM, dataStr], { type: 'application/json;charset=utf-8' });

        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `browser-metrics-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        console.log('📁 Métricas do navegador exportadas para arquivo JSON com codificação UTF-8');
    }

    // Exportar relatório comparativo detalhado entre servidor e cliente
    exportComparativeReport() {
        const report = this.generateComparativeReport();

        // Tratar problemas de codificação antes de exportar
        const cleanReport = this.cleanSpecialChars(report);

        // Usar UTF-8 explicitamente para garantir a codificação correta de caracteres especiais
        const dataStr = JSON.stringify(cleanReport, null, 2);

        // Adicionar BOM (Byte Order Mark) para garantir que o arquivo seja reconhecido como UTF-8
        const BOM = new Uint8Array([0xEF, 0xBB, 0xBF]);
        const dataBlob = new Blob([BOM, dataStr], { type: 'application/json;charset=utf-8' });

        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `comparativo-servidor-cliente-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        console.log('📁 Relatório comparativo servidor-cliente exportado para arquivo JSON');
        return report;
    }

    // Exportar métricas do servidor (funcionando com Raspberry Pi ou qualquer outro servidor)
    exportServerMetrics() {
        // Extrair e exportar apenas os dados específicos do servidor
        const report = this.generateComparativeReport();

        // Detectar tipo de dispositivo para nomear o arquivo
        const isRaspberryPi = this.metrics.serverInfo?.isRaspberryPi;
        const deviceName = isRaspberryPi ? 'raspberry-pi' :
            this.metrics.serverInfo?.platform === 'Darwin' ? 'mac' :
                this.metrics.serverInfo?.platform === 'Windows' ? 'windows' :
                    this.metrics.serverInfo?.platform === 'Linux' ? 'linux' : 'dispositivo';

        // Construir relatório
        const serverData = {
            timestamp: new Date().toISOString(),
            servidor: {
                tipo: this.metrics.serverInfo?.isRaspberryPi ? 'Raspberry Pi' : this.metrics.serverInfo?.platform || 'Desconhecido',
                modelo: isRaspberryPi ? (this.metrics.serverInfo?.raspberryPiModel || "Modelo não detectado") :
                    this.metrics.serverInfo?.architecture || "Arquitetura não detectada",
                temperatura: report.servidor.temperatura,
                cpu: report.servidor.cpu,
                memoria: report.servidor.memoria,
                armazenamento: report.servidor.armazenamento,
                sistema: report.servidor.sistema
            }
        };

        // Adicionar dados específicos do Raspberry Pi se disponíveis
        if (isRaspberryPi && report.servidor.detalhesRaspberryPi) {
            serverData.servidor.detalhesRaspberryPi = report.servidor.detalhesRaspberryPi;
        }

        // Limpar caracteres especiais e exportar
        const cleanReport = this.cleanSpecialChars(serverData);
        const BOM = new Uint8Array([0xEF, 0xBB, 0xBF]);
        const dataStr = JSON.stringify(cleanReport, null, 2);
        const dataBlob = new Blob([BOM, dataStr], { type: 'application/json;charset=utf-8' });

        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${deviceName}-metrics-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        console.log(`📁 Métricas do servidor ${isRaspberryPi ? '(Raspberry Pi)' : ''} exportadas para arquivo JSON`);
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

    // Exibir relatório comparativo no console
    logComparativeReport() {
        const report = this.generateComparativeReport();
        console.log('📊 RELATÓRIO COMPARATIVO SERVIDOR-CLIENTE');
        console.log('=======================================');
        console.log(report);

        console.log('\n📡 SERVIDOR (Execução dos modelos de tradução):');
        console.log(`CPU: ${report.servidor.cpu.utilizacaoMedia} (média), ${report.servidor.cpu.utilizacaoPico} (pico)`);
        console.log(`Memória: ${report.servidor.memoria.utilizacaoMedia} (média), ${report.servidor.memoria.utilizacaoPico} (pico)`);
        console.log(`Temperatura: ${report.servidor.temperatura.media} (média), ${report.servidor.temperatura.pico} (pico)`);

        console.log('\n💻 COMPUTADOR LOCAL (Navegador do cliente):');
        if (typeof report.computadorLocal.navegador !== 'string') {
            console.log(`Navegador: ${report.computadorLocal.navegador.plataforma}, ${report.computadorLocal.navegador.nucleosCPU} núcleos`);
            console.log(`Memória JS: ${report.computadorLocal.memoria.utilizacaoMedia} (média), ${report.computadorLocal.memoria.utilizacaoPico} (pico)`);
            console.log(`Conexão: ${report.computadorLocal.rede.tipoConexao}, ${report.computadorLocal.rede.velocidade}, ${report.computadorLocal.rede.latencia} latência`);
        }

        console.log('\n⚖️ COMPARATIVO:');
        console.log(report.comparativo.memoriaNavegadorVsServidor);

        return report;
    }

    // Função auxiliar para remover caracteres problemáticos e normalizar acentos
    cleanSpecialChars(obj) {
        // Se for string, limpar caracteres problemáticos
        if (typeof obj === 'string') {
            // Remover Â indesejado que às vezes aparece antes de acentos
            return obj.replace(/Â/g, '')
                // Normalizar acentos
                .normalize('NFC');
        }

        // Se for array, aplicar recursivamente em cada elemento
        if (Array.isArray(obj)) {
            return obj.map(item => this.cleanSpecialChars(item));
        }

        // Se for objeto, aplicar recursivamente em cada propriedade
        if (obj !== null && typeof obj === 'object') {
            const result = {};
            for (const [key, value] of Object.entries(obj)) {
                result[key] = this.cleanSpecialChars(value);
            }
            return result;
        }

        // Outros tipos de dados retornam sem alteração
        return obj;
    }

    // Função para atualizar os botões de métricas quando informações do servidor estiverem disponíveis
    updateMetricsButtons() {
        // Atualizar o texto do botão de exportação do servidor com base no tipo de servidor
        const serverButton = document.getElementById('export-server');

        if (serverButton && this.metrics.serverInfo) {
            const isRaspberryPi = this.metrics.serverInfo?.isRaspberryPi;

            // Customizar texto do botão baseado no tipo de servidor
            if (isRaspberryPi) {
                serverButton.innerHTML = '<i class="fas fa-microchip mr-2"></i>Dados do Raspberry Pi';
                serverButton.title = `Exportar métricas do Raspberry Pi ${this.metrics.serverInfo?.raspberryPiModel || ''}`;
            } else if (this.metrics.serverInfo?.platform === 'Darwin') {
                serverButton.innerHTML = '<i class="fas fa-apple mr-2"></i>Dados do Mac';
                serverButton.title = "Exportar métricas do servidor Mac";
            } else if (this.metrics.serverInfo?.platform === 'Windows') {
                serverButton.innerHTML = '<i class="fab fa-windows mr-2"></i>Dados do Windows';
                serverButton.title = "Exportar métricas do servidor Windows";
            } else if (this.metrics.serverInfo?.platform === 'Linux') {
                serverButton.innerHTML = '<i class="fab fa-linux mr-2"></i>Dados do Linux';
                serverButton.title = "Exportar métricas do servidor Linux";
            }

            console.log(`🖥️ Botão de métricas do servidor atualizado: ${this.metrics.serverInfo?.platform || 'Desconhecido'}`);
        }
    }

    // (Função exportRaspberryPiMetrics removida - substituída por exportServerMetrics)
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
            <button id="export-comparative" class="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors mr-2">
                <i class="fas fa-exchange-alt mr-2"></i>Exportar Comparativo
            </button>
            <button id="export-server" class="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors mr-2">
                <i class="fas fa-server mr-2"></i>Dados do Servidor
            </button>
            <button id="log-report" class="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                <i class="fas fa-chart-line mr-2"></i>Ver Relatório
            </button>
        </div>
    `; const metricsSection = document.querySelector('.mt-8.bg-gray-50');
    if (metricsSection) {
        metricsSection.appendChild(metricsControls);

        // Event listeners para os botões
        document.getElementById('export-metrics').addEventListener('click', () => {
            window.performanceMetrics.exportData();
        });

        document.getElementById('export-comparative').addEventListener('click', () => {
            window.performanceMetrics.exportComparativeReport();
        });

        // Adicionar event listener para o botão de métricas do servidor
        document.getElementById('export-server').addEventListener('click', () => {
            window.performanceMetrics.exportServerMetrics();
        });

        document.getElementById('log-report').addEventListener('click', () => {
            window.performanceMetrics.logComparativeReport();
        });
    }
});

// Integração com o sistema de tradução existente
window.addEventListener('beforeunload', function () {
    window.performanceMetrics.stopCollection();
});
