FROM ubuntu:18.04

RUN apt-get update -y

RUN apt-get install -y qemu-kvm libvirt-daemon-system libvirt-dev
RUN apt-get install -y linux-image-4.18.0-18-generic
RUN apt-get install -y curl net-tools jq

RUN curl -O https://releases.hashicorp.com/vagrant/2.2.10/vagrant_2.2.10_x86_64.deb
RUN dpkg -i vagrant_2.2.10_x86_64.deb

RUN vagrant plugin install vagrant-libvirt
RUN vagrant box add --provider libvirt peru/windows-10-enterprise-x64-eval
RUN vagrant init peru/windows-10-enterprise-x64-eval

COPY startup.sh /

ENTRYPOINT ["/startup.sh"]