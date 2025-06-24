# 🚀 AUTOMAÇÃO COMPLETA - CNPJ PARA WORDPRESS

## ⚡ EXECUÇÃO RÁPIDA

Simplesmente execute um dos comandos abaixo:

### 🧪 Teste Rápido (10-30 minutos)
```bash
python executar_rapido.py
# Escolha opção 1
```

### 🚀 Processo Completo (3-8 horas)
```bash
python executar_rapido.py
# Escolha opção 2
```

## 📋 O QUE CADA SCRIPT FAZ

### `executar_rapido.py` - **RECOMENDADO**
- ✅ Menu simples e intuitivo
- ✅ Execução com 1 clique
- ✅ Opções de teste e completo
- ✅ Verificações automáticas
- ✅ **Configurações avançadas (MEI, Estados, etc.)**

### `processo_completo.py` - Script Master
- ✅ Execução 100% automática
- ✅ Download + Processamento + CSVs
- ✅ Tratamento de erros robusto
- ✅ Logs detalhados

### `gerar_csv_estados.py` - Gerador de CSVs
- ✅ Arquivos por estado (SP.csv, RJ.csv, etc)
- ✅ Máximo 100 mil linhas por arquivo
- ✅ Dados completos em uma linha
- ✅ Pronto para WordPress

## 🎯 RESULTADO FINAL

Você terá arquivos CSV assim:
```
csv_estados/
├── SP_001.csv (100.000 linhas)
├── SP_002.csv (100.000 linhas)
├── SP_003.csv (50.000 linhas)
├── RJ_001.csv (100.000 linhas)
├── RJ_002.csv (80.000 linhas)
├── MG.csv (95.000 linhas)
└── RESUMO.txt
```

## 📊 DADOS INCLUÍDOS

Cada linha do CSV contém:
- **Empresa**: CNPJ, razão social, capital, porte
- **Estabelecimento**: endereço, telefone, email, situação
- **Localização**: cidade, estado, CEP
- **Atividade**: CNAE principal e descrição
- **Simples**: dados do Simples Nacional
- **Sócios**: quantidade de sócios

## 🏢 CONTROLE DE MEI (MICROEMPREENDEDOR INDIVIDUAL)

### Opção Padrão - Incluir MEI:
- ✅ MEI será incluído na importação
- 🔒 **CPF dos sócios anonimizado** (***.***.***-**)
- 📊 Dados completos para análise

### Opção Alternativa - Excluir MEI:
- 🚫 MEI completamente excluído
- 📉 Volume de dados reduzido
- 🎯 Foco em empresas maiores

### Como escolher:
1. Execute: `python executar_rapido.py`
2. Escolha opção **5) Configurações Avançadas**
3. Configure MEI conforme sua necessidade

## 🔧 COMANDOS AVANÇADOS

```bash
# Apenas alguns estados
python processo_completo.py --estados SP RJ MG

# Modo teste
python processo_completo.py --teste

# Excluir MEI da importação
python processo_completo.py --excluir-mei

# Combinações
python processo_completo.py --teste --excluir-mei --estados SP RJ

# Usar banco existente
python gerar_csv_estados.py --db cnpj_dados.db

# Gerar apenas CSVs (interface)
python executar_rapido.py
# Escolha opção 3
```

## ⚠️ REQUISITOS

- **Espaço**: 50GB livres
- **Tempo**: 3-8 horas (completo) ou 10-30 min (teste)
- **Internet**: Conexão estável
- **Python**: 3.7+ (criado automaticamente)

## 🆘 PROBLEMAS?

1. **Erro de espaço**: Libere mais espaço em disco
2. **Erro de conexão**: Verifique internet e tente novamente
3. **Processo lento**: É normal, os arquivos são grandes
4. **Erro de Python**: O script instala automaticamente

## 🎉 INÍCIO RÁPIDO

1. Abra o terminal no diretório do projeto
2. Execute: `python executar_rapido.py`
3. Escolha a opção desejada
4. Aguarde o processo terminar
5. Seus CSVs estarão em `csv_estados/`

**Pronto para WordPress!** 🚀
