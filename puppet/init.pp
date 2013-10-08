class update {
  # There seems to be a problem with apt-get update without this.
  exec {'dpkg-configure':
    command => '/usr/bin/dpkg --configure -a',
    before => Exec['apt-initialize']
  }
  
  exec {'apt-initialize':
    command => '/usr/bin/apt-get update',
    before => Package['python-software-properties']
  }

  package {'python-software-properties':
    ensure => present,
    before => Exec['apt-update']
  }
  
  exec {'apt-update':
    command => '/usr/bin/apt-get update'
  }
}

class inasafe {
  package {['python-pip', 'rsync', 'git', 'pep8', 'python-nose', 'python-coverage', 'python-sphinx',
            'pyqt4-dev-tools', 'pyflakes', 'python-dev', 'python-gdal', 'curl', 'libpq-dev',
            'python-psycopg2', 'gdal-bin', 'postgresql', 'vim', ]:
    ensure => present,
    provider => 'apt'
  }
  
  package { ['tornado', 'numpy', 'sqlalchemy',]:
    ensure  => installed,
    provider => pip
  }
  
}

class django {
  package {['django', 'djangorestframework', 'django-leaflet', 'pinax-theme-bootstrap', 'django-braces', 'django-smart-selects']:
    ensure => installed,
    provider => pip
  }
}


class {'update':}
class {'inasafe':}
class {'django':}

#cloud-sptheme 
#python-nosexcover