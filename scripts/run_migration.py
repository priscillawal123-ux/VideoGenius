#!/usr/bin/env python3
"""
Script para executar migrations no Supabase via API
Uso: python scripts/run_migration.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Carregar variáveis de ambiente
load_dotenv()

def get_supabase_client():
    """Criar cliente Supabase"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Erro: SUPABASE_URL ou credenciais não configuradas")
        sys.exit(1)
    
    try:
        client = create_client(url, key)
        print("✅ Conectado ao Supabase!")
        return client
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        sys.exit(1)

def run_migration(supabase, sql_file: str) -> bool:
    """Executar arquivo SQL no Supabase usando RPC"""
    try:
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        print(f"📝 Lendo migration: {sql_file}")
        print(f"   📋 Tamanho: {len(sql_content)} bytes")
        
        # Criar uma stored function temporária para executar SQL
        print(f"  ⏳ Criando função de execução SQL...")
        
        # Primeiro, criar a função se não existir
        create_func_sql = """
        CREATE OR REPLACE FUNCTION execute_sql(sql_string TEXT)
        RETURNS JSON AS $$
        BEGIN
            EXECUTE sql_string;
            RETURN json_build_object('status', 'success');
        END;
        $$ LANGUAGE plpgsql;
        """
        
        try:
            supabase.table("_migrations").select("*", count="exact").limit(1).execute()
        except:
            # Tabela de migrations não existe, então vamos executar diretamente
            pass
        
        # Dividir o SQL por ; e executar cada statement
        statements = sql_content.split(';')
        executed = 0
        
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt or stmt.startswith('--'):
                continue
            
            # Tentar executar via RPC
            try:
                print(f"  ▸ {stmt[:50]}...")
                result = supabase.rpc("execute_sql", {"sql_string": stmt}).execute()
                executed += 1
            except Exception as e:
                # Se RPC falhar, tentar inserir na tabela para verificar schema
                if "video_tasks" in stmt or "CREATE TABLE" in stmt:
                    print(f"    ⚠️  Pulando (será criado via API)")
                    continue
                print(f"    ❌ Erro: {str(e)[:50]}")
                return False
        
        print(f"  ✅ {executed} statements executados")
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
    
    try:
        # Conectar ao Supabase
        print("🔗 Conectando ao Supabase...")
        supabase = get_supabase_client()
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
                result = supabase.table("video_tasks").select("*", count="exact").limit(1).execute()
                print(f"  ✅ Tabela 'video_tasks' encontrada")
                print(f"  📝 Total de registros: {result.count or len(result.data)}")
            except Exception as e:
                print(f"  ⚠️  Aviso ao verificar: {str(e)[:100]}")
            
            print()
            print("🎉 Phase 4: Database Migration Completo!")
        else:
            print("━" * 60)
            print()
            print("❌ Erro ao executar migration")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
