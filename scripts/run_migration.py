#!/usr/bin/env python3
"""
Script para executar migrations no Supabase
Uso: python scripts/run_migration.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Supabase imports
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Criar cliente Supabase"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Erro: SUPABASE_URL e SUPABASE_KEY não configuradas")
        sys.exit(1)
    
    return create_client(url, key)

def run_migration(supabase: Client, sql_file: str) -> bool:
    """Executar arquivo SQL no Supabase"""
    try:
        with open(sql_file, 'r') as f:
            sql = f.read()
        
        print(f"📝 Executando migration: {sql_file}")
        
        # Executar cada statement SQL
        for statement in sql.split(';'):
            statement = statement.strip()
            if not statement:
                continue
            
            print(f"  ▸ Executando: {statement[:60]}...")
            
            # Usar o cliente HTTP do Supabase para executar SQL bruto
            response = supabase.postgrest.session.post(
                f"{supabase.postgrest.base_url}/rpc/execute_sql",
                json={"sql": statement}
            )
            
            if response.status_code not in [200, 201]:
                print(f"  ❌ Erro: {response.text}")
                return False
            
            print(f"  ✅ OK")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro ao executar migration: {e}")
        return False

def main():
    """Main"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║           🚀 Supabase Migration Runner                    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Conectar ao Supabase
    print("🔗 Conectando ao Supabase...")
    supabase = get_supabase_client()
    print("✅ Conectado!")
    print()
    
    # Encontrar migration file
    migration_file = "migrations/20241018_create_video_tasks.sql"
    
    if not os.path.exists(migration_file):
        print(f"❌ Arquivo não encontrado: {migration_file}")
        sys.exit(1)
    
    # Executar migration
    print("━" * 60)
    if run_migration(supabase, migration_file):
        print("━" * 60)
        print()
        print("✅ Migration executada com sucesso!")
        print()
        print("📊 Verificando tabela criada...")
        
        # Verificar se tabela foi criada
        try:
            response = supabase.table("video_tasks").select("*", count="exact").execute()
            print(f"  ✅ Tabela 'video_tasks' criada")
            print(f"  📝 Registros: {response.count}")
        except Exception as e:
            print(f"  ⚠️  Aviso: {e}")
        
        print()
        print("🎉 Phase 2: Database Setup Completo!")
    else:
        print("━" * 60)
        print()
        print("❌ Erro ao executar migration")
        sys.exit(1)

if __name__ == "__main__":
    main()
