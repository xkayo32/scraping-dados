import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "news_scraper", log_dir: str = "logs") -> logging.Logger:
    """
    Configura e retorna um logger personalizado
    
    Args:
        name: Nome do logger
        log_dir: Diretório para salvar logs
        
    Returns:
        Logger configurado
    """
    # Cria diretório de logs se não existir
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Nome do arquivo de log com timestamp
    log_file = log_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Cria logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Remove handlers existentes para evitar duplicação
    logger.handlers.clear()
    
    # Formato das mensagens
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger