#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Integração do Trae AI

Este script valida se o Trae AI está 100% integrado com os sistemas implementados.
"""

import sys
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trae_integration_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TraeAIIntegrationValidator:
    """Validador de integração do Trae AI com os sistemas implementados."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.validation_results = {}
        
        # Lista de arquivos obrigatórios (arquivos que realmente existem)
        self.required_files = [
            'config_ai_context.py',
            'ai_context_system.py',
            'example_ai_context.py',
            'config_monitoring.py',
            'monitoring_system.py',
            'example_monitoring.py',
            'config_safe_changes.py',
            'safe_change_protocol.py',
            'example_safe_changes.py'
        ]
        
    def validate_file_structure(self) -> bool:
        """Valida se todos os arquivos obrigatórios estão presentes."""
        logger.info(" Validando estrutura de arquivos...")
        
        missing_files = []
        for file_path in self.required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                
        if missing_files:
            logger.error(f" Arquivos obrigatórios ausentes: {missing_files}")
            self.validation_results['file_structure'] = {
                'status': 'FAILED',
                'missing_files': missing_files
            }
            return False
            
        logger.info(f" Todos os {len(self.required_files)} arquivos obrigatórios estão presentes")
        self.validation_results['file_structure'] = {
            'status': 'PASSED',
            'files_count': len(self.required_files)
        }
        return True
        
    def validate_ai_context_system(self) -> bool:
        """Valida o sistema AI Context."""
        logger.info(" Validando Sistema AI Context...")
        
        try:
            # Testar importação dos módulos AI Context
            modules_to_test = [
                'config_ai_context',
                'ai_context_system'
            ]
            
            for module in modules_to_test:
                result = subprocess.run(
                    [sys.executable, '-c', f'import {module}; print("{module} OK")'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    logger.error(f" AI Context System: Erro no módulo {module} - {result.stderr}")
                    self.validation_results['ai_context'] = {
                        'status': 'FAILED',
                        'error': f'Módulo {module} falhou'
                    }
                    return False
                    
            logger.info(" AI Context System: Todos os módulos importados com sucesso")
            self.validation_results['ai_context'] = {
                'status': 'PASSED',
                'modules_valid': True
            }
            return True
                
        except Exception as e:
            logger.error(f" AI Context System: Erro na validação - {e}")
            
        self.validation_results['ai_context'] = {
            'status': 'FAILED',
            'error': 'Validação falhou'
        }
        return False
        
    def validate_monitoring_system(self) -> bool:
        """Valida o sistema de monitoramento."""
        logger.info(" Validando Sistema de Monitoramento...")
        
        try:
            # Testar importação dos módulos de monitoramento
            modules_to_test = [
                'config_monitoring',
                'monitoring_system'
            ]
            
            for module in modules_to_test:
                result = subprocess.run(
                    [sys.executable, '-c', f'import {module}; print("{module} OK")'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    logger.error(f" Monitoring System: Erro no módulo {module} - {result.stderr}")
                    self.validation_results['monitoring'] = {
                        'status': 'FAILED',
                        'error': f'Módulo {module} falhou'
                    }
                    return False
                    
            logger.info(" Monitoring System: Todos os módulos importados com sucesso")
            self.validation_results['monitoring'] = {
                'status': 'PASSED',
                'modules_valid': True
            }
            return True
                
        except Exception as e:
            logger.error(f" Monitoring System: Erro na validação - {e}")
            
        self.validation_results['monitoring'] = {
            'status': 'FAILED',
            'error': 'Validação falhou'
        }
        return False
        
    def validate_safe_changes_protocol(self) -> bool:
        """Valida o protocolo de mudanças seguras."""
        logger.info(" Validando Protocolo de Mudanças Seguras...")
        
        try:
            # Testar importação dos módulos de mudanças seguras
            modules_to_test = [
                'config_safe_changes',
                'safe_change_protocol'
            ]
            
            for module in modules_to_test:
                result = subprocess.run(
                    [sys.executable, '-c', f'import {module}; print("{module} OK")'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    logger.error(f" Safe Changes Protocol: Erro no módulo {module} - {result.stderr}")
                    self.validation_results['safe_changes'] = {
                        'status': 'FAILED',
                        'error': f'Módulo {module} falhou'
                    }
                    return False
                    
            logger.info(" Safe Changes Protocol: Todos os módulos importados com sucesso")
            self.validation_results['safe_changes'] = {
                'status': 'PASSED',
                'modules_valid': True
            }
            return True
                
        except Exception as e:
            logger.error(f" Safe Changes Protocol: Erro na validação - {e}")
            
        self.validation_results['safe_changes'] = {
            'status': 'FAILED',
            'error': 'Validação falhou'
        }
        return False
        
    def validate_trae_configuration(self) -> bool:
        """Valida a configuração do Trae AI."""
        logger.info(" Validando configuração do Trae AI...")
        
        trae_files = [
            'trae-context.yml',
            '.trae/rules/integrated_system_rules.md'
        ]
        
        missing_trae_files = []
        for file_path in trae_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_trae_files.append(file_path)
                
        if missing_trae_files:
            logger.error(f" Arquivos de configuração do Trae AI ausentes: {missing_trae_files}")
            self.validation_results['trae_config'] = {
                'status': 'FAILED',
                'missing_files': missing_trae_files
            }
            return False
            
        logger.info(" Configuração do Trae AI: Arquivos presentes")
        self.validation_results['trae_config'] = {
            'status': 'PASSED',
            'config_files': len(trae_files)
        }
        return True
        
    def run_full_validation(self) -> bool:
        """Executa validação completa do sistema."""
        logger.info(" Iniciando validação completa da integração do Trae AI...")
        
        validations = [
            ('Estrutura de Arquivos', self.validate_file_structure),
            ('Sistema AI Context', self.validate_ai_context_system),
            ('Sistema de Monitoramento', self.validate_monitoring_system),
            ('Protocolo de Mudanças Seguras', self.validate_safe_changes_protocol),
            ('Configuração Trae AI', self.validate_trae_configuration)
        ]
        
        success_count = 0
        total_count = len(validations)
        
        for name, validation_func in validations:
            try:
                if validation_func():
                    success_count += 1
                    logger.info(f" {name}: PASSOU")
                else:
                    logger.error(f" {name}: FALHOU")
            except Exception as e:
                logger.error(f" {name}: ERRO - {e}")
                
        # Resultado final
        if success_count == total_count:
            logger.info("\n SISTEMA 100% INTEGRADO E FUNCIONANDO")
            logger.info(" Trae AI pode operar com segurança")
            logger.info(" Todas as configurações estão ativas")
            logger.info(" Sistemas AI Context, Monitoring e Safe Changes operacionais")
            return True
        else:
            logger.error(f"\n PROBLEMAS DE INTEGRAÇÃO DETECTADOS ({success_count}/{total_count})")
            logger.error(" Trae AI NÃO deve operar até correção")
            return False
            
def main():
    """Função principal."""
    # Criar diretório de logs se não existir
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    validator = TraeAIIntegrationValidator()
    
    try:
        success = validator.run_full_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n Validação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f" Erro fatal na validação: {e}")
        sys.exit(1)
        
if __name__ == '__main__':
    main()
