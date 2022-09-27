FROM 071032557399.dkr.ecr.sa-east-1.amazonaws.com/python:3.8

USER root

RUN curl -s https://raw.githubusercontent.com/envkey/envkey-source/master/install.sh | bash
RUN touch /root/.bashrc && echo "eval \$(envkey-source)" > /root/.bashrc

RUN apt-get -yqq update && apt-get -yqq install zip unzip libcurl4-gnutls-dev librtmp-dev

# Install Chrome WebDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver && \
    ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver /usr/local/bin/chromedriver

# Install Google Chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get -yqq update && \
    apt-get -yqq install google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE settings
ENV PYTHONPATH /home/userapp/app/

COPY --chown=userapp:userapp requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=userapp:userapp . .

USER userapp

RUN chmod +x ./start.sh
CMD ["./start.sh"]