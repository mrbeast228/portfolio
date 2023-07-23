#!/bin/sh
set -e

apt_install_kuber() {
    sudo apt install gnupg gnupg2 curl software-properties-common -y
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmour -o /etc/apt/trusted.gpg.d/cgoogle.gpg
    sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
    sudo apt install kubelet kubeadm kubectl -y
    sudo apt-mark hold kubelet kubeadm kubectl
}

check_exists() {
    if ! command -v $1 &> /dev/null
    then
        echo "$1 not installed, please install it"
        exit 1
    fi
}

# kernel modules for Kubernetes
cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf >/dev/null 2>&1
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# network settings
cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-k8s.conf >/dev/null 2>&1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

# apply sysctl settings
sudo sysctl --system

# configure containerd
check_exists containerd

mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml >/dev/null 2>&1
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml

sudo systemctl restart containerd

# create cluster
#apt_install_kuber
for kubecmd in kubeadm kubelet kubectl; do
    check_exists $kubecmd
done
sudo kubeadm init --control-plane-endpoint=$(hostname)

# configure kubectl
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# configure CNI
cat <<EOF | sudo tee /etc/cni/net.d/1-k8s.conflist >/dev/null 2>&1
{
  "cniVersion": "0.3.1",
  "name": "bridge",
  "plugins": [
    {
      "type": "bridge",
      "bridge": "bridge",
      "addIf": "true",
      "isDefaultGateway": true,
      "forceAddress": false,
      "ipMasq": true,
      "hairpinMode": true,
      "ipam": {
          "type": "host-local",
          "subnet": "10.244.0.0/16"
      }
    },
    {
      "type": "portmap",
      "capabilities": {
          "portMappings": true
      }
    }
  ]
}
EOF

# untaint nodes
set +e
kubectl taint nodes --all node-role.kubernetes.io/control-plane:NoSchedule-

exit 0
