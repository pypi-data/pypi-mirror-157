# Django Find My Device

![django-fmd @ PyPi](https://img.shields.io/pypi/v/django-fmd?label=django-fmd%20%40%20PyPi)
![Python Versions](https://img.shields.io/pypi/pyversions/django-fmd)
![License GPL V3+](https://img.shields.io/pypi/l/django-fmd)

Find My Device Server implemented in Python using Django.
Usable for the Andorid App: https://gitlab.com/Nulide/findmydevice

Plan is to make is usable and create a [YunoHost package](https://gitlab.com/Nulide/findmydeviceserver/-/issues/9) for it.

## State

It's in early developing stage and not really usable ;)

What worked (a little bit) with Django's development server:

* App can register the device
* App can send a new location
* App can delete all server data from the device
* The Web page can fetch the location of a device

TODOs:

* Paginate between locations in Web page
* Commands/Push/Pictures
* Write tests, setup CI, deploy python package etc.


## Start hacking:

```bash
~$ git clone https://gitlab.com/jedie/django-find-my-device.git
~$ cd django-find-my-device
~/django-find-my-device$ ./devshell.py
...
(findmydevice) run_testserver
```

## versions

* [*dev*](https://gitlab.com/jedie/django-find-my-device/-/compare/11d09ecb...main)
  * TBD v0.0.1
