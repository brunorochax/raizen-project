FROM jrei/systemd-ubuntu:18.04

ENV VAGRANT_VERSION=2.2.16

# Utils
RUN apt update
RUN apt -y install \
    wget \
    gnupg2 \
    systemd \
    software-properties-common \
    iptables \
    ssh \
    net-tools

# Virtualbox installation
RUN wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | apt-key add -
RUN wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | apt-key add -
RUN add-apt-repository "deb https://download.virtualbox.org/virtualbox/debian bionic contrib"
RUN apt update 
RUN apt-get -y install virtualbox-6.1 virtualbox-dkms dkms

# Vagrant installation
RUN wget -q https://releases.hashicorp.com/vagrant/${VAGRANT_VERSION}/vagrant_${VAGRANT_VERSION}_x86_64.deb
RUN dpkg -i vagrant_${VAGRANT_VERSION}_x86_64.deb

RUN vagrant box add senglin/win-10-enterprise-vs2015community
RUN vagrant init senglin/win-10-enterprise-vs2015community
RUN vagrant plugin install vagrant-vbguest