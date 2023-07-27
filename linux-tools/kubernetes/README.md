# Kubernetes auto-deploy
This scripts automatically deploys Kubernetes cluster on any Linux system

## Requirments
+ sudo
+ curl
+ sed

## Usage
If you have Debian/Ubuntu, you should uncomment line 49, and Kubernetes will be installed automatically, else you should manually install `kubeadm`, `kubetel`, `kubectl` utilities. After that, you should disable swap and run:
```
$ ./kuber_deploy.sh
```
Kubernetes cluster will be deployed automatically
