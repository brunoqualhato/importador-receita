#!/usr/bin/env python3
"""
Script de Execução Rápida - CNPJ para WordPress
Executa todo o processo com configurações padrão

Autor: Bruno Qualhato
Data: 23 de junho de 2025
"""

import os
import sys
from pathlib import Path

def main():
    """Execução rápida com menu simples"""
    print("🚀 CNPJ PARA WORDPRESS - EXECUÇÃO AUTOMÁTICA")
    print("=" * 50)
    
    # Verificar se está no diretório correto
    base_dir = Path.cwd()
    if not (base_dir / 'processo_completo.py').exists():
        print("❌ Erro: Execute este script no diretório do projeto")
        print("Arquivos necessários não encontrados!")
        return
    
    print("Escolha uma opção:")
    print("1) 🧪 TESTE RÁPIDO (poucos dados, ~10 minutos)")
    print("2) 🚀 PROCESSO COMPLETO (todos os dados, várias horas)")
    print("3) 📊 Apenas gerar CSVs (usar dados já baixados)")
    print("4) 🧹 Limpar e recomeçar do zero")
    print("0) ❌ Sair")
    
    try:
        opcao = input("\nDigite sua opção (0-4): ").strip()
        
        if opcao == "0":
            print("Saindo...")
            return
        
        elif opcao == "1":
            print("\n🧪 Iniciando TESTE RÁPIDO...")
            print("- Download de poucos arquivos")
            print("- Processamento de SP, RJ, MG apenas")
            print("- Tempo estimado: 10-30 minutos")
            
            confirma = input("\nContinuar? (s/n): ").lower().strip()
            if confirma in ['s', 'sim', 'y', 'yes']:
                os.system(f"{sys.executable} processo_completo.py --teste")
            
        elif opcao == "2":
            print("\n🚀 Iniciando PROCESSO COMPLETO...")
            print("- Download de TODOS os dados (~10GB)")
            print("- Processamento de TODOS os estados")
            print("- Tempo estimado: 3-8 horas")
            print("\n⚠️  ATENÇÃO: Certifique-se de ter:")
            print("- Conexão estável com a internet")
            print("- Pelo menos 50GB de espaço livre")
            print("- Tempo disponível (processo longo)")
            
            confirma = input("\nContinuar mesmo assim? (s/n): ").lower().strip()
            if confirma in ['s', 'sim', 'y', 'yes']:
                os.system(f"{sys.executable} processo_completo.py")
            
        elif opcao == "3":
            print("\n📊 Gerando CSVs com dados existentes...")
            
            # Verificar se existe banco
            banco_completo = base_dir / 'cnpj_dados.db'
            banco_teste = base_dir / 'cnpj_teste.db'
            
            if banco_completo.exists():
                print("✅ Banco completo encontrado")
                os.system(f"{sys.executable} gerar_csv_estados.py --db cnpj_dados.db")
            elif banco_teste.exists():
                print("✅ Banco de teste encontrado")
                estados = input("Estados para processar (ex: SP RJ MG) ou ENTER para todos: ").strip()
                if estados:
                    os.system(f"{sys.executable} gerar_csv_estados.py --db cnpj_teste.db --estados {estados}")
                else:
                    os.system(f"{sys.executable} gerar_csv_estados.py --db cnpj_teste.db")
            else:
                print("❌ Nenhum banco de dados encontrado!")
                print("Execute primeiro a opção 1 ou 2 para baixar os dados")
        
        elif opcao == "4":
            print("\n🧹 LIMPEZA E REINÍCIO...")
            print("Isso irá apagar:")
            print("- Todos os arquivos baixados")
            print("- Bancos de dados")
            print("- CSVs gerados")
            
            confirma = input("\nTem certeza? (s/n): ").lower().strip()
            if confirma in ['s', 'sim', 'y', 'yes']:
                # Limpar arquivos
                import shutil
                
                dirs_para_limpar = ['dados_cnpj', 'dados_teste', 'csv_estados']
                arquivos_para_limpar = ['cnpj_dados.db', 'cnpj_teste.db', '*.log']
                
                for dir_name in dirs_para_limpar:
                    dir_path = base_dir / dir_name
                    if dir_path.exists():
                        print(f"Removendo {dir_name}...")
                        shutil.rmtree(dir_path)
                
                import glob
                for pattern in arquivos_para_limpar:
                    for arquivo in glob.glob(pattern):
                        print(f"Removendo {arquivo}...")
                        os.remove(arquivo)
                
                print("✅ Limpeza concluída!")
                
                # Perguntar se quer recomeçar
                recomecar = input("\nRecomeçar processo? (1=teste, 2=completo, n=não): ").strip()
                if recomecar == "1":
                    os.system(f"{sys.executable} processo_completo.py --teste --limpar")
                elif recomecar == "2":
                    os.system(f"{sys.executable} processo_completo.py --limpar")
        
        else:
            print("❌ Opção inválida!")
    
    except KeyboardInterrupt:
        print("\n\n❌ Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

    print("\n" + "="*50)
    print("Processo finalizado!")


if __name__ == "__main__":
    main()
