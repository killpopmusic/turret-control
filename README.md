# RC Airsoft Sentry Turret 

## Overview 
This is a repository containing control scripts for an autonomous turret project. 

## Dependencies


## Raspberry PI setup
The fisrt version of the project was meant to run entirely on Raspberry Pi 4b. Below presented is the proper connection scheme, which will enable the work of default control scripts.


## Software setup
1. Generalnie na początek trzeba wpiąć kamerkę i sprawdzić czy system ją widzi. Dobry check to komenda 'rpicam-still'. Może być potrzeba uruchomienia ręcznego kamery (ale raczej nie): 

**sudo raspi-config -> interfacing options -> yes**.

2. Potrzebna jest biblioteka **libcamera**, która powinna być z automatu zainstalowana na Raspbianie. Jeśli nie ma to troche lipa. Druga to **picamera2** - pythonowa wtyczka do c++'owego API do obsługi kamerki. Jak nie ma to:

```sudo apt install python3-libcamera``` 

```sudo apt install python3-picamera2```

3. Teraz jeszcze zostało do zainstalowania OpenCV. Najlepiej to zrobić w środowisku wirtualnym, żeby sobie czegoś nie zepsuć, także uprzednio instalujemy:

```pip install virtualenv```

tworzymy virtual environment:

```virtualenv env --system-site-packages```

Teraz mamy katalog o nazwie env, który bedzie zawierał potrzebne paczki (a w zasadzie jedną w tym przypadku) ale ma też dostęp do kamerki i bibliotek ją obsługujących, które są na zewnątrz.
Wchodzimy do środka:

```source env/bin/activate```

i robimy instalacje:

```pip install opencv-python-headless```
