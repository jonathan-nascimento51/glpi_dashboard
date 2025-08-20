#!/usr/bin/env python3
"""
Sandbox Runner - GLPI Dashboard AI Integration Testing

Este script executa testes automatizados para validar integrações de IA,
prompts contextuais e funcionalidades experimentais.

Usage:
    python run_sandbox.py --test-type all
    python run_sandbox.py --test-type prompts --category development
    python run_sandbox.py --config custom_config.json
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SandboxConfig:
    """Configuração do sandbox"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> Path:
        """Retorna caminho padrão do arquivo de configuração"""
        return Path(__file__).parent.parent / 'config' / 'sandbox.json'
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear configuração: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão"""
        return {
            "environment": "sandbox",
            "ai_models": {
                "primary": "claude-3-sonnet",
                "fallback": "gpt-4"
            },
            "test_settings": {
                "timeout": 30,
                "max_retries": 3,
                "parallel_tests": 4
            },
            "mock_data": {
                "glpi_url": "http://localhost:8080/mock-glpi",
                "redis_url": "redis://localhost:6379/15"
            },
            "metrics": {
                "accuracy_threshold": 0.85,
                "performance_threshold": 2.0,
                "quality_threshold": 0.90
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor da configuração"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

class TestResult:
    """Resultado de um teste individual"""
    
    def __init__(self, test_id: str, category: str, status: str = 'pending'):
        self.test_id = test_id
        self.category = category
        self.status = status
        self.start_time = None
        self.end_time = None
        self.metrics = {}
        self.errors = []
        self.output = None
    
    def start(self):
        """Marca início do teste"""
        self.start_time = time.time()
        self.status = 'running'
    
    def finish(self, status: str, output: Any = None):
        """Marca fim do teste"""
        self.end_time = time.time()
        self.status = status
        self.output = output
    
    def add_error(self, error: str):
        """Adiciona erro ao teste"""
        self.errors.append(error)
    
    def add_metric(self, name: str, value: float):
        """Adiciona métrica ao teste"""
        self.metrics[name] = value
    
    @property
    def duration(self) -> Optional[float]:
        """Duração do teste em segundos"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultado para dicionário"""
        return {
            'test_id': self.test_id,
            'category': self.category,
            'status': self.status,
            'duration': self.duration,
            'metrics': self.metrics,
            'errors': self.errors,
            'output': self.output
        }

