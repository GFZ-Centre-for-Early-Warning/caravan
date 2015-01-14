INSTALLATION INSTRUCTIONS (TESTED ON UBUNTU 12.04 LTS)

We assume python and apache are already installed (browse the internet in case, 
it's straighforward)

REQUIRED PYTHON LIBRARIES INSTALLATION

#install psycopg2
sudo apt-get install python-psycopg2

#install mcerp. NEEDS TO HAVE pip, scipy, numpy and matplotlib INSTALLED! (see below)
sudo pip install mcerp

#Does it works? no? is pip installed?
sudo apt-get install python-pip
#(and retype pip install mcerp) afterwards

#Does it works? no? is scipy numpy and matplotlob installed? 
#eg. it shows an error like import scipy.stats
sudo apt-get install python-numpy python-scipy python-matplotlib
#(and re-type pip install mcerp)


SIMPLE README TESTED ON UBUNTU 14.04 with apache and mod_wsgi installed

1) make (or edit, should be already in this directory) caravan.wsgi file, if needed (it should not be the case)
see https://code.google.com/p/modwsgi/wiki/QuickConfigurationGuide

2) control to have installed mod_wsgi in apache. Type in terminal: 
	ll /etc/apache2/mods-enabled/
You should see the following two links:
	wsgi.conf -> ../mods-available/wsgi.conf
	wsgi.load -> ../mods-available/wsgi.load
If not, then do:
		sudo a2enmod wsgi
	and you can restart apache with:
		sudo service apache2 stop
		sudo service apache2 start
Check again if you see the two links above

3) Create a file /etc/apache2/conf-available/caravan.conf  
(NOTE: superuser rights needed!!)
Add the following lines:
	
	WSGIScriptAlias /caravan /var/www/html/caravan/caravan.wsgi
    WSGIApplicationGroup %{GLOBAL}
	<Directory /var/www/html/caravan/>
	Order allow,deny
	Allow from all
	</Directory> 

Note that the second line (application group) is ESSENTIAL and its absence caused 
many bugs resolved with the aid of peter evans and Javier Pastore

4) Make a link in /etc/apache2/conf-enabled/caravan.conf pointing to
the newly created file in conf-available 

$) change ownership to files:
    sudo chown -R www-data.www-data /var/www/html/caravan