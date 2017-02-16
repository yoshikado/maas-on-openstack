Deploy MAAS on OpenStack
========================

How to deploy MAAS on OpenStack
-------------------------------
### Prerequisite
In order to have MAAS on Openstack running, first install the following packages.
```
$ sudo apt install virtualenv libssl-dev
```
After you cloned this repository, you can simply install in virtualenv.
```
$ virtualenv -p python3 ~/venv
$ source ~/venv/bin/activate
$ pip install --editable .
```

### Deploy
After installation is complete, now you can deploy MAAS:

```
$ moo deploy -r xenial
```

### Enlist nodes
T.B.D
