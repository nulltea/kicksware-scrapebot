# Service dev image
FROM python:3.8 as build
# Name service
LABEL Name=data-provider-bot
# Setup working directory /build
WORKDIR /build
# Install pipenv package manager
RUN pip install pipenv
# Set option to install venv in build directory
ENV PIPENV_VENV_IN_PROJECT=1
# Copy & download dependency using go mod
COPY Pipfile /build/
RUN pipenv lock
RUN pipenv install
# Export necessary port
EXPOSE 8080

# Service prod image
FROM python:3.8 as prod
# Setup working directory /root/
WORKDIR /root/
# Copy source code into the container
ADD . /root/
# Copy dependencies
COPY --from=build /build /root/
ENV PATH=/root/.venv/bin:$PATH
# Download and install chrome
RUN apt-get -y update && apt-get install -y wget && apt-get install -y gnupg2 && apt-get install -y curl
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable
# Install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
# Install remote screen aka Xcfb
RUN apt-get install -y xvfb
# set display port to avoid crash
ENV DISPLAY=:99
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null
# Service listens on port 8080.
EXPOSE 8080
# Run product service container when the container starts
COPY docker/entrypoint.sh /root/
ENTRYPOINT ["bash", "./entrypoint.sh"]



