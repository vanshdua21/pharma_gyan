FROM centos:7
LABEL maintainer="Vansh Team"

RUN \
 yum install -y epel-release && \
 yum install -y wget \
                git \
                which \
                make \
                python-setuptools \
                python-pip \
                python-dev \
                zlib-devel \
                openssl-devel \
                mysql-devel \
                python-devel \
                gcc-c++ \
                snappy-devel \
                gcc \
                postgresql \
                postgresql-devel \
                sqlite-devel \
                expat-devel \
                bzip2-devel \
                libffi-devel \
                zlib-devel \
                libxslt-devel \
                libxml2-devel \
                python-argparse \
                xmlsec1-devel \
                xmlsec1-openssl-devel \
                libtool-ltdl-devel && \
 yum install -y nginx && \
 yum install -y screen && \
 wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.centos7.x86_64.rpm && \
 yum localinstall -y wkhtmltox-0.12.6-1.centos7.x86_64.rpm && \
 pip install --upgrade pip && \
 pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host=api.github.com supervisor --no-cache-dir && \
 mkdir -p /var/log/supervisor /etc/supervisord.d /logs /opt/logs /etc/newrelic && \
 yum clean all

WORKDIR /usr/local/pharma_gyan/
ARG BUILD_ENV="uat"
ENV BUILD_ENV=$BUILD_ENV

EXPOSE 80


RUN \
 yum update -y nss \
        nss-sysinit \
        nss-tools \
        systemd \
        systemd-libs \
        bind-license \
        rpm \
        rpm-build-libs \
        rpm-python \
        rpm-libs \
        glib2 \
        openldap \
        gzip \
        kernel \
        kernel-headers \
        binutils \
        cyrus-sasl \
        cyrus-sasl-lib \
        kpartx \
        curl \
        libcurl \
        libssh2


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


COPY pharma_gyan_proj/server_config/pip/requirements.txt /etc/pip/requirements.txt
RUN pip install --upgrade pip && \
     pip install -r /etc/pip/requirements.txt
# RUN if [ "$BUILD_ENV" = "prod" ] ; then sed -i "/app_name/s/pharma_gyan/pharma_gyan-${BANK_NAME}/g" /etc/newrelic/newrelic_pharma_gyan.ini ; else sed -i "/app_name/s/pharma_gyan/pharma_gyan-${BUILD_ENV}-${BANK_NAME}/g" /etc/newrelic/newrelic_pharma_gyan.ini ; fi

COPY ./ /usr/local/pharma_gyan
RUN chmod 755 /etc/rc.d/init.d/supervisord

RUN \
   /usr/local/python3.8/bin/python3.8  /usr/local/pharma_gyan/pharma_gyan_proj/manage.py collectstatic && \
  chmod 755 /etc/rc.d/init.d/supervisord

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisord.d/pharma_gyan_web_service.conf"]
