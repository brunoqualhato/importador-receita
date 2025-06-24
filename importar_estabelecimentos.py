#!/usr/bin/env python3
"""
Script para importar dados de estabelecimentos com empresas para o banco
Necessário antes de gerar os CSVs unificados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from downloader_cnpj import CNPJDownloader
import logging

def importar_estabelecimentos():
    """Importa dados de estabelecimentos se ainda não foram importados"""
    
    print("=== IMPORTAÇÃO DE ESTABELECIMENTOS ===\n")
    
    # Usar banco principal se existir, senão banco de teste
    db_paths = ["./cnpj_dados.db", "./cnpj_teste.db"]
    db_path = None
    
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Nenhum banco de dados encontrado!")
        print("Execute primeiro o downloader_cnpj.py ou download_teste.py")
        return False
    
    print(f"📊 Usando banco: {db_path}")
    
    # Verificar se já tem estabelecimentos
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM estabelecimentos")
    count_est = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM empresas")
    count_emp = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"📈 Empresas no banco: {count_emp:,}")
    print(f"📈 Estabelecimentos no banco: {count_est:,}")
    
    if count_est > 0:
        print("✅ Estabelecimentos já foram importados!")
        return True
    
    if count_emp == 0:
        print("❌ Não há dados de empresas. Execute primeiro o download dos dados.")
        return False
    
    print("\n📥 Estabelecimentos não encontrados. Iniciando importação...")
    
    # Buscar arquivos de estabelecimentos
    download_dirs = ["./dados_cnpj", "./dados_teste"]
    download_dir = None
    
    for dir_path in download_dirs:
        if os.path.exists(dir_path):
            files = [f for f in os.listdir(dir_path) if f.startswith('Estabelecimentos') and f.endswith('.zip')]
            if files:
                download_dir = dir_path
                break
    
    if not download_dir:
        print("❌ Arquivos de estabelecimentos não encontrados!")
        print("Execute o download completo para obter todos os dados.")
        return False
    
    print(f"📁 Arquivos encontrados em: {download_dir}")
    
    # Configurar downloader para processar apenas estabelecimentos
    if "teste" in db_path:
        downloader = CNPJDownloader(
            download_dir=download_dir,
            db_path=db_path,
            max_workers=2
        )
    else:
        downloader = CNPJDownloader(
            download_dir=download_dir,
            db_path=db_path,
            max_workers=4
        )
    
    # Processar apenas arquivos de estabelecimentos
    estabelecimentos_files = [f for f in os.listdir(download_dir) 
                             if f.startswith('Estabelecimentos') and f.endswith('.zip')]
    
    if not estabelecimentos_files:
        print("❌ Nenhum arquivo de estabelecimentos encontrado!")
        return False
    
    print(f"📦 Arquivos de estabelecimentos encontrados: {len(estabelecimentos_files)}")
    
    # Processar apenas primeiro arquivo se for banco de teste
    if "teste" in db_path:
        estabelecimentos_files = estabelecimentos_files[:1]
        print(f"🧪 Modo teste: processando apenas {estabelecimentos_files[0]}")
    
    success_count = 0
    for filename in estabelecimentos_files:
        try:
            print(f"\n📋 Processando {filename}...")
            success = downloader.extract_and_process_file(filename)
            if success:
                success_count += 1
                
                # Verificar progresso
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM estabelecimentos")
                current_count = cursor.fetchone()[0]
                conn.close()
                
                print(f"✅ {filename} processado! Total de estabelecimentos: {current_count:,}")
            else:
                print(f"❌ Erro ao processar {filename}")
                
        except Exception as e:
            print(f"❌ Erro ao processar {filename}: {e}")
    
    print(f"\n🎯 Processamento concluído!")
    print(f"📊 Arquivos processados com sucesso: {success_count}/{len(estabelecimentos_files)}")
    
    # Estatísticas finais
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM estabelecimentos")
    final_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM estabelecimentos WHERE uf IS NOT NULL")
    with_uf = cursor.fetchone()[0]
    
    cursor.execute("SELECT uf, COUNT(*) FROM estabelecimentos WHERE uf IS NOT NULL GROUP BY uf ORDER BY COUNT(*) DESC LIMIT 5")
    top_ufs = cursor.fetchall()
    
    conn.close()
    
    print(f"\n📈 ESTATÍSTICAS FINAIS:")
    print(f"   Total de estabelecimentos: {final_count:,}")
    print(f"   Com UF definida: {with_uf:,}")
    print(f"\n🏆 TOP 5 ESTADOS:")
    for uf, count in top_ufs:
        print(f"   {uf}: {count:,}")
    
    return final_count > 0


if __name__ == "__main__":
    try:
        success = importar_estabelecimentos()
        if success:
            print("\n✅ Importação concluída com sucesso!")
            print("🔄 Agora você pode executar: python gerar_csv_estados.py")
        else:
            print("\n❌ Importação falhou!")
    except KeyboardInterrupt:
        print("\n⏹️  Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        logging.exception("Erro detalhado:")
