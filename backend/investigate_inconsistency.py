#!/usr/bin/env python3
"""
Script para investigar inconsistência nos dados do dashboard
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Adicionar o diretório backend ao path
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
except Exception as e:
    print(f"Erro ao configurar path: {e}")
    sys.exit(1)

try:
    from services.glpi_service import GLPIService
except ImportError as e:
    print(f"Erro ao importar GLPIService: {e}")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def safe_get_metrics(glpi_service: GLPIService, metric_type: str) -> Optional[Dict[str, Any]]:
    """
    Obtém métricas de forma segura com tratamento de erros.
    
    Args:
        glpi_service: Instância do serviço GLPI
        metric_type: Tipo de métrica ('general' ou 'level')
        
    Returns:
        Dicionário com métricas ou None em caso de erro
    """
    try:
        if not isinstance(glpi_service, GLPIService):
            logger.error(f"Serviço GLPI inválido para obter métricas {metric_type}")
            return None
            
        if metric_type == 'general':
            return glpi_service._get_general_metrics_internal()
        elif metric_type == 'level':
            return glpi_service._get_metrics_by_level_internal()
        else:
            logger.error(f"Tipo de métrica inválido: {metric_type}")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao obter métricas {metric_type}: {e}")
        return None


def calculate_totals(metrics: Dict[str, Any], is_level_metrics: bool = False) -> Dict[str, int]:
    """
    Calcula totais das métricas de forma segura.
    
    Args:
        metrics: Dicionário com métricas
        is_level_metrics: Se são métricas por nível
        
    Returns:
        Dicionário com totais calculados
    """
    try:
        if not isinstance(metrics, dict):
            logger.warning("Métricas inválidas para cálculo de totais")
            return {'novos': 0, 'pendentes': 0, 'progresso': 0, 'resolvidos': 0, 'total': 0}
        
        if is_level_metrics:
            # Calcular totais das métricas por nível
            level_totals = {
                'Novo': 0,
                'Pendente': 0,
                'Processando (atribuído)': 0,
                'Processando (planejado)': 0,
                'Solucionado': 0,
                'Fechado': 0
            }
            
            for level_name, level_data in metrics.items():
                if isinstance(level_data, dict):
                    for status, count in level_data.items():
                        if status in level_totals and isinstance(count, (int, float)):
                            level_totals[status] += int(count)
            
            novos = level_totals.get('Novo', 0)
            pendentes = level_totals.get('Pendente', 0)
            progresso = level_totals.get('Processando (atribuído)', 0) + level_totals.get('Processando (planejado)', 0)
            resolvidos = level_totals.get('Solucionado', 0) + level_totals.get('Fechado', 0)
        else:
            # Métricas gerais
            novos = metrics.get("Novo", 0) if isinstance(metrics.get("Novo"), (int, float)) else 0
            pendentes = metrics.get("Pendente", 0) if isinstance(metrics.get("Pendente"), (int, float)) else 0
            progresso = (
                (metrics.get("Processando (atribuído)", 0) if isinstance(metrics.get("Processando (atribuído)"), (int, float)) else 0) +
                (metrics.get("Processando (planejado)", 0) if isinstance(metrics.get("Processando (planejado)"), (int, float)) else 0)
            )
            resolvidos = (
                (metrics.get("Solucionado", 0) if isinstance(metrics.get("Solucionado"), (int, float)) else 0) +
                (metrics.get("Fechado", 0) if isinstance(metrics.get("Fechado"), (int, float)) else 0)
            )
        
        total = novos + pendentes + progresso + resolvidos
        
        return {
            'novos': int(novos),
            'pendentes': int(pendentes),
            'progresso': int(progresso),
            'resolvidos': int(resolvidos),
            'total': int(total)
        }
        
    except Exception as e:
        logger.error(f"Erro ao calcular totais: {e}")
        return {'novos': 0, 'pendentes': 0, 'progresso': 0, 'resolvidos': 0, 'total': 0}


def main():
    """Função principal para investigação de inconsistências."""
    try:
        print("=" * 80)
        print("INVESTIGAÇÃO DE INCONSISTÊNCIA NOS DADOS DO DASHBOARD")
        print("=" * 80)
        
        # Inicializar serviço GLPI
        try:
            glpi = GLPIService()
        except Exception as e:
            logger.error(f"Erro ao inicializar GLPIService: {e}")
            print("❌ Falha ao inicializar serviço GLPI")
            return
        
        # Garantir que o serviço está autenticado e configurado
        try:
            if not glpi._ensure_authenticated():
                logger.error("Falha na autenticação com GLPI")
                print("❌ Falha na autenticação com GLPI")
                return
        except Exception as e:
            logger.error(f"Erro durante autenticação: {e}")
            print("❌ Erro durante autenticação")
            return
            
        try:
            if not glpi.discover_field_ids():
                logger.error("Falha ao descobrir IDs dos campos")
                print("❌ Falha ao descobrir IDs dos campos")
                return
        except Exception as e:
            logger.error(f"Erro ao descobrir IDs dos campos: {e}")
            print("❌ Erro ao descobrir IDs dos campos")
            return
        
        print("\n1. OBTENDO MÉTRICAS GERAIS (TODOS OS GRUPOS)")
        print("-" * 50)
        
        # Métricas gerais (todos os grupos)
        general_metrics = safe_get_metrics(glpi, 'general')
        if general_metrics is None:
            print("❌ Falha ao obter métricas gerais")
            return
            
        try:
            print(f"Métricas gerais: {json.dumps(general_metrics, indent=2, ensure_ascii=False)}")
        except Exception as e:
            logger.warning(f"Erro ao serializar métricas gerais: {e}")
            print(f"Métricas gerais obtidas (erro na serialização): {type(general_metrics)}")
        
        general_totals = calculate_totals(general_metrics, is_level_metrics=False)
        general_novos = general_totals['novos']
        general_pendentes = general_totals['pendentes']
        general_progresso = general_totals['progresso']
        general_resolvidos = general_totals['resolvidos']
        general_total = general_totals['total']
        
        print(f"\nTOTAIS GERAIS PROCESSADOS:")
        print(f"  Novos: {general_novos}")
        print(f"  Pendentes: {general_pendentes}")
        print(f"  Progresso: {general_progresso}")
        print(f"  Resolvidos: {general_resolvidos}")
        print(f"  TOTAL GERAL: {general_total}")
        
        print("\n2. OBTENDO MÉTRICAS POR NÍVEL (APENAS N1-N4)")
        print("-" * 50)
        
        # Métricas por nível (apenas grupos N1-N4)
        level_metrics = safe_get_metrics(glpi, 'level')
        if level_metrics is None:
            print("❌ Falha ao obter métricas por nível")
            return
            
        try:
            print(f"Métricas por nível: {json.dumps(level_metrics, indent=2, ensure_ascii=False)}")
        except Exception as e:
            logger.warning(f"Erro ao serializar métricas por nível: {e}")
            print(f"Métricas por nível obtidas (erro na serialização): {type(level_metrics)}")
        
        # Exibir detalhes por nível
        try:
            for level_name, level_data in level_metrics.items():
                if isinstance(level_data, dict):
                    print(f"\nNível {level_name}:")
                    level_total = 0
                    for status, count in level_data.items():
                        if isinstance(count, (int, float)):
                            level_total += int(count)
                            print(f"  {status}: {count}")
                        else:
                            print(f"  {status}: {count} (valor inválido)")
                    print(f"  Total do nível: {level_total}")
                else:
                    print(f"\nNível {level_name}: dados inválidos ({type(level_data)})")
        except Exception as e:
            logger.error(f"Erro ao exibir detalhes por nível: {e}")
        
        level_totals = calculate_totals(level_metrics, is_level_metrics=True)
        level_novos = level_totals['novos']
        level_pendentes = level_totals['pendentes']
        level_progresso = level_totals['progresso']
        level_resolvidos = level_totals['resolvidos']
        level_total_all = level_totals['total']
        
        print(f"\nTOTAIS DOS NÍVEIS PROCESSADOS:")
        print(f"  Novos: {level_novos}")
        print(f"  Pendentes: {level_pendentes}")
        print(f"  Progresso: {level_progresso}")
        print(f"  Resolvidos: {level_resolvidos}")
        print(f"  TOTAL NÍVEIS: {level_total_all}")
        
        print("\n" + "=" * 80)
        print("3. ANÁLISE DE INCONSISTÊNCIAS")
        print("=" * 80)
        
        print(f"\nCOMPARAÇÃO DETALHADA:")
        print(f"  Novos - Geral: {general_novos} | Níveis: {level_novos} | Diferença: {general_novos - level_novos}")
        print(f"  Pendentes - Geral: {general_pendentes} | Níveis: {level_pendentes} | Diferença: {general_pendentes - level_pendentes}")
        print(f"  Progresso - Geral: {general_progresso} | Níveis: {level_progresso} | Diferença: {general_progresso - level_progresso}")
        print(f"  Resolvidos - Geral: {general_resolvidos} | Níveis: {level_resolvidos} | Diferença: {general_resolvidos - level_resolvidos}")
        print(f"  TOTAL - Geral: {general_total} | Níveis: {level_total_all} | Diferença: {general_total - level_total_all}")
        
        # Verificar se há inconsistências
        try:
            inconsistencies = []
            
            # Validar dados antes da comparação
            if not all(isinstance(x, int) for x in [general_novos, level_novos, general_pendentes, level_pendentes, 
                                                   general_progresso, level_progresso, general_resolvidos, level_resolvidos]):
                logger.warning("Alguns valores não são inteiros válidos para comparação")
            
            if general_novos != level_novos:
                diff = general_novos - level_novos
                inconsistencies.append(f"Novos: {diff} tickets fora dos níveis N1-N4")
                
            if general_pendentes != level_pendentes:
                diff = general_pendentes - level_pendentes
                inconsistencies.append(f"Pendentes: {diff} tickets fora dos níveis N1-N4")
                
            if general_progresso != level_progresso:
                diff = general_progresso - level_progresso
                inconsistencies.append(f"Progresso: {diff} tickets fora dos níveis N1-N4")
                
            if general_resolvidos != level_resolvidos:
                diff = general_resolvidos - level_resolvidos
                inconsistencies.append(f"Resolvidos: {diff} tickets fora dos níveis N1-N4")
            
            if inconsistencies:
                print(f"\n⚠️  INCONSISTÊNCIAS DETECTADAS:")
                for inconsistency in inconsistencies:
                    print(f"  - {inconsistency}")
                    
                total_diff = general_total - level_total_all
                print(f"\n📊 RESUMO:")
                print(f"  - Total de tickets fora dos níveis N1-N4: {total_diff}")
                print(f"  - Isso indica que existem tickets em outros grupos além de N1, N2, N3 e N4")
                print(f"  - O dashboard está mostrando totais gerais de TODOS os grupos, mas detalhes apenas dos níveis N1-N4")
                
                logger.info(f"Inconsistências detectadas: {len(inconsistencies)} categorias afetadas")
            else:
                print(f"\n✅ DADOS CONSISTENTES: Não foram detectadas inconsistências")
                logger.info("Dados consistentes - nenhuma inconsistência detectada")
                
        except Exception as e:
            logger.error(f"Erro ao verificar inconsistências: {e}")
            print(f"❌ Erro ao verificar inconsistências: {e}")
        
        print("\n" + "=" * 80)
        print("4. INVESTIGANDO GRUPOS EXISTENTES")
        print("=" * 80)
        
        # Verificar quais grupos existem no sistema
        try:
            print(f"\nGrupos configurados no sistema:")
            service_levels = getattr(glpi, 'service_levels', {})
            if isinstance(service_levels, dict):
                print(f"Service Levels: {service_levels}")
            else:
                print(f"Service Levels: dados inválidos ({type(service_levels)})")
                logger.warning(f"Service levels inválidos: {type(service_levels)}")
        except Exception as e:
            logger.error(f"Erro ao obter grupos configurados: {e}")
            print(f"❌ Erro ao obter grupos configurados")
        
        # Verificar se há outros grupos
        try:
            if general_total > level_total_all:
                total_diff = general_total - level_total_all
                print(f"\n🔍 RECOMENDAÇÕES:")
                print(f"  1. Verificar se existem outros grupos de atendimento além de N1-N4")
                print(f"  2. Considerar incluir esses grupos no dashboard ou")
                print(f"  3. Ajustar o cálculo dos totais gerais para incluir apenas os grupos N1-N4")
                print(f"  4. Documentar claramente que os totais gerais incluem todos os grupos")
                print(f"  5. Total de tickets em outros grupos: {total_diff}")
                
                logger.info(f"Detectados {total_diff} tickets em grupos não monitorados")
            else:
                print(f"\n✅ Todos os tickets estão nos grupos monitorados (N1-N4)")
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
            print(f"❌ Erro ao gerar recomendações")
        
    except Exception as e:
        logger.error(f"Erro crítico durante a investigação: {e}")
        print(f"❌ Erro durante a investigação: {e}")
        try:
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            traceback.print_exc()
        except Exception:
            print("Erro adicional ao exibir stack trace")
    
    finally:
        # Fechar conexão de forma segura
        try:
            if 'glpi' in locals() and hasattr(glpi, 'close_session'):
                glpi.close_session()
                logger.info("Sessão GLPI fechada com sucesso")
        except Exception as e:
            logger.warning(f"Erro ao fechar sessão GLPI: {e}")
        
        print("\n" + "=" * 80)
        print("INVESTIGAÇÃO CONCLUÍDA")
        print("=" * 80)

if __name__ == "__main__":
    main()