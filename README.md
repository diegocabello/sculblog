# Sculblog

Full documentation is available at [https://sculblog.org](https://sculblog.org). 

*The best blogging framework for the internet!*

Licensed under MIT License. Techologic license is parody. 

## Supported Operating Systems

- Debian 12 (HVM)

More operating systems will be supported later. 

## Installation 

From a fresh virtual instance:

1. Run `sudo apt install git` to install git
2. Install your server of choice (apache2, nginx) with `sudo apt install apache2` or `sudo apt install nginx`
3. Go to a directory you can put temp install files (eg. `cd ~/Downloads`)
4. Run `git clone https://github.com/diegocabello/sculblog.git` to clone the repo 
    - Later the repo will also hosted on sculblog.org
5. Run `sudo source setup.sh` in the temp install directory to build Sculblog and install remaining dependancies
    - PHP, sqlite3, python3, rust
    - Rust will build sculblog from source 
    - Your server choice (apache, nginx) will be automatically detected and required files will be extracted to the server folder (`/var/www/html`, `/usr/share/nginx/html`)
    - Temp installation files can be removed after successful installation
