#!/usr/bin/env python3
"""
Script para download e teste de um subconjunto dos dados CNPJ
Útil para testar o sistema sem baixar todos os dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from downloader_cnpj import CNPJDownloader
import logging

def download_teste():
    """Baixa apenas alguns arquivos para teste"""
    print("=== DOWNLOAD DE TESTE - DADOS CNPJ ===\n")
    
    # Configurar para teste
    downloader = CNPJDownloader(
        download_dir="./dados_teste",
        db_path="./cnpj_teste.db",
        max_workers=2
    )
    
    # Obter lista de arquivos
    files = downloader.get_file_list()
    if not files:
        print("Erro: Não foi possível obter lista de arquivos")
        return
    
    # Selecionar apenas alguns arquivos para teste
    arquivos_teste = []
    tipos_desejados = ['Cnaes', 'Municipios', 'Naturezas', 'Paises', 'Qualificacoes', 'Motivos']
    
    for file_info in files:
        for tipo in tipos_desejados:
            if file_info['filename'].startswith(tipo):
                arquivos_teste.append(file_info)
                break
    
    # Adicionar um arquivo de empresas pequeno se disponível
    for file_info in files:
        if file_info['filename'].startswith('Empresas') and '1.zip' in file_info['filename']:
            arquivos_teste.append(file_info)
            break
    
    print(f"Arquivos selecionados para teste ({len(arquivos_teste)}):")
    for file_info in arquivos_teste:
        print(f"  - {file_info['filename']} ({file_info['size']})")
    
    print("\nIniciando download...")
    
    # Baixar arquivos selecionados
    downloaded = []
    for file_info in arquivos_teste:
        success = downloader.download_file(file_info)
        if success:
            downloaded.append(file_info['filename'])
    
    print(f"\nDownload concluído: {len(downloaded)} arquivos")
    
    # Processar arquivos baixados
    if downloaded:
        print("\nProcessando arquivos...")
        for filename in downloaded:
            downloader.extract_and_process_file(filename)
        
        # Mostrar estatísticas
        stats = downloader.get_database_stats()
        print("\n=== ESTATÍSTICAS DO BANCO DE TESTE ===")
        total_registros = 0
        for table, count in stats.items():
            if count > 0:
                print(f"{table}: {count:,} registros")
                total_registros += count
        
        print(f"\nTotal de registros: {total_registros:,}")
        print(f"Banco de dados: {downloader.db_path}")
        
        # Testar consultas
        print("\n=== TESTE DE CONSULTAS ===")
        from consultar_cnpj import CNPJQuery
        
        query = CNPJQuery(downloader.db_path)
        
        # Mostrar algumas empresas
        import sqlite3
        conn = sqlite3.connect(downloader.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT cnpj_basico, razao_social FROM empresas LIMIT 3")
        empresas = cursor.fetchall()
        
        if empresas:
            print("Primeiras empresas encontradas:")
            for cnpj, razao in empresas:
                print(f"  {cnpj} - {razao}")
                
                # Testar consulta completa
                empresa = query.buscar_empresa_por_cnpj(cnpj)
                if empresa:
                    capital = empresa['capital_social'] or 0
                    try:
                        capital_float = float(capital)
                    except (ValueError, TypeError):
                        capital_float = 0.0
                    print(f"    Capital: R$ {capital_float:,.2f}")
        
        # Mostrar CNAEs
        cursor.execute("SELECT codigo, descricao FROM cnaes LIMIT 5")
        cnaes = cursor.fetchall()
        
        if cnaes:
            print("\nCNAEs cadastrados:")
            for codigo, desc in cnaes:
                print(f"  {codigo} - {desc}")
        
        conn.close()
        
        print("\n=== TESTE CONCLUÍDO COM SUCESSO! ===")
        print(f"Banco de teste criado: {downloader.db_path}")
        print("Use este comando para consultas:")
        print(f"python consultar_cnpj.py --db {downloader.db_path} --stats")
    
    else:
        print("Nenhum arquivo foi baixado com sucesso")

if __name__ == "__main__":
    try:
        download_teste()
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário")
    except Exception as e:
        print(f"Erro: {e}")
        logging.exception("Erro detalhado:")
