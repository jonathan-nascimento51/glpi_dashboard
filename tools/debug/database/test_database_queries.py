#!/usr/bin/env python3
"""
Script para testar queries do banco de dados do GLPI Dashboard
Uso: python test_database_queries.py [--config CONFIG_FILE]
"""

import sqlite3
import json
import argparse
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

def load_config(config_file=None):
    """Carrega configuração do banco de dados"""
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    
    # Tenta carregar do arquivo padrão do backend
    backend_config = Path(__file__).parent.parent.parent.parent / 'backend' / 'config.json'
    if backend_config.exists():
        with open(backend_config, 'r') as f:
            config = json.load(f)
            return config.get('database', {})
    
    # Configuração padrão
    return {
        'path': 'backend/glpi_dashboard.db'
    }

def connect_database(config):
    """Conecta ao banco de dados"""
    db_path = config.get('path', 'backend/glpi_dashboard.db')
    
    # Ajusta o caminho relativo
    if not os.path.isabs(db_path):
        script_dir = Path(__file__).parent.parent.parent.parent
        db_path = script_dir / db_path
    
    print(f"🔍 Conectando ao banco: {db_path}")
    
    try:
        if not os.path.exists(db_path):
            print(f"❌ Arquivo do banco não encontrado: {db_path}")
            return None
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        print("✅ Conexão estabelecida")
        return conn
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def test_table_structure(conn):
    """Testa a estrutura das tabelas"""
    print("\n🏗️  Testando estrutura das tabelas...")
    
    try:
        cursor = conn.cursor()
        
        # Lista todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"  📋 {table}")
        
        # Verifica estrutura das tabelas principais
        important_tables = ['technicians', 'tickets', 'ticket_assignments']
        
        for table in important_tables:
            if table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print(f"\n📊 Estrutura da tabela '{table}':")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
            else:
                print(f"⚠️  Tabela '{table}' não encontrada")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False

def test_data_counts(conn):
    """Testa contagens básicas de dados"""
    print("\n📊 Testando contagens de dados...")
    
    queries = [
        ("SELECT COUNT(*) FROM technicians", "Total de técnicos"),
        ("SELECT COUNT(*) FROM tickets", "Total de tickets"),
        ("SELECT COUNT(*) FROM ticket_assignments", "Total de atribuições"),
        ("SELECT COUNT(DISTINCT level) FROM technicians", "Níveis únicos de técnicos"),
        ("SELECT COUNT(*) FROM tickets WHERE status = 'resolved'", "Tickets resolvidos"),
        ("SELECT COUNT(*) FROM tickets WHERE status = 'pending'", "Tickets pendentes")
    ]
    
    try:
        cursor = conn.cursor()
        results = []
        
        for query, description in queries:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"  ✅ {description}: {count}")
                results.append((description, count, True))
            except sqlite3.Error as e:
                print(f"  ❌ {description}: Erro - {e}")
                results.append((description, 0, False))
        
        return results
        
    except sqlite3.Error as e:
        print(f"❌ Erro geral nas contagens: {e}")
        return []

