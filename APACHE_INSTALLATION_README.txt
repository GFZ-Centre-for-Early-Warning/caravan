SIMPLE README TESTED ON UBUNTU 14.04 with apache and mod_wsgi installed

1) make (or edit, should be already there) caravan.wsgi file, if needed (it should not be the case)

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
	
	WSGIScriptAlias /caravan /var/www/caravan/caravan.wsgi
	<Directory /var/www/caravan/>
	Order allow,deny
	Allow from all
	</Directory> 
