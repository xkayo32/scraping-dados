# 📰 Guia Completo de Uso - Sistema de Scraping de Notícias

## 🚀 Início Rápido

### Instalação em 3 Passos

```bash
# 1. Ative o ambiente virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o sistema
python main.py
```

## 📊 Comandos Principais

### Comando Básico
```bash
python main.py
```
> Coleta notícias do Hacker News e salva em TODOS os formatos

### Estrutura do Comando
```bash
python main.py --source [FONTE] --storage [FORMATO]
```

## 🌐 Fontes Disponíveis

### Sites Internacionais (Inglês)

#### 1. Hacker News
```bash
python main.py --source hackernews
```
- **Conteúdo**: Tecnologia, startups, programação
- **Quantidade**: ~30 notícias
- **Idioma**: Inglês

#### 2. BBC News
```bash
python main.py --source bbc
```
- **Conteúdo**: Notícias internacionais
- **Quantidade**: ~30 manchetes
- **Idioma**: Inglês

### Sites Brasileiros (Português)

#### 3. G1 (Portal Globo)
```bash
python main.py --source g1
```
- **Conteúdo**: Notícias nacionais e regionais
- **Quantidade**: ~30 notícias
- **Idioma**: Português

#### 4. Folha de S.Paulo
```bash
python main.py --source folha
```
- **Conteúdo**: Jornalismo brasileiro
- **Quantidade**: ~30 manchetes
- **Idioma**: Português

## 💾 Formatos de Armazenamento

### 1. SQLite (Banco de Dados)
```bash
python main.py --source g1 --storage sqlite
```
- **Arquivo**: `data/news_data.db`
- **Vantagens**: Consultas SQL, relacionamentos, índices
- **Uso ideal**: Análises complexas, aplicações web

### 2. CSV (Planilha)
```bash
python main.py --source bbc --storage csv
```
- **Arquivo**: `data/news_[fonte]_[timestamp].csv`
- **Vantagens**: Abre no Excel, fácil visualização
- **Uso ideal**: Análises rápidas, compartilhamento

### 3. JSON (Estruturado)
```bash
python main.py --source folha --storage json
```
- **Arquivo**: `data/news_analysis_[timestamp].json`
- **Vantagens**: Metadados completos, hierarquia
- **Uso ideal**: APIs, integração com outros sistemas

### 4. Parquet (Comprimido)
```bash
python main.py --source hackernews --storage parquet
```
- **Arquivo**: `data/news_[fonte]_[timestamp].parquet`
- **Vantagens**: Compactado, rápido para big data
- **Uso ideal**: Análise de dados, machine learning

### 5. Todos os Formatos
```bash
python main.py --source g1 --storage all
```
- **Gera**: SQLite + CSV + JSON + Parquet
- **Uso ideal**: Backup completo, múltiplas análises

## 📈 Exemplos Práticos de Uso

### Caso 1: Monitoramento Diário de Tecnologia
```bash
# Coleta notícias tech toda manhã
python main.py --source hackernews --storage sqlite

# Visualiza no Excel
python main.py --source hackernews --storage csv
```

### Caso 2: Análise de Tendências Brasileiras
```bash
# Coleta do G1 para análise
python main.py --source g1 --storage all

# Compara com Folha
python main.py --source folha --storage all
```

### Caso 3: Dataset para Machine Learning
```bash
# Formato otimizado para ML
python main.py --source bbc --storage parquet
python main.py --source g1 --storage parquet
```

### Caso 4: API de Notícias
```bash
# JSON para servir via API
python main.py --source folha --storage json
```

## 📊 Visualizando os Resultados

### No Terminal
Durante a execução, você verá:
- ✅ Barra de progresso da coleta
- 📊 Tabela com palavras mais frequentes
- 📈 Estatísticas do processamento
- ✨ Resumo colorido final

### Arquivos Gerados

```
data/
├── news_data.db                    # Banco SQLite
├── news_g1_20240825_143022.csv     # Notícias em CSV
├── word_frequency_20240825.csv     # Frequência de palavras
├── news_analysis_20240825.json     # JSON completo
└── news_folha_20240825.parquet     # Formato comprimido
```

## 🔍 Analisando os Dados

### SQLite - Consultas SQL
```sql
-- Conecte ao banco: data/news_data.db

-- Últimas 10 notícias
SELECT title, source, collected_at 
FROM raw_news 
ORDER BY created_at DESC 
LIMIT 10;

-- Palavras mais frequentes
SELECT word, frequency 
FROM word_frequency 
ORDER BY frequency DESC 
LIMIT 20;
```

### CSV - Excel/Google Sheets
1. Abra o arquivo CSV no Excel
2. Use filtros para análise
3. Crie gráficos de frequência
4. Exporte relatórios

