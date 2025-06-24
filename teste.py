#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do utilitário CNPJ
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from downloader_cnpj import CNPJDownloader
import time

def teste_basico():
    """Teste básico do sistema"""
    print("=== TESTE DO UTILITÁRIO CNPJ ===\n")
    
    # Criar instância do downloader
    downloader = CNPJDownloader(
        download_dir="./teste_dados",
        db_path="./teste_cnpj.db",
        max_workers=2
    )
    
    print("✓ Downloader criado com sucesso")
    
    # Testar conexão com o site
    print("Testando conexão com o site da Receita Federal...")
    try:
        files = downloader.get_file_list()
        print(f"✓ Conexão OK - {len(files)} arquivos encontrados")
        
        # Mostrar alguns arquivos
        print("\nPrimeiros 5 arquivos encontrados:")
        for file_info in files[:5]:
            print(f"  - {file_info['filename']} ({file_info['size']})")
        
    except Exception as e:
        print(f"✗ Erro na conexão: {e}")
        return False
    
    # Testar banco de dados
    print("\nTestando criação do banco de dados...")
    try:
        stats = downloader.get_database_stats()
        print("✓ Banco de dados criado com sucesso")
        print(f"  Tabelas criadas: {len(stats)}")
        
    except Exception as e:
        print(f"✗ Erro no banco: {e}")
        return False
    
    print("\n=== TESTE CONCLUÍDO COM SUCESSO! ===")
    print("\nPara usar o sistema completo:")
    print("1. Execute: python downloader_cnpj.py")
    print("2. Aguarde o download e processamento (pode levar horas)")
    print("3. Use: python consultar_cnpj.py --stats")
    
    return True

if __name__ == "__main__":
    teste_basico()
