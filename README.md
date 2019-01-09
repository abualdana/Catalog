
# About Catalog Application:
The application provides a list of cars within their manufacturing companies as well as provides a user registration and authentication system. Registered users will have the ability to post, edit and delete their own records.



## How to run the application:

* Install <a href="https://www.virtualbox.org/wiki/Downloads">VirtualBox</a> and <a href="https://www.vagrantup.com">Vagrant</a>.

* Clone <a href="https://github.com/udacity/fullstack-nanodegree-vm">fullstack-nanodegree-vm</a>

* Clone this application and place the files in the vagrant directory of the fullstack-nanodegree-vm.

* Start your virtual machine with the command ```vagrant up``` and log into it with ```vagrant ssh```

* Change the current directory to vagrant directory using ```cd /vagrant```

* Install SQLAlchemy with the command ```pip install SQLAlchemy```

* Install flask framework with the command ```pip install flask```

* Get into the Catalog directory with the command ```cd catalog``` and run the database file with the command ```python db_setup.py```

* Run the seeder file with the command ```python seeder.py```

* Run the application file with the command ```python application.py```

* You will need to use your google account to register.