### JSON - Programação
```python
import json

# Ler dados
with open('data/news_analysis_20240825.json', 'r') as f:
    data = json.load(f)

# Acessar notícias
for news in data['news'][:5]:
    print(f"- {news['title']}")

# Ver estatísticas
print(f"Total: {data['metadata']['total_news']}")
```

### Parquet - Pandas/Data Science
```python
import pandas as pd

# Carregar dados
df = pd.read_parquet('data/news_g1_20240825.parquet')

# Análise rápida
print(df.head())
print(df['source'].value_counts())

# Palavras mais comuns nos títulos
df['title'].str.split().explode().value_counts().head(10)
```

## 🎯 Casos de Uso Reais

### 1. **Pesquisa Acadêmica**
```bash
# Coleta dados para TCC sobre mídia brasileira
python main.py --source g1 --storage all
python main.py --source folha --storage all
```

### 2. **Inteligência de Mercado**
```bash
# Monitora tendências tech
python main.py --source hackernews --storage sqlite
```

### 3. **Análise de Sentimento**
```bash
# Dataset para treinar modelo
python main.py --source bbc --storage parquet
```

### 4. **Comparação de Coberturas**
```bash
# Compara como G1 e Folha cobrem notícias
python main.py --source g1 --storage csv
python main.py --source folha --storage csv
```

## 🛠️ Dicas Avançadas

### Automatização com Cron (Linux/Mac)
```bash
# Adicione ao crontab para executar diariamente às 8h
0 8 * * * cd /caminho/projeto && venv/bin/python main.py --source g1
```

### Automatização com Task Scheduler (Windows)
1. Abra o Agendador de Tarefas
2. Crie tarefa básica
3. Configure para executar `python main.py --source g1`
4. Defina horário desejado

### Script de Coleta Múltipla
```bash
# criar arquivo: coleta_completa.sh ou .bat

#!/bin/bash
echo "Iniciando coleta completa..."

# Coleta de todas as fontes
python main.py --source hackernews --storage all
sleep 5
python main.py --source bbc --storage all
sleep 5
python main.py --source g1 --storage all
sleep 5
python main.py --source folha --storage all

echo "Coleta concluída!"
```

## 📝 Logs e Monitoramento

### Verificar Logs
```bash
# Logs são salvos em logs/
cat logs/news_scraper_20240825.log

# Acompanhar em tempo real
tail -f logs/news_scraper_20240825.log
```

### Informações nos Logs
- 🟢 INFO: Operações normais
- 🟡 WARNING: Avisos (ex: notícia não processada)
- 🔴 ERROR: Erros (ex: site indisponível)

## ❓ Resolução de Problemas

### Site não responde
```bash
# Tente novamente após alguns minutos
python main.py --source g1

# Ou use outra fonte
python main.py --source folha
```

### Erro de dependências
```bash
# Reinstale as dependências
pip install --upgrade -r requirements.txt
```

### Pouco espaço em disco
```bash
# Use apenas CSV (menor tamanho)
python main.py --storage csv

# Ou limpe dados antigos
rm data/*.parquet
```

## 🎨 Personalização

### Modificar quantidade de notícias
Edite `src/scrapers/news_scraper.py`:
```python
# Mude de 30 para 50 notícias
stories_to_process = stories[:50]
```

### Adicionar novo site
1. Crie classe em `src/scrapers/news_scraper.py`
2. Adicione no `main.py`
3. Configure idioma apropriado

### Alterar stopwords
Edite `src/transformers/text_processor.py`:
```python
self.custom_stopwords = {
    # Adicione suas palavras aqui
}
```

## 📞 Suporte

### Estrutura de Arquivos
```
📁 scraping-dados/
  📁 src/           # Código fonte
  📁 data/          # Dados coletados
  📁 logs/          # Arquivos de log
  📄 main.py        # Script principal
  📄 requirements.txt # Dependências
```

### Comandos Úteis
```bash
# Ver ajuda
python main.py --help

# Verificar versão do Python
python --version

# Listar arquivos gerados
dir data\  # Windows
ls -la data/  # Linux/Mac
```

## 🚀 Próximos Passos

Após dominar o uso básico:

1. **Explore os dados** gerados com ferramentas de análise
2. **Automatize** a coleta com scripts
3. **Integre** com outros sistemas via API
4. **Visualize** com dashboards (Power BI, Tableau)
5. **Analise tendências** ao longo do tempo

---

💡 **Dica Final**: Execute o sistema regularmente para construir um histórico rico de dados para análises temporais!

🎯 **Objetivo**: Transforme dados brutos em insights valiosos!