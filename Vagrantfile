# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  module_path = ["puppet/modules"]
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  
  # Try to access http://localhost:8000
  config.vm.network :forwarded_port, guest: 5000, host: 8000, auto_correct: true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  config.vm.synced_folder "/Users/Ton/Documents/GitHub/noah-inasafe", "/home/vagrant/"

  config.vm.provider :virtualbox do |vb|
    vb.gui = true
    vb.customize ["modifyvm", :id, "--memory", "4096"]
  end
  
  config.vm.provision :puppet, :module_path => module_path do |puppet|
    puppet.manifests_path = "puppet"
    puppet.manifest_file  = "init.pp"
  end
end
