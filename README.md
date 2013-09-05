============
noah-inasafe
============
This is the noah-inasafe project: a web-based InaSAFE-like tool for the Philippines

About Project NOAH: http://noah.dost.gov.ph/#about

About InaSAFE: http://www.inasafe.org/en/

InaSAFE was cloned from https://github.com/AIFDR/inasafe

Installation
============
First, Download Vagrant: <http://downloads.vagrantup.com/tags/v1.2.7>

Vagrant is a tool that provides easily configurable and reproducible virtual environments. 
For more information on Vagrant: http://docs.vagrantup.com/v2/getting-started/index.html
    
After downloading Vagrant, navigate to the root of this directory and run:

    % vagrant up

and wait for vagrant to finish setting up. If running vagrant up for the first time, it will download a virtual image (~300Mb). 
For more information on configuring and provisioning your virtual environment:

http://docs.vagrantup.com/v2/provisioning/puppet_apply.html

http://puppetlabs.com/puppet/puppet-enterprise


Accessing the virtual machine
=============================
In order to log into the virtual machine, use SSH:

    % host: 127.0.0.1
    % port: 2222
    % username: vagrant
    % password: vagrant

Note: Windows operating systems do not have SSH natively and you will have to download and install an SSH tool like PuTTY

Contents
========
The project root contains primarily the git files (README, LICENSE, .gitignore, etc) and the files needed by Vagrant.
The project root also contains subdirectories corresponding to different python-based frameworks or web servers. 
Currently, there are subdirectories for:

 - Django

 - Tornado
