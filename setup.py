import sys
from cx_Freeze import setup, Executable

# Dependências automáticas
build_exe_options = {
    "packages": ["os", "flet"],  # coloque aqui pacotes extras que você usa
    "include_files": [
        ("assets", "assets"),       # inclui a pasta de assets inteira
        ("database", "database"),   # inclui a pasta database
        ("screens", "screens"),     # inclui as telas
        ("storage", "storage"),     # inclui storage
        ("utils", "utils"),         # inclui utils
        "requirements.txt",         # inclui o requirements
        "README.md",                # inclui o readme
    ],
    "excludes": ["tkinter"],  # se não usa tkinter, exclui
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # evita abrir console junto com o app

setup(
    name="NuvigApp",
    version="1.0",
    author="Rafael Costa",
    description="Aplicativo de gestão NUViG",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            script="main.py",
            base=base,
            target_name="nuvig.exe",
            icon="assets/icons/nuvig.ico"
        )
    ]
)
