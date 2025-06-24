#!/usr/bin/env python3
"""
Utilitário para baixar e processar dados CNPJ da Receita Federal
Autor: Bruno Qualhato
Data: 23 de junho de 2025
"""

import os
import sys
import sqlite3
import zipfile
import requests
import re
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time
from datetime import datetime
import csv
import tempfile
import shutil
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cnpj_downloader.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CNPJDownloader:
    """Classe principal para download e processamento dos dados CNPJ"""
    
    def __init__(self, base_url: str = "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/2025-06/",
                 download_dir: str = "./dados_cnpj",
                 db_path: str = "./cnpj_dados.db",
                 max_workers: int = 4):
        """
        Inicializa o downloader
        
        Args:
            base_url: URL base dos dados CNPJ
            download_dir: Diretório para salvar os arquivos baixados
            db_path: Caminho do banco SQLite
            max_workers: Número máximo de threads para download
        """
        self.base_url = base_url
        self.download_dir = Path(download_dir)
        self.db_path = db_path
        self.max_workers = max_workers
        
        # Criar diretório de download se não existir
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar banco de dados
        self._init_database()
        
        # Configurar sessão HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _init_database(self):
        """Inicializa o banco de dados SQLite com as tabelas necessárias"""
        logger.info("Inicializando banco de dados SQLite...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de empresas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresas (
                cnpj_basico TEXT PRIMARY KEY,
                razao_social TEXT,
                natureza_juridica TEXT,
                qualificacao_responsavel TEXT,
                capital_social REAL,
                porte_empresa TEXT,
                ente_federativo TEXT
            )
        ''')
        
        # Tabela de estabelecimentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estabelecimentos (
                cnpj_basico TEXT,
                cnpj_ordem TEXT,
                cnpj_dv TEXT,
                identificador_matriz_filial TEXT,
                nome_fantasia TEXT,
                situacao_cadastral TEXT,
                data_situacao_cadastral TEXT,
                motivo_situacao_cadastral TEXT,
                nome_cidade_exterior TEXT,
                codigo_pais TEXT,
                data_inicio_atividade TEXT,
                cnae_fiscal_principal TEXT,
                cnae_fiscal_secundaria TEXT,
                tipo_logradouro TEXT,
                logradouro TEXT,
                numero TEXT,
                complemento TEXT,
                bairro TEXT,
                cep TEXT,
                uf TEXT,
                codigo_municipio TEXT,
                ddd_1 TEXT,
                telefone_1 TEXT,
                ddd_2 TEXT,
                telefone_2 TEXT,
                ddd_fax TEXT,
                fax TEXT,
                correio_eletronico TEXT,
                situacao_especial TEXT,
                data_situacao_especial TEXT,
                PRIMARY KEY (cnpj_basico, cnpj_ordem, cnpj_dv)
            )
        ''')
        
        # Tabela de sócios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS socios (
                cnpj_basico TEXT,
                identificador_socio TEXT,
                nome_socio TEXT,
                cpf_cnpj_socio TEXT,
                codigo_qualificacao_socio TEXT,
                data_entrada_sociedade TEXT,
                codigo_pais TEXT,
                representante_legal TEXT,
                nome_representante TEXT,
                codigo_qualificacao_representante TEXT,
                faixa_etaria TEXT
            )
        ''')
        
        # Tabela do Simples Nacional
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simples (
                cnpj_basico TEXT PRIMARY KEY,
                opcao_simples TEXT,
                data_opcao_simples TEXT,
                data_exclusao_simples TEXT,
                opcao_mei TEXT,
                data_opcao_mei TEXT,
                data_exclusao_mei TEXT
            )
        ''')
        
        # Tabelas de referência
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cnaes (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS municipios (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS naturezas (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paises (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qualificacoes (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS motivos (
                codigo TEXT PRIMARY KEY,
                descricao TEXT
            )
        ''')
        
        # Índices para melhor performance
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_empresas_razao ON empresas(razao_social)",
            "CREATE INDEX IF NOT EXISTS idx_estabelecimentos_cnpj ON estabelecimentos(cnpj_basico)",
            "CREATE INDEX IF NOT EXISTS idx_estabelecimentos_nome ON estabelecimentos(nome_fantasia)",
            "CREATE INDEX IF NOT EXISTS idx_estabelecimentos_uf ON estabelecimentos(uf)",
            "CREATE INDEX IF NOT EXISTS idx_socios_cnpj ON socios(cnpj_basico)",
            "CREATE INDEX IF NOT EXISTS idx_socios_nome ON socios(nome_socio)",
        ]
        
        for idx in indices:
            cursor.execute(idx)
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados inicializado com sucesso!")
    
    def get_file_list(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de arquivos disponíveis para download
        
        Returns:
            Lista de dicionários com informações dos arquivos
        """
        logger.info(f"Obtendo lista de arquivos de {self.base_url}")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            files = []
            
            # Encontrar todos os links para arquivos .zip
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.zip'):
                    # Obter informações do arquivo da tabela
                    row = link.find_parent('tr')
                    if row:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            filename = href
                            size_text = cells[2].get_text(strip=True)
                            
                            files.append({
                                'filename': filename,
                                'url': urljoin(self.base_url, href),
                                'size': size_text
                            })
            
            logger.info(f"Encontrados {len(files)} arquivos para download")
            return files
            
        except Exception as e:
            logger.error(f"Erro ao obter lista de arquivos: {e}")
            return []
    
    def download_file(self, file_info: Dict[str, Any]) -> bool:
        """
        Baixa um arquivo específico
        
        Args:
            file_info: Informações do arquivo a ser baixado
            
        Returns:
            True se o download foi bem-sucedido
        """
        url = file_info['url']
        filename = file_info['filename']
        filepath = self.download_dir / filename
        
        # Verificar se o arquivo já existe
        if filepath.exists():
            logger.info(f"Arquivo {filename} já existe, pulando download")
            return True
        
        try:
            logger.info(f"Baixando {filename} ({file_info['size']})...")
            
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Mostrar progresso a cada 10MB
                        if downloaded % (10 * 1024 * 1024) == 0:
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                logger.info(f"  Progresso {filename}: {progress:.1f}%")
            
            logger.info(f"Download concluído: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao baixar {filename}: {e}")
            if filepath.exists():
                filepath.unlink()  # Remove arquivo parcial
            return False
    
    def download_all_files(self) -> List[str]:
        """
        Baixa todos os arquivos disponíveis
        
        Returns:
            Lista de arquivos baixados com sucesso
        """
        files = self.get_file_list()
        if not files:
            logger.error("Nenhum arquivo encontrado para download")
            return []
        
        logger.info(f"Iniciando download de {len(files)} arquivos...")
        
        downloaded_files = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submeter todos os downloads
            future_to_file = {executor.submit(self.download_file, file_info): file_info 
                             for file_info in files}
            
            # Aguardar conclusão
            for future in as_completed(future_to_file):
                file_info = future_to_file[future]
                try:
                    success = future.result()
                    if success:
                        downloaded_files.append(file_info['filename'])
                except Exception as e:
                    logger.error(f"Erro no download de {file_info['filename']}: {e}")
        
        logger.info(f"Download concluído! {len(downloaded_files)} arquivos baixados")
        return downloaded_files
    
    def extract_and_process_file(self, zip_filename: str) -> bool:
        """
        Extrai e processa um arquivo ZIP
        
        Args:
            zip_filename: Nome do arquivo ZIP
            
        Returns:
            True se o processamento foi bem-sucedido
        """
        zip_path = self.download_dir / zip_filename
        
        if not zip_path.exists():
            logger.error(f"Arquivo não encontrado: {zip_path}")
            return False
        
        try:
            logger.info(f"Processando {zip_filename}...")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extrair para diretório temporário
                with tempfile.TemporaryDirectory() as temp_dir:
                    zip_ref.extractall(temp_dir)
                    
                    # Processar arquivos extraídos
                    for extracted_file in os.listdir(temp_dir):
                        # Aceitar qualquer arquivo que não seja diretório
                        csv_path = os.path.join(temp_dir, extracted_file)
                        if os.path.isfile(csv_path):
                            self._process_csv_file(csv_path, zip_filename)
            
            logger.info(f"Processamento concluído: {zip_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar {zip_filename}: {e}")
            return False
    
    def _process_csv_file(self, csv_path: str, zip_filename: str):
        """
        Processa um arquivo CSV específico
        
        Args:
            csv_path: Caminho do arquivo CSV
            zip_filename: Nome do arquivo ZIP original
        """
        try:
            # Determinar o tipo de dados baseado no nome do arquivo
            file_type = self._get_file_type(zip_filename)
            
            if not file_type:
                logger.warning(f"Tipo de arquivo não reconhecido: {zip_filename}")
                return
            
            logger.info(f"Importando dados de {zip_filename} para tabela {file_type}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ler CSV e inserir dados
            with open(csv_path, 'r', encoding='latin-1', errors='ignore') as csvfile:
                # Tentar diferentes delimitadores
                sample = csvfile.read(2048)
                csvfile.seek(0)
                
                # Detectar delimitador
                delimiter = ';'
                if sample.count(';') == 0 and '|' in sample:
                    delimiter = '|'
                elif sample.count(';') == 0 and '\t' in sample:
                    delimiter = '\t'
                
                logger.info(f"  Usando delimitador: '{delimiter}'")
                
                reader = csv.reader(csvfile, delimiter=delimiter)
                
                batch_size = 1000
                batch = []
                
                for row_num, row in enumerate(reader):
                    if row_num % 10000 == 0:
                        logger.info(f"  Processando linha {row_num}...")
                    
                    # Preparar dados baseado no tipo
                    processed_row = self._prepare_row_data(row, file_type)
                    if processed_row:
                        batch.append(processed_row)
                    
                    # Inserir em lotes
                    if len(batch) >= batch_size:
                        self._insert_batch(cursor, batch, file_type)
                        batch = []
                
                # Inserir lote final
                if batch:
                    self._insert_batch(cursor, batch, file_type)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Importação concluída: {zip_filename}")
            
        except Exception as e:
            logger.error(f"Erro ao processar CSV {csv_path}: {e}")
    
    def _get_file_type(self, filename: str) -> Optional[str]:
        """
        Determina o tipo de arquivo baseado no nome
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Tipo do arquivo ou None
        """
        filename_lower = filename.lower()
        
        if filename_lower.startswith('empresas'):
            return 'empresas'
        elif filename_lower.startswith('estabelecimentos'):
            return 'estabelecimentos'
        elif filename_lower.startswith('socios'):
            return 'socios'
        elif filename_lower.startswith('simples'):
            return 'simples'
        elif filename_lower.startswith('cnaes'):
            return 'cnaes'
        elif filename_lower.startswith('municipios'):
            return 'municipios'
        elif filename_lower.startswith('naturezas'):
            return 'naturezas'
        elif filename_lower.startswith('paises'):
            return 'paises'
        elif filename_lower.startswith('qualificacoes'):
            return 'qualificacoes'
        elif filename_lower.startswith('motivos'):
            return 'motivos'
        
        return None
    
    def _prepare_row_data(self, row: List[str], file_type: str) -> Optional[tuple]:
        """
        Prepara os dados de uma linha para inserção
        
        Args:
            row: Dados da linha
            file_type: Tipo do arquivo
            
        Returns:
            Tupla com dados preparados ou None
        """
        try:
            # Limpar e normalizar dados
            clean_row = [cell.strip().replace('"', '') if cell else None for cell in row]
            
            # Mapear campos baseado no tipo
            if file_type == 'empresas':
                if len(clean_row) >= 7:
                    return tuple(clean_row[:7])
            elif file_type == 'estabelecimentos':
                if len(clean_row) >= 30:
                    return tuple(clean_row[:30])
            elif file_type == 'socios':
                if len(clean_row) >= 11:
                    return tuple(clean_row[:11])
            elif file_type == 'simples':
                if len(clean_row) >= 7:
                    return tuple(clean_row[:7])
            elif file_type in ['cnaes', 'municipios', 'naturezas', 'paises', 'qualificacoes', 'motivos']:
                if len(clean_row) >= 2:
                    return tuple(clean_row[:2])
            
            return None
            
        except Exception as e:
            logger.warning(f"Erro ao preparar dados da linha: {e}")
            return None
    
    def _insert_batch(self, cursor, batch: List[tuple], file_type: str):
        """
        Insere um lote de dados no banco
        
        Args:
            cursor: Cursor do banco
            batch: Lote de dados
            file_type: Tipo do arquivo
        """
        try:
            placeholders = {
                'empresas': '(?, ?, ?, ?, ?, ?, ?)',
                'estabelecimentos': '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                'socios': '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                'simples': '(?, ?, ?, ?, ?, ?, ?)',
                'cnaes': '(?, ?)',
                'municipios': '(?, ?)',
                'naturezas': '(?, ?)',
                'paises': '(?, ?)',
                'qualificacoes': '(?, ?)',
                'motivos': '(?, ?)'
            }
            
            if file_type in placeholders:
                query = f"INSERT OR REPLACE INTO {file_type} VALUES {placeholders[file_type]}"
                cursor.executemany(query, batch)
            
        except Exception as e:
            logger.error(f"Erro ao inserir lote na tabela {file_type}: {e}")
    
    def process_all_files(self):
        """Processa todos os arquivos baixados"""
        zip_files = [f for f in os.listdir(self.download_dir) if f.endswith('.zip')]
        
        if not zip_files:
            logger.warning("Nenhum arquivo ZIP encontrado para processar")
            return
        
        logger.info(f"Processando {len(zip_files)} arquivos...")
        
        for zip_file in zip_files:
            self.extract_and_process_file(zip_file)
    
    def get_database_stats(self) -> Dict[str, int]:
        """
        Obtém estatísticas do banco de dados
        
        Returns:
            Dicionário com contagem de registros por tabela
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tables = ['empresas', 'estabelecimentos', 'socios', 'simples', 
                 'cnaes', 'municipios', 'naturezas', 'paises', 'qualificacoes', 'motivos']
        
        stats = {}
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            except Exception as e:
                logger.warning(f"Erro ao obter estatísticas da tabela {table}: {e}")
                stats[table] = 0
        
        conn.close()
        return stats
    
    def run_complete_process(self):
        """Executa o processo completo de download e processamento"""
        logger.info("Iniciando processo completo de download e processamento...")
        
        start_time = time.time()
        
        # 1. Baixar arquivos
        downloaded_files = self.download_all_files()
        
        if not downloaded_files:
            logger.error("Nenhum arquivo foi baixado. Encerrando processo.")
            return
        
        # 2. Processar arquivos
        self.process_all_files()
        
        # 3. Mostrar estatísticas
        stats = self.get_database_stats()
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info("="*50)
        logger.info("PROCESSO CONCLUÍDO!")
        logger.info(f"Tempo total: {duration:.2f} segundos")
        logger.info(f"Arquivos baixados: {len(downloaded_files)}")
        logger.info(f"Banco de dados: {self.db_path}")
        logger.info("="*50)
        logger.info("ESTATÍSTICAS DO BANCO:")
        for table, count in stats.items():
            logger.info(f"  {table}: {count:,} registros")
        logger.info("="*50)


if __name__ == "__main__":
    # Configurações
    BASE_URL = "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/2025-06/"
    DOWNLOAD_DIR = "./dados_cnpj"
    DB_PATH = "./cnpj_dados.db"
    MAX_WORKERS = 4
    
    # Criar e executar o downloader
    downloader = CNPJDownloader(
        base_url=BASE_URL,
        download_dir=DOWNLOAD_DIR,
        db_path=DB_PATH,
        max_workers=MAX_WORKERS
    )
    
    try:
        downloader.run_complete_process()
    except KeyboardInterrupt:
        logger.info("Processo interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro no processo: {e}")
