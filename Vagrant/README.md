
A **Vagrantfile** exists in the subdirectories 'ansible' and 'basic'. 

### Basic 

Contain a configuration script to setup a virtual box

    sudo apt-get install vagrant wget -y
    wget https://github.com/vecna/trackmap/archive/master.zip
    unzip master.zip
    cd trackmap-master/Vagrant/basic
    vagrant up

When you type the command **vagrant up** will download the virtual machine image, perform an upgrade, install the needed packages, copy an SSH public key, run Tor and give you the address of the Tor hidden service pointing to the SSH port of the virtual machine.

We're only going to run the defined script, but if new tests are available, we might ask you to re-type **vagrant up**.

In this case, will be pretty easy to us update the test and run them, without having to ask to you specific tasks. At the moment the Vagrant is still under cleaning and review, but if you've the avalability of a constantly runnig box, that's would be excellent for the project.

### ansible

TODO description
