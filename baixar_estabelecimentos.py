#!/usr/bin/env python3
"""
Script para baixar estabelecimentos específicos para teste
"""

import sys
from pathlib import Path

# Adicionar diretório atual ao path
sys.path.append(str(Path.cwd()))

from downloader_cnpj import CNPJDownloader
import logging

def baixar_estabelecimentos_teste():
    """Baixa um arquivo de estabelecimentos para teste"""
    
    print("🏪 Baixando dados de estabelecimentos para teste...")
    
    downloader = CNPJDownloader(
        download_dir="./dados_teste",
        db_path="./cnpj_teste.db",
        max_workers=2
    )
    
    # Obter lista de arquivos
    files = downloader.get_file_list()
    
    # Encontrar arquivo de estabelecimentos pequeno
    estabelecimentos_files = [f for f in files if f['filename'].startswith('Estabelecimentos')]
    
    if not estabelecimentos_files:
        print("❌ Nenhum arquivo de estabelecimentos encontrado")
        return False
    
    # Pegar o último arquivo (geralmente menor)
    arquivo_escolhido = estabelecimentos_files[-1]
    
    print(f"📥 Baixando {arquivo_escolhido['filename']} ({arquivo_escolhido['size']})...")
    
    # Baixar e processar
    success = downloader.download_file(arquivo_escolhido)
    if success:
        print("📦 Extraindo e processando...")
        downloader.extract_and_process_file(arquivo_escolhido['filename'])
        
        # Verificar resultado
        stats = downloader.get_database_stats()
        estabelecimentos = stats.get('estabelecimentos', 0)
        
        print(f"✅ Processamento concluído!")
        print(f"📊 Estabelecimentos importados: {estabelecimentos:,}")
        
        return estabelecimentos > 0
    
    return False

if __name__ == "__main__":
    baixar_estabelecimentos_teste()
