#!/usr/bin/env python3
"""
Script de exemplo para consultar os dados CNPJ no SQLite
Autor: Bruno Qualhato
Data: 23 de junho de 2025
"""

import sqlite3
import sys
from typing import List, Tuple, Optional
import argparse

class CNPJQuery:
    """Classe para consultas no banco de dados CNPJ"""
    
    def __init__(self, db_path: str = "./cnpj_dados.db"):
        """
        Inicializa a classe de consultas
        
        Args:
            db_path: Caminho do banco SQLite
        """
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Retorna uma conexão com o banco"""
        return sqlite3.connect(self.db_path)
    
    def buscar_empresa_por_cnpj(self, cnpj_basico: str) -> Optional[dict]:
        """
        Busca empresa pelo CNPJ básico
        
        Args:
            cnpj_basico: CNPJ básico (8 primeiros dígitos)
            
        Returns:
            Dados da empresa ou None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT cnpj_basico, razao_social, natureza_juridica, 
               qualificacao_responsavel, capital_social, porte_empresa, ente_federativo
        FROM empresas 
        WHERE cnpj_basico = ?
        """
        
        cursor.execute(query, (cnpj_basico,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                'cnpj_basico': result[0],
                'razao_social': result[1],
                'natureza_juridica': result[2],
                'qualificacao_responsavel': result[3],
                'capital_social': result[4],
                'porte_empresa': result[5],
                'ente_federativo': result[6]
            }
        return None
    
    def buscar_estabelecimentos_por_cnpj(self, cnpj_basico: str) -> List[dict]:
        """
        Busca estabelecimentos pelo CNPJ básico
        
        Args:
            cnpj_basico: CNPJ básico (8 primeiros dígitos)
            
        Returns:
            Lista de estabelecimentos
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT cnpj_basico, cnpj_ordem, cnpj_dv, identificador_matriz_filial,
               nome_fantasia, situacao_cadastral, data_situacao_cadastral,
               nome_cidade_exterior, data_inicio_atividade, cnae_fiscal_principal,
               tipo_logradouro, logradouro, numero, complemento, bairro,
               cep, uf, codigo_municipio, ddd_1, telefone_1, correio_eletronico
        FROM estabelecimentos 
        WHERE cnpj_basico = ?
        """
        
        cursor.execute(query, (cnpj_basico,))
        results = cursor.fetchall()
        
        conn.close()
        
        estabelecimentos = []
        for result in results:
            estabelecimentos.append({
                'cnpj_completo': f"{result[0]}{result[1]}{result[2]}",
                'cnpj_basico': result[0],
                'cnpj_ordem': result[1],
                'cnpj_dv': result[2],
                'tipo': 'Matriz' if result[3] == '1' else 'Filial',
                'nome_fantasia': result[4],
                'situacao': result[5],
                'data_situacao': result[6],
                'cidade_exterior': result[7],
                'data_inicio': result[8],
                'cnae_principal': result[9],
                'endereco': f"{result[10]} {result[11]}, {result[12]} - {result[14]}",
                'cep': result[15],
                'uf': result[16],
                'municipio': result[17],
                'telefone': f"({result[18]}) {result[19]}" if result[18] and result[19] else None,
                'email': result[20]
            })
        
        return estabelecimentos
    
    def buscar_socios_por_cnpj(self, cnpj_basico: str) -> List[dict]:
        """
        Busca sócios pelo CNPJ básico
        
        Args:
            cnpj_basico: CNPJ básico (8 primeiros dígitos)
            
        Returns:
            Lista de sócios
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT nome_socio, cpf_cnpj_socio, codigo_qualificacao_socio,
               data_entrada_sociedade, representante_legal, nome_representante
        FROM socios 
        WHERE cnpj_basico = ?
        """
        
        cursor.execute(query, (cnpj_basico,))
        results = cursor.fetchall()
        
        conn.close()
        
        socios = []
        for result in results:
            socios.append({
                'nome': result[0],
                'cpf_cnpj': result[1],
                'qualificacao': result[2],
                'data_entrada': result[3],
                'representante_legal': result[4],
                'nome_representante': result[5]
            })
        
        return socios
    
    def buscar_por_razao_social(self, termo: str, limit: int = 10) -> List[dict]:
        """
        Busca empresas por razão social
        
        Args:
            termo: Termo para busca
            limit: Limite de resultados
            
        Returns:
            Lista de empresas encontradas
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT cnpj_basico, razao_social, porte_empresa
        FROM empresas 
        WHERE razao_social LIKE ?
        ORDER BY razao_social
        LIMIT ?
        """
        
        cursor.execute(query, (f"%{termo}%", limit))
        results = cursor.fetchall()
        
        conn.close()
        
        empresas = []
        for result in results:
            empresas.append({
                'cnpj_basico': result[0],
                'razao_social': result[1],
                'porte': result[2]
            })
        
        return empresas
    
    def buscar_por_uf(self, uf: str, limit: int = 100) -> List[dict]:
        """
        Busca estabelecimentos por UF
        
        Args:
            uf: Sigla da UF
            limit: Limite de resultados
            
        Returns:
            Lista de estabelecimentos
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT e.cnpj_basico, emp.razao_social, e.nome_fantasia, 
               e.uf, e.codigo_municipio, e.situacao_cadastral
        FROM estabelecimentos e
        LEFT JOIN empresas emp ON e.cnpj_basico = emp.cnpj_basico
        WHERE e.uf = ?
        ORDER BY emp.razao_social
        LIMIT ?
        """
        
        cursor.execute(query, (uf.upper(), limit))
        results = cursor.fetchall()
        
        conn.close()
        
        estabelecimentos = []
        for result in results:
            estabelecimentos.append({
                'cnpj_basico': result[0],
                'razao_social': result[1],
                'nome_fantasia': result[2],
                'uf': result[3],
                'municipio': result[4],
                'situacao': result[5]
            })
        
        return estabelecimentos
    
    def estatisticas_gerais(self) -> dict:
        """
        Retorna estatísticas gerais do banco
        
        Returns:
            Dicionário com estatísticas
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total de empresas
        cursor.execute("SELECT COUNT(*) FROM empresas")
        stats['total_empresas'] = cursor.fetchone()[0]
        
        # Total de estabelecimentos
        cursor.execute("SELECT COUNT(*) FROM estabelecimentos")
        stats['total_estabelecimentos'] = cursor.fetchone()[0]
        
        # Estabelecimentos ativos
        cursor.execute("SELECT COUNT(*) FROM estabelecimentos WHERE situacao_cadastral = '02'")
        stats['estabelecimentos_ativos'] = cursor.fetchone()[0]
        
        # Empresas por UF
        cursor.execute("""
            SELECT uf, COUNT(*) as total 
            FROM estabelecimentos 
            WHERE uf IS NOT NULL 
            GROUP BY uf 
            ORDER BY total DESC 
            LIMIT 10
        """)
        stats['top_ufs'] = cursor.fetchall()
        
        # Portes de empresa
        cursor.execute("""
            SELECT porte_empresa, COUNT(*) as total 
            FROM empresas 
            WHERE porte_empresa IS NOT NULL 
            GROUP BY porte_empresa 
            ORDER BY total DESC
        """)
        stats['portes'] = cursor.fetchall()
        
        conn.close()
        return stats


