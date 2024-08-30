@echo off
rem Nougaro : a python-interpreted high-level programming language
rem Copyright (C) 2021-2024  Jean Dubois (https://github.com/jd-develop) jd-dev@laposte.net

rem You should have received a copy of the GNU General Public License
rem along with this program.  If not, see https://www.gnu.org/licenses/.

rem This file is used to build Nougaro for Windows using Nuitka (requires pip and python dir in environnement variables)

echo WARNING: please execute this script ONLY in a safe environnement, like in a sandbox directory.
echo WARNING: this script may use Internet connection, and having an Internet connection is recommended. However, you can execute the script without any Internet connection.
echo You can exit this script safely without building anything by pressing CTRL+C or by closing this window :)
pause

echo The following Python version will be used:
python --version
echo Please make sure that you use a Python version supported by Nougaro AND Nuitka
echo Moreover, you will need Windows 10 or any later version to run this script.
echo You can stop this script now if you want.
pause

rem We update pip and nuitka
rem We use ordered-set to have a bast compilation time
python -m pip install --upgrade pip nuitka wheel ordered-set colorama

rem We delete useless files and directories
for %%y in (.\.gitignore, .\.gitattributes, example_file, grammar.txt, tests.noug, todo.md) do if exist %%y (del %%y)

for %%y in (.\.git, .\.github, .\.vscode, .\.idea, .\__pycache__, src\__pycache__, src\errors\__pycache__, src\lexer\__pycache__, src\parser\__pycache__, src\runtime\__pycache__, src\runtime\values\__pycache__, src\runtime\values\basevalues\__pycache__, src\runtime\values\functions\__pycache__, lib_\runtime\values\tools\__pycache__, sandbox) do if exist %%y (rmdir /s /q %%y)

rem Then we fetch the version
python shell.py -d "import noug_version; noug_version.clean_version_for_nuitka_under_windows(1, 0)" > tempversionnuitka.txt
python shell.py -V > tempfullversion.txt
set /p NOUGVERSIONNUITKA=<tempversionnuitka.txt
set /p NOUGVERSION=<tempfullversion.txt

echo Nougaro version: %NOUGVERSION%
echo Nougaro version for Nuitka: %NOUGVERSIONNUITKA%

rem We build
python -m nuitka --standalone --windows-company-name=Nougaro --windows-product-name=Nougaro --windows-product-version=%NOUGVERSIONNUITKA% --include-package=lib_ --no-deployment-flag=self-execution shell.py

rem We copy the important files to the created directory
echo "Copying files…"
for %%y in (example.noug LICENSE README.md README.fr.md shell.py "CODE_OF_CONDUCT.md" CONTRIBUTING.md how_it_works.md noug_version.json CHANGELOG.md) do xcopy %%y shell.dist\

echo "Copying directories…"
for %%y in (examples lib_ src tests repo-image) do xcopy /s /i %%y shell.dist\%%y

rem We delete __pycache__
echo "Removing bloat…"
cd "shell.dist"
for %%y in (.\__pycache__, src\__pycache__, src\errors\__pycache__, src\lexer\__pycache__, src\parser\__pycache__, src\runtime\__pycache__, src\runtime\values\__pycache__, src\runtime\values\basevalues\__pycache__, src\runtime\values\functions\__pycache__, lib_\runtime\values\tools\__pycache__) do if exist %%y (rmdir /s /q %%y)
cd ..

rem Then we rename our directory
echo "Renaming and compressing…"
RENAME shell.dist nougaro-"%NOUGVERSION%"-windows-exe

rem Finally, we compress the output directory to a .zip file
rem Note: Windows 10 cames with tar
tar -a -c -f nougaro-"%NOUGVERSION%"-windows-exe.zip nougaro-"%NOUGVERSION%"-windows-exe

