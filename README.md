# Sistema de Scraping e Análise de Notícias

Sistema robusto para coleta, processamento e análise de notícias de múltiplas fontes web, com suporte a diversos formatos de persistência de dados.

## Características Principais

- **Coleta de Dados**: Extração automatizada de notícias de sites populares (internacionais e brasileiros)
- **Processamento de Texto**: Limpeza e normalização de títulos com remoção de stopwords (português e inglês)
- **Análise de Frequência**: Identificação das palavras mais relevantes nos títulos
- **Múltiplos Formatos**: Suporte para SQLite, CSV, Parquet e JSON
- **Arquitetura Modular**: Código organizado e facilmente extensível
- **Logging Completo**: Rastreamento detalhado de todas as operações
- **Indicadores Visuais**: Barras de progresso e interface colorida

## Estrutura do Projeto

```
scraping-dados/
│
├── src/
│   ├── scrapers/          # Módulos de extração de dados
│   │   ├── __init__.py
│   │   └── news_scraper.py
│   │
│   ├── transformers/      # Processamento e transformação
│   │   ├── __init__.py
│   │   └── text_processor.py
│   │
│   ├── storage/           # Persistência de dados
│   │   ├── __init__.py
│   │   └── data_storage.py
│   │
│   └── utils/             # Utilitários
│       ├── __init__.py
│       └── logger.py
│
├── data/                  # Diretório de saída dos dados
├── logs/                  # Arquivos de log
├── main.py                # Script principal
├── requirements.txt       # Dependências
└── README.md             # Documentação
```

## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Conexão com internet para baixar as notícias

### Configuração do Ambiente

1. Clone ou baixe o projeto:
```bash
git clone <url-do-repositorio>
cd scraping-dados
```

2. Crie um ambiente virtual (recomendado):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Baixe os recursos do NLTK (executado automaticamente na primeira execução):
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Uso

### Execução Básica

Execute o sistema com as configurações padrão:
```bash
python main.py
```

### Opções de Linha de Comando

O sistema oferece diversas opções de configuração:

```bash
python main.py [--source FONTE] [--storage FORMATO]
```

#### Parâmetros:

- `--source`: Fonte de notícias para scraping
  - `hackernews` (padrão): Hacker News (inglês)
  - `bbc`: BBC News (inglês)
  - `g1`: Portal G1 - Globo (português)
  - `folha`: Folha de S.Paulo (português)

- `--storage`: Formato de armazenamento dos dados
  - `sqlite`: Banco de dados SQLite
  - `csv`: Arquivos CSV
  - `parquet`: Arquivos Parquet (comprimidos)
  - `json`: Arquivos JSON
  - `all` (padrão): Todos os formatos

### Exemplos de Uso

```bash
# Coletar notícias do Hacker News e salvar em todos os formatos
python main.py

# Coletar notícias da BBC e salvar apenas em CSV
python main.py --source bbc --storage csv

# Coletar notícias do G1 (Brasil) e salvar em todos os formatos
python main.py --source g1

# Coletar notícias da Folha de S.Paulo
python main.py --source folha --storage sqlite

# G1 com armazenamento em JSON
python main.py --source g1 --storage json
```

## Saída do Sistema

### Estrutura dos Dados Coletados

Cada notícia coletada contém:
- **title**: Título original da notícia
- **link**: URL da notícia
- **source**: Fonte da notícia (Hacker News ou BBC)
- **collected_at**: Data/hora da coleta
- **processed_title**: Título após processamento (limpeza e remoção de stopwords)

### Análise de Frequência

O sistema gera uma análise das palavras mais frequentes encontradas nos títulos, incluindo:
- Top 20 palavras mais comuns
- Estatísticas de vocabulário
- Riqueza lexical

### Formatos de Saída

#### SQLite
- Arquivo: `data/news_data.db`
- Tabelas:
  - `raw_news`: Notícias brutas
  - `processed_news`: Notícias processadas
  - `word_frequency`: Frequência de palavras

#### CSV
- Arquivos gerados com timestamp:
  - `data/news_[fonte]_[timestamp].csv`: Dados das notícias
  - `data/word_frequency_[timestamp].csv`: Frequência de palavras

#### Parquet
- Arquivo: `data/news_[fonte]_[timestamp].parquet`
- Formato comprimido e eficiente para análise

#### JSON
- Arquivo: `data/news_analysis_[timestamp].json`
- Estrutura completa com metadados, notícias e análise

## Logs e Monitoramento

O sistema gera logs detalhados em `logs/news_scraper_[data].log` contendo:
- Informações de execução
- Erros e avisos
- Estatísticas de processamento
- Tempo de execução

## Extensibilidade

### Fontes Suportadas

#### Sites Internacionais:
- **Hacker News**: Tecnologia e startups
- **BBC News**: Notícias internacionais

#### Sites Brasileiros:
- **G1 (Globo)**: Portal de notícias brasileiro
- **Folha de S.Paulo**: Jornal brasileiro

### Adicionando Novas Fontes

Para adicionar uma nova fonte de notícias:

1. Crie uma nova classe em `src/scrapers/news_scraper.py`:
```python
class NovaFonteScraper(NewsScraper):
    def __init__(self):
        super().__init__('https://exemplo.com')
    
    def extract_news(self, html_content: str) -> List[Dict[str, str]]:
        # Implementar extração específica
        pass
```

2. Adicione a fonte no `main.py`:
```python
elif source.lower() == 'novafonte':
    self.scraper = NovaFonteScraper()
    self.language = 'portuguese'  # ou 'english'
```

### Personalizando Processamento

Modifique `src/transformers/text_processor.py` para:
- Adicionar novas stopwords
- Implementar diferentes técnicas de limpeza
- Adicionar análises linguísticas

## Solução de Problemas

### Erro de Conexão
- Verifique sua conexão com a internet
- Alguns sites podem estar temporariamente indisponíveis

### Erro de Dependências
```bash
pip install --upgrade -r requirements.txt
```

### Erro de NLTK
```bash
python -c "import nltk; nltk.download('all')"
```

### Permissões de Escrita
- Certifique-se de ter permissões para criar arquivos nos diretórios `data/` e `logs/`

## Requisitos do Sistema

### Dependências Python
- requests: Requisições HTTP
- beautifulsoup4: Parsing HTML
- pandas: Manipulação de dados
- nltk: Processamento de linguagem natural
- lxml: Parser XML/HTML
- python-dateutil: Manipulação de datas

### Recursos de Hardware
- Memória RAM: Mínimo 512MB
- Espaço em disco: 100MB para dados e logs
- Processador: Qualquer processador moderno

## Considerações de Performance

- O scraping respeita timeouts de 10 segundos por requisição
- Processamento em lote para otimizar memória
- Cache de sessão HTTP para múltiplas requisições
- Compressão automática em formato Parquet

## Licença

Este projeto é fornecido como está, para fins educacionais e de demonstração.

## Suporte

Para questões ou problemas, verifique:
1. Os logs em `logs/` para detalhes de erros
2. A documentação das bibliotecas utilizadas
3. As configurações de rede e proxy se aplicável