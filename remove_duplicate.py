import os
from pathlib import Path

import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def browse_directory():
    current = Path.cwd()

    while True:
        console.clear()

        console.print(
            Panel(
                f"[bold cyan]Current Directory[/bold cyan]\n{current}",
                title="File Renamer",
            )
        )

        folders = sorted(
            [p for p in current.iterdir() if p.is_dir()], key=lambda x: x.name.lower()
        )

        choices = []

        if current.parent != current:
            choices.append("⬆ Go Back")

        for folder in folders:
            choices.append(f"📁 {folder.name}")

        choices.append("✅ Select This Folder")
        choices.append("❌ Exit")

        choice = questionary.select("Choose an option:", choices=choices).ask()

        if choice == "⬆ Go Back":
            current = current.parent

        elif choice == "✅ Select This Folder":
            return current

        elif choice == "❌ Exit":
            raise SystemExit

        else:
            folder_name = choice.replace("📁 ", "")
            current = current / folder_name


def get_files(folder):
    return sorted(
        [f for f in folder.iterdir() if f.is_file()], key=lambda x: x.name.lower()
    )


def preview_renames(files, base_name, start_num, padding):
    table = Table(title="Rename Preview")

    table.add_column("Current Name")
    table.add_column("New Name")

    rename_map = []

    number = start_num

    for file in files:
        new_name = f"{base_name}_" f"{str(number).zfill(padding)}" f"{file.suffix}"

        rename_map.append((file, new_name))

        table.add_row(file.name, new_name)

        number += 1

    console.print(table)

    return rename_map


def rename_files(rename_map):
    renamed = 0

    for old_file, new_name in rename_map:
        new_path = old_file.parent / new_name

        old_file.rename(new_path)

        renamed += 1

    return renamed


def main():
    console.clear()

    console.print(Panel.fit("[bold green]Interactive File Renamer[/bold green]"))

    folder = browse_directory()

    files = get_files(folder)

    if not files:
        console.print("\n[red]No files found in selected folder.[/red]")
        return

    console.print(f"\n[green]{len(files)} files found.[/green]")

    rename_mode = questionary.select(
        "Rename which files?",
        choices=["All Files", "Images Only", "Videos Only", "Audio Only"],
    ).ask()

    image_ext = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    video_ext = {".mp4", ".mov", ".avi", ".mkv"}
    audio_ext = {".mp3", ".wav", ".aac", ".m4a"}

    if rename_mode == "Images Only":
        files = [f for f in files if f.suffix.lower() in image_ext]

    elif rename_mode == "Videos Only":
        files = [f for f in files if f.suffix.lower() in video_ext]

    elif rename_mode == "Audio Only":
        files = [f for f in files if f.suffix.lower() in audio_ext]

    if not files:
        console.print("[red]No matching files found.[/red]")
        return

    base_name = questionary.text("Enter base filename:", default="File").ask()

    start_num = int(questionary.text("Starting number:", default="1").ask())

    padding = int(questionary.text("Number padding:", default="3").ask())

    console.print("\n")

    rename_map = preview_renames(files, base_name, start_num, padding)

    proceed = questionary.confirm("Apply these changes?").ask()

    if not proceed:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
        return

    count = rename_files(rename_map)

    console.print(
        Panel.fit(f"[bold green]✓ Success![/bold green]\n\n" f"Renamed {count} files.")
    )


if __name__ == "__main__":
    main()
