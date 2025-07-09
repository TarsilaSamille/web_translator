#!/bin/bash
# Script de configuração e teste para Raspberry Pi
# Autor: Sistema de Tradução Neural Edge

echo "🍓 Configurando Sistema de Tradução Neural no Raspberry Pi"
echo "=========================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Verificar se é Raspberry Pi
check_raspberry_pi() {
    if grep -q "Raspberry Pi" /proc/cpuinfo; then
        model=$(grep "Model" /proc/cpuinfo | cut -d ':' -f2 | sed 's/^ *//')
        log "Raspberry Pi detectado: $model"
        return 0
    else
        warn "Sistema não parece ser um Raspberry Pi"
        return 1
    fi
}

# Verificar recursos do sistema
check_system_resources() {
    log "Verificando recursos do sistema..."
    
    # CPU
    cpu_count=$(nproc)
    log "CPUs disponíveis: $cpu_count"
    
    # Memória
    memory_total=$(free -h | grep "Mem:" | awk '{print $2}')
    log "Memória total: $memory_total"
    
    # Espaço em disco
    disk_space=$(df -h / | tail -1 | awk '{print $4}')
    log "Espaço livre em disco: $disk_space"
    
    # Temperatura
    if [ -f "/sys/class/thermal/thermal_zone0/temp" ]; then
        temp=$(cat /sys/class/thermal/thermal_zone0/temp)
        temp_c=$((temp / 1000))
        log "Temperatura atual da CPU: ${temp_c}°C"
        
        if [ $temp_c -gt 70 ]; then
            warn "Temperatura da CPU alta: ${temp_c}°C"
        fi
    fi
}

# Instalar dependências
install_dependencies() {
    log "Instalando dependências do sistema..."
    
    # Atualizar package list
    sudo apt update
    
    # Instalar dependências essenciais
    sudo apt install -y python3 python3-pip python3-venv git htop
    
    # Instalar dependências específicas para monitoramento
    sudo apt install -y lm-sensors
    
    log "Dependências instaladas"
}

# Configurar ambiente Python
setup_python_environment() {
    log "Configurando ambiente Python..."
    
    # Criar ambiente virtual se não existir
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log "Ambiente virtual criado"
    fi
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Atualizar pip
    pip install --upgrade pip
    
    # Instalar dependências Python
    if [ -f "requirements.txt" ]; then
        log "Instalando dependências Python..."
        pip install -r requirements.txt
        log "Dependências Python instaladas"
    else
        error "Arquivo requirements.txt não encontrado"
        return 1
    fi
}

