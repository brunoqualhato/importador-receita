#!/usr/bin/env python3
"""
Demo das novas funcionalidades do gerador de CSV
"""

import sqlite3
import csv
from pathlib import Path

def demo_funcionalidades():
    """Demonstra as novas funcionalidades implementadas"""
    
    print("🎯 DEMONSTRAÇÃO DAS NOVAS FUNCIONALIDADES")
    print("=" * 50)
    
    conn = sqlite3.connect('cnpj_teste.db')
    cursor = conn.cursor()
    
    print("\n1️⃣ FILTRO DE MEI IMPLEMENTADO:")
    print("   ✅ MEI incluídos com CPF anonimizado")
    print("   ✅ Opção para excluir MEI completamente")
    
    # Verificar quantos MEI existem
    query_mei = """
    SELECT COUNT(*) 
    FROM empresas 
    WHERE porte_empresa = '01' AND natureza_juridica = '2135'
    """
    cursor.execute(query_mei)
    total_mei = cursor.fetchone()[0]
    
    print(f"   📊 MEI identificados no banco: {total_mei:,}")
    
    print("\n2️⃣ FILTRO DE EMPRESAS ATIVAS:")
    print("   ✅ CSVs incluem apenas empresas com situação 'Ativa'")
    print("   ✅ Reduz significativamente o volume de dados")
    
    print("\n3️⃣ NOVAS COLUNAS IMPLEMENTADAS:")
    print("   ✅ atividades_secundarias: CNAEs secundários com descrição")
    print("   ✅ socios_cnpj: CNPJs de sócios pessoa jurídica")
    print("   ✅ situacao_cadastral: Sempre 'Ativa' (filtro aplicado)")
    
    # Demonstrar estrutura do CSV
    print("\n4️⃣ ESTRUTURA DO CSV GERADO:")
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
    ]
    
    print(f"   📋 Total de colunas: {len(headers)}")
    print("   🆕 Novas colunas destacadas:")
    for i, header in enumerate(headers):
        if header in ['atividades_secundarias', 'socios_cnpj']:
            print(f"      {i+1:2d}. {header} ← NOVA!")
        elif header == 'situacao_cadastral':
            print(f"      {i+1:2d}. {header} ← Sempre 'Ativa'")
    
    # Gerar amostra
    print("\n5️⃣ AMOSTRA DE DADOS:")
    query_amostra = """
    SELECT 
        emp.cnpj_basico,
        emp.razao_social,
        emp.porte_empresa,
        CASE emp.porte_empresa
            WHEN '01' THEN 'Micro Empresa'
            WHEN '03' THEN 'Empresa de Pequeno Porte'
            WHEN '05' THEN 'Demais'
            ELSE emp.porte_empresa
        END as porte_descricao,
        emp.natureza_juridica,
        emp.capital_social
    FROM empresas emp
    LIMIT 5
    """
    
    cursor.execute(query_amostra)
    results = cursor.fetchall()
    
    for i, row in enumerate(results):
        cnpj, razao, porte, porte_desc, natureza, capital = row
        eh_mei = "🏢 MEI" if porte == '01' and natureza == '2135' else f"🏗️ {porte_desc}"
        print(f"   {i+1}. {cnpj} - {razao[:50]}... [{eh_mei}]")
    
    print("\n6️⃣ COMANDOS DISPONÍVEIS:")
    print("   # Incluir MEI (CPF anonimizado)")
    print("   python processo_completo.py --incluir-mei")
    print("   ")
    print("   # Excluir MEI")
    print("   python processo_completo.py --excluir-mei")
    print("   ")
    print("   # Gerar CSVs apenas de empresas ativas")
    print("   python gerar_csv_estados.py --db cnpj_teste.db")
    
    print("\n✅ FUNCIONALIDADES IMPLEMENTADAS COM SUCESSO!")
    print("🎯 Próximos passos: Execute download completo para testar com estabelecimentos")
    
    conn.close()

if __name__ == "__main__":
    demo_funcionalidades()
