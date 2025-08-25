"""
Módulo de progresso e indicadores visuais
"""

from tqdm import tqdm
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import print as rprint
import time
from typing import Optional, List, Dict
from colorama import init, Fore, Style

# Inicializa colorama para cores no terminal Windows
init(autoreset=True)

console = Console()


class ProgressIndicator:
    """Classe para gerenciar indicadores de progresso"""
    
    def __init__(self):
        self.console = Console()
        self.current_task = None
        self.progress = None
    
    def create_progress_bar(self, total: int, description: str = "Processando", 
                           color: str = "cyan", leave: bool = True) -> tqdm:
        """
        Cria uma barra de progresso simples usando tqdm
        
        Args:
            total: Total de itens a processar
            description: Descrição da tarefa
            color: Cor da barra
            leave: Se deve manter a barra após conclusão
        
        Returns:
            Objeto tqdm para atualização
        """
        return tqdm(
            total=total,
            desc=description,
            bar_format=f'{{l_bar}}{{bar:30}}| {{n_fmt}}/{{total_fmt}} [{{elapsed}}<{{remaining}}]',
            colour=color,
            leave=leave,
            ncols=100
        )
    
    def create_rich_progress(self) -> Progress:
        """
        Cria um indicador de progresso rico com múltiplas colunas
        
        Returns:
            Objeto Progress do Rich
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self.console,
            expand=False
        )
    
    def show_status(self, message: str, status: str = "info"):
        """
        Mostra uma mensagem de status com formatação
        
        Args:
            message: Mensagem a exibir
            status: Tipo de status (info, success, warning, error)
        """
        colors = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red"
        }
        
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        color = colors.get(status, "white")
        icon = icons.get(status, "")
        
        self.console.print(f"{icon} [{color}]{message}[/{color}]")
    
    def show_spinner(self, message: str, task_function, *args, **kwargs):
        """
        Mostra um spinner enquanto executa uma tarefa
        
        Args:
            message: Mensagem a exibir
            task_function: Função a executar
            *args, **kwargs: Argumentos para a função
        
        Returns:
            Resultado da função executada
        """
        with self.console.status(f"[bold green]{message}...", spinner="dots") as status:
            result = task_function(*args, **kwargs)
            return result
    
    def create_table(self, title: str, headers: List[str], rows: List[List]) -> Table:
        """
        Cria uma tabela formatada
        
        Args:
            title: Título da tabela
            headers: Cabeçalhos das colunas
            rows: Linhas de dados
        
        Returns:
            Objeto Table do Rich
        """
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        for header in headers:
            table.add_column(header, style="cyan")
        
        for row in rows:
            table.add_row(*[str(item) for item in row])
        
        return table
    
    def show_panel(self, content: str, title: str = "", border_style: str = "blue"):
        """
        Mostra conteúdo em um painel
        
        Args:
            content: Conteúdo a exibir
            title: Título do painel
            border_style: Estilo da borda
        """
        panel = Panel(content, title=title, border_style=border_style, expand=False)
        self.console.print(panel)
    
    def print_step(self, step_number: int, total_steps: int, description: str):
        """
        Imprime um passo do processo com formatação
        
        Args:
            step_number: Número do passo atual
            total_steps: Total de passos
            description: Descrição do passo
        """
        percentage = (step_number / total_steps) * 100
        bar_length = 20
        filled = int(bar_length * step_number / total_steps)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        self.console.print(
            f"\n[bold cyan]Passo {step_number}/{total_steps}[/bold cyan] "
            f"[green]{bar}[/green] {percentage:.0f}% - {description}"
        )
    
    def animate_text(self, text: str, delay: float = 0.03):
        """
        Anima texto caractere por caractere
        
        Args:
            text: Texto a animar
            delay: Delay entre caracteres
        """
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()


class TaskTracker:
    """Rastreador de tarefas com progresso detalhado"""
    
    def __init__(self):
        self.tasks = {}
        self.console = Console()
        
    def add_task(self, task_id: str, description: str, total: int):
        """
        Adiciona uma nova tarefa para rastrear
        
        Args:
            task_id: ID único da tarefa
            description: Descrição da tarefa
            total: Total de itens na tarefa
        """
        self.tasks[task_id] = {
            'description': description,
            'total': total,
            'completed': 0,
            'status': 'pending',
            'start_time': time.time()
        }
    
    def update_task(self, task_id: str, increment: int = 1):
        """
        Atualiza o progresso de uma tarefa
        
        Args:
            task_id: ID da tarefa
            increment: Quantidade a incrementar
        """
        if task_id in self.tasks:
            self.tasks[task_id]['completed'] += increment
            if self.tasks[task_id]['completed'] >= self.tasks[task_id]['total']:
                self.tasks[task_id]['status'] = 'completed'
            else:
                self.tasks[task_id]['status'] = 'in_progress'
    
    def complete_task(self, task_id: str):
        """
        Marca uma tarefa como completa
        
        Args:
            task_id: ID da tarefa
        """
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['completed'] = self.tasks[task_id]['total']
            self.tasks[task_id]['end_time'] = time.time()
    
    def fail_task(self, task_id: str, error: str = None):
        """
        Marca uma tarefa como falhada
        
        Args:
            task_id: ID da tarefa
            error: Mensagem de erro opcional
        """
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'failed'
            self.tasks[task_id]['error'] = error
            self.tasks[task_id]['end_time'] = time.time()
    
    def get_summary(self) -> Dict:
        """
        Obtém resumo de todas as tarefas
        
        Returns:
            Dicionário com resumo das tarefas
        """
        summary = {
            'total': len(self.tasks),
            'completed': sum(1 for t in self.tasks.values() if t['status'] == 'completed'),
            'in_progress': sum(1 for t in self.tasks.values() if t['status'] == 'in_progress'),
            'failed': sum(1 for t in self.tasks.values() if t['status'] == 'failed'),
            'pending': sum(1 for t in self.tasks.values() if t['status'] == 'pending')
        }
        return summary
    
    def display_summary(self):
        """Exibe um resumo visual das tarefas"""
        summary = self.get_summary()
        
        table = Table(title="📊 Resumo de Tarefas", show_header=True, header_style="bold magenta")
        table.add_column("Status", style="cyan", width=15)
        table.add_column("Quantidade", justify="right", style="green")
        table.add_column("Porcentagem", justify="right", style="yellow")
        
        for status, count in [
            ("✅ Completas", summary['completed']),
            ("🔄 Em Progresso", summary['in_progress']),
            ("❌ Falhadas", summary['failed']),
            ("⏳ Pendentes", summary['pending'])
        ]:
            percentage = (count / summary['total'] * 100) if summary['total'] > 0 else 0
            table.add_row(status, str(count), f"{percentage:.1f}%")
        
        table.add_row("", "", "", style="dim")
        table.add_row("Total", str(summary['total']), "100%", style="bold")
        
        self.console.print(table)


def create_ascii_banner(text: str) -> str:
    """
    Cria um banner ASCII simples
    
    Args:
        text: Texto do banner
    
    Returns:
        Banner formatado
    """
    border = "=" * (len(text) + 4)
    return f"""
{border}
  {text}
{border}
"""


def show_welcome_message():
    """Mostra mensagem de boas-vindas com formatação"""
    console = Console()
    
    welcome_text = """
