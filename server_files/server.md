# Setting up the Server
The files in here are to help you in setting up your server.
## Nginx
Move the nginx.conf to your nginx.conf directory(use locate to find it on linux).
This is the nginx.config that I'm basically running myself.
## making it a service
move capstone_project.service to /etc/systemd/system.
Then you should start it with systemctl capstone_project start after you've finished setting up everything else.
If it fails make sure to check out the dirctory ```/tmp/ctf_err.log```. Windows users, you're on your own.
## Changing the default secret key
This secret isn't that good as it's one that's already known(as I have to include something). So run ```python3 generate_secret_key.py``` from within this folder.
## Setting up postgres
All you have to do is run the postgres.sh script in this directory to have it create your user, get all of the databases created and ready to go for django.

