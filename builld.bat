@echo off
pause
del .\.gitignore
del .\.gitattributes
del example_file
del grammar.txt
del tests.noug
del todo.md
rmdir /s /q .\.github
rmdir /s /q .\.vscode
rmdir /s /q .\.idea
set /p NOUGVERSION="Nougaro version: "
python -m nuitka --standalone --windows-product-name=Nougaro --windows-product-version=%NOUGVERSION% shell.py