class PromptTester:
    """Testador de prompts contextuais"""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.prompts_dir = Path(__file__).parent.parent / 'test-prompts'
    
    def run_tests(self, category: Optional[str] = None) -> List[TestResult]:
        """Executa testes de prompts"""
        results = []
        test_cases = self._load_test_cases(category)
        
        for case in test_cases:
            result = self._execute_test_case(case)
            results.append(result)
        
        return results
    
    def _load_test_cases(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Carrega casos de teste"""
        test_cases = []
        
        # Casos de teste simulados
        if not category or category == 'development':
            test_cases.extend([
                {
                    'id': 'dev_001',
                    'category': 'development',
                    'name': 'Criar endpoint API',
                    'prompt': 'Criar endpoint /api/test que retorna status do sistema',
                    'expected_elements': ['@api_bp.route', 'def test()', 'return ResponseFormatter.success']
                },
                {
                    'id': 'dev_002',
                    'category': 'development',
                    'name': 'Componente React',
                    'prompt': 'Criar componente StatusCard que exibe status do sistema',
                    'expected_elements': ['interface StatusCardProps', 'export const StatusCard', 'React.FC']
                }
            ])
        
        if not category or category == 'debug':
            test_cases.extend([
                {
                    'id': 'debug_001',
                    'category': 'debug',
                    'name': 'Análise de performance',
                    'prompt': 'API lenta, analisar logs: múltiplas chamadas GLPI, cache miss',
                    'expected_elements': ['cache', 'performance', 'optimization']
                }
            ])
        
        return test_cases
    
    def _execute_test_case(self, case: Dict[str, Any]) -> TestResult:
        """Executa um caso de teste"""
        result = TestResult(case['id'], case['category'])
        result.start()
        
        try:
            # Simular execução do prompt
            response = self._simulate_ai_response(case['prompt'])
            
            # Avaliar resposta
            accuracy = self._measure_accuracy(response, case.get('expected_elements', []))
            quality = self._assess_code_quality(response)
            
            result.add_metric('accuracy', accuracy)
            result.add_metric('quality', quality)
            
            # Determinar status
            if accuracy >= self.config.get('metrics.accuracy_threshold', 0.85):
                result.finish('passed', response)
            else:
                result.finish('failed', response)
                result.add_error(f"Accuracy {accuracy:.2f} below threshold")
        
        except Exception as e:
            result.finish('error')
            result.add_error(str(e))
            logger.error(f"Erro no teste {case['id']}: {e}")
        
        return result
    
    def _simulate_ai_response(self, prompt: str) -> str:
        """Simula resposta da IA (placeholder)"""
        # Em implementação real, aqui seria feita a chamada para a IA
        time.sleep(0.5)  # Simular latência
        
        if 'endpoint' in prompt.lower():
            return '''
@api_bp.route('/api/test', methods=['GET'])
@observability_logger.monitor_endpoint()
def test():
    correlation_id = request.headers.get('X-Correlation-ID', generate_correlation_id())
    
    try:
        status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }
        return ResponseFormatter.success(status, correlation_id)
    except Exception as e:
        return ResponseFormatter.error(str(e), correlation_id)
'''
        
        elif 'componente' in prompt.lower() or 'component' in prompt.lower():
            return '''
interface StatusCardProps {
  status: 'healthy' | 'warning' | 'error';
  title: string;
  description?: string;
}

export const StatusCard: React.FC<StatusCardProps> = ({ status, title, description }) => {
  const statusColors = {
    healthy: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800'
  };
  
  return (
    <div className={`p-4 rounded-lg ${statusColors[status]}`}>
      <h3 className="font-semibold">{title}</h3>
      {description && <p className="text-sm mt-1">{description}</p>}
    </div>
  );
};
'''
        
        else:
            return f"Análise do problema: {prompt}\n\nRecomendações:\n1. Implementar cache\n2. Otimizar queries\n3. Adicionar monitoramento"
    
    def _measure_accuracy(self, response: str, expected_elements: List[str]) -> float:
        """Mede precisão da resposta"""
        if not expected_elements:
            return 0.8  # Score padrão quando não há elementos esperados
        
        found_elements = sum(1 for element in expected_elements if element in response)
        return found_elements / len(expected_elements)
    
    def _assess_code_quality(self, response: str) -> float:
        """Avalia qualidade do código gerado"""
        quality_indicators = [
            'def ' in response or 'const ' in response,  # Definições
            'try:' in response or 'catch' in response,   # Tratamento de erro
            'import ' in response or 'from ' in response, # Imports
            len(response.split('\n')) > 5,               # Complexidade mínima
            'return' in response                         # Retorno
        ]
        
        return sum(quality_indicators) / len(quality_indicators)

class PerformanceTester:
    """Testador de performance"""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
    
    def run_tests(self) -> List[TestResult]:
        """Executa testes de performance"""
        results = []
        
        # Teste de latência
        latency_result = self._test_latency()
        results.append(latency_result)
        
        # Teste de throughput
        throughput_result = self._test_throughput()
        results.append(throughput_result)
        
        return results
    
    def _test_latency(self) -> TestResult:
        """Testa latência das operações"""
        result = TestResult('perf_latency', 'performance')
        result.start()
        
        try:
            # Simular múltiplas operações
            latencies = []
            for i in range(10):
                start = time.time()
                # Simular operação
                time.sleep(0.1 + (i * 0.01))  # Latência variável
                end = time.time()
                latencies.append(end - start)
            
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            
            result.add_metric('avg_latency', avg_latency)
            result.add_metric('max_latency', max_latency)
            
            threshold = self.config.get('metrics.performance_threshold', 2.0)
            if avg_latency <= threshold:
                result.finish('passed')
            else:
                result.finish('failed')
                result.add_error(f"Latência média {avg_latency:.2f}s acima do limite {threshold}s")
        
        except Exception as e:
            result.finish('error')
            result.add_error(str(e))
        
        return result
    
    def _test_throughput(self) -> TestResult:
        """Testa throughput do sistema"""
        result = TestResult('perf_throughput', 'performance')
        result.start()
        
        try:
            # Simular processamento de múltiplas requisições
            start_time = time.time()
            operations = 100
            
            for i in range(operations):
                # Simular processamento
                time.sleep(0.001)  # 1ms por operação
            
            end_time = time.time()
            duration = end_time - start_time
            throughput = operations / duration
            
            result.add_metric('throughput', throughput)
            result.add_metric('operations', operations)
            
            # Critério: pelo menos 50 ops/segundo
            if throughput >= 50:
                result.finish('passed')
            else:
                result.finish('failed')
                result.add_error(f"Throughput {throughput:.2f} ops/s abaixo do mínimo")
        
        except Exception as e:
            result.finish('error')
            result.add_error(str(e))
        
        return result

class SandboxRunner:
    """Executor principal do sandbox"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = SandboxConfig(config_path)
        self.run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.results = []
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes do sandbox"""
        logger.info(f"Iniciando execução completa do sandbox - Run ID: {self.run_id}")
        
        start_time = time.time()
        
        # Executar diferentes tipos de teste
        prompt_results = self.run_prompt_tests()
        performance_results = self.run_performance_tests()
        
        end_time = time.time()
        
        # Consolidar resultados
        all_results = prompt_results + performance_results
        
        summary = self._generate_summary(all_results, end_time - start_time)
        
        # Gerar relatório
        report = {
            'test_run': {
                'id': self.run_id,
                'timestamp': datetime.now().isoformat(),
                'duration': end_time - start_time,
                'environment': self.config.get('environment', 'sandbox')
            },
            'summary': summary,
            'results': [result.to_dict() for result in all_results]
        }
        
        self._save_report(report)
        self._print_summary(summary)
        
        return report
    
    def run_prompt_tests(self, category: Optional[str] = None) -> List[TestResult]:
        """Executa testes de prompts"""
        logger.info(f"Executando testes de prompts - categoria: {category or 'todas'}")
        
        tester = PromptTester(self.config)
        return tester.run_tests(category)
    
    def run_performance_tests(self) -> List[TestResult]:
        """Executa testes de performance"""
        logger.info("Executando testes de performance")
        
        tester = PerformanceTester(self.config)
        return tester.run_tests()
    
    def _generate_summary(self, results: List[TestResult], duration: float) -> Dict[str, Any]:
        """Gera resumo dos resultados"""
        total_tests = len(results)
        passed = sum(1 for r in results if r.status == 'passed')
        failed = sum(1 for r in results if r.status == 'failed')
        errors = sum(1 for r in results if r.status == 'error')
        
        # Calcular métricas médias
        accuracy_scores = [r.metrics.get('accuracy', 0) for r in results if 'accuracy' in r.metrics]
        quality_scores = [r.metrics.get('quality', 0) for r in results if 'quality' in r.metrics]
        
        return {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'success_rate': passed / total_tests if total_tests > 0 else 0,
            'duration': duration,
            'avg_accuracy': sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0,
            'avg_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0
        }
    
    def _save_report(self, report: Dict[str, Any]) -> None:
        """Salva relatório em arquivo"""
        results_dir = Path(__file__).parent.parent / 'results'
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar relatório específico
        report_file = results_dir / f"{self.run_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Atualizar relatório mais recente
        latest_file = results_dir / 'latest_report.json'
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Relatório salvo: {report_file}")
    
    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Imprime resumo dos resultados"""
        print("\n" + "="*60)
        print(f"🧪 SANDBOX RESULTS - Run ID: {self.run_id}")
        print("="*60)
        print(f"Total de testes: {summary['total_tests']}")
        print(f"✅ Passou: {summary['passed']}")
        print(f"❌ Falhou: {summary['failed']}")
        print(f"🚨 Erros: {summary['errors']}")
        print(f"📊 Taxa de sucesso: {summary['success_rate']:.2%}")
        print(f"⏱️  Duração: {summary['duration']:.2f}s")
        
        if summary['avg_accuracy'] > 0:
            print(f"🎯 Precisão média: {summary['avg_accuracy']:.2%}")
        
        if summary['avg_quality'] > 0:
            print(f"⭐ Qualidade média: {summary['avg_quality']:.2%}")
        
        print("="*60)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Sandbox de Testes para IA - GLPI Dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemplos:
  python run_sandbox.py --test-type all
  python run_sandbox.py --test-type prompts --category development
  python run_sandbox.py --test-type performance
  python run_sandbox.py --config custom_config.json
'''
    )
    
    parser.add_argument(
        '--config',
        help='Arquivo de configuração personalizado'
    )
    
    parser.add_argument(
        '--test-type',
        choices=['all', 'prompts', 'performance'],
        default='all',
        help='Tipo de teste a executar (padrão: all)'
    )
    
    parser.add_argument(
        '--category',
        choices=['development', 'debug', 'refactoring'],
        help='Categoria específica para testes de prompts'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Saída detalhada'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        runner = SandboxRunner(args.config)
        
        if args.test_type == 'all':
            results = runner.run_all_tests()
        elif args.test_type == 'prompts':
            results = runner.run_prompt_tests(args.category)
            print(f"\n✅ Testes de prompts concluídos: {len(results)} casos testados")
        elif args.test_type == 'performance':
            results = runner.run_performance_tests()
            print(f"\n✅ Testes de performance concluídos: {len(results)} casos testados")
        
        # Código de saída baseado nos resultados
        if args.test_type == 'all':
            success_rate = results['summary']['success_rate']
            sys.exit(0 if success_rate >= 0.8 else 1)
        else:
            failed_tests = sum(1 for r in results if r.status in ['failed', 'error'])
            sys.exit(0 if failed_tests == 0 else 1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Execução interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erro durante execução: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()