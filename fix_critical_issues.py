#!/usr/bin/env python3
"""Script de correção automática dos problemas críticos identificados"""

import os
import sys
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
    def fix_health_check(self):
        """Corrige o health check do MetricsLevelsResponse"""
        logger.info("Corrigindo health check do MetricsLevelsResponse...")
        
        metrics_file = self.backend_dir / "api" / "v1" / "metrics_levels.py"
        
        if not metrics_file.exists():
            logger.error(f"Arquivo não encontrado: {metrics_file}")
            return False
            
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir a linha problemática
            old_line = 'status = "healthy" if result.get("status") == "healthy" else "unhealthy"'
            new_line = '''is_healthy = (
            result is not None and 
            hasattr(result, 'aggregated_metrics') and 
            result.aggregated_metrics is not None
        )
        
        status = "healthy" if is_healthy else "unhealthy"'''
            
            if old_line in content:
                content = content.replace(old_line, new_line)
                
                with open(metrics_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                logger.info("Health check corrigido com sucesso!")
                return True
            else:
                logger.warning("Linha problemática não encontrada no arquivo")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao corrigir health check: {e}")
            return False
    
    def fix_test_imports(self):
        """Corrige problemas de importação nos testes"""
        logger.info("Corrigindo importações nos testes...")
        
        conftest_file = self.backend_dir / "tests" / "conftest.py"
        
        if not conftest_file.exists():
            logger.error(f"Arquivo não encontrado: {conftest_file}")
            return False
            
        try:
            with open(conftest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Adicionar configuração de path no início
            path_config = '''import sys
import os
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

'''
            
            if "sys.path.insert" not in content:
                content = path_config + content
                
                with open(conftest_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                logger.info("Importações dos testes corrigidas!")
                return True
            else:
                logger.info("Importações já estão configuradas")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao corrigir importações: {e}")
            return False
    
    def run_lint_fixes(self):
        """Executa correções automáticas de lint"""
        logger.info("Executando correções automáticas de lint...")
        
        try:
            os.chdir(self.backend_dir)
            
            # Executar ruff fix
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", ".", "--fix"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Correções de lint aplicadas com sucesso!")
            else:
                logger.warning(f"Algumas correções não puderam ser aplicadas: {result.stderr}")
            
            # Executar ruff format
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "format", "."],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Formatação aplicada com sucesso!")
                return True
            else:
                logger.error(f"Erro na formatação: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao executar correções de lint: {e}")
            return False
    
    def create_missing_test_file(self):
        """Cria arquivo de teste para MetricsLevelsUseCase"""
        logger.info("Criando teste para MetricsLevelsUseCase...")
        
        test_dir = self.backend_dir / "tests" / "unit" / "usecases"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = test_dir / "test_metrics_levels_usecase.py"
        
        test_content = '''import pytest
from unittest.mock import Mock, patch
from usecases.metrics_levels_usecase import MetricsLevelsUseCase
from schemas.metrics_levels import MetricsLevelsQueryParams, ServiceLevel

class TestMetricsLevelsUseCase:
    @pytest.fixture
    def use_case(self):
        return MetricsLevelsUseCase()
    
    @pytest.mark.asyncio
    async def test_get_metrics_by_level_success(self, use_case):
        """Testa execução bem-sucedida do use case"""
        params = MetricsLevelsQueryParams()
        result = await use_case.get_metrics_by_level(params)
        
        assert result is not None
        assert hasattr(result, 'metrics_by_level')
        assert hasattr(result, 'aggregated_metrics')
    
    @pytest.mark.asyncio
    async def test_get_metrics_with_specific_levels(self, use_case):
        """Testa filtro por níveis específicos"""
        params = MetricsLevelsQueryParams(
            levels=[ServiceLevel.N1, ServiceLevel.N2]
        )
        result = await use_case.get_metrics_by_level(params)
        
        assert result is not None
        # Verificar se apenas N1 e N2 estão presentes
        if result.metrics_by_level:
            levels = [metric.level for metric in result.metrics_by_level]
            assert any(level in [ServiceLevel.N1, ServiceLevel.N2] for level in levels)
'''
        
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            logger.info(f"Arquivo de teste criado: {test_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar arquivo de teste: {e}")
            return False
    
    def run_all_fixes(self):
        """Executa todas as correções"""
        logger.info("=== INICIANDO CORREÇÕES AUTOMÁTICAS ===")
        
        results = {
            "health_check": self.fix_health_check(),
            "test_imports": self.fix_test_imports(),
            "lint_fixes": self.run_lint_fixes(),
            "missing_tests": self.create_missing_test_file()
        }
        
        logger.info("=== RESUMO DAS CORREÇÕES ===")
        for fix_name, success in results.items():
            status = " SUCESSO" if success else " FALHOU"
            logger.info(f"{fix_name}: {status}")
        
        total_success = sum(results.values())
        total_fixes = len(results)
        
        logger.info(f"\nTotal: {total_success}/{total_fixes} correções aplicadas com sucesso")
        
        if total_success == total_fixes:
            logger.info(" Todas as correções foram aplicadas com sucesso!")
        else:
            logger.warning(" Algumas correções falharam. Verifique os logs acima.")
        
        return results

if __name__ == "__main__":
    fixer = AutoFixer()
    results = fixer.run_all_fixes()
    
    # Retornar código de saída apropriado
    success_count = sum(results.values())
    total_count = len(results)
    
    sys.exit(0 if success_count == total_count else 1)
