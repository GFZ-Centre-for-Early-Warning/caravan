INSTALLATION INSTRUCTIONS (TESTED ON UBUNTU 14.04 LTS WITH APACHE 2.4.7)
KNOWN UNRESOLVED ISSUES IN lhotse21 (Ubuntu 12.04.5 LTS with Apache/2.2.22)

We assume python and apache are already installed (browse the internet in case, 
it's straighforward)

--------------------------------------
REQUIRED PYTHON LIBRARIES INSTALLATION
--------------------------------------

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

#check if lxml is installed (see at the bottom, it wasn't in lhotse21)

--------------------------------------
WEB APP APACHE INSTALLATION
--------------------------------------

1) Edit, IF NEEDED, caravan.wsgi file:
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

PS: no mod-wsgi installed? then:
    sudo apt-get install libapache2-mod-wsgi

3) Create a file /etc/apache2/conf-available/caravan.conf  
or /etc/apache2/conf.d/caravan.conf (depending on apache distribution)

(NOTE: superuser rights needed!!)
Add the following lines:
	
	WSGIScriptAlias /caravan /var/www/html/caravan/caravan.wsgi
    WSGIApplicationGroup %{GLOBAL}
	<Directory /var/www/html/caravan/>
	Order allow,deny
	Allow from all
	</Directory> 

Modify /var/www/html/caravan/caravan in the lines above if you mean to have a different 
caravan site folder path. BUT IN THIS CASE MODIFY ALSO CARAVAN.WSGI SYS PATH APPEND (OR INSERT) 
COMMAND ARGUMENT

Note that the second line (application group) is ESSENTIAL and its absence caused 
many bugs resolved with the aid of peter evans and Javier Pastore

4) IF YOU CREATED THE FILE /etc/apache2/conf-available/caravan.conf, 
then make a link in /etc/apache2/conf-enabled/caravan.conf pointing to
the newly created file in conf-available 

5) change ownership to files:
    sudo chown -R www-data.www-data /var/www/html/caravan
where the last argument is the site folder (here we use the one provided above, provide your one if different)

6) create a caravan directory according to the path specified above 
(/var/www/html/caravan/ in the example). In lhotse for instance, everything is 
under /home/caravan (it's a git repository also). After pulling from therein potential changes, 
just run (check paths! is an example): 
sudo rsync -avru --delete /home/caravan /var/www
(just for curiosity and avoid reduncancies, 
needs still to check if the -v option makes sense with the --delete)

================================================================================

YOU CAN ALWAYS CHECK THE SERVER ERROR BY TYPING ON THE SERVER TERMINAL:
sudo tail -f /var/log/apache2/error.log
and then go to a browser and reload
The terminal then shows server errors

KNOWN ISSUES:

1) MCERP and MATPLOTLIB PROBLEMS (DERIVED FROM MCERP USING IT)
mcerp has problems with apache2. It seems that by using matplotlib, the latter
writes directories for which we need permissions.

The line WSGIApplicationGroup %{GLOBAL} in the apache caravan config file for apache seems to solve the
problem in Ubuntu 14.04 and Apache/2.4.7, NOT IN Ubuntu 12.04.5 LTS with Apache/2.2.22

In case of issues, see first http://stackoverflow.com/questions/9827377/setting-matplotlib-mplconfigdir-consider-setting-mplconfigdir-to-a-writable-dir
and potentially modify caravan.wsgi os.environ (see caravan.wsgi)
IT IS NEVERTHLESS STRONGLY SUGGESTED TO ADDRESS THIS PROBLEM TO APACHE EXPERTS ONLY

2) sometimes lxml is not installed (PYTHON PACKAGE):
sudo apt-get install libxml2-dev libxslt-dev python-dev
sudo pip install lxml
Browse the internet for installing missing packages, if any. the /var/log/apache2/error.log file should warn for it (see above)


Final note (just as reminder): no caravan under /home? or want to clone somewhere else? then remember to use https for lhotse21:
    git clone https://github.com/GFZ-Centre-for-Early-Warning/caravan
will create the caravan folder in current dir
