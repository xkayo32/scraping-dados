import re
import string
from collections import Counter
from typing import List, Dict, Tuple
import logging
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from tqdm import tqdm
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


class TextProcessor:
    """Classe para processamento e transformação de textos"""
    
    def __init__(self, language: str = 'english'):
        """
        Inicializa o processador de texto
        
        Args:
            language: Idioma para stopwords (english ou portuguese)
        """
        self.language = language
        self._download_nltk_data()
        
        try:
            self.stop_words = set(stopwords.words(language))
        except OSError:
            # Fallback se o idioma não estiver disponível
            console.print(f"[yellow]Stopwords para '{language}' não disponíveis, usando inglês[/yellow]")
            self.stop_words = set(stopwords.words('english'))
        
        # Adiciona stopwords customizadas baseadas no idioma
        if language == 'portuguese':
            self.custom_stopwords = {
                'de', 'a', 'o', 'que', 'e', 'é', 'do', 'da', 'em', 'um', 'uma',
                'para', 'com', 'não', 'os', 'no', 'se', 'na', 'por', 'mais',
                'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem',
                'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos',
                'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até',
                'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos',
                'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'estão',
                'você', 'tinha', 'foram', 'essa', 'num', 'nem', 'suas', 'meu',
                'às', 'minha', 'têm', 'numa', 'pelos', 'elas', 'havia', 'seja',
                'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 'esses',
                'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'vos',
                'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso',
                'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes',
                'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo',
                'estou', 'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos',
                'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos',
                'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos',
                'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há',
                'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera',
                'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos',
                'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá',
                'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam',
                'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi',
                'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 'sejam',
                'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei',
                'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho',
                'tem', 'temos', 'tém', 'tinha', 'tínhamos', 'tinham', 'tive', 'teve',
                'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos',
                'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 'tivermos',
                'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam'
            }
        else:
            self.custom_stopwords = {
                'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
                'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
                'do', 'at', 'this', 'but', 'his', 'by', 'from', 'up', 'about',
                'into', 'through', 'during', 'after', 'above', 'below', 'between'
            }
        
        self.stop_words.update(self.custom_stopwords)
    
    def _download_nltk_data(self):
        """Baixa dados necessários do NLTK se ainda não estiverem disponíveis"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            console.print("[yellow]Baixando dados do NLTK pela primeira vez...[/yellow]")
            with tqdm(total=3, desc="Baixando pacotes NLTK", colour='yellow') as pbar:
                nltk.download('punkt', quiet=True)
                pbar.update(1)
                nltk.download('stopwords', quiet=True)
                pbar.update(1)
                nltk.download('punkt_tab', quiet=True)
                pbar.update(1)
    
    def clean_text(self, text: str) -> str:
        """
        Limpa o texto removendo caracteres especiais e normalizando
        
        Args:
            text: Texto a ser limpo
            
        Returns:
            Texto limpo e normalizado
        """
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove menções (@usuario)
        text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags
        text = re.sub(r'#\w+', '', text)
        
        # Remove números isolados
        text = re.sub(r'\b\d+\b', '', text)
        
        # Remove caracteres especiais mantendo espaços e letras
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        
        # Converte para minúsculas e remove espaços nas extremidades
        text = text.lower().strip()
        
        return text
    
    def remove_stopwords(self, text: str) -> str:
        """
        Remove stopwords do texto
        
        Args:
            text: Texto de entrada
            
        Returns:
            Texto sem stopwords
        """
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        return ' '.join(filtered_words)
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokeniza o texto em palavras
        
        Args:
            text: Texto a ser tokenizado
            
        Returns:
            Lista de tokens
        """
        try:
            # Tenta usar o tokenizador do NLTK
            tokens = word_tokenize(text.lower())
        except:
            # Fallback para split simples se NLTK falhar
            tokens = text.lower().split()
        
        # Remove tokens vazios e muito curtos
        tokens = [token for token in tokens if len(token) > 2]
        
        return tokens
    
    def process_titles(self, titles: List[str]) -> List[str]:
        """
        Processa uma lista de títulos aplicando limpeza e remoção de stopwords
        
        Args:
            titles: Lista de títulos para processar
            
        Returns:
            Lista de títulos processados
        """
        processed = []
        
        with tqdm(total=len(titles), desc="Processando títulos",
                  bar_format='{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}]',
                  colour='blue') as pbar:
            for title in titles:
                # Limpa o texto
                cleaned = self.clean_text(title)
                
                # Remove stopwords
                without_stopwords = self.remove_stopwords(cleaned)
                
                if without_stopwords:  # Adiciona apenas se não estiver vazio
                    processed.append(without_stopwords)
                
                pbar.update(1)
        
        return processed
    
    def get_word_frequency(self, texts: List[str], top_n: int = 20) -> List[Tuple[str, int]]:
        """
        Calcula a frequência de palavras nos textos
        
        Args:
            texts: Lista de textos para análise
            top_n: Número de palavras mais frequentes a retornar
            
        Returns:
            Lista de tuplas (palavra, frequência) ordenada por frequência
        """
        all_words = []
        
        with tqdm(total=len(texts), desc="Analisando frequência",
                  bar_format='{l_bar}{bar:30}| {n_fmt}/{total_fmt}',
                  colour='magenta') as pbar:
            for text in texts:
                # Tokeniza e adiciona palavras à lista
                tokens = self.tokenize(text)
                all_words.extend(tokens)
                pbar.update(1)
        
        # Conta frequência das palavras com progresso
        console.print("[cyan]Calculando palavras mais frequentes...[/cyan]")
        word_freq = Counter(all_words)
        
        # Retorna as N palavras mais comuns
        return word_freq.most_common(top_n)
    
    def get_statistics(self, texts: List[str]) -> Dict:
        """
        Calcula estatísticas sobre os textos processados
        
        Args:
            texts: Lista de textos
            
        Returns:
            Dicionário com estatísticas
        """
        all_words = []
        for text in texts:
            all_words.extend(self.tokenize(text))
        
        unique_words = set(all_words)
        
        stats = {
            'total_texts': len(texts),
            'total_words': len(all_words),
            'unique_words': len(unique_words),
            'avg_words_per_text': len(all_words) / len(texts) if texts else 0,
            'vocabulary_richness': len(unique_words) / len(all_words) if all_words else 0
        }
        
        return stats
    
    def generate_word_cloud_data(self, texts: List[str]) -> Dict[str, int]:
        """
        Gera dados para visualização em nuvem de palavras
        
        Args:
            texts: Lista de textos
            
        Returns:
            Dicionário com palavras e suas frequências
        """
        word_freq = self.get_word_frequency(texts, top_n=50)
        return dict(word_freq)