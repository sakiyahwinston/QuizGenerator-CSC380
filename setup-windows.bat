@echo off

set "python_path=%LOCALAPPDATA%\Microsoft\WindowsApps\python3.11.exe"

if exist "%python_path%" (
	if exist "venv" (
		echo Virtual environment found
	) else (
	echo Creating virtual environment...
		python3.11 -m venv venv
		echo Virtual environment created
	)
	call venv\Scripts\activate
	echo installing packages...
	pip3 install customtkinter openai dotenv
	echo Finished!
) else (
    echo Python 3.11 is not installed. Please install it via the Microsoft Store.
)
pause