@echo off
rem Nougaro : a python-interpreted high-level programming language
rem Copyright (C) 2021-2023  Jean Dubois (https://github.com/jd-develop) jd-dev@laposte.net
rem
rem This program is free software: you can redistribute it and/or modify
rem it under the terms of the GNU General Public License as published by
rem the Free Software Foundation, either version 3 of the License, or
rem (at your option) any later version.
rem
rem This program is distributed in the hope that it will be useful,
rem but WITHOUT ANY WARRANTY; without even the implied warranty of
rem MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
rem GNU General Public License for more details.
rem
rem You should have received a copy of the GNU General Public License
rem along with this program.  If not, see https://www.gnu.org/licenses/.

rem This file is used for build Nougaro for Windows using Nuitka (requires pip and python dir in environnement variables)

echo WARNING: please execute this script ONLY in a safe environnement, like in a sandbox directory.
echo WARNING: this script may use Internet connection, and having an Internet connection is recommended. However, you can execute the script without any Internet connection.
echo You can exit this script safely without building anything by pressing CTRL+C or by closing this window :)
pause

rem We update pip and nuitka
rem We use ordered-set to have a bast compilation time
python -m pip install --upgrade pip nuitka wheel ordered-set colorama

rem We delete useless files and directories
for %%y in (.\.gitignore, .\.gitattributes, example_file, grammar.txt, tests.noug, todo.md) do if exist %%y (del %%y)

for %%y in (.\.git, .\.github, .\.vscode, .\.idea, .\__pycache__, src\__pycache__, src\values\__pycache__, src\values\functions\__pycache__, src\values\specific_values\__pycache__, lib_\__pycache__, sandbox) do if exist %%y (rmdir /s /q %%y)

rem Then we ask for the version
set /p NOUGVERSION="Nougaro version: "
set /p NOUGPHASE="Phase: ""

rem We build
python -m nuitka --standalone --windows-company-name=Nougaro --windows-product-name=Nougaro --windows-product-version=%NOUGVERSION% --include-package=lib_ shell.py

rem We copy the important files to the created directory
for %%y in (example.noug "highlight theme for NPP.xml" LICENSE noug_version.json README.md shell.py "CODE_OF_CONDUCT.md" how_it_works.md test_file.noug) do xcopy %%y shell.dist\

for %%y in (examples lib_ src config) do xcopy /s /i %%y shell.dist\%%y

rem Then we rename our directory
RENAME shell.dist nougaro-"%NOUGVERSION%"-%NOUGPHASE%-windows-exe
