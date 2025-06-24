# 📁 ESTRUTURA DO PROJETO - CNPJ PARA WORDPRESS

## 🎯 ARQUIVOS ESSENCIAIS

### 🚀 **Scripts Principais**
| Arquivo | Função | Uso |
|---------|--------|-----|
| `executar_rapido.py` | **Menu principal** | `python executar_rapido.py` |
| `processo_completo.py` | **Automação total** | `python processo_completo.py` |
| `downloader_cnpj.py` | Download dados CNPJ | Executado automaticamente |
| `gerar_csv_estados.py` | Gerar CSVs por estado | Executado automaticamente |
| `consultar_cnpj.py` | Consultar dados | `python consultar_cnpj.py --stats` |

### 📝 **Scripts Auxiliares**
| Arquivo | Função |
|---------|--------|
| `download_teste.py` | Download parcial para teste |
| `teste.py` | Verificar funcionamento básico |

### 📚 **Documentação**
| Arquivo | Conteúdo |
|---------|----------|
| `README.md` | **Documentação completa** |
| `requirements.txt` | Dependências Python |
| `.gitignore` | Arquivos ignorados pelo Git |
| `INDEX.md` | Este arquivo |

### 🗂️ **Diretórios** (criados automaticamente)
| Diretório | Conteúdo |
|-----------|----------|
| `.venv/` | Ambiente virtual Python |
| `dados_cnpj/` | Arquivos ZIP baixados (completo) |
| `dados_teste/` | Arquivos ZIP baixados (teste) |
| `csv_estados/` | **CSVs finais para WordPress** |

### 🗃️ **Bancos de Dados** (criados automaticamente)
| Arquivo | Conteúdo |
|---------|----------|
| `cnpj_dados.db` | Banco completo (todos os dados) |
| `cnpj_teste.db` | Banco de teste (dados limitados) |

## ⚡ COMO USAR

### 1. **Execução Rápida** (RECOMENDADO)
```bash
python executar_rapido.py
```

### 2. **Processo Completo Direto**
```bash
# Teste (rápido)
python processo_completo.py --teste

# Completo (longo)
python processo_completo.py
```

### 3. **Apenas Gerar CSVs** (se já tem dados)
```bash
python gerar_csv_estados.py --db cnpj_dados.db
```

### 4. **Consultar Dados**
```bash
python consultar_cnpj.py --stats
python consultar_cnpj.py --empresa "PETROBRAS"
python consultar_cnpj.py --cnpj 12345678
```

## 📊 FLUXO DO PROCESSO

```
1. executar_rapido.py (Menu)
   ↓
2. processo_completo.py (Orquestração)
   ↓
3. downloader_cnpj.py (Download + SQLite)
   ↓
4. gerar_csv_estados.py (CSVs para WordPress)
   ↓
5. csv_estados/ (Arquivos finais)
```

## 🎯 ARQUIVOS RESULTADO

### CSVs para WordPress:
```
csv_estados/
├── SP_001.csv (≤100k linhas)
├── SP_002.csv (≤100k linhas)
├── RJ_001.csv (≤100k linhas)
├── MG.csv (<100k linhas)
├── ...outros estados...
├── SP_socios.csv (opcional)
└── RESUMO.txt
```

### Cada linha CSV contém:
- Dados da empresa (CNPJ, razão social, capital)
- Dados do estabelecimento (endereço, telefone, email)
- Localização (cidade, estado, CEP)
- Atividade econômica (CNAE)
- Simples Nacional
- Total de sócios

## 🧹 LIMPEZA

Para limpar dados antigos:
```bash
rm -rf dados_cnpj/ dados_teste/ csv_estados/
rm -f *.db *.log
```

---

**📝 Desenvolvido por Bruno Qualhato - Junho 2025**
