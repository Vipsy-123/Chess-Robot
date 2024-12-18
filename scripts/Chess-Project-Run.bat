@echo off

REM Run Extraction.py
echo Running Extraction.py...
python Extraction.py
echo Extraction completed.
timeout /t 10 /nobreak

REM Run Detection.py
echo Running Detection.py...
python Detection.py
echo Detection completed.
timeout /t 10 /nobreak

REM Run Localisation.py
echo Running Localisation.py...
python Localisation.py
echo Localisation completed.
timeout /t 10 /nobreak

REM Run Communication.py
echo Running Communication.py...
python Communication.py
echo Communication completed.