def main():
    """Função principal com exemplos de uso"""
    parser = argparse.ArgumentParser(description='Consultar dados CNPJ')
    parser.add_argument('--db', default='./cnpj_dados.db', help='Caminho do banco SQLite')
    parser.add_argument('--cnpj', help='CNPJ básico para consulta')
    parser.add_argument('--empresa', help='Nome da empresa para busca')
    parser.add_argument('--uf', help='UF para busca de estabelecimentos')
    parser.add_argument('--stats', action='store_true', help='Mostrar estatísticas')
    
    args = parser.parse_args()
    
    query = CNPJQuery(args.db)
    
    try:
        if args.stats:
            print("=== ESTATÍSTICAS GERAIS ===")
            stats = query.estatisticas_gerais()
            print(f"Total de empresas: {stats['total_empresas']:,}")
            print(f"Total de estabelecimentos: {stats['total_estabelecimentos']:,}")
            print(f"Estabelecimentos ativos: {stats['estabelecimentos_ativos']:,}")
            
            print("\n=== TOP 10 UFs ===")
            for uf, total in stats['top_ufs']:
                print(f"{uf}: {total:,}")
            
            print("\n=== PORTES DE EMPRESA ===")
            for porte, total in stats['portes']:
                porte_desc = {
                    '01': 'Micro Empresa',
                    '03': 'Empresa de Pequeno Porte',
                    '05': 'Demais'
                }.get(porte, porte)
                print(f"{porte_desc}: {total:,}")
        
        elif args.cnpj:
            cnpj = args.cnpj.replace('.', '').replace('/', '').replace('-', '')[:8]
            
            print(f"=== DADOS DA EMPRESA (CNPJ: {cnpj}) ===")
            empresa = query.buscar_empresa_por_cnpj(cnpj)
            if empresa:
                print(f"Razão Social: {empresa['razao_social']}")
                capital = empresa['capital_social'] or 0
                try:
                    capital_float = float(capital)
                except (ValueError, TypeError):
                    capital_float = 0.0
                print(f"Capital Social: R$ {capital_float:,.2f}")
                print(f"Porte: {empresa['porte_empresa']}")
                print(f"Natureza Jurídica: {empresa['natureza_juridica']}")
            else:
                print("Empresa não encontrada")
                return
            
            print(f"\n=== ESTABELECIMENTOS ===")
            estabelecimentos = query.buscar_estabelecimentos_por_cnpj(cnpj)
            for est in estabelecimentos:
                print(f"\nCNPJ: {est['cnpj_completo']}")
                print(f"Tipo: {est['tipo']}")
                print(f"Nome Fantasia: {est['nome_fantasia'] or 'N/A'}")
                print(f"Situação: {est['situacao']}")
                print(f"Endereço: {est['endereco']}")
                print(f"CEP: {est['cep']} - {est['uf']}")
                if est['telefone']:
                    print(f"Telefone: {est['telefone']}")
                if est['email']:
                    print(f"Email: {est['email']}")
            
            print(f"\n=== SÓCIOS ===")
            socios = query.buscar_socios_por_cnpj(cnpj)
            for socio in socios:
                print(f"\nNome: {socio['nome']}")
                print(f"CPF/CNPJ: {socio['cpf_cnpj'] or 'N/A'}")
                print(f"Qualificação: {socio['qualificacao']}")
                if socio['data_entrada']:
                    print(f"Data Entrada: {socio['data_entrada']}")
        
        elif args.empresa:
            print(f"=== BUSCA POR EMPRESA: {args.empresa} ===")
            empresas = query.buscar_por_razao_social(args.empresa)
            for emp in empresas:
                print(f"CNPJ: {emp['cnpj_basico']} - {emp['razao_social']}")
        
        elif args.uf:
            print(f"=== ESTABELECIMENTOS EM {args.uf.upper()} ===")
            estabelecimentos = query.buscar_por_uf(args.uf)
            for est in estabelecimentos:
                print(f"{est['cnpj_basico']} - {est['razao_social']} ({est['situacao']})")
        
        else:
            print("Use --help para ver as opções disponíveis")
            print("\nExemplos:")
            print("  python consultar_cnpj.py --stats")
            print("  python consultar_cnpj.py --cnpj 12345678")
            print("  python consultar_cnpj.py --empresa 'PETROBRAS'")
            print("  python consultar_cnpj.py --uf SP")
    
    except FileNotFoundError:
        print(f"Banco de dados não encontrado: {args.db}")
        print("Execute primeiro o downloader_cnpj.py para baixar os dados")
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    main()
