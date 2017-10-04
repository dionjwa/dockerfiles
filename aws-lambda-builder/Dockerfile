# Description:
#
# To build aws nodejs lambdas you need a build environment
# package up the scripts
#

FROM amazonlinux:2016.09

RUN mkdir /tmp/docker-build && \
  yum -y update && \
  curl -X GET -o /tmp/docker-build/RPM-GPG-KEY-lambda-epll https://lambda-linux.io/RPM-GPG-KEY-lambda-epll && \
  rpm --import /tmp/docker-build/RPM-GPG-KEY-lambda-epll && \
  curl -X GET -o /tmp/docker-build/epll-release-2016.09-1.2.ll1.noarch.rpm https://lambda-linux.io/epll-release-2016.09-1.2.ll1.noarch.rpm && \
  yum install -y /tmp/docker-build/epll-release-2016.09-1.2.ll1.noarch.rpm && \
  curl --silent --location https://rpm.nodesource.com/setup_6.x | bash - && \
  yum install -y nodejs && \
  yum install -y gcc gcc-c++ make && \
  yum install -y aws-cli && \
  yum install -y zip && \
  yum install -y jq && \
  yum clean all && \
  rm -rf /var/cache/yum/* && \
  rm -rf /tmp/* && \
  rm -rf /var/tmp/*