# Verificar modelos
check_models() {
    log "Verificando modelos de tradução..."
    
    if [ -d "models" ]; then
        model_count=$(find models -name "*.keras" | wc -l)
        log "Modelos encontrados: $model_count"
        
        # Listar modelos disponíveis
        for model_dir in models/*/; do
            if [ -d "$model_dir" ]; then
                model_name=$(basename "$model_dir")
                if [ -f "$model_dir/model.keras" ]; then
                    model_size=$(du -h "$model_dir/model.keras" | cut -f1)
                    log "  - $model_name (${model_size})"
                else
                    warn "  - $model_name (modelo não encontrado)"
                fi
            fi
        done
    else
        error "Diretório de modelos não encontrado"
        return 1
    fi
}

# Configurar otimizações para Raspberry Pi
optimize_for_raspberry_pi() {
    log "Aplicando otimizações para Raspberry Pi..."
    
    # Configurar swap se necessário
    if [ $(free | grep Swap | awk '{print $2}') -eq 0 ]; then
        warn "Swap não configurado. Recomendado para operação com modelos grandes."
    fi
    
    # Configurar limites de memória
    if [ -f "/boot/cmdline.txt" ]; then
        if ! grep -q "cma=128M" /boot/cmdline.txt; then
            warn "Considere adicionar 'cma=128M' ao /boot/cmdline.txt para melhor gestão de memória"
        fi
    fi
    
    # Configurar governor de CPU para performance
    if [ -f "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor" ]; then
        current_governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
        log "Governor atual da CPU: $current_governor"
        
        if [ "$current_governor" != "performance" ]; then
            warn "Para melhor performance, considere usar o governor 'performance'"
            echo "  sudo echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
        fi
    fi
}

# Testar servidor
test_server() {
    log "Testando servidor de tradução..."
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Iniciar servidor em background
    python3 app.py &
    SERVER_PID=$!
    
    # Aguardar servidor inicializar
    sleep 10
    
    # Testar se servidor está respondendo
    if curl -s http://localhost:5000 > /dev/null; then
        log "Servidor iniciado com sucesso"
        
        # Testar API de tradução
        response=$(curl -s -X POST -H "Content-Type: application/json" \
            -d '{"text":"Hello world","model":"hausa-english-translator"}' \
            http://localhost:5000/api/translate)
        
        if echo "$response" | grep -q "success"; then
            log "API de tradução funcionando"
        else
            warn "API de tradução não respondeu corretamente"
        fi
        
        # Parar servidor
        kill $SERVER_PID
        wait $SERVER_PID 2>/dev/null
        
    else
        error "Servidor não está respondendo"
        kill $SERVER_PID 2>/dev/null
        return 1
    fi
}

# Executar benchmark
run_benchmark() {
    log "Executando benchmark de performance..."
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Iniciar servidor em background
    python3 app.py &
    SERVER_PID=$!
    
    # Aguardar servidor inicializar
    sleep 10
    
    # Executar benchmark
    python3 raspberry_pi_benchmark.py
    
    # Parar servidor
    kill $SERVER_PID
    wait $SERVER_PID 2>/dev/null
    
    log "Benchmark concluído"
}

# Monitorar recursos em tempo real
monitor_resources() {
    log "Iniciando monitoramento de recursos..."
    
    # Função para monitoramento contínuo
    while true; do
        clear
        echo "🍓 Monitoramento de Recursos - Raspberry Pi"
        echo "=========================================="
        echo "Timestamp: $(date)"
        echo ""
        
        # CPU
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
        echo "CPU Usage: ${cpu_usage}%"
        
        # Memória
        memory_info=$(free -h | grep "Mem:")
        echo "Memória: $memory_info"
        
        # Temperatura
        if [ -f "/sys/class/thermal/thermal_zone0/temp" ]; then
            temp=$(cat /sys/class/thermal/thermal_zone0/temp)
            temp_c=$((temp / 1000))
            echo "Temperatura CPU: ${temp_c}°C"
        fi
        
        # Processos Python
        echo ""
        echo "Processos Python:"
        ps aux | grep python3 | grep -v grep | head -5
        
        echo ""
        echo "Pressione Ctrl+C para sair..."
        
        sleep 5
    done
}

# Menu principal
show_menu() {
    echo ""
    echo "🍓 Sistema de Tradução Neural - Raspberry Pi"
    echo "============================================"
    echo "1. Verificar sistema"
    echo "2. Instalar dependências"
    echo "3. Configurar ambiente"
    echo "4. Testar servidor"
    echo "5. Executar benchmark"
    echo "6. Monitorar recursos"
    echo "7. Sair"
    echo ""
    read -p "Escolha uma opção: " choice
    
    case $choice in
        1)
            check_raspberry_pi
            check_system_resources
            check_models
            ;;
        2)
            install_dependencies
            ;;
        3)
            setup_python_environment
            ;;
        4)
            test_server
            ;;
        5)
            run_benchmark
            ;;
        6)
            monitor_resources
            ;;
        7)
            log "Saindo..."
            exit 0
            ;;
        *)
            error "Opção inválida"
            ;;
    esac
}

# Verificar se script está sendo executado como root para algumas operações
check_root() {
    if [[ $EUID -eq 0 ]]; then
        warn "Executando como root. Algumas operações podem não funcionar corretamente."
    fi
}

# Função principal
main() {
    log "Iniciando configuração do Sistema de Tradução Neural"
    
    check_root
    
    # Se argumentos foram passados, executar diretamente
    if [ $# -gt 0 ]; then
        case $1 in
            "check")
                check_raspberry_pi
                check_system_resources
                check_models
                ;;
            "install")
                install_dependencies
                ;;
            "setup")
                setup_python_environment
                ;;
            "test")
                test_server
                ;;
            "benchmark")
                run_benchmark
                ;;
            "monitor")
                monitor_resources
                ;;
            *)
                error "Comando inválido: $1"
                echo "Comandos disponíveis: check, install, setup, test, benchmark, monitor"
                exit 1
                ;;
        esac
    else
        # Modo interativo
        while true; do
            show_menu
            echo ""
            read -p "Pressione Enter para continuar..."
        done
    fi
}

# Executar função principal
main "$@"
