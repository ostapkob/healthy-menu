FROM  jenkins/inbound-agent

USER root

RUN groupadd -g 131 docker && \
    usermod -aG docker jenkins

USER jenkins
