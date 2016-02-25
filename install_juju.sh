#!/bin/bash

set -u
set -e

SetVars(){
  source setvars
  maas_url="http:\/\/${maas_server_ip}\/MAAS\/"
  maas_key=`sudo maas-region-admin apikey --username $maas_user_name`
}

InstallJuju(){
  sudo apt-get install -y juju-core juju-deployer
}

ConfigureJuju(){
  juju init -f
  sed -i -e "s/maas-server:.*/maas-server: \'$maas_url\'/g" "$HOME/.juju/environments.yaml"
  sed -i -e "s/maas-oauth:.*/maas-oauth: \'$maas_key\'/g" "$HOME/.juju/environments.yaml"
  juju switch maas
}

DeployBootstrap(){
  juju bootstrap --debug --constraints tags=bootstrap
}

SetVars
InstallJuju
ConfigureJuju
#DeployBootstrap
