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
    print("5) ⚙️ Configurações avançadas (MEI, Estados, etc.)")
    print("0) ❌ Sair")
    
    try:
        opcao = input("\nDigite sua opção (0-5): ").strip()
        
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
        
        elif opcao == "5":
            print("\n⚙️ CONFIGURAÇÕES AVANÇADAS")
            executar_configuracoes_avancadas()
        
        else:
            print("❌ Opção inválida!")
    
    except KeyboardInterrupt:
        print("\n\n❌ Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

    print("\n" + "="*50)
    print("Processo finalizado!")


def executar_configuracoes_avancadas():
    """Menu de configurações avançadas"""
    print("="*50)
    print("CONFIGURAÇÕES AVANÇADAS")
    print("="*50)
    
    # Configuração de MEI
    print("\n📊 MICROEMPREENDEDOR INDIVIDUAL (MEI)")
    print("1) ✅ Incluir MEI (CPF será anonimizado para privacidade)")
    print("2) 🚫 Excluir MEI da importação")
    
    mei_opcao = input("\nOpção MEI (1-2): ").strip()
    parametro_mei = ""
    
    if mei_opcao == "2":
        parametro_mei = "--excluir-mei"
        print("✅ MEI será EXCLUÍDO da importação")
    else:
        print("✅ MEI será INCLUÍDO (CPF anonimizado)")
    
    # Configuração de Estados
    print("\n🗺️ ESTADOS A PROCESSAR")
    print("1) Todos os estados")
    print("2) Apenas alguns estados específicos")
    
    estados_opcao = input("\nOpção Estados (1-2): ").strip()
    parametro_estados = ""
    
    if estados_opcao == "2":
        estados = input("Digite os estados (ex: SP RJ MG): ").upper().strip()
        if estados:
            parametro_estados = f"--estados {estados}"
            print(f"✅ Estados selecionados: {estados}")
    
    # Configuração de Tipo de Processo
    print("\n🔄 TIPO DE PROCESSO")
    print("1) 🧪 Teste rápido (poucos dados)")
    print("2) 🚀 Processo completo (todos os dados)")
    
    tipo_opcao = input("\nTipo de processo (1-2): ").strip()
    parametro_teste = ""
    
    if tipo_opcao == "1":
        parametro_teste = "--teste"
        print("✅ Modo teste selecionado")
    else:
        print("✅ Processo completo selecionado")
    
    # Executar com as configurações
    print("\n" + "="*50)
    print("RESUMO DAS CONFIGURAÇÕES:")
    if parametro_mei:
        print("- MEI: Excluído")
    else:
        print("- MEI: Incluído (CPF anonimizado)")
    
    if parametro_estados:
        print(f"- Estados: {estados}")
    else:
        print("- Estados: Todos")
    
    if parametro_teste:
        print("- Tipo: Teste rápido")
    else:
        print("- Tipo: Processo completo")
    
    print("="*50)
    
    confirma = input("\nExecutar com essas configurações? (s/n): ").lower().strip()
    if confirma in ['s', 'sim', 'y', 'yes']:
        # Montar comando
        comando = f"{sys.executable} processo_completo.py"
        if parametro_teste:
            comando += f" {parametro_teste}"
        if parametro_mei:
            comando += f" {parametro_mei}"
        if parametro_estados:
            comando += f" {parametro_estados}"
        
        print(f"\nExecutando: {comando}")
        os.system(comando)
    else:
        print("Execução cancelada")


if __name__ == "__main__":
    main()
