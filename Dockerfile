# Use Ubuntu as the base image
FROM ubuntu:20.04
LABEL maintainer="Vansh Team"
ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHON_VERSION=3.8
RUN apt-get update && apt-get install -y \
    wget \
    git \
    make \
    python3-setuptools \
    python3-pip \
    python3-dev \
    zlib1g-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    libpq-dev \
    libsqlite3-dev \
    libexpat1-dev \
    libbz2-dev \
    libffi-dev \
    libxslt1-dev \
    libxml2-dev \
    xmlsec1 \
    libxmlsec1-dev \
    perl \
    libpcre3-dev \
    libtool \
    nginx \
    supervisor \
    ffmpeg \
    xfonts-75dpi \
    xfonts-base \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install supervisor
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org supervisor && \
    mkdir -p /var/log/supervisor /etc/supervisord.d /logs /opt/logs /etc/newrelic

WORKDIR /usr/local/pharma_gyan/
ARG BUILD_ENV="uat"
ENV BUILD_ENV=$BUILD_ENV

EXPOSE 80

RUN apt-get update && \
    apt-get -y install \
    libnss3 \
    systemd \
    gzip \
    libsasl2-2 \
    libsasl2-modules \
    libssh2-1 \
    libldap-2.4-2 \
    binutils \
    kpartx \
    curl \
    libcurl4 \
    libglib2.0-0 \
    rpm \
    libpq-dev \
    postgresql \
    libssl1.1 \
    openssl

RUN \
 cd /opt && \
 wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz  && \
 tar xvf Python-3.8.0.tgz && \
 cd /opt/Python-3.8.0 && \
 ./configure --enable-shared --with-system-ffi --with-system-expat --enable-unicode=ucs4 --prefix=/usr/local/python3.8 LDFLAGS="-L/usr/local/python3.8/lib -Wl,--rpath=/usr/local/python3.8/lib"  && \
 make && \
 make altinstall && \
 rm -f /etc/localtime && \
 ln -s /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
 rm -Rf Python-3.8.0.tgz /opt/Python-3.8.0

COPY pharma_gyan_proj/server_config/supervisord /etc/rc.d/init.d/supervisord
ADD  pharma_gyan_proj/server_config/services/* /etc/supervisord.d/
COPY pharma_gyan_proj/server_config/nginx/nginx.conf /etc/nginx/nginx.conf
COPY pharma_gyan_proj/server_config/uwsgi/uwsgi_params /etc/nginx/uwsgi_params
COPY pharma_gyan_proj/server_config/uwsgi/uwsgi_params /etc/nginx/conf.d/uwsgi_params
COPY pharma_gyan_proj/server_config/uwsgi/pharma_gyan_uwsgi.ini /etc/pharma_gyan_uwsgi.ini
COPY pharma_gyan_proj/server_config/nginx/pharma_gyan.conf /etc/nginx/conf.d/pharma_gyan.conf
COPY pharma_gyan_proj/server_config/newrelic/* /etc/newrelic/


# Install pip and upgrade it along with setuptools and wheel
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip setuptools wheel

# Add and install greenlet wheel file
#RUN wget https://files.pythonhosted.org/packages/7b/2e/ae57d807c49ae8a3a1c50d489e86e4f3bb5d82c3c7a1ec3c68e6ab3e9e60/greenlet-1.1.0-cp38-cp38-manylinux1_x86_64.whl
#COPY greenlet-1.1.0-cp38-cp38-manylinux1_x86_64.whl /tmp/
#RUN pip3 install /tmp/greenlet-1.1.0-cp38-cp38-manylinux1_x86_64.whl


COPY pharma_gyan_proj/server_config/pip/requirements.txt /etc/pip/requirements.txt
RUN /usr/local/python3.8/bin/pip3.8 install -r /etc/pip/requirements.txt
# RUN if [ "$BUILD_ENV" = "prod" ] ; then sed -i "/app_name/s/pharma_gyan/pharma_gyan-${BANK_NAME}/g" /etc/newrelic/newrelic_pharma_gyan.ini ; else sed -i "/app_name/s/pharma_gyan/pharma_gyan-${BUILD_ENV}-${BANK_NAME}/g" /etc/newrelic/newrelic_pharma_gyan.ini ; fi

COPY ./ /usr/local/pharma_gyan
RUN chmod 755 /etc/rc.d/init.d/supervisord

RUN \
   /usr/local/python3.8/bin/python3.8  /usr/local/pharma_gyan/pharma_gyan_proj/manage.py collectstatic && \
  chmod 755 /etc/rc.d/init.d/supervisord

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisord.d/pharma_gyan_web_service.conf"]