FROM haxe:3.4.2-stretch
MAINTAINER dion@transition9.com

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - && \
		apt-get install -y nodejs && \
		npm install -g chokidar-cli && \
		rm -rf /var/lib/apt/lists/*