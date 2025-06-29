#!/usr/bin/env python3
"""
Gerador de arquivos CSV unificados por estado para importação no WordPress
Autor: Bruno Qualhato
Data: 23 de junho de 2025
"""

import sqlite3
import csv
import os
from pathlib import Path
import logging
from typing import Dict, List, Optional
import sys

# Configuração de lo        # Cabeçalho do CSV
        headers = [
            'cnpj_basico', 'razao_social', 'natureza_juridica', 'natureza_descricao',
            'capital_social', 'porte_empresa', 'porte_descricao',
            'cnpj_ordem', 'cnpj_dv', 'cnpj_completo', 'tipo_estabelecimento',
            'nome_fantasia', 'situacao_cadastral', 'data_situacao_cadastral', 'data_inicio_atividade',
            'cnae_fiscal_principal', 'cnae_descricao', 'cnae_fiscal_secundaria', 'atividades_secundarias',
            'tipo_logradouro', 'logradouro', 'numero', 'complemento', 'bairro', 'cep',
            'uf', 'codigo_municipio', 'municipio_nome',
            'ddd_1', 'telefone_1', 'ddd_2', 'telefone_2', 'ddd_fax', 'fax', 'correio_eletronico',
            'situacao_especial', 'data_situacao_especial',
            'opcao_simples', 'data_opcao_simples', 'data_exclusao_simples',
            'opcao_mei', 'data_opcao_mei', 'data_exclusao_mei',
            'total_socios', 'socios_cnpj'
        ]asicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gerador_csv.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class GeradorCSVEstados:
    """Gera arquivos CSV unificados por estado para WordPress"""
    
    def __init__(self, db_path: str = "./cnpj_dados.db", output_dir: str = "./csv_estados"):
        """
        Inicializa o gerador
        
        Args:
            db_path: Caminho do banco SQLite
            output_dir: Diretório de saída dos arquivos CSV
        """
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.max_linhas_arquivo = 100000  # 100 mil linhas por arquivo
        
        # Criar diretório de saída
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Gerador inicializado - Banco: {db_path}, Saída: {output_dir}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Retorna conexão com o banco"""
        return sqlite3.connect(self.db_path)
    
    def get_atividades_secundarias(self, cnae_secundaria: str) -> str:
        """
        Processa e formata as atividades secundárias
        
        Args:
            cnae_secundaria: String com CNAEs secundários separados por algum delimitador
            
        Returns:
            String com descrições das atividades separadas por vírgula
        """
        if not cnae_secundaria or cnae_secundaria.strip() == '':
            return ''
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Separar os códigos CNAE (pode estar separado por vírgula, ponto e vírgula, etc.)
            cnaes = []
            for delim in [',', ';', '|', ' ']:
                if delim in cnae_secundaria:
                    cnaes = [cnae.strip() for cnae in cnae_secundaria.split(delim) if cnae.strip()]
                    break
            
            if not cnaes:
                cnaes = [cnae_secundaria.strip()]
            
            # Buscar descrições dos CNAEs
            descricoes = []
            for cnae in cnaes:
                if cnae and cnae != '':
                    cursor.execute("SELECT descricao FROM cnaes WHERE codigo = ?", (cnae,))
                    result = cursor.fetchone()
                    if result:
                        descricoes.append(result[0])
                    else:
                        descricoes.append(f"CNAE {cnae}")
            
            return ', '.join(descricoes)
        
        except Exception as e:
            logger.warning(f"Erro ao processar atividades secundárias: {e}")
            return cnae_secundaria or ''
        
        finally:
            conn.close()
    
    def get_socios_cnpj(self, cnpj_basico: str) -> str:
        """
        Busca todos os CNPJs dos sócios de uma empresa
        
        Args:
            cnpj_basico: CNPJ básico da empresa
            
        Returns:
            String com CNPJs dos sócios separados por vírgula
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
            SELECT cpf_cnpj_socio 
            FROM socios 
            WHERE cnpj_basico = ? AND cpf_cnpj_socio IS NOT NULL AND cpf_cnpj_socio != ''
            """
            
            cursor.execute(query, (cnpj_basico,))
            results = cursor.fetchall()
            
            cnpjs = []
            for result in results:
                cpf_cnpj = result[0].strip()
                # Verificar se é CNPJ (14 dígitos) e não CPF (11 dígitos)
                if len(cpf_cnpj) == 14 and cpf_cnpj.isdigit():
                    cnpjs.append(cpf_cnpj)
            
            return ', '.join(cnpjs)
        
        except Exception as e:
            logger.warning(f"Erro ao buscar sócios CNPJ: {e}")
            return ''
        
        finally:
            conn.close()

    def get_estados_disponiveis(self) -> List[str]:
        """
        Obtém lista de estados com dados
        
        Returns:
            Lista de códigos UF
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT DISTINCT uf 
        FROM estabelecimentos 
        WHERE uf IS NOT NULL AND uf != ''
        ORDER BY uf
        """
        
        cursor.execute(query)
        estados = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        logger.info(f"Estados encontrados: {len(estados)} - {', '.join(estados)}")
        return estados
    
    def contar_registros_por_estado(self, uf: str) -> int:
        """
        Conta quantos registros existem para um estado
        
        Args:
            uf: Código do estado
            
        Returns:
            Número de registros
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT COUNT(*)
        FROM estabelecimentos e
        LEFT JOIN empresas emp ON e.cnpj_basico = emp.cnpj_basico
        WHERE e.uf = ? AND e.situacao_cadastral = '02'
        """
        
        cursor.execute(query, (uf,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def gerar_csv_para_estado(self, uf: str) -> List[str]:
        """
        Gera arquivos CSV para um estado específico
        
        Args:
            uf: Código do estado
            
        Returns:
            Lista de arquivos gerados
        """
        logger.info(f"Processando estado: {uf}")
        
        total_registros = self.contar_registros_por_estado(uf)
        logger.info(f"Total de registros para {uf}: {total_registros:,}")
        
        if total_registros == 0:
            logger.warning(f"Nenhum registro encontrado para {uf}")
            return []
        
        # Calcular número de arquivos necessários
        num_arquivos = (total_registros + self.max_linhas_arquivo - 1) // self.max_linhas_arquivo
        
        arquivos_gerados = []
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Query principal unindo todas as tabelas
        query = """
        SELECT 
            -- Dados da empresa
            emp.cnpj_basico,
            emp.razao_social,
            emp.natureza_juridica,
            nat.descricao as natureza_descricao,
            emp.capital_social,
            emp.porte_empresa,
            CASE emp.porte_empresa
                WHEN '01' THEN 'Micro Empresa'
                WHEN '03' THEN 'Empresa de Pequeno Porte'
                WHEN '05' THEN 'Demais'
                ELSE emp.porte_empresa
            END as porte_descricao,
            
            -- Dados do estabelecimento
            e.cnpj_ordem,
            e.cnpj_dv,
            (emp.cnpj_basico || e.cnpj_ordem || e.cnpj_dv) as cnpj_completo,
            CASE e.identificador_matriz_filial
                WHEN '1' THEN 'Matriz'
                WHEN '2' THEN 'Filial'
                ELSE 'N/A'
            END as tipo_estabelecimento,
            e.nome_fantasia,
            'Ativa' as situacao_cadastral,
            e.data_situacao_cadastral,
            e.data_inicio_atividade,
            
            -- CNAE
            e.cnae_fiscal_principal,
            cnae.descricao as cnae_descricao,
            e.cnae_fiscal_secundaria,
            
            -- Endereço
            e.tipo_logradouro,
            e.logradouro,
            e.numero,
            e.complemento,
            e.bairro,
            e.cep,
            e.uf,
            e.codigo_municipio,
            mun.descricao as municipio_nome,
            
            -- Contato
            e.ddd_1,
            e.telefone_1,
            e.ddd_2,
            e.telefone_2,
            e.ddd_fax,
            e.fax,
            e.correio_eletronico,
            
            -- Situação especial
            e.situacao_especial,
            e.data_situacao_especial,
            
            -- Simples Nacional
            s.opcao_simples,
            s.data_opcao_simples,
            s.data_exclusao_simples,
            s.opcao_mei,
            s.data_opcao_mei,
            s.data_exclusao_mei,
            
            -- Contagem de sócios
            (SELECT COUNT(*) FROM socios soc WHERE soc.cnpj_basico = emp.cnpj_basico) as total_socios,
            
            -- Atividades secundárias
            e.cnae_fiscal_secundaria,
            (SELECT GROUP_CONCAT(descricao, ', ') FROM cnaes WHERE codigo IN (e.cnae_fiscal_secundaria)) as atividades_secundarias,
            
            -- CNPJs dos sócios
            (SELECT GROUP_CONCAT(cpf_cnpj_socio, ', ') FROM socios WHERE cnpj_basico = emp.cnpj_basico AND cpf_cnpj_socio IS NOT NULL AND cpf_cnpj_socio != '') as cnpjs_socios
            
        FROM estabelecimentos e
        JOIN empresas emp ON e.cnpj_basico = emp.cnpj_basico
        LEFT JOIN naturezas nat ON emp.natureza_juridica = nat.codigo
        LEFT JOIN cnaes cnae ON e.cnae_fiscal_principal = cnae.codigo
        LEFT JOIN municipios mun ON e.codigo_municipio = mun.codigo
        LEFT JOIN simples s ON emp.cnpj_basico = s.cnpj_basico
        WHERE e.uf = ? AND e.situacao_cadastral = '02'
        ORDER BY emp.razao_social, e.cnpj_ordem
        """
        
        # Cabeçalho do CSV
        headers = [
            'cnpj_basico', 'razao_social', 'natureza_juridica', 'natureza_descricao',
            'capital_social', 'porte_empresa', 'porte_descricao',
            'cnpj_ordem', 'cnpj_dv', 'cnpj_completo', 'tipo_estabelecimento',
            'nome_fantasia', 'situacao_cadastral', 'data_situacao_cadastral', 'data_inicio_atividade',
            'cnae_fiscal_principal', 'cnae_descricao', 'cnae_fiscal_secundaria',
            'tipo_logradouro', 'logradouro', 'numero', 'complemento', 'bairro', 'cep',
            'uf', 'codigo_municipio', 'municipio_nome',
            'ddd_1', 'telefone_1', 'ddd_2', 'telefone_2', 'ddd_fax', 'fax', 'correio_eletronico',
            'situacao_especial', 'data_situacao_especial',
            'opcao_simples', 'data_opcao_simples', 'data_exclusao_simples',
            'opcao_mei', 'data_opcao_mei', 'data_exclusao_mei',
            'total_socios', 'atividades_secundarias', 'cnpjs_socios'
        ]
        
        cursor.execute(query, (uf,))
        
        arquivo_atual = 1
        linha_atual = 0
        csv_writer = None
        csv_file = None
        
        try:
            while True:
                # Buscar lote de dados
                rows = cursor.fetchmany(10000)  # Processar em lotes de 10k
                if not rows:
                    break
                
                for row in rows:
                    # Verificar se precisa criar novo arquivo
                    if linha_atual % self.max_linhas_arquivo == 0:
                        # Fechar arquivo anterior se existir
                        if csv_file:
                            csv_file.close()
                            logger.info(f"Arquivo concluído: {arquivo_nome} ({linha_atual_arquivo:,} linhas)")
                        
                        # Criar novo arquivo
                        if num_arquivos > 1:
                            arquivo_nome = f"{uf}_{arquivo_atual:03d}.csv"
                        else:
                            arquivo_nome = f"{uf}.csv"
                        
                        arquivo_path = self.output_dir / arquivo_nome
                        csv_file = open(arquivo_path, 'w', newline='', encoding='utf-8')
                        csv_writer = csv.writer(csv_file)
                        
                        # Escrever cabeçalho
                        csv_writer.writerow(headers)
                        
                        arquivos_gerados.append(str(arquivo_path))
                        linha_atual_arquivo = 1  # Começar contando o cabeçalho
                        
                        logger.info(f"Criando arquivo: {arquivo_nome}")
                    
                    # Escrever linha
                    csv_writer.writerow(row)
                    linha_atual += 1
                    linha_atual_arquivo += 1
                    
                    # Verificar se precisa mudar de arquivo
                    if linha_atual_arquivo >= self.max_linhas_arquivo:
                        arquivo_atual += 1
                
                # Log de progresso
                if linha_atual % 50000 == 0:
                    logger.info(f"Processadas {linha_atual:,} linhas para {uf}")
            
            # Fechar último arquivo
            if csv_file:
                csv_file.close()
                logger.info(f"Arquivo concluído: {arquivo_nome} ({linha_atual_arquivo:,} linhas)")
        
        except Exception as e:
            logger.error(f"Erro ao processar {uf}: {e}")
            if csv_file:
                csv_file.close()
            raise
        
        finally:
            conn.close()
        
        logger.info(f"Estado {uf} concluído: {len(arquivos_gerados)} arquivos, {linha_atual:,} registros")
        return arquivos_gerados
    
    def gerar_arquivo_socios_separado(self, uf: str) -> Optional[str]:
        """
        Gera arquivo separado com dados dos sócios para um estado
        
        Args:
            uf: Código do estado
            
        Returns:
            Caminho do arquivo gerado ou None
        """
        logger.info(f"Gerando arquivo de sócios para {uf}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT DISTINCT
            s.cnpj_basico,
            emp.razao_social,
            s.identificador_socio,
            s.nome_socio,
            s.cpf_cnpj_socio,
            s.codigo_qualificacao_socio,
            q.descricao as qualificacao_descricao,
            s.data_entrada_sociedade,
            s.codigo_pais,
            p.descricao as pais_descricao,
            s.representante_legal,
            s.nome_representante,
            s.codigo_qualificacao_representante,
            s.faixa_etaria
        FROM socios s
        JOIN empresas emp ON s.cnpj_basico = emp.cnpj_basico
        JOIN estabelecimentos e ON s.cnpj_basico = e.cnpj_basico
        LEFT JOIN qualificacoes q ON s.codigo_qualificacao_socio = q.codigo
        LEFT JOIN paises p ON s.codigo_pais = p.codigo
        WHERE e.uf = ?
        ORDER BY s.cnpj_basico, s.nome_socio
        """
        
        cursor.execute(query, (uf,))
        rows = cursor.fetchall()
        
        if not rows:
            logger.info(f"Nenhum sócio encontrado para {uf}")
            conn.close()
            return None
        
        arquivo_nome = f"{uf}_socios.csv"
        arquivo_path = self.output_dir / arquivo_nome
        
        headers = [
            'cnpj_basico', 'razao_social', 'identificador_socio', 'nome_socio',
            'cpf_cnpj_socio', 'codigo_qualificacao_socio', 'qualificacao_descricao',
            'data_entrada_sociedade', 'codigo_pais', 'pais_descricao',
            'representante_legal', 'nome_representante', 'codigo_qualificacao_representante',
            'faixa_etaria'
        ]
        
        with open(arquivo_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(rows)
        
        conn.close()
        
        logger.info(f"Arquivo de sócios criado: {arquivo_nome} ({len(rows):,} registros)")
        return str(arquivo_path)
    
    def gerar_todos_estados(self, incluir_socios: bool = True, estados_especificos: List[str] = None):
        """
        Gera arquivos CSV para todos os estados
        
        Args:
            incluir_socios: Se deve gerar arquivos separados de sócios
            estados_especificos: Lista de estados específicos (None = todos)
        """
        logger.info("Iniciando geração de arquivos CSV por estado")
        
        if estados_especificos:
            estados = estados_especificos
            logger.info(f"Processando estados específicos: {', '.join(estados)}")
        else:
            estados = self.get_estados_disponiveis()
        
        total_arquivos = 0
        resumo = {}
        
        for uf in estados:
            try:
                # Gerar arquivos principais
                arquivos = self.gerar_csv_para_estado(uf)
                total_arquivos += len(arquivos)
                
                resumo[uf] = {
                    'arquivos_principais': len(arquivos),
                    'arquivo_socios': False
                }
                
                # Gerar arquivo de sócios se solicitado
                if incluir_socios:
                    arquivo_socios = self.gerar_arquivo_socios_separado(uf)
                    if arquivo_socios:
                        total_arquivos += 1
                        resumo[uf]['arquivo_socios'] = True
                
            except Exception as e:
                logger.error(f"Erro ao processar estado {uf}: {e}")
                resumo[uf] = {'erro': str(e)}
        
        # Mostrar resumo
        logger.info("="*60)
        logger.info("RESUMO DA GERAÇÃO")
        logger.info("="*60)
        logger.info(f"Total de arquivos gerados: {total_arquivos}")
        logger.info(f"Diretório de saída: {self.output_dir}")
        
        for uf, info in resumo.items():
            if 'erro' in info:
                logger.error(f"{uf}: ERRO - {info['erro']}")
            else:
                socios_txt = " + sócios" if info['arquivo_socios'] else ""
                logger.info(f"{uf}: {info['arquivos_principais']} arquivo(s){socios_txt}")
        
        logger.info("="*60)
        
        # Gerar arquivo de resumo
        self.gerar_arquivo_resumo(resumo)
    
    def gerar_arquivo_resumo(self, resumo: Dict):
        """
        Gera arquivo de resumo da geração
        
        Args:
            resumo: Dicionário com resumo da geração
        """
        resumo_path = self.output_dir / "RESUMO.txt"
        
        with open(resumo_path, 'w', encoding='utf-8') as f:
            f.write("RESUMO DA GERAÇÃO DE ARQUIVOS CSV\n")
            f.write("=" * 50 + "\n")
            f.write(f"Data: {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Diretório: {self.output_dir}\n")
            f.write(f"Limite por arquivo: {self.max_linhas_arquivo:,} linhas\n\n")
            
            total_arquivos = 0
            for uf, info in resumo.items():
                if 'erro' not in info:
                    total_arquivos += info['arquivos_principais']
                    if info['arquivo_socios']:
                        total_arquivos += 1
            
            f.write(f"Total de arquivos gerados: {total_arquivos}\n\n")
            
            f.write("DETALHES POR ESTADO:\n")
            f.write("-" * 30 + "\n")
            
            for uf in sorted(resumo.keys()):
                info = resumo[uf]
                if 'erro' in info:
                    f.write(f"{uf}: ERRO - {info['erro']}\n")
                else:
                    socios_txt = " + arquivo de sócios" if info['arquivo_socios'] else ""
                    f.write(f"{uf}: {info['arquivos_principais']} arquivo(s) principal(is){socios_txt}\n")
            
            f.write("\nFORMATO DOS ARQUIVOS:\n")
            f.write("-" * 20 + "\n")
            f.write("- {UF}.csv: Dados completos (se < 100k registros)\n")
            f.write("- {UF}_001.csv, {UF}_002.csv, etc: Dados divididos (se > 100k registros)\n")
            f.write("- {UF}_socios.csv: Dados dos sócios separados\n")
            f.write("\nEncoding: UTF-8\n")
            f.write("Separador: vírgula (,)\n")
        
        logger.info(f"Arquivo de resumo criado: {resumo_path}")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerar arquivos CSV por estado para WordPress')
    parser.add_argument('--db', default='./cnpj_dados.db', help='Caminho do banco SQLite')
    parser.add_argument('--output', default='./csv_estados', help='Diretório de saída')
    parser.add_argument('--estados', nargs='+', help='Estados específicos (ex: SP RJ MG)')
    parser.add_argument('--sem-socios', action='store_true', help='Não gerar arquivos de sócios')
    parser.add_argument('--teste', action='store_true', help='Processar apenas alguns estados para teste')
    
    args = parser.parse_args()
    
    # Verificar se banco existe
    if not os.path.exists(args.db):
        print(f"Erro: Banco de dados não encontrado: {args.db}")
        print("Execute primeiro o downloader_cnpj.py para baixar os dados")
        return
    
    # Criar gerador
    gerador = GeradorCSVEstados(args.db, args.output)
    
    # Determinar estados a processar
    estados = None
    if args.teste:
        estados = ['SP', 'RJ', 'MG']  # Apenas alguns para teste
        print("Modo teste: processando apenas SP, RJ e MG")
    elif args.estados:
        estados = [e.upper() for e in args.estados]
    
    try:
        # Gerar arquivos
        gerador.gerar_todos_estados(
            incluir_socios=not args.sem_socios,
            estados_especificos=estados
        )
        
        print(f"\n✅ Processo concluído!")
        print(f"📁 Arquivos salvos em: {args.output}")
        print(f"📄 Veja o arquivo RESUMO.txt para detalhes")
        
    except KeyboardInterrupt:
        print("\n❌ Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        logger.exception("Erro detalhado:")


if __name__ == "__main__":
    main()
