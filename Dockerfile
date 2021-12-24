######################################################################
# PY stage that simply does a pip install on our requirements
######################################################################
ARG PY_VER=3.8.12
FROM python:${PY_VER} AS superset-py

ENV SUPERSET_HOME=/app
WORKDIR $SUPERSET_HOME
ENV SUPERSET_VERSION=1.3.2

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        libpq-dev \
        libsasl2-dev \
        libecpg-dev \
    && rm -rf /var/lib/apt/lists/*

# Download source code
RUN wget -qO /tmp/superset.tar.gz https://github.com/apache/superset/archive/$SUPERSET_VERSION.tar.gz   \
    && tar xzf /tmp/superset.tar.gz -C $SUPERSET_HOME --strip-components=1 \
    && ls -lah docker   \
    && mkdir -p superset/static \
    && touch superset/static/version_info.json \
    && pip install --no-cache -r requirements/local.txt

######################################################################
# Node stage to deal with static asset construction
######################################################################
FROM node:16 AS superset-node

ARG NPM_VER=7
RUN npm install -g npm@${NPM_VER}

ENV SUPERSET_HOME=/app
WORKDIR $SUPERSET_HOME

COPY --from=superset-py /app/docker/frontend-mem-nag.sh /app/docker/frontend-mem-nag.sh
COPY --from=superset-py /app/superset-frontend /app/superset-frontend

# NPM ci first, as to NOT invalidate previous steps except for when package.json changes

RUN docker/frontend-mem-nag.sh \
    && cd /app/superset-frontend \
    && npm ci       \
    && cd /app/superset-frontend \
    && npm run build \
    && rm -rf node_modules

######################################################################
# Final lean image...
######################################################################
ARG PY_VER=3.8.12
FROM python:${PY_VER} AS lean

ENV SUPERSET_HOME=/app
WORKDIR $SUPERSET_HOME

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    FLASK_ENV=production \
    FLASK_APP="superset.app:create_app()" \
    PYTHONPATH="/app/pythonpath" \
    SUPERSET_HOME="/app/superset_home" \
    SUPERSET_PORT=8088

RUN mkdir -p ${PYTHONPATH} \
    && useradd --user-group -d ${SUPERSET_HOME} -m --no-log-init --shell /bin/bash superset \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        libsasl2-modules-gssapi-mit \
        libpq-dev \
        libecpg-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=superset-py /usr/local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages/
COPY --from=superset-py /usr/local/bin/gunicorn /usr/local/bin/celery /usr/local/bin/flask /usr/bin/
COPY --from=superset-node /app/superset/static/assets /app/superset/static/assets
COPY --from=superset-node /app/superset-frontend /app/superset-frontend
COPY --from=superset-py /app/superset /app/superset
COPY --from=superset-py /app/setup.py /app/MANIFEST.in /app/README.md /app/
COPY --from=superset-py /app/docker/docker-entrypoint.sh /usr/bin/docker-entrypoint.sh
## Lastly, let's install superset itself

RUN chown -R superset:superset * \
    && pip install -e .          \
    && chmod a+x /usr/bin/docker-entrypoint.sh

USER superset

HEALTHCHECK CMD curl -f "http://localhost:$SUPERSET_PORT/health"

EXPOSE ${SUPERSET_PORT}

CMD /usr/bin/docker-entrypoint.sh

######################################################################
# CI image...
######################################################################
FROM lean AS ci

ARG GECKODRIVER_VERSION=v0.28.0
ARG FIREFOX_VERSION=88.0

COPY --from=superset-py /app/requirements /app/requirements
COPY --from=superset-py /app/docker /app/docker

USER root

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libnss3 libdbus-glib-1-2 libgtk-3-0 libx11-xcb1 curl

# Install GeckoDriver WebDriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz -O /tmp/geckodriver.tar.gz \
    && tar xvfz /tmp/geckodriver.tar.gz -C /tmp \
    && mv /tmp/geckodriver /usr/local/bin/geckodriver \
    && rm /tmp/geckodriver.tar.gz

# Install Firefox
RUN wget https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VERSION}/linux-x86_64/en-US/firefox-${FIREFOX_VERSION}.tar.bz2 -O /opt/firefox.tar.bz2 \
    && tar xvf /opt/firefox.tar.bz2 -C /opt \
    && ln -s /opt/firefox/firefox /usr/local/bin/firefox

# Install Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y --no-install-recommends ./google-chrome-stable_current_amd64.deb \
    && rm -f google-chrome-stable_current_amd64.deb   \
    && export CHROMEDRIVER_VERSION=$(curl --silent https://chromedriver.storage.googleapis.com/LATEST_RELEASE_88) \
    && wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/bin \
    && chmod 755 /usr/bin/chromedriver \
    && rm -f chromedriver_linux64.zip

# Cache everything for dev purposes...
RUN cd /app \
    && pip install --no-cache -r requirements/docker.txt \
    && pip install --no-cache -r requirements/local.txt || true    \
    && chmod a+x /app/docker/*.sh

USER superset

CMD /app/docker/docker-ci.sh
