@echo off
pause
python -m pip install --upgrade pip nuitka
del .\.gitignore
del .\.gitattributes
del example_file
del grammar.txt
del tests.noug
del todo.md
rmdir /s /q .\.git
rmdir /s /q .\.github
rmdir /s /q .\.vscode
rmdir /s /q .\.idea
rmdir /s /q .\__pycache__
rmdir /s /q src\__pycache__
rmdir /s /q src\values\__pycache__
rmdir /s /q src\values\functions\__pycache__
rmdir /s /q src\values\specific_values\__pycache__
rmdir /s /q lib_\__pycache__
set /p NOUGVERSION="Nougaro version: "
python -m nuitka --standalone --windows-company-name=Nougaro --windows-product-name=Nougaro --windows-product-version=%NOUGVERSION% shell.py
