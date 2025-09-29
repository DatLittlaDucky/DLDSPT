# phone

import rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
console = Console()

def messages():
    console.print(Panel(Text("Candy 19e Messages", style="bold green"), title="Messages"))
    
    table = Table(title="Candy 19e Messages Menu")
    table.add_column("Option", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    table.add_row("[bold blue]1[/bold blue]", "[bold green]Send Message[/bold green]")
    table.add_row("[bold blue]2[/bold blue]", "[bold green]View Inbox[/bold green]")
    table.add_row("[bold blue]3[/bold blue]", "[bold green]Exit Messages[/bold green]")

    console.print(table)

    choice = input("Select an option: ")
    
    if choice == "1":
        console.print("Sending a message...")
        console.print("[bold green]Message sent successfully![/bold green]")
        messages()
    elif choice == "2":
        console.print("Viewing inbox...")
        console.print("[bold green]Inbox is empty![/bold green]")
        messages()
    elif choice == "3":
        console.print("Exiting Messages...")
        Phone()
    else:
        console.print("[red]Invalid option![/red]")
        messages()

def contacts():
    console.print("[bold red] Contacts dont exist yet![/bold red]")
    Main_Menu()

def settings():
    console.print(Panel(Text("Candy 19e Settings", style="bold green"), title="Settings"))
    
    table = Table(title="Candy 19e Settings Menu")
    table.add_column("Option", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    table.add_row("[bold blue]1[/bold blue]", "[bold green]Change Wallpaper[/bold green]")
    table.add_row("[bold blue]2[/bold blue]", "[bold green]Adjust Volume[/bold green]")
    table.add_row("[bold blue]3[/bold blue]", "[bold green]Exit Settings[/bold green]")

    console.print(table)

    choice = input("Select an option: ")
    
    if choice == "1":
        console.print("Changing wallpaper...")
        console.print("[bold green]Wallpaper changed successfully![/bold green]")
        settings()
    elif choice == "2":
        console.print("Adjusting volume...")
        console.print("[bold green]Volume adjusted successfully![/bold green]")
        settings()
    elif choice == "3":
        console.print("Exiting Settings...")
        Phone()
    else:
        console.print("[red]Invalid option![/red]")
        settings()

def Phone():
    console.print(Panel(Text("Candy 19e Phone", style="bold green"), title="Phone"))
    
    table = Table(title="Candy 19e Phone Menu")
    table.add_column("Option", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    table.add_row("[bold blue]1[/bold blue]", "[bold green]Open Messages[/bold green]")
    table.add_row("[bold blue]2[/bold blue]", "[bold green]Open Contacts[/bold green]")
    table.add_row("[bold blue]3[/bold blue]", "[bold green]Open Settings[/bold green]")
    table.add_row("[bold blue]4[/bold blue]", "[bold green]Exit Phone[/bold green]")

    console.print(table)

    choice = input("Select an option: ")
    
    if choice == "1":
        console.print("Opening Messages...")
        messages()
    elif choice == "2":
        console.print("Opening Contacts...")
        contacts()
    elif choice == "3":
        console.print("Opening Settings...")
        settings()
    elif choice == "4":
        console.print("Exiting Phone...")
        Main_Menu()
    else:
        console.print("[red]Invalid option![/red]")

def Main_Menu():
    console.print(Text("Welcome to the life 9 Menu", style="bold green"))

    console.print("[bold blue]1.[/bold blue] [bold green]Open Candy 19e Phone[/bold green]")

    choice = input("Select an option: ")
    if choice == "1":
        Phone()
    else:
        console.print("[red]Invalid option![/red]")
        Main_Menu()

Main_Menu()