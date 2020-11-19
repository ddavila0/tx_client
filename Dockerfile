FROM centos:7
RUN yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm -y
RUN yum install https://repo.opensciencegrid.org/osg/3.5/osg-3.5-el7-release-latest.rpm -y
RUN yum install yum-plugin-priorities -y
RUN yum install vim less -y
RUN yum install yum install voms-clients-cpp  vo-client -y
RUN yum install xrootd-client xrootd-server -y
RUN yum install fts-client gfal2-util gfal2-plugin-http gfal2-plugin-xrootd gfal2-plugin-file gfal2-plugin-gridftp gfal2-plugin-srm -y
RUN yum install git -y
RUN yum install fetch-crl -y
RUN yum install python-pip -y
RUN pip install --upgrade pip
RUN pip install pymacaroons
