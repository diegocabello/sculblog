# Sculblog

Full documentation is availale at [https://sculblog.org](https://sculblog.org). 

The best blogging framework for the internet!

Licensed under MIT License. Techologic license is parody. 

## Supported Operation Systems

- Debian 12 (HVM)

More operating systems will be supported later. 

## Installation 

From a fresh virtual instance:


1. Install your server of choice (apache2, nginx) with `sudo apt install apache2` or `sudo apt install nginx`
2. Change to the folder the files will be served from 
    - Apache: `cd /var/www/html`
    - Nginx: `cd /usr/share/nginx/html`
3. Run `sudo apt install git` to install git
4. Run `git clone https://github.com/diegocabello/sculblog.git` to clone the repo into the serving folder
    - Later the repo will also hosted on sculblog.org
5. Run `source setup.sh` to install remaining dependancies
