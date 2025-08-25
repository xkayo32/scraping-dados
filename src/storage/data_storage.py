import sqlite3
import csv
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging
from tqdm import tqdm
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

logger = logging.getLogger(__name__)
console = Console()


class DataStorage:
    """Classe base para armazenamento de dados"""
    
    def __init__(self, base_path: str = "data"):
        """
        Inicializa o sistema de armazenamento
        
        Args:
            base_path: Diretório base para armazenar dados
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def save(self, data: List[Dict], filename: str):
        """Método abstrato para salvar dados"""
        raise NotImplementedError("Subclasses devem implementar o método save")
    
    def load(self, filename: str):
        """Método abstrato para carregar dados"""
        raise NotImplementedError("Subclasses devem implementar o método load")


class SQLiteStorage(DataStorage):
    """Armazenamento usando SQLite"""
    
    def __init__(self, base_path: str = "data", db_name: str = "news_data.db"):
        """
        Inicializa conexão com SQLite
        
        Args:
            base_path: Diretório para o banco de dados
            db_name: Nome do arquivo do banco
        """
        super().__init__(base_path)
        self.db_path = self.base_path / db_name
        self._create_tables()
    
    def _create_tables(self):
        """Cria tabelas necessárias no banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de notícias brutas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS raw_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    source TEXT,
                    collected_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(link)
                )
            ''')
            
            # Tabela de notícias processadas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    raw_news_id INTEGER,
                    cleaned_title TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (raw_news_id) REFERENCES raw_news(id)
                )
            ''')
            
            # Tabela de frequência de palavras
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS word_frequency (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    frequency INTEGER,
                    analysis_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info(f"Banco de dados criado/verificado em {self.db_path}")
    
    def save_raw_news(self, news_items: List[Dict]) -> int:
        """
        Salva notícias brutas no banco de dados
        
        Args:
            news_items: Lista de dicionários com dados das notícias
            
        Returns:
            Número de registros inseridos
        """
        inserted = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            with tqdm(total=len(news_items), desc="Salvando em SQLite",
                      bar_format='{l_bar}{bar:30}| {n_fmt}/{total_fmt}',
                      colour='yellow') as pbar:
                for item in news_items:
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO raw_news (title, link, source, collected_at)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            item.get('title'),
                            item.get('link'),
                            item.get('source'),
                            item.get('collected_at', datetime.now().isoformat())
                        ))
                        if cursor.rowcount > 0:
                            inserted += 1
                    except sqlite3.Error as e:
                        logger.error(f"Erro ao inserir notícia: {e}")
                        continue
                    finally:
                        pbar.update(1)
                
                conn.commit()
        
        console.print(f"[green]✓ Inseridas {inserted} notícias no SQLite[/green]")
        return inserted
    
    def save_processed_news(self, processed_items: List[Dict]):
        """
        Salva notícias processadas no banco
        
        Args:
            processed_items: Lista de notícias processadas
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for item in processed_items:
                cursor.execute('''
                    INSERT INTO processed_news (raw_news_id, cleaned_title)
                    VALUES (?, ?)
                ''', (item.get('raw_id'), item.get('cleaned_title')))
            
            conn.commit()
    
    def save_word_frequency(self, word_freq: List[tuple]):
        """
        Salva frequência de palavras no banco
        
        Args:
            word_freq: Lista de tuplas (palavra, frequência)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            analysis_date = datetime.now().date()
            
            for word, freq in word_freq:
                cursor.execute('''
                    INSERT INTO word_frequency (word, frequency, analysis_date)
                    VALUES (?, ?, ?)
                ''', (word, freq, analysis_date))
            
            conn.commit()
            logger.info(f"Salvou frequência de {len(word_freq)} palavras")
    
    def get_recent_news(self, limit: int = 100) -> List[Dict]:
        """
        Recupera notícias recentes do banco
        
        Args:
            limit: Número máximo de notícias a retornar
            
        Returns:
            Lista de notícias
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, link, source, collected_at
                FROM raw_news
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do banco de dados
        
        Returns:
            Dicionário com estatísticas
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total de notícias
            cursor.execute("SELECT COUNT(*) FROM raw_news")
            total_news = cursor.fetchone()[0]
            
            # Notícias por fonte
            cursor.execute("""
                SELECT source, COUNT(*) as count
                FROM raw_news
                GROUP BY source
            """)
            by_source = dict(cursor.fetchall())
            
            # Total de palavras analisadas
            cursor.execute("SELECT COUNT(DISTINCT word) FROM word_frequency")
            unique_words = cursor.fetchone()[0]
            
            return {
                'total_news': total_news,
                'news_by_source': by_source,
                'unique_words_analyzed': unique_words
            }


class CSVStorage(DataStorage):
    """Armazenamento usando arquivos CSV"""
    
    def save(self, data: List[Dict], filename: str = "news_data.csv"):
        """
        Salva dados em arquivo CSV
        
        Args:
            data: Lista de dicionários para salvar
            filename: Nome do arquivo CSV
        """
        if not data:
            logger.warning("Nenhum dado para salvar em CSV")
            return
        
        filepath = self.base_path / filename
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Salvando CSV..."),
            console=console
        ) as progress:
            task = progress.add_task("Salvando", total=1)
            
            # Usa pandas para facilitar a escrita
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            progress.update(task, advance=1)
        
        console.print(f"[green]✓ Salvou {len(data)} registros em CSV[/green]")
    
    def load(self, filename: str = "news_data.csv") -> List[Dict]:
        """
        Carrega dados de arquivo CSV
        
        Args:
            filename: Nome do arquivo CSV
            
        Returns:
            Lista de dicionários com os dados
        """
        filepath = self.base_path / filename
        
        if not filepath.exists():
            logger.warning(f"Arquivo {filepath} não encontrado")
            return []
        
        df = pd.read_csv(filepath, encoding='utf-8')
        return df.to_dict('records')
    
    def append(self, data: List[Dict], filename: str = "news_data.csv"):
        """
        Adiciona dados a um arquivo CSV existente
        
        Args:
            data: Dados para adicionar
            filename: Nome do arquivo
        """
        filepath = self.base_path / filename
        
        if not data:
            return
        
        df_new = pd.DataFrame(data)
        
        if filepath.exists():
            df_existing = pd.read_csv(filepath, encoding='utf-8')
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            # Remove duplicatas baseadas no link
            if 'link' in df_combined.columns:
                df_combined = df_combined.drop_duplicates(subset=['link'], keep='first')
        else:
            df_combined = df_new
        
        df_combined.to_csv(filepath, index=False, encoding='utf-8')
        logger.info(f"Adicionados {len(data)} registros ao CSV")


class ParquetStorage(DataStorage):
    """Armazenamento usando arquivos Parquet"""
    
    def save(self, data: List[Dict], filename: str = "news_data.parquet"):
        """
        Salva dados em arquivo Parquet
        
        Args:
            data: Lista de dicionários para salvar
            filename: Nome do arquivo Parquet
        """
        if not data:
            logger.warning("Nenhum dado para salvar em Parquet")
            return
        
        filepath = self.base_path / filename
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Salvando Parquet..."),
            console=console
        ) as progress:
            task = progress.add_task("Salvando", total=1)
            
            df = pd.DataFrame(data)
            try:
                # Tenta usar pyarrow se disponível
                df.to_parquet(filepath, engine='pyarrow', compression='snappy')
            except ImportError:
                # Fallback para fastparquet ou salva como CSV comprimido
                csv_path = filepath.with_suffix('.csv.gz')
                df.to_csv(csv_path, index=False, compression='gzip')
                console.print(f"[yellow]⚠ Parquet não disponível, salvou como CSV comprimido[/yellow]")
                progress.update(task, advance=1)
                return
            
            progress.update(task, advance=1)
        
        console.print(f"[green]✓ Salvou {len(data)} registros em Parquet[/green]")
    
    def load(self, filename: str = "news_data.parquet") -> List[Dict]:
        """
        Carrega dados de arquivo Parquet
        
        Args:
            filename: Nome do arquivo Parquet
            
        Returns:
            Lista de dicionários com os dados
        """
        filepath = self.base_path / filename
        
        if not filepath.exists():
            logger.warning(f"Arquivo {filepath} não encontrado")
            return []
        
        df = pd.read_parquet(filepath, engine='pyarrow')
        return df.to_dict('records')


class JSONStorage(DataStorage):
    """Armazenamento usando arquivos JSON"""
    
    def save(self, data: List[Dict] | Dict, filename: str = "news_data.json"):
        """
        Salva dados em arquivo JSON
        
        Args:
            data: Lista de dicionários ou dicionário para salvar
            filename: Nome do arquivo JSON
        """
        filepath = self.base_path / filename
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Salvando JSON..."),
            console=console
        ) as progress:
            task = progress.add_task("Salvando", total=1)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            progress.update(task, advance=1)
        
        items_count = len(data) if isinstance(data, list) else 1
        console.print(f"[green]✓ Salvou dados em JSON[/green]")
    
    def load(self, filename: str = "news_data.json") -> List[Dict]:
        """
        Carrega dados de arquivo JSON
        
        Args:
            filename: Nome do arquivo JSON
            
        Returns:
            Lista de dicionários com os dados
        """
        filepath = self.base_path / filename
        
        if not filepath.exists():
            logger.warning(f"Arquivo {filepath} não encontrado")
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)