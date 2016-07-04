New Site Provisioning
=====================

## required packages

* nginx
* Python
* pyenv
* Git

Example of Excute in UBUNTU

sudo apt-get install nginx git
https://github.com/yyuu/pyenv


## Nginx virtual host config

* Reference : nginx.template.conf
* Replace SITENAME parts like this : staging.my-domain.com


## Upstart Job

* Reference : gunicorn-upstart.template.conf
* Replace SITENAME parts like this : staging.my-domain.com