╔════════════════════════════════════════════════╗
║     🌐 Sistema de Scraping de Notícias 🌐      ║
║                                                ║
║         Coleta • Processa • Analisa           ║
╚════════════════════════════════════════════════╝
"""
    
    console.print(welcome_text, style="bold blue")


def show_completion_message(stats: Dict):
    """
    Mostra mensagem de conclusão com estatísticas
    
    Args:
        stats: Dicionário com estatísticas da execução
    """
    console = Console()
    
    panel_content = f"""
[bold green]✨ Pipeline Concluído com Sucesso![/bold green]

📰 Notícias Coletadas: [cyan]{stats.get('news_count', 0)}[/cyan]
📝 Palavras Processadas: [cyan]{stats.get('words_processed', 0)}[/cyan]
💾 Arquivos Salvos: [cyan]{stats.get('files_saved', 0)}[/cyan]
⏱️ Tempo Total: [cyan]{stats.get('execution_time', '0s')}[/cyan]
"""
    
    console.print(Panel(panel_content, title="📊 Resultados", border_style="green"))


# Funções auxiliares para uso rápido
def simple_progress(items, description="Processando"):
    """
    Wrapper simples para tqdm com formatação padrão
    
    Args:
        items: Itens a processar
        description: Descrição da tarefa
    
    Yields:
        Item processado
    """
    for item in tqdm(items, desc=description, colour='green', ncols=100):
        yield item


def print_colored(text: str, color: str = "white"):
    """
    Imprime texto colorido
    
    Args:
        text: Texto a imprimir
        color: Cor do texto
    """
    colors = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE
    }
    
    color_code = colors.get(color.lower(), Fore.WHITE)
    print(f"{color_code}{text}{Style.RESET_ALL}")