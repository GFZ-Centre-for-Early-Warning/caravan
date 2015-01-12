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

1) make (or edit, should be already there) caravan.wsgi file, if needed (it should not be the case)
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

3) edit apache2.conf  
(e.g. via sudo gedit /etc/apache2/apache2.conf. NOTE: superuser rights needed!!)
the following lines:
	
	WSGIScriptAlias /caravan /var/www/html/caravan/caravan.wsgi
	<Directory /var/www/html/caravan/>
	Order allow,deny
	Allow from all
	</Directory> 
