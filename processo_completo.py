#!/usr/bin/env python3
"""
Script Master - Execução Automática Completa
Baixa dados CNPJ, processa e gera CSVs por estado automaticamente

Autor: Bruno Qualhato
Data: 23 de junho de 2025
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import logging
from datetime import datetime
import shutil

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('processo_completo.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ProcessoCompleto:
    """Executa todo o processo automaticamente"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.python_cmd = self._get_python_command()
        self.inicio_processo = datetime.now()
        
        # Configurações
        self.config = {
            'download_completo': True,  # True = todos os dados, False = apenas teste
            'estados_prioritarios': ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'ES', 'DF'],
            'max_tentativas': 3,
            'limpar_downloads_antigos': False,
            'verificar_espaco_disco': True,
            'espaco_minimo_gb': 50,
            'espaco_minimo_teste_gb': 10,  # Menor requisito para teste
            'incluir_mei': True  # Incluir MEI na importação (CPF anonimizado)
        }
        
        logger.info("Iniciando processo completo automatizado")
        logger.info(f"Diretório base: {self.base_dir}")
        logger.info(f"Comando Python: {self.python_cmd}")
    
    def _get_python_command(self) -> str:
        """Detecta o comando Python correto"""
        venv_python = self.base_dir / '.venv' / 'bin' / 'python'
        if venv_python.exists():
            return str(venv_python)
        
        # Tentar comandos alternativos
        for cmd in ['python3', 'python']:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and '3.' in result.stdout:
                    return cmd
            except FileNotFoundError:
                continue
        
        raise Exception("Python 3 não encontrado!")
    
    def verificar_prerequisites(self) -> bool:
        """Verifica se todos os pré-requisitos estão atendidos"""
        logger.info("Verificando pré-requisitos...")
        
        # Verificar arquivos necessários
        arquivos_necessarios = [
            'downloader_cnpj.py',
            'gerar_csv_estados.py',
            'requirements.txt'
        ]
        
        for arquivo in arquivos_necessarios:
            if not (self.base_dir / arquivo).exists():
                logger.error(f"Arquivo necessário não encontrado: {arquivo}")
                return False
        
        # Verificar espaço em disco
        if self.config['verificar_espaco_disco']:
            espaco_livre = shutil.disk_usage(self.base_dir).free / (1024**3)  # GB
            espaco_necessario = self.config['espaco_minimo_teste_gb'] if not self.config['download_completo'] else self.config['espaco_minimo_gb']
            
            if espaco_livre < espaco_necessario:
                logger.error(f"Espaço em disco insuficiente: {espaco_livre:.1f}GB "
                           f"(mínimo: {espaco_necessario}GB)")
                return False
            logger.info(f"Espaço em disco OK: {espaco_livre:.1f}GB disponível (necessário: {espaco_necessario}GB)")
        
        # Verificar Python e dependências
        try:
            result = subprocess.run([self.python_cmd, '-c', 'import requests, sqlite3, csv'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Dependências Python não instaladas")
                return False
        except Exception as e:
            logger.error(f"Erro ao verificar Python: {e}")
            return False
        
        logger.info("✅ Todos os pré-requisitos atendidos")
        return True
    
    def instalar_dependencias(self) -> bool:
        """Instala as dependências necessárias"""
        logger.info("Instalando dependências...")
        
        try:
            # Verificar se existe ambiente virtual
            venv_dir = self.base_dir / '.venv'
            if not venv_dir.exists():
                logger.info("Criando ambiente virtual...")
                subprocess.run([sys.executable, '-m', 'venv', '.venv'], 
                             check=True, cwd=self.base_dir)
            
            # Instalar dependências
            pip_cmd = str(venv_dir / 'bin' / 'pip')
            subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], 
                         check=True, cwd=self.base_dir)
            
            logger.info("✅ Dependências instaladas com sucesso")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao instalar dependências: {e}")
            return False
    
    def executar_download(self) -> bool:
        """Executa o download dos dados"""
        logger.info("="*60)
        logger.info("ETAPA 1: DOWNLOAD DOS DADOS")
        logger.info("="*60)
        
        # Limpar downloads antigos se solicitado
        if self.config['limpar_downloads_antigos']:
            dados_dir = self.base_dir / 'dados_cnpj'
            if dados_dir.exists():
                logger.info("Removendo downloads antigos...")
                shutil.rmtree(dados_dir)
        
        # Escolher script de download
        if self.config['download_completo']:
            script = 'downloader_cnpj.py'
            logger.info("Iniciando download COMPLETO (pode levar várias horas)")
        else:
            script = 'download_teste.py'
            logger.info("Iniciando download de TESTE")
        
        tentativa = 1
        while tentativa <= self.config['max_tentativas']:
            try:
                logger.info(f"Tentativa {tentativa}/{self.config['max_tentativas']}")
                
                # Executar download
                cmd = [self.python_cmd, script]
                
                # Adicionar parâmetros de MEI
                if not self.config['incluir_mei']:
                    cmd.append('--excluir-mei')
                
                result = subprocess.run(
                    cmd,
                    cwd=self.base_dir,
                    timeout=None if self.config['download_completo'] else 1800  # 30min para teste
                )
                
                if result.returncode == 0:
                    logger.info("✅ Download concluído com sucesso")
                    return True
                else:
                    logger.warning(f"Download falhou com código {result.returncode}")
                
            except subprocess.TimeoutExpired:
                logger.error("Download interrompido por timeout")
            except KeyboardInterrupt:
                logger.info("Download interrompido pelo usuário")
                return False
            except Exception as e:
                logger.error(f"Erro no download: {e}")
            
            tentativa += 1
            if tentativa <= self.config['max_tentativas']:
                logger.info("Aguardando 30 segundos antes da próxima tentativa...")
                time.sleep(30)
        
        logger.error("❌ Download falhou após todas as tentativas")
        return False
    
    def verificar_banco_dados(self) -> str:
        """Verifica qual banco de dados está disponível"""
        logger.info("Verificando bancos de dados disponíveis...")
        
        banco_completo = self.base_dir / 'cnpj_dados.db'
        banco_teste = self.base_dir / 'cnpj_teste.db'
        
        if banco_completo.exists():
            # Verificar se tem dados de estabelecimentos
            import sqlite3
            try:
                conn = sqlite3.connect(banco_completo)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM estabelecimentos")
                count = cursor.fetchone()[0]
                conn.close()
                
                if count > 0:
                    logger.info(f"✅ Banco completo encontrado: {count:,} estabelecimentos")
                    return str(banco_completo)
                else:
                    logger.warning("Banco completo existe mas não tem estabelecimentos")
            except Exception as e:
                logger.warning(f"Erro ao verificar banco completo: {e}")
        
        if banco_teste.exists():
            logger.info("✅ Banco de teste encontrado")
            return str(banco_teste)
        
        logger.error("❌ Nenhum banco de dados válido encontrado")
        return ""
    
    def baixar_estabelecimentos(self, banco_path: str) -> bool:
        """Baixa dados de estabelecimentos se necessário"""
        logger.info("="*60)
        logger.info("ETAPA 2: VERIFICAÇÃO DE ESTABELECIMENTOS")
        logger.info("="*60)
        
        import sqlite3
        
        try:
            conn = sqlite3.connect(banco_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM estabelecimentos")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count > 0:
                logger.info(f"✅ Estabelecimentos já disponíveis: {count:,} registros")
                return True
            
            logger.info("Dados de estabelecimentos não encontrados")
            
            # Se for banco de teste, tentar baixar um arquivo de estabelecimentos
            if 'teste' in banco_path:
                logger.info("Baixando arquivo de estabelecimentos para teste...")
                
                # Importar e usar o downloader
                sys.path.append(str(self.base_dir))
                from downloader_cnpj import CNPJDownloader
                
                downloader = CNPJDownloader(
                    download_dir="./dados_teste",
                    db_path=banco_path,
                    incluir_mei=self.config['incluir_mei']
                )
                
                # Obter lista de arquivos
                files = downloader.get_file_list()
                
                # Encontrar um arquivo pequeno de estabelecimentos
                for file_info in files:
                    if file_info['filename'].startswith('Estabelecimentos') and '9.zip' in file_info['filename']:
                        logger.info(f"Baixando {file_info['filename']}...")
                        success = downloader.download_file(file_info)
                        if success:
                            downloader.extract_and_process_file(file_info['filename'])
                            logger.info("✅ Estabelecimentos processados")
                            return True
                        break
                
                logger.warning("Não foi possível baixar estabelecimentos para teste")
                return False
            
            else:
                logger.error("Banco completo sem estabelecimentos - execute novamente o download")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao verificar estabelecimentos: {e}")
            return False
    
    def gerar_csvs(self, banco_path: str) -> bool:
        """Gera os arquivos CSV por estado"""
        logger.info("="*60)
        logger.info("ETAPA 3: GERAÇÃO DE CSVs POR ESTADO")
        logger.info("="*60)
        
        try:
            # Preparar argumentos
            args = [self.python_cmd, 'gerar_csv_estados.py', '--db', banco_path]
            
            # Se for banco de teste, processar apenas estados prioritários
            if 'teste' in banco_path:
                args.extend(['--estados'] + self.config['estados_prioritarios'][:3])
                logger.info("Modo teste: processando apenas SP, RJ, MG")
            
            # Executar geração
            logger.info("Iniciando geração de CSVs...")
            result = subprocess.run(args, cwd=self.base_dir)
            
            if result.returncode == 0:
                logger.info("✅ CSVs gerados com sucesso")
                return True
            else:
                logger.error(f"Geração de CSVs falhou com código {result.returncode}")
                return False
                
        except Exception as e:
            logger.error(f"Erro na geração de CSVs: {e}")
            return False
    
    def mostrar_resumo_final(self, banco_usado: str, sucesso: bool):
        """Mostra resumo final do processo"""
        fim_processo = datetime.now()
        duracao = fim_processo - self.inicio_processo
        
        logger.info("="*80)
        logger.info("RESUMO FINAL DO PROCESSO AUTOMATIZADO")
        logger.info("="*80)
        logger.info(f"Início: {self.inicio_processo.strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info(f"Fim: {fim_processo.strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info(f"Duração total: {duracao}")
        logger.info(f"Status: {'✅ SUCESSO' if sucesso else '❌ FALHA'}")
        
        if sucesso:
            logger.info(f"Banco utilizado: {banco_usado}")
            
            # Verificar arquivos gerados
            csv_dir = self.base_dir / 'csv_estados'
            if csv_dir.exists():
                arquivos_csv = list(csv_dir.glob('*.csv'))
                logger.info(f"Arquivos CSV gerados: {len(arquivos_csv)}")
                logger.info(f"Diretório de saída: {csv_dir}")
                
                # Mostrar alguns exemplos
                if arquivos_csv:
                    logger.info("Exemplos de arquivos gerados:")
                    for arquivo in sorted(arquivos_csv)[:10]:
                        size_mb = arquivo.stat().st_size / (1024*1024)
                        logger.info(f"  - {arquivo.name} ({size_mb:.1f} MB)")
                    
                    if len(arquivos_csv) > 10:
                        logger.info(f"  ... e mais {len(arquivos_csv) - 10} arquivos")
            
            logger.info("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
            logger.info("📁 Arquivos CSV prontos para importação no WordPress")
            logger.info("📄 Veja o arquivo csv_estados/RESUMO.txt para detalhes")
        
        else:
            logger.error("\n❌ PROCESSO FALHOU")
            logger.error("📋 Verifique o log processo_completo.log para detalhes")
        
        logger.info("="*80)
    
    def executar_processo_completo(self):
        """Executa todo o processo do início ao fim"""
        try:
            logger.info("🚀 INICIANDO PROCESSO AUTOMATIZADO COMPLETO")
            logger.info("Este processo pode levar várias horas dependendo da configuração")
            
            # 1. Verificar pré-requisitos
            if not self.verificar_prerequisites():
                logger.error("Pré-requisitos não atendidos")
                return False
            
            # 2. Instalar dependências se necessário
            if not self.instalar_dependencias():
                logger.error("Falha na instalação de dependências")
                return False
            
            # 3. Executar download
            if not self.executar_download():
                logger.error("Falha no download")
                return False
            
            # 4. Verificar banco de dados
            banco_path = self.verificar_banco_dados()
            if not banco_path:
                logger.error("Banco de dados não disponível")
                return False
            
            # 5. Baixar estabelecimentos se necessário
            if not self.baixar_estabelecimentos(banco_path):
                logger.error("Falha ao obter dados de estabelecimentos")
                return False
            
            # 6. Gerar CSVs
            if not self.gerar_csvs(banco_path):
                logger.error("Falha na geração de CSVs")
                return False
            
            # 7. Sucesso!
            self.mostrar_resumo_final(banco_path, True)
            return True
            
        except KeyboardInterrupt:
            logger.info("Processo interrompido pelo usuário")
            self.mostrar_resumo_final("", False)
            return False
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            logger.exception("Detalhes do erro:")
            self.mostrar_resumo_final("", False)
            return False


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Processo completo automatizado - Download e geração de CSVs')
    parser.add_argument('--teste', action='store_true', 
                       help='Modo teste (download parcial e poucos estados)')
    parser.add_argument('--estados', nargs='+', 
                       help='Estados específicos para processar (ex: SP RJ MG)')
    parser.add_argument('--sem-download', action='store_true',
                       help='Pular download e usar banco existente')
    parser.add_argument('--limpar', action='store_true',
                       help='Limpar downloads e CSVs antigos antes de começar')
    parser.add_argument('--incluir-mei', action='store_true', default=True,
                       help='Incluir dados de MEI na importação (padrão: True)')
    parser.add_argument('--excluir-mei', action='store_true',
                       help='Excluir dados de MEI da importação')
    
    args = parser.parse_args()
    
    # Criar instância do processo
    processo = ProcessoCompleto()
    
    # Configurar baseado nos argumentos
    if args.teste:
        processo.config['download_completo'] = False
        print("🧪 Modo TESTE ativado - Download parcial e processamento rápido")
    else:
        print("🚀 Modo COMPLETO - Download de todos os dados (pode levar horas)")
    
    if args.estados:
        processo.config['estados_prioritarios'] = [e.upper() for e in args.estados]
        print(f"Estados específicos: {', '.join(processo.config['estados_prioritarios'])}")
    
    if args.limpar:
        processo.config['limpar_downloads_antigos'] = True
        print("🧹 Limpeza de arquivos antigos ativada")
    
    # Configurar opção de MEI
    incluir_mei = True
    if args.excluir_mei:
        incluir_mei = False
        print("🚫 MEI será EXCLUÍDO da importação")
    elif args.incluir_mei:
        incluir_mei = True
        print("✅ MEI será INCLUÍDO na importação (CPF será anonimizado)")
    
    processo.config['incluir_mei'] = incluir_mei
    
    # Confirmar execução se modo completo
    if not args.teste and not args.sem_download:
        print("\n⚠️  ATENÇÃO: O download completo pode levar várias horas e ocupar muito espaço em disco!")
        resposta = input("Deseja continuar? (sim/não): ").lower().strip()
        if resposta not in ['sim', 's', 'yes', 'y']:
            print("Processo cancelado pelo usuário")
            return
    
    # Executar processo
    print(f"\n{'='*60}")
    print("INICIANDO PROCESSO AUTOMATIZADO")
    print(f"{'='*60}")
    
    sucesso = processo.executar_processo_completo()
    
    if sucesso:
        print("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print("Os arquivos CSV estão prontos para importação no WordPress")
    else:
        print("\n❌ PROCESSO FALHOU")
        print("Verifique os logs para mais detalhes")
    
    return sucesso


if __name__ == "__main__":
    main()
