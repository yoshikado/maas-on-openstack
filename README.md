Deploy MAAS on OpenStack
========================

How to deploy MAAS on OpenStack
-------------------------------
### Snap
You can install MAAS on OpenStack(moo) from snap.
```
$ sudo snap install moo
```

### Deploy
After installation is complete, now you can deploy MAAS:

```
$ moo deploy -r xenial
```

### Enlist nodes
After MAAS is deployed, you can add nodes to your MAAS cluster:

```
$ moo add_node --flavor m1.medium node1
```
