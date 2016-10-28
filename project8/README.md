# Linux Server Configuration Project

* IP Address: 35.161.45.169
* SSH Port: 2200
* sername: grader
* Website address: http://ec2-35-161-45-169.us-west-2.compute.amazonaws.com

To login to the server, ensure you have the private key and type the following command:

```
ssh -i location_of_private_key.rsa grader@35.161.45.169 -p 2200
```

Applications were first upgraded using:

```
sudo apt-get update
sudo apt-get upgrade
```

### Applications Installed
* Git
* PostgreSQL
* Apache
* Pip

### Python Modules
* oauth2client
* sqlalchemy
* httplib2
* psycopg2


### Configuration Changes
* Changed SSH port from 22 to 2200
* Added sudo privileges to grader via the command: 
  * sudo usermod -aG sudo grader
* Enabled public/private key login for grader by copying ~/.ssh/authorized keys to grader's home directory and adjusting permissions
* Disabled root login via etc/ssh/sshd\_config
* Changed local timezone to UTC via sudo dpkg-reconfigure tzdata

### Installing Flask Application on Server
* Setup postgres and appropriate roles
* Setup apache with flask application configuration file in sites-available and sites-enabled
* Created a server.wsgi file to allow the web server to interface properly with Apache

### Resources
* Changing ssh port: [http://www.linuxlookup.com/howto/change_default_ssh_port](http://www.linuxlookup.com/howto/change_default_ssh_port)
* Changing local timezone: [http://askubuntu.com/questions/138423/how-do-i-change-my-timezone-to-utc-gmt](http://askubuntu.com/questions/138423/how-do-i-change-my-timezone-to-utc-gmt)
* Setting up a Flask App on a VPS: [https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)
