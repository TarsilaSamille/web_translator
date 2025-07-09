#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Benchmark para Raspberry Pi
Coleta métricas de desempenho para análise científica
"""

import time
import json
import psutil
import threading
import datetime
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from statistics import mean, median, stdev

class RaspberryPiBenchmark:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'temperature': [],
            'translation_times': [],
            'concurrent_performance': [],
            'model_performance': {},
            'system_info': self.get_system_info()
        }
        self.is_running = False
        
    def get_system_info(self):
        """Coleta informações básicas do sistema"""
        info = {
            'platform': sys.platform,
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Tentar obter informações específicas do Raspberry Pi
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'Raspberry Pi' in cpuinfo:
                    info['device'] = 'Raspberry Pi'
                    # Extrair modelo se possível
                    for line in cpuinfo.split('\n'):
                        if 'Model' in line:
                            info['model'] = line.split(':')[1].strip()
                            break
        except:
            pass
            
        return info
    
    def start_monitoring(self):
        """Inicia o monitoramento de sistema"""
        self.is_running = True
        
        def monitor_loop():
            while self.is_running:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    self.metrics['cpu_usage'].append({
                        'timestamp': time.time(),
                        'value': cpu_percent
                    })
                    
                    self.metrics['memory_usage'].append({
                        'timestamp': time.time(),
                        'value': memory.used / (1024 * 1024)  # MB
                    })
                    
                    # Tentar obter temperatura
                    try:
                        temp = self.get_cpu_temperature()
                        if temp:
                            self.metrics['temperature'].append({
                                'timestamp': time.time(),
                                'value': temp
                            })
                    except:
                        pass
                        
                    time.sleep(2)  # Coleta a cada 2 segundos
                    
                except Exception as e:
                    print(f"Erro no monitoramento: {e}")
                    time.sleep(5)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🔄 Monitoramento de sistema iniciado")
    
    def get_cpu_temperature(self):
        """Obtém temperatura da CPU (específico para Raspberry Pi)"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read()) / 1000.0
                return temp
        except:
            # Fallback para sistemas que não têm esse arquivo
            try:
                temps = psutil.sensors_temperatures()
                for name, entries in temps.items():
                    if 'cpu' in name.lower() or 'thermal' in name.lower():
                        if entries:
                            return entries[0].current
            except:
                pass
        return None
    
    def test_translation_performance(self, test_texts, model_id, iterations=10):
        """Testa performance de tradução para um modelo específico"""
        print(f"🧪 Testando performance do modelo {model_id}")
        
        results = []
        
        for i in range(iterations):
            for text in test_texts:
                start_time = time.time()
                
                try:
                    response = requests.post(
                        f"{self.base_url}/api/translate",
                        json={'text': text, 'model': model_id},
                        timeout=30
                    )
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # ms
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            results.append({
                                'text_length': len(text),
                                'response_time': response_time,
                                'success': True,
                                'timestamp': time.time()
                            })
                        else:
                            results.append({
                                'text_length': len(text),
                                'response_time': response_time,
                                'success': False,
                                'error': data.get('error', 'Unknown error'),
                                'timestamp': time.time()
                            })
                    else:
                        results.append({
                            'text_length': len(text),
                            'response_time': response_time,
                            'success': False,
                            'error': f'HTTP {response.status_code}',
                            'timestamp': time.time()
                        })
                        
                except Exception as e:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    results.append({
                        'text_length': len(text),
                        'response_time': response_time,
                        'success': False,
                        'error': str(e),
                        'timestamp': time.time()
                    })
                
                # Pequena pausa entre requisições
                time.sleep(0.5)
        
        self.metrics['model_performance'][model_id] = results
        return results
    
    def test_concurrent_users(self, test_text, model_id, num_users=5, requests_per_user=10):
        """Testa performance com múltiplos usuários simultâneos"""
        print(f"👥 Testando {num_users} usuários simultâneos")
        
        results = []
        
        def user_simulation(user_id):
            user_results = []
            for i in range(requests_per_user):
                start_time = time.time()
                
                try:
                    response = requests.post(
                        f"{self.base_url}/api/translate",
                        json={'text': test_text, 'model': model_id},
                        timeout=30
                    )
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    user_results.append({
                        'user_id': user_id,
                        'request_id': i,
                        'response_time': response_time,
                        'success': response.status_code == 200,
                        'timestamp': time.time()
                    })
                    
                except Exception as e:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    user_results.append({
                        'user_id': user_id,
                        'request_id': i,
                        'response_time': response_time,
                        'success': False,
                        'error': str(e),
                        'timestamp': time.time()
                    })
                
                time.sleep(0.1)  # Pequena pausa entre requisições do mesmo usuário
            
            return user_results
        
        # Executar simulações concorrentes
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(user_simulation, i) for i in range(num_users)]
            
            for future in as_completed(futures):
                results.extend(future.result())
        
        self.metrics['concurrent_performance'] = results
        return results
    
    def run_comprehensive_benchmark(self):
        """Executa benchmark completo"""
        print("🚀 Iniciando benchmark completo do sistema")
        
        # Iniciar monitoramento
        self.start_monitoring()
        
        # Textos de teste de diferentes tamanhos
        test_texts = [
            "Hello world",  # Curto
            "This is a medium length sentence for testing translation performance.",  # Médio
            "This is a longer text that contains multiple sentences and should provide a good test for the translation system performance under different load conditions and text lengths.",  # Longo
        ]
        
        # Obter modelos disponíveis
        try:
            response = requests.get(f"{self.base_url}/api/models")
            if response.status_code == 200:
                models = response.json()
                print(f"📋 Modelos disponíveis: {len(models)}")
                
                # Testar cada modelo
                for model in models:
                    model_id = model['id']
                    print(f"\n🔍 Testando modelo: {model['display_name']}")
                    self.test_translation_performance(test_texts, model_id, iterations=5)
                    
                    # Teste de concorrência com o primeiro modelo
                    if model == models[0]:
                        self.test_concurrent_users(test_texts[1], model_id, num_users=3, requests_per_user=5)
                
        except Exception as e:
            print(f"❌ Erro ao obter modelos: {e}")
        
        # Aguardar um pouco para coletar mais métricas
        print("\n⏳ Coletando métricas adicionais...")
        time.sleep(30)
        
        # Parar monitoramento
        self.is_running = False
        
        print("✅ Benchmark concluído!")
        return self.generate_report()
    
    def generate_report(self):
        """Gera relatório detalhado dos resultados"""
        report = {
            'system_info': self.metrics['system_info'],
            'duration': time.time() - self.metrics['system_info']['timestamp'],
            'summary': {},
            'detailed_metrics': self.metrics
        }
        
        # Análise de CPU
        if self.metrics['cpu_usage']:
            cpu_values = [m['value'] for m in self.metrics['cpu_usage']]
            report['summary']['cpu'] = {
                'average': mean(cpu_values),
                'median': median(cpu_values),
                'min': min(cpu_values),
                'max': max(cpu_values),
                'std_dev': stdev(cpu_values) if len(cpu_values) > 1 else 0
            }
        
        # Análise de memória
        if self.metrics['memory_usage']:
            memory_values = [m['value'] for m in self.metrics['memory_usage']]
            report['summary']['memory'] = {
                'average_mb': mean(memory_values),
                'median_mb': median(memory_values),
                'min_mb': min(memory_values),
                'max_mb': max(memory_values),
                'std_dev_mb': stdev(memory_values) if len(memory_values) > 1 else 0
            }
        
        # Análise de temperatura
        if self.metrics['temperature']:
            temp_values = [m['value'] for m in self.metrics['temperature']]
            report['summary']['temperature'] = {
                'average_c': mean(temp_values),
                'median_c': median(temp_values),
                'min_c': min(temp_values),
                'max_c': max(temp_values),
                'std_dev_c': stdev(temp_values) if len(temp_values) > 1 else 0
            }
        
        # Análise de performance dos modelos
        for model_id, results in self.metrics['model_performance'].items():
            successful_results = [r for r in results if r['success']]
            if successful_results:
                response_times = [r['response_time'] for r in successful_results]
                report['summary'][f'model_{model_id}'] = {
                    'total_requests': len(results),
                    'successful_requests': len(successful_results),
                    'success_rate': len(successful_results) / len(results) * 100,
                    'avg_response_time_ms': mean(response_times),
                    'median_response_time_ms': median(response_times),
                    'min_response_time_ms': min(response_times),
                    'max_response_time_ms': max(response_times)
                }
        
        # Análise de concorrência
        if self.metrics['concurrent_performance']:
            concurrent_results = [r for r in self.metrics['concurrent_performance'] if r['success']]
            if concurrent_results:
                response_times = [r['response_time'] for r in concurrent_results]
                report['summary']['concurrent_performance'] = {
                    'total_requests': len(self.metrics['concurrent_performance']),
                    'successful_requests': len(concurrent_results),
                    'success_rate': len(concurrent_results) / len(self.metrics['concurrent_performance']) * 100,
                    'avg_response_time_ms': mean(response_times),
                    'median_response_time_ms': median(response_times),
                    'throughput_requests_per_second': len(concurrent_results) / max(1, (max(r['timestamp'] for r in concurrent_results) - min(r['timestamp'] for r in concurrent_results)))
                }
        
        return report
    
    def save_report(self, report, filename=None):
        """Salva relatório em arquivo JSON"""
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"raspberry_pi_benchmark_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Relatório salvo em: {filename}")
        return filename
    
    def print_summary(self, report):
        """Imprime resumo dos resultados"""
        print("\n" + "="*60)
        print("📊 RESUMO DO BENCHMARK - RASPBERRY PI")
        print("="*60)
        
        print(f"🖥️  Sistema: {report['system_info'].get('device', 'Desconhecido')}")
        print(f"💻 Modelo: {report['system_info'].get('model', 'N/A')}")
        print(f"🧠 CPUs: {report['system_info']['cpu_count']}")
        print(f"💾 Memória: {report['system_info']['memory_total'] / (1024**3):.1f} GB")
        
        if 'cpu' in report['summary']:
            cpu = report['summary']['cpu']
            print(f"\n📈 CPU:")
            print(f"   Média: {cpu['average']:.1f}%")
            print(f"   Mediana: {cpu['median']:.1f}%")
            print(f"   Mín/Máx: {cpu['min']:.1f}% / {cpu['max']:.1f}%")
        
        if 'memory' in report['summary']:
            mem = report['summary']['memory']
            print(f"\n🧠 Memória:")
            print(f"   Média: {mem['average_mb']:.1f} MB")
            print(f"   Mediana: {mem['median_mb']:.1f} MB")
            print(f"   Mín/Máx: {mem['min_mb']:.1f} MB / {mem['max_mb']:.1f} MB")
        
        if 'temperature' in report['summary']:
            temp = report['summary']['temperature']
            print(f"\n🌡️  Temperatura:")
            print(f"   Média: {temp['average_c']:.1f}°C")
            print(f"   Mediana: {temp['median_c']:.1f}°C")
            print(f"   Mín/Máx: {temp['min_c']:.1f}°C / {temp['max_c']:.1f}°C")
        
        # Performance dos modelos
        for key, value in report['summary'].items():
            if key.startswith('model_'):
                model_name = key.replace('model_', '')
                print(f"\n🔤 Modelo {model_name}:")
                print(f"   Taxa de sucesso: {value['success_rate']:.1f}%")
                print(f"   Tempo médio: {value['avg_response_time_ms']:.0f}ms")
                print(f"   Tempo mediano: {value['median_response_time_ms']:.0f}ms")
                print(f"   Mín/Máx: {value['min_response_time_ms']:.0f}ms / {value['max_response_time_ms']:.0f}ms")
        
        if 'concurrent_performance' in report['summary']:
            conc = report['summary']['concurrent_performance']
            print(f"\n👥 Performance Concorrente:")
            print(f"   Taxa de sucesso: {conc['success_rate']:.1f}%")
            print(f"   Tempo médio: {conc['avg_response_time_ms']:.0f}ms")
            print(f"   Throughput: {conc['throughput_requests_per_second']:.2f} req/s")
        
        print("\n" + "="*60)

def main():
    """Função principal"""
    print("🔧 Iniciando Benchmark do Sistema de Tradução no Raspberry Pi")
    
    # Verificar se o servidor está rodando
    benchmark = RaspberryPiBenchmark()
    
    try:
        response = requests.get(f"{benchmark.base_url}/")
        if response.status_code != 200:
            print("❌ Servidor não está respondendo. Inicie o servidor primeiro.")
            return
    except Exception as e:
        print(f"❌ Erro ao conectar com servidor: {e}")
        print("Certifique-se de que o servidor está rodando em http://localhost:5000")
        return
    
    # Executar benchmark
    report = benchmark.run_comprehensive_benchmark()
    
    # Salvar e exibir resultados
    filename = benchmark.save_report(report)
    benchmark.print_summary(report)
    
    print(f"\n✅ Benchmark concluído! Relatório salvo em: {filename}")

if __name__ == "__main__":
    main()
