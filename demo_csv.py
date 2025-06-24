#!/usr/bin/env python3
"""
Script para demonstrar o gerador de CSV com dados de exemplo
"""

import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def criar_dados_exemplo():
    """Cria alguns dados de exemplo no banco de teste"""
    print("🔨 Criando dados de exemplo...")
    
    conn = sqlite3.connect("./cnpj_teste.db")
    cursor = conn.cursor()
    
    # Limpar estabelecimentos existentes
    cursor.execute("DELETE FROM estabelecimentos")
    
    # Inserir alguns estabelecimentos de exemplo
    estabelecimentos_exemplo = [
        # SP
        ('12345678', '0001', '95', '1', 'EMPRESA TESTE SP LTDA', '02', '20200101', None, '20200101', 
         '6201501', 'RUA', 'RUA DAS FLORES', '123', 'SALA 1', 'CENTRO', '01234567', 'SP', '3550308', 
         '11', '99998888', None, None, None, None, 'contato@teste.com.br', None, None),
        ('12345678', '0002', '76', '2', 'FILIAL TESTE SP', '02', '20210101', None, '20210101', 
         '6201501', 'AVENIDA', 'AV PAULISTA', '1000', None, 'BELA VISTA', '01310100', 'SP', '3550308',
         '11', '88887777', None, None, None, None, 'filial@teste.com.br', None, None),
        ('87654321', '0001', '12', '1', 'OUTRA EMPRESA SP', '02', '20190101', None, '20190101',
         '4712100', 'RUA', 'RUA DO COMERCIO', '456', None, 'VILA NOVA', '02345678', 'SP', '3550308',
         '11', '77776666', None, None, None, None, 'info@outra.com.br', None, None),
        
        # RJ  
        ('23456789', '0001', '83', '1', 'EMPRESA RJ LTDA', '02', '20200601', None, '20200601',
         '6209100', 'RUA', 'RUA COPACABANA', '789', 'COBERTURA', 'COPACABANA', '22070000', 'RJ', '3304557',
         '21', '55554444', None, None, None, None, 'contato@rj.com.br', None, None),
        ('34567890', '0001', '74', '1', 'TECH RJ INOVACAO', '02', '20210301', None, '20210301',
         '6201501', 'AVENIDA', 'AV ATLANTICA', '2000', None, 'IPANEMA', '22071000', 'RJ', '3304557',
         '21', '44443333', None, None, None, None, 'tech@rj.com.br', None, None),
         
        # MG
        ('45678901', '0001', '65', '1', 'MINERACAO MG SA', '02', '20180101', None, '20180101',
         '0710302', 'RUA', 'RUA DA LIBERDADE', '100', None, 'CENTRO', '30100000', 'MG', '3106200',
         '31', '33332222', None, None, None, None, 'mineracao@mg.com.br', None, None),
         
        # RS
        ('56789012', '0001', '56', '1', 'AGRICOLA RS LTDA', '02', '20170101', None, '20170101',
         '0111301', 'ESTRADA', 'ESTRADA RURAL', 'KM 10', None, 'ZONA RURAL', '90000000', 'RS', '4314902',
         '51', '22221111', None, None, None, None, 'agricola@rs.com.br', None, None)
    ]
    
    # Estrutura da tabela estabelecimentos
    for est in estabelecimentos_exemplo:
        cursor.execute('''
            INSERT INTO estabelecimentos (
                cnpj_basico, cnpj_ordem, cnpj_dv, identificador_matriz_filial,
                nome_fantasia, situacao_cadastral, data_situacao_cadastral, motivo_situacao_cadastral,
                data_inicio_atividade, cnae_fiscal_principal, tipo_logradouro, logradouro, 
                numero, complemento, bairro, cep, uf, codigo_municipio,
                ddd_1, telefone_1, ddd_2, telefone_2, ddd_fax, fax, correio_eletronico,
                situacao_especial, data_situacao_especial
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', est)
    
    # Inserir alguns sócios de exemplo
    socios_exemplo = [
        ('12345678', '2', 'JOAO DA SILVA', '12345678901', '49', '20200101', '105', None, None, None, '4'),
        ('12345678', '1', 'EMPRESA HOLDING LTDA', '98765432000195', '22', '20200101', '105', None, None, None, None),
        ('87654321', '2', 'MARIA SANTOS', '98765432109', '49', '20190101', '105', None, None, None, '3'),
        ('23456789', '2', 'PEDRO OLIVEIRA', '11122233344', '49', '20200601', '105', None, None, None, '5'),
        ('45678901', '2', 'ANA COSTA', '55566677788', '16', '20180101', '105', None, None, None, '4')
    ]
    
    for socio in socios_exemplo:
        cursor.execute('''
            INSERT INTO socios (
                cnpj_basico, identificador_socio, nome_socio, cpf_cnpj_socio,
                codigo_qualificacao_socio, data_entrada_sociedade, codigo_pais,
                representante_legal, nome_representante, codigo_qualificacao_representante, faixa_etaria
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', socio)
    
    # Inserir dados do Simples Nacional
    simples_exemplo = [
        ('12345678', 'S', '20200201', None, 'S', '20200201', None),
        ('87654321', 'N', None, None, 'N', None, None),
        ('23456789', 'S', '20200701', None, 'N', None, None)
    ]
    
    for simples in simples_exemplo:
        cursor.execute('''
            INSERT OR REPLACE INTO simples (
                cnpj_basico, opcao_simples, data_opcao_simples, data_exclusao_simples,
                opcao_mei, data_opcao_mei, data_exclusao_mei
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', simples)
    
    conn.commit()
    conn.close()
    
    print("✅ Dados de exemplo criados!")
    print("   - 7 estabelecimentos (SP: 3, RJ: 2, MG: 1, RS: 1)")
    print("   - 5 sócios")
    print("   - 3 registros no Simples Nacional")

def testar_gerador():
    """Testa o gerador de CSV com os dados de exemplo"""
    print("\n🧪 Testando gerador de CSV...")
    
    from gerar_csv_estados import GeradorCSVEstados
    
    # Criar gerador
    gerador = GeradorCSVEstados(
        db_path="./cnpj_teste.db",
        output_dir="./csv_exemplo"
    )
    
    # Configurar para arquivos pequenos (para demonstração)
    gerador.max_linhas_arquivo = 3  # Só 3 linhas por arquivo para demonstrar divisão
    
    # Gerar apenas para alguns estados
    print("📊 Gerando CSVs para SP e RJ...")
    gerador.gerar_todos_estados(
        incluir_socios=True,
        estados_especificos=['SP', 'RJ']
    )
    
    print("\n📁 Arquivos gerados:")
    output_dir = "./csv_exemplo"
    if os.path.exists(output_dir):
        for file in sorted(os.listdir(output_dir)):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"   📄 {file} ({size} bytes)")
                
                # Mostrar conteúdo do primeiro arquivo CSV
                if file.endswith('.csv') and not file.endswith('_socios.csv'):
                    print(f"      📋 Primeiras linhas de {file}:")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            if i < 3:  # Mostrar só 3 linhas
                                print(f"         {line.strip()}")
                            else:
                                break
                    print()

if __name__ == "__main__":
    try:
        # Verificar se banco existe
        if not os.path.exists("./cnpj_teste.db"):
            print("❌ Banco de teste não encontrado!")
            print("Execute primeiro o download_teste.py")
            sys.exit(1)
        
        # Criar dados de exemplo
        criar_dados_exemplo()
        
        # Testar gerador
        testar_gerador()
        
        print("🎉 Demonstração concluída!")
        print("\n💡 Para usar com dados reais:")
        print("   1. Execute o download completo: python downloader_cnpj.py")
        print("   2. Gere os CSVs: python gerar_csv_estados.py")
        print("   3. Os arquivos estarão em ./csv_estados/")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
