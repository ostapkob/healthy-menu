FROM  jenkins/inbound-agent

USER root

ENV DEBIAN_FRONTEND=noninteractive

# install docker-buildx-plugin
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-buildx-plugin \
    && apt-get install -y curl host\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# get gid -> $ ls -ln /var/run/docker.sock
RUN groupadd -g 131 docker && \
    usermod -aG docker jenkins

USER jenkins
