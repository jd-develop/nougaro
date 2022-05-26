@echo off
pause

rem We update pip and nuitka
python -m pip install --upgrade pip nuitka

rem We delete useless files and directories
for %%y in (.\.gitignore, .\.gitattributes, example_file, grammar.txt, tests.noug, todo.md) do if exist %%y (del %%y)

for %%y in (.\.git, .\.github, .\.vscode, .\.idea, .\__pycache__, src\__pycache__, src\values\__pycache__, src\values\functions\__pycache__, src\values\specific_values\__pycache__, lib_\__pycache__, sandbox) do if exist %%y (rmdir /s /q %%y)

rem Then we ask for the version
set /p NOUGVERSION="Nougaro version: "

rem We build
python -m nuitka --standalone --windows-company-name=Nougaro --windows-product-name=Nougaro --windows-product-version=%NOUGVERSION% shell.py

rem We copy the important files to the created directory
for %%y in (example.noug "highlight theme for NPP.xml" LICENSE noug_version.json README.md shell.py) do xcopy %%y shell.dist\

for %%y in (examples lib_ src) do xcopy /s /i %%y shell.dist\%%y

rem Then we rename our directory
RENAME shell.dist nougaro-"%NOUGVERSION%"-alpha-windows-exe
