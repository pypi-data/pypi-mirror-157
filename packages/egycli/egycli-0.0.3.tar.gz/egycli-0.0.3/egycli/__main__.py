from simple_term_menu import TerminalMenu
from multiprocessing import Process
from rich.console import Console
from rich.theme import Theme
from rich.text import Text
from time import sleep
from egybest import *

THEME = Theme(
    {
        "ok": "green bold",
        "error": "red bold",
        "prompt": "blue bold", 
        "loading": "yellow bold"
    }
)

egybest = EgyBest()
console = Console(theme=THEME)

class Spinner:
    def __init__(self, text):
        self.text = text
        self.__process = None

    def __spin(self):
        chars = "\-/|"
        bold = '\033[1m'
        yellow = '\033[93m'
        magenta = '\033[95m'
        end = '\033[0m'
        while True:
            for char in chars:
                print(bold + yellow + f"\r{self.text} {magenta}{char}" + end, end="")
                sleep(0.1)

    def start(self):
        process = Process(target=self.__spin, args=())
        process.start()
        self.__process = process
    
    def stop(self):
        if not self.__process:
            return
        self.__process.terminate()
        


def generate_info(page: BaseClassStructure) -> str:
    text = f"[bold]Title:[/] [blue]{page.title}[/]\n" \
           f"[bold]Link:[/] [blue]{page.link}[/]\n" \
           f"[bold]Rating[/]: [yellow]{page.rating}[/]⭐\n"
    return text

def prompt(text) -> str:
    console.print(text, style="prompt")
    return input("-> ")

def create_term_menu(options: list, title="select one of the following options: ") -> int:
        terminal_menu = TerminalMenu(options, title=title)
        return terminal_menu.show()

def generate_links(episode: Episode) -> str:
    spinner = Spinner("fetching download sources")
    spinner.start()
    downloads = episode.get_download_sources()
    spinner.stop()
    if not downloads:
        console.clear()
        console.print("failed to get download sources. please try again later", style="error")

    qualities = []

    for download in downloads:
        quality = str(download.quality) + "p"
        if quality in qualities:
            continue
        qualities.append(quality)

    selected_option_index = create_term_menu(qualities)
    link = downloads[selected_option_index].link
    return link

def main():
    console.clear()
    query = prompt("What would you like to search for?")
    if not query:
        console.print("error input given.", style="error")
        return

    spinner = Spinner(f"Looking for: {query}")
    spinner.start()
    results = egybest.search(query)
    spinner.stop()

    if not results:
        console.clear()
        return console.print(f"couldn't find any matches for: \"{query}\"", style="error")

    options = [f"{'Show' if isinstance(result, Show) else 'movie'} - {result.title}" for result in results]
    selected_option_index = create_term_menu(options)
    selected = results[selected_option_index]
    console.print(generate_info(selected))
    link = None

    if isinstance(selected, Show):
        selected = selected
        seasons = selected.get_seasons()
        options = [f"{selected.title} - Season {index+1}" for index, season in enumerate(seasons)]
        selected_option_index = create_term_menu(options)
        season = seasons[selected_option_index]

        episodes = season.get_episodes()
        options = [f"{selected.title} - Episode {index+1}" for index, episode in enumerate(episodes)]
        selected_option_index = create_term_menu(options)

        episode = episodes[selected_option_index]
        link = generate_links(episode)

    else:
        link = generate_links(selected)
        
    if not link:
        return
    
    console.print(f"[bold]Download[/]: [blue]{link}")

if __name__ == "__main__":
    main()