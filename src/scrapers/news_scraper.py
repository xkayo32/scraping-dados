import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import time

logger = logging.getLogger(__name__)


class NewsScraper:
    """Classe responsável por fazer scraping de sites de notícias"""
    
    def __init__(self, base_url: str, timeout: int = 10):
        """
        Inicializa o scraper com URL base e timeout configurável
        
        Args:
            base_url: URL base do site a ser raspado
            timeout: Tempo máximo de espera para requisições HTTP
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_page(self, url: Optional[str] = None, show_progress: bool = True) -> Optional[str]:
        """
        Busca o conteúdo HTML de uma página
        
        Args:
            url: URL específica para buscar, usa base_url se None
            show_progress: Se deve mostrar progresso
            
        Returns:
            Conteúdo HTML da página ou None em caso de erro
        """
        target_url = url or self.base_url
        
        try:
            if show_progress:
                with tqdm(total=1, desc=f"Conectando a {self.base_url.split('//')[1].split('/')[0]}", 
                         bar_format='{l_bar}{bar:20}| {n_fmt}/{total_fmt}', colour='cyan') as pbar:
                    response = self.session.get(target_url, timeout=self.timeout, stream=True)
                    response.raise_for_status()
                    pbar.update(1)
                    return response.text
            else:
                response = self.session.get(target_url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
        except requests.RequestException as e:
            logger.error(f"Erro ao buscar página {target_url}: {e}")
            return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Converte HTML em objeto BeautifulSoup para parsing
        
        Args:
            html_content: String contendo HTML
            
        Returns:
            Objeto BeautifulSoup parseado
        """
        return BeautifulSoup(html_content, 'lxml')
    
    def extract_news(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extrai notícias do conteúdo HTML
        Deve ser sobrescrito por subclasses específicas
        
        Args:
            html_content: Conteúdo HTML da página
            
        Returns:
            Lista de dicionários com dados das notícias
        """
        raise NotImplementedError("Subclasses devem implementar extract_news")
    
    def scrape(self) -> List[Dict[str, str]]:
        """
        Executa o processo completo de scraping
        
        Returns:
            Lista de notícias extraídas
        """
        html_content = self.fetch_page()
        if not html_content:
            return []
        
        news_items = self.extract_news(html_content)
        
        # Adiciona timestamp de coleta
        timestamp = datetime.now().isoformat()
        for item in news_items:
            item['collected_at'] = timestamp
        
        return news_items


class HackerNewsScraper(NewsScraper):
    """Scraper específico para Hacker News"""
    
    def __init__(self):
        super().__init__('https://news.ycombinator.com')
    
    def extract_news(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extrai notícias do Hacker News
        
        Args:
            html_content: HTML da página do Hacker News
            
        Returns:
            Lista de notícias com título e link
        """
        soup = self.parse_html(html_content)
        news_items = []
        
        # Busca elementos com classe 'athing' que contêm as notícias
        stories = soup.find_all('tr', class_='athing')
        
        # Processa notícias com barra de progresso
        stories_to_process = stories[:30]  # Limita a 30 notícias
        
        with tqdm(total=len(stories_to_process), desc="Extraindo notícias", 
                  bar_format='{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}]',
                  colour='green') as pbar:
            for story in stories_to_process:
                try:
                    title_cell = story.find('span', class_='titleline')
                    if title_cell:
                        link_elem = title_cell.find('a')
                        if link_elem:
                            title = link_elem.get_text(strip=True)
                            href = link_elem.get('href', '')
                            
                            # Trata links relativos
                            if href.startswith('item?'):
                                href = urljoin(self.base_url, href)
                            
                            news_items.append({
                                'title': title,
                                'link': href,
                                'source': 'Hacker News'
                            })
                except Exception as e:
                    logger.warning(f"Erro ao processar notícia: {e}")
                    continue
                finally:
                    pbar.update(1)
                    time.sleep(0.01)  # Pequeno delay para visualização
        
        return news_items


class BBCNewsScraper(NewsScraper):
    """Scraper específico para BBC News"""
    
    def __init__(self):
        super().__init__('https://www.bbc.com/news')
    
    def extract_news(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extrai notícias da BBC News
        
        Args:
            html_content: HTML da página da BBC
            
        Returns:
            Lista de notícias com título e link
        """
        soup = self.parse_html(html_content)
        news_items = []
        
        # Busca por diferentes padrões de manchetes na BBC
        headlines = soup.find_all('h2', {'data-testid': True})
        
        # Processa manchetes com progresso
        headlines_to_process = headlines[:30]
        
        if headlines_to_process:
            with tqdm(total=len(headlines_to_process), desc="Extraindo manchetes BBC",
                      bar_format='{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}]',
                      colour='green') as pbar:
                for headline in headlines_to_process:
                    try:
                        link = headline.find_parent('a')
                        if link:
                            title = headline.get_text(strip=True)
                            href = link.get('href', '')
                            
                            # Converte links relativos em absolutos
                            if href.startswith('/'):
                                href = f"https://www.bbc.com{href}"
                            
                            if title and href:
                                news_items.append({
                                    'title': title,
                                    'link': href,
                                    'source': 'BBC News'
                                })
                    except Exception as e:
                        logger.warning(f"Erro ao processar manchete BBC: {e}")
                        continue
                    finally:
                        pbar.update(1)
                        time.sleep(0.01)
        
        # Busca alternativa por artigos
        if not news_items:
            articles = soup.find_all('article')
            articles_to_process = articles[:30]
            with tqdm(total=len(articles_to_process), desc="Extraindo artigos BBC",
                      bar_format='{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}]',
                      colour='green') as pbar:
                for article in articles_to_process:
                    try:
                        h3 = article.find('h3')
                        if h3:
                            link = h3.find_parent('a') or article.find('a')
                            if link:
                                title = h3.get_text(strip=True)
                                href = link.get('href', '')
                                
                                if href.startswith('/'):
                                    href = f"https://www.bbc.com{href}"
                                
                                if title and href:
                                    news_items.append({
                                        'title': title,
                                        'link': href,
                                        'source': 'BBC News'
                                    })
                    except Exception as e:
                        logger.warning(f"Erro ao processar artigo BBC: {e}")
                        continue
                    finally:
                        pbar.update(1)
                        time.sleep(0.01)
        
        return news_items


class G1Scraper(NewsScraper):
    """Scraper específico para G1 (Portal Globo)"""
    
    def __init__(self):
        super().__init__('https://g1.globo.com')
    
    def extract_news(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extrai notícias do G1
        
        Args:
            html_content: HTML da página do G1
            
        Returns:
            Lista de notícias com título e link
        """
        soup = self.parse_html(html_content)
        news_items = []
        
        # Busca por posts e manchetes principais
        # G1 usa classes específicas para diferentes tipos de conteúdo
        selectors = [
            ('a.feed-post-link', None),  # Links de posts no feed
            ('div.bastian-page a', None),  # Links na página principal
            ('div.feed-post-body', 'a'),  # Posts no feed de notícias
            ('div._evt', 'a'),  # Elementos com eventos
            ('div.hui-premium', 'a'),  # Conteúdo premium
            ('h2', 'a'),  # Títulos em h2 com links
        ]
        
        all_articles = []
        
        # Coleta elementos usando diferentes seletores
        for selector, child_selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                if child_selector:
                    link_elem = elem.find(child_selector)
                else:
                    link_elem = elem if elem.name == 'a' else elem.find('a')
                
                if link_elem and link_elem not in all_articles:
                    all_articles.append(link_elem)
        
        # Remove duplicatas mantendo ordem
        seen_hrefs = set()
        unique_articles = []
        for article in all_articles:
            href = article.get('href', '')
            if href and href not in seen_hrefs:
                seen_hrefs.add(href)
                unique_articles.append(article)
        
        # Processa artigos únicos com progresso
        articles_to_process = unique_articles[:30]
        
        if articles_to_process:
            with tqdm(total=len(articles_to_process), desc="Extraindo notícias G1",
                      bar_format='{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}]',
                      colour='green') as pbar:
                for article in articles_to_process:
                    try:
                        # Extrai título - pode estar no texto do link ou em elemento filho
                        title = article.get_text(strip=True)
                        
                        # Se título muito curto, tenta pegar de elementos filhos
                        if len(title) < 10:
                            title_elem = article.find(['h2', 'h3', 'span', 'div'])
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                        
                        # Pega o link
                        href = article.get('href', '')
                        
                        # Garante que é um link válido do G1
                        if href and not href.startswith('http'):
                            if href.startswith('/'):
                                href = f"https://g1.globo.com{href}"
                            else:
                                href = f"https:{href}" if href.startswith('//') else ''
                        
                        # Filtra apenas links válidos de notícias
                        if (href and title and len(title) > 10 and 
                            ('globo.com' in href or 'g1.com' in href)):
                            news_items.append({
                                'title': title,
                                'link': href,
                                'source': 'G1'
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao processar notícia G1: {e}")
                        continue
                    finally:
                        pbar.update(1)
                        time.sleep(0.01)
        
        # Se não encontrou notícias, tenta busca mais genérica
        if not news_items:
            all_links = soup.find_all('a', href=True)[:50]
            
            with tqdm(total=len(all_links), desc="Busca alternativa G1",
                      bar_format='{l_bar}{bar:30}| {n_fmt}/{total_fmt}',
                      colour='yellow') as pbar:
                for link in all_links:
                    try:
                        title = link.get_text(strip=True)
                        href = link.get('href', '')
                        
                        if not href.startswith('http'):
                            if href.startswith('/'):
                                href = f"https://g1.globo.com{href}"
                        
                        # Filtra links válidos de notícias
                        if (title and len(title) > 20 and href and 
                            'globo.com' in href and 'noticia' in href.lower()):
                            news_items.append({
                                'title': title,
                                'link': href,
                                'source': 'G1'
                            })
                            
                            if len(news_items) >= 30:
                                break
                    except:
                        pass
                    finally:
                        pbar.update(1)
        
        return news_items


class FolhaScraper(NewsScraper):
    """Scraper específico para Folha de S.Paulo"""
    
    def __init__(self):
        super().__init__('https://www.folha.uol.com.br')
    
    def extract_news(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extrai notícias da Folha de S.Paulo
        
        Args:
            html_content: HTML da página da Folha
            
        Returns:
            Lista de notícias com título e link
        """
        soup = self.parse_html(html_content)
        news_items = []
        
        # Seletores específicos da Folha
        selectors = [
            'h2.c-headline__title a',  # Manchetes principais
            'h3.c-headline__title a',  # Manchetes secundárias
            'div.c-headline a',  # Links de manchetes
            'article a.c-headline__url',  # Artigos
            'div.u-list-unstyled a',  # Listas de notícias
            'a[href*="/2024/"], a[href*="/2025/"]'  # Links com padrão de data
        ]
        
        all_articles = []
        for selector in selectors:
            all_articles.extend(soup.select(selector))
        
        # Remove duplicatas
        seen = set()
        unique_articles = []
        for article in all_articles:
            href = article.get('href', '')
            if href and href not in seen:
                seen.add(href)
                unique_articles.append(article)
        
        articles_to_process = unique_articles[:30]
        
        if articles_to_process:
            with tqdm(total=len(articles_to_process), desc="Extraindo notícias Folha",
                      bar_format='{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}]',
                      colour='green') as pbar:
                for article in articles_to_process:
                    try:
                        title = article.get_text(strip=True)
                        href = article.get('href', '')
                        
                        # Ajusta URLs relativas
                        if href and not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        
                        if title and len(title) > 10 and href:
                            news_items.append({
                                'title': title,
                                'link': href,
                                'source': 'Folha de S.Paulo'
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao processar notícia Folha: {e}")
                        continue
                    finally:
                        pbar.update(1)
                        time.sleep(0.01)
        
        return news_items