def test_ranking_query(conn):
    """Testa a query de ranking de técnicos"""
    print("\n🏆 Testando query de ranking...")
    
    ranking_query = """
    SELECT 
        t.id,
        t.name,
        t.level,
        COUNT(CASE WHEN tk.status = 'resolved' THEN 1 END) as resolved_tickets,
        COUNT(CASE WHEN tk.status = 'pending' THEN 1 END) as pending_tickets,
        COUNT(tk.id) as total_tickets,
        AVG(CASE 
            WHEN tk.status = 'resolved' AND tk.resolved_at IS NOT NULL 
            THEN (julianday(tk.resolved_at) - julianday(tk.created_at)) * 24 * 60
            ELSE NULL 
        END) as avg_resolution_time
    FROM technicians t
    LEFT JOIN ticket_assignments ta ON t.id = ta.technician_id
    LEFT JOIN tickets tk ON ta.ticket_id = tk.id
    GROUP BY t.id, t.name, t.level
    ORDER BY resolved_tickets DESC, avg_resolution_time ASC
    LIMIT 10
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(ranking_query)
        results = cursor.fetchall()
        
        print(f"✅ Query executada com sucesso - {len(results)} técnicos encontrados")
        
        if results:
            print("\n🥇 Top 5 técnicos:")
            for i, row in enumerate(results[:5], 1):
                name = row['name']
                level = row['level']
                resolved = row['resolved_tickets']
                pending = row['pending_tickets']
                total = row['total_tickets']
                avg_time = row['avg_resolution_time']
                
                print(f"  {i}. {name} ({level})")
                print(f"     Resolvidos: {resolved}, Pendentes: {pending}, Total: {total}")
                if avg_time:
                    print(f"     Tempo médio: {avg_time:.1f} minutos")
                else:
                    print(f"     Tempo médio: N/A")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro na query de ranking: {e}")
        return False

def test_date_filters(conn):
    """Testa queries com filtros de data"""
    print("\n📅 Testando filtros de data...")
    
    # Data de 30 dias atrás
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    date_queries = [
        (f"SELECT COUNT(*) FROM tickets WHERE created_at >= '{start_date}'", 
         f"Tickets criados desde {start_date}"),
        (f"SELECT COUNT(*) FROM tickets WHERE created_at BETWEEN '{start_date}' AND '{end_date}'", 
         f"Tickets no período {start_date} a {end_date}"),
        (f"SELECT COUNT(*) FROM tickets WHERE resolved_at >= '{start_date}'", 
         f"Tickets resolvidos desde {start_date}")
    ]
    
    try:
        cursor = conn.cursor()
        results = []
        
        for query, description in date_queries:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"  ✅ {description}: {count}")
                results.append((description, count, True))
            except sqlite3.Error as e:
                print(f"  ❌ {description}: Erro - {e}")
                results.append((description, 0, False))
        
        return results
        
    except sqlite3.Error as e:
        print(f"❌ Erro geral nos filtros de data: {e}")
        return []

def test_level_filters(conn):
    """Testa queries com filtros de nível"""
    print("\n🎯 Testando filtros de nível...")
    
    level_queries = [
        ("SELECT COUNT(*) FROM technicians WHERE level = 'N1'", "Técnicos N1"),
        ("SELECT COUNT(*) FROM technicians WHERE level = 'N2'", "Técnicos N2"),
        ("SELECT COUNT(*) FROM technicians WHERE level = 'N3'", "Técnicos N3"),
        ("SELECT COUNT(*) FROM technicians WHERE level = 'N4'", "Técnicos N4")
    ]
    
    try:
        cursor = conn.cursor()
        results = []
        
        for query, description in level_queries:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"  ✅ {description}: {count}")
                results.append((description, count, True))
            except sqlite3.Error as e:
                print(f"  ❌ {description}: Erro - {e}")
                results.append((description, 0, False))
        
        return results
        
    except sqlite3.Error as e:
        print(f"❌ Erro geral nos filtros de nível: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Testa queries do banco de dados')
    parser.add_argument('--config', help='Arquivo de configuração JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Saída verbosa')
    
    args = parser.parse_args()
    
    print(f"🚀 Testando banco de dados do GLPI Dashboard")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Carrega configuração
    config = load_config(args.config)
    
    # Conecta ao banco
    conn = connect_database(config)
    if not conn:
        sys.exit(1)
    
    try:
        # Executa testes
        tests_passed = 0
        total_tests = 6
        
        # Teste 1: Estrutura das tabelas
        if test_table_structure(conn):
            tests_passed += 1
        
        # Teste 2: Contagens básicas
        count_results = test_data_counts(conn)
        if count_results and any(result[2] for result in count_results):
            tests_passed += 1
        
        # Teste 3: Query de ranking
        if test_ranking_query(conn):
            tests_passed += 1
        
        # Teste 4: Filtros de data
        date_results = test_date_filters(conn)
        if date_results and any(result[2] for result in date_results):
            tests_passed += 1
        
        # Teste 5: Filtros de nível
        level_results = test_level_filters(conn)
        if level_results and any(result[2] for result in level_results):
            tests_passed += 1
        
        # Teste 6: Integridade referencial
        print("\n🔗 Testando integridade referencial...")
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM ticket_assignments ta
                LEFT JOIN technicians t ON ta.technician_id = t.id
                WHERE t.id IS NULL
            """)
            orphaned_assignments = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM ticket_assignments ta
                LEFT JOIN tickets tk ON ta.ticket_id = tk.id
                WHERE tk.id IS NULL
            """)
            orphaned_tickets = cursor.fetchone()[0]
            
            if orphaned_assignments == 0 and orphaned_tickets == 0:
                print("✅ Integridade referencial OK")
                tests_passed += 1
            else:
                print(f"❌ Problemas de integridade: {orphaned_assignments} atribuições órfãs, {orphaned_tickets} tickets órfãos")
                
        except sqlite3.Error as e:
            print(f"❌ Erro no teste de integridade: {e}")
        
        # Resumo
        print("\n📊 RESUMO DOS TESTES")
        print("=" * 50)
        print(f"🎯 Resultado Final: {tests_passed}/{total_tests} testes passaram")
        
        if tests_passed == total_tests:
            print("🎉 Todos os testes passaram! Banco de dados está íntegro.")
            sys.exit(0)
        else:
            print("⚠️  Alguns testes falharam. Verifique a integridade dos dados.")
            sys.exit(1)
    
    finally:
        conn.close()
        print("\n🔒 Conexão com banco fechada")

if __name__ == "__main__":
    main()