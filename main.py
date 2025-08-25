import argparse
import sys
from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime
import time

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.scrapers.news_scraper import HackerNewsScraper, BBCNewsScraper, G1Scraper, FolhaScraper
from src.transformers.text_processor import TextProcessor
from src.storage.data_storage import SQLiteStorage, CSVStorage, ParquetStorage, JSONStorage
from src.utils.logger import setup_logger
from src.utils.progress import (
    ProgressIndicator, TaskTracker, show_welcome_message, 
    show_completion_message, print_colored
)
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich import print as rprint

# Configuração do logger e console
logger = setup_logger()
console = Console()


class NewsScraperPipeline:
    """Pipeline principal para scraping e processamento de notícias"""
    
    def __init__(self, source: str = 'hackernews', storage_type: str = 'all'):
        """
        Inicializa o pipeline
        
        Args:
            source: Fonte de notícias ('hackernews', 'bbc', 'g1', 'folha')
            storage_type: Tipo de armazenamento ('sqlite', 'csv', 'parquet', 'json', 'all')
        """
        self.source = source
        self.storage_type = storage_type
        
        # Inicializa scraper baseado na fonte
        if source.lower() == 'hackernews':
            self.scraper = HackerNewsScraper()
            self.language = 'english'
        elif source.lower() == 'bbc':
            self.scraper = BBCNewsScraper()
            self.language = 'english'
        elif source.lower() == 'g1':
            self.scraper = G1Scraper()
            self.language = 'portuguese'
        elif source.lower() == 'folha':
            self.scraper = FolhaScraper()
            self.language = 'portuguese'
        else:
            raise ValueError(f"Fonte não suportada: {source}")
        
        # Inicializa processador de texto com idioma apropriado
        self.text_processor = TextProcessor(language=self.language)
        
        # Inicializa sistemas de armazenamento
        self.sqlite_storage = SQLiteStorage()
        self.csv_storage = CSVStorage()
        self.parquet_storage = ParquetStorage()
        self.json_storage = JSONStorage()
        
        # Inicializa rastreadores de progresso
        self.progress_indicator = ProgressIndicator()
        self.task_tracker = TaskTracker()
        self.start_time = None
        
        logger.info(f"Pipeline inicializado para fonte: {source}")
    
    def run(self):
        """Executa o pipeline completo"""
        self.start_time = time.time()
        
        # Mostra mensagem de boas-vindas
        show_welcome_message()
        
        # Adiciona tarefas ao rastreador
        self.task_tracker.add_task('scraping', 'Extraindo notícias', 1)
        self.task_tracker.add_task('processing', 'Processando textos', 1)
        self.task_tracker.add_task('analysis', 'Analisando frequência', 1)
        self.task_tracker.add_task('storage', 'Salvando dados', 1)
        
        # Etapa 1: Scraping
        self.progress_indicator.print_step(1, 4, "Fazendo scraping das notícias")
        self.task_tracker.update_task('scraping')
        news_items = self._scrape_news()
        self.task_tracker.complete_task('scraping')
        
        if not news_items:
            self.progress_indicator.show_status(
                "Nenhuma notícia foi extraída. Encerrando pipeline.", 
                "error"
            )
            return
        
        # Etapa 2: Transformação
        self.progress_indicator.print_step(2, 4, "Processando e transformando dados")
        self.task_tracker.update_task('processing')
        processed_data = self._process_news(news_items)
        self.task_tracker.complete_task('processing')
        
        # Etapa 3: Análise
        self.progress_indicator.print_step(3, 4, "Analisando frequência de palavras")
        self.task_tracker.update_task('analysis')
        word_frequency = self._analyze_frequency(processed_data)
        self.task_tracker.complete_task('analysis')
        
        # Etapa 4: Persistência
        self.progress_indicator.print_step(4, 4, "Salvando dados")
        self.task_tracker.update_task('storage')
        files_saved = self._save_data(news_items, processed_data, word_frequency)
        self.task_tracker.complete_task('storage')
        
        # Mostra resumo das tarefas
        console.print("\n")
        self.task_tracker.display_summary()
        
        # Relatório final
        self._print_report(news_items, processed_data, word_frequency)
    
    def _scrape_news(self) -> List[Dict]:
        """Executa o scraping de notícias"""
        try:
            news_items = self.scraper.scrape()
            self.progress_indicator.show_status(
                f"Extraídas {len(news_items)} notícias de {self.source}",
                "success"
            )
            return news_items
        except Exception as e:
            logger.error(f"Erro durante scraping: {e}")
            return []
    
    def _process_news(self, news_items: List[Dict]) -> Dict:
        """Processa e transforma as notícias"""
        # Extrai apenas os títulos
        titles = [item['title'] for item in news_items]
        
        # Processa títulos
        processed_titles = self.text_processor.process_titles(titles)
        
        # Calcula estatísticas
        stats = self.text_processor.get_statistics(processed_titles)
        
        console.print(f"[cyan]✓ Processados {len(processed_titles)} títulos[/cyan]")
        console.print(f"[cyan]✓ Palavras únicas encontradas: {stats['unique_words']}[/cyan]")
        
        return {
            'original_titles': titles,
            'processed_titles': processed_titles,
            'statistics': stats
        }
    
    def _analyze_frequency(self, processed_data: Dict) -> List[tuple]:
        """Analisa frequência de palavras"""
        processed_titles = processed_data['processed_titles']
        
        # Obtém frequência das palavras
        word_freq = self.text_processor.get_word_frequency(processed_titles, top_n=20)
        
        # Mostra top 5 palavras em uma tabela
        table = Table(title="Top 5 Palavras Mais Frequentes", show_header=True)
        table.add_column("Palavra", style="cyan")
        table.add_column("Frequência", justify="right", style="magenta")
        
        for word, freq in word_freq[:5]:
            table.add_row(word, str(freq))
        
        console.print(table)
        
        return word_freq
    
    def _save_data(self, news_items: List[Dict], processed_data: Dict, word_frequency: List[tuple]) -> int:
        """Salva dados nos formatos especificados"""
        
        # Prepara dados para salvamento
        export_data = []
        for i, item in enumerate(news_items):
            processed_title = ""
            if i < len(processed_data['processed_titles']):
                processed_title = processed_data['processed_titles'][i]
            
            export_data.append({
                'title': item['title'],
                'processed_title': processed_title,
                'link': item['link'],
                'source': item['source'],
                'collected_at': item['collected_at']
            })
        
        # Salva em SQLite
        if self.storage_type in ['sqlite', 'all']:
            try:
                self.sqlite_storage.save_raw_news(news_items)
                self.sqlite_storage.save_word_frequency(word_frequency)
            except Exception as e:
                console.print(f"[red]✗ Erro ao salvar em SQLite: {e}[/red]")
        
        # Salva em CSV
        if self.storage_type in ['csv', 'all']:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                self.csv_storage.save(export_data, f"news_{self.source}_{timestamp}.csv")
                
                # Salva frequência de palavras em CSV separado
                freq_data = [{'word': w, 'frequency': f} for w, f in word_frequency]
                self.csv_storage.save(freq_data, f"word_frequency_{timestamp}.csv")
            except Exception as e:
                console.print(f"[red]✗ Erro ao salvar em CSV: {e}[/red]")
        
        # Salva em Parquet
        if self.storage_type in ['parquet', 'all']:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                self.parquet_storage.save(export_data, f"news_{self.source}_{timestamp}.parquet")
            except Exception as e:
                console.print(f"[red]✗ Erro ao salvar em Parquet: {e}[/red]")
        
        # Salva em JSON
        if self.storage_type in ['json', 'all']:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Estrutura completa em JSON
                full_data = {
                    'metadata': {
                        'source': self.source,
                        'collected_at': datetime.now().isoformat(),
                        'total_news': len(news_items),
                        'statistics': processed_data['statistics']
                    },
                    'news': export_data,
                    'word_frequency': [{'word': w, 'frequency': f} for w, f in word_frequency]
                }
                
                self.json_storage.save(full_data, f"news_analysis_{timestamp}.json")
            except Exception as e:
                console.print(f"[red]✗ Erro ao salvar em JSON: {e}[/red]")
        
        # Retorna quantidade de arquivos salvos
        files_saved = 0
        if self.storage_type == 'all':
            files_saved = 4
        else:
            files_saved = 1
        return files_saved
    
    def _print_report(self, news_items: List[Dict], processed_data: Dict, word_frequency: List[tuple]):
        """Imprime relatório final da execução"""
        execution_time = time.time() - self.start_time
        
        # Prepara estatísticas para exibição
        stats = processed_data['statistics']
        
        # Cria tabela de estatísticas
        stats_table = Table(title="📊 Estatísticas de Processamento", show_header=False)
        stats_table.add_column("Métrica", style="cyan")
        stats_table.add_column("Valor", justify="right", style="green")
        
        stats_table.add_row("Fonte", self.source.upper())
        stats_table.add_row("Notícias Coletadas", str(len(news_items)))
        stats_table.add_row("Total de Palavras", str(stats['total_words']))
        stats_table.add_row("Palavras Únicas", str(stats['unique_words']))
        stats_table.add_row("Média Palavras/Título", f"{stats['avg_words_per_text']:.2f}")
        stats_table.add_row("Riqueza Vocabular", f"{stats['vocabulary_richness']:.3f}")
        
        console.print("\n")
        console.print(stats_table)
        
        # Cria tabela com top 10 palavras
        word_table = Table(title="🔝 Top 10 Palavras Mais Frequentes")
        word_table.add_column("#", justify="right", style="dim")
        word_table.add_column("Palavra", style="cyan")
        word_table.add_column("Frequência", justify="right", style="magenta")
        word_table.add_column("Barra", style="green")
        
        max_freq = word_frequency[0][1] if word_frequency else 1
        for i, (word, freq) in enumerate(word_frequency[:10], 1):
            bar_length = int((freq / max_freq) * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            word_table.add_row(str(i), word, str(freq), bar)
        
        console.print("\n")
        console.print(word_table)
        
        # Mostra mensagem de conclusão
        completion_stats = {
            'news_count': len(news_items),
            'words_processed': stats['total_words'],
            'files_saved': 4 if self.storage_type == 'all' else 1,
            'execution_time': f"{execution_time:.2f}s"
        }
        
        console.print("\n")
        show_completion_message(completion_stats)


def main():
    """Função principal"""
    # Limpa a tela no início
    console.clear()
    parser = argparse.ArgumentParser(
        description='Sistema de Scraping e Análise de Notícias',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemplos de uso:
  python main.py                          # Usa configurações padrão (Hacker News, todos os formatos)
  python main.py --source bbc             # Scraping da BBC News
  python main.py --source g1              # Scraping do G1 (Brasil)
  python main.py --source folha           # Scraping da Folha de S.Paulo
  python main.py --storage csv            # Salva apenas em CSV
  python main.py --source g1 --storage sqlite  # G1 salvando em SQLite
        '''
    )
    
    parser.add_argument(
        '--source',
        type=str,
        choices=['hackernews', 'bbc', 'g1', 'folha'],
        default='hackernews',
        help='Fonte de notícias para scraping (padrão: hackernews)'
    )
    
    parser.add_argument(
        '--storage',
        type=str,
        choices=['sqlite', 'csv', 'parquet', 'json', 'all'],
        default='all',
        help='Formato de armazenamento dos dados (padrão: all)'
    )
    
    args = parser.parse_args()
    
    try:
        # Cria e executa o pipeline
        pipeline = NewsScraperPipeline(
            source=args.source,
            storage_type=args.storage
        )
        pipeline.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Execução interrompida pelo usuário[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Erro fatal: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()