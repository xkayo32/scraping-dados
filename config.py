"""
Arquivo de configuração central do sistema de scraping
"""

from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Configurações de scraping
SCRAPING_CONFIG = {
    'timeout': 10,  # Timeout em segundos para requisições HTTP
    'max_retries': 3,  # Número máximo de tentativas
    'delay_between_requests': 1,  # Delay entre requisições em segundos
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'max_news_items': 30  # Número máximo de notícias por scraping
}

# URLs das fontes
SOURCES = {
    'hackernews': {
        'url': 'https://news.ycombinator.com',
        'name': 'Hacker News',
        'language': 'english'
    },
    'bbc': {
        'url': 'https://www.bbc.com/news',
        'name': 'BBC News',
        'language': 'english'
    }
}

# Configurações de processamento de texto
TEXT_PROCESSING = {
    'min_word_length': 3,  # Comprimento mínimo de palavra
    'top_words_count': 20,  # Número de palavras mais frequentes a mostrar
    'remove_numbers': True,  # Remover números do texto
    'lowercase': True,  # Converter para minúsculas
    'remove_punctuation': True  # Remover pontuação
}

# Configurações de armazenamento
STORAGE_CONFIG = {
    'sqlite': {
        'db_name': 'news_data.db',
        'enable': True
    },
    'csv': {
        'encoding': 'utf-8',
        'enable': True
    },
    'parquet': {
        'compression': 'snappy',
        'enable': True
    },
    'json': {
        'indent': 2,
        'ensure_ascii': False,
        'enable': True
    }
}

# Configurações de logging
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'file_prefix': 'news_scraper',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5  # Número de arquivos de backup
}

# Stopwords adicionais personalizadas
CUSTOM_STOPWORDS = {
    'english': [
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
        'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
        'do', 'at', 'this', 'but', 'his', 'by', 'from', 'up', 'about'
    ],
    'portuguese': [
        'de', 'a', 'o', 'que', 'e', 'é', 'do', 'da', 'em', 'um',
        'para', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por'
    ]
}

# Configurações de análise
ANALYSIS_CONFIG = {
    'generate_word_cloud': True,  # Gerar dados para nuvem de palavras
    'calculate_statistics': True,  # Calcular estatísticas
    'min_word_frequency': 2,  # Frequência mínima para considerar palavra relevante
    'vocabulary_analysis': True  # Análise de riqueza vocabular
}

# Configurações de exportação
EXPORT_CONFIG = {
    'timestamp_format': '%Y%m%d_%H%M%S',
    'include_metadata': True,  # Incluir metadados na exportação
    'pretty_print': True,  # Formatação legível para humanos
    'compress_output': False  # Comprimir arquivos de saída
}

# Validação de diretórios
def ensure_directories():
    """Cria diretórios necessários se não existirem"""
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

# Executar validação ao importar
ensure_directories()