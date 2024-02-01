ARG ODOO_VERSION

FROM odoo:${ODOO_VERSION:-16.0}
MAINTAINER "Samuel Luciano <sluciano@accounterprise.com>"

LABEL com.accounterprise.owner="Accounterprise SRL <contabilidad@accounterprise.com>"
LABEL com.accounterprise.author="Samuel Luciano <sluciano@accounterprise.com>"
LABEL version=1.0
LABEL description="Customizaciones implementadas al ERP Odoo\
por el equipo de TI de Accounterprise SRL para la adaptación\
a las leyes fiscales de la República Dominicana.\
(c) 2024 Copyright. Todos los derechos reservados."

ENV ODOO_EDITION=ce
ENV ODOO_ENVIRONMENT=dev
ENV DATABASE_NAME=
ENV ODOO_CONFIG_FILE=/etc/odoo/odoo.conf
ENV ODOO_INITIAL_MODULES=
ENV USE_DEFAULT_ADDONS_PATH=y
ENV MAX_RETRIES=
ENV SLEEP_TIME=

COPY odoo-entrypoint.sh /
COPY remove_modules_on_odoo_version.sh /
COPY test_database_settings.py /usr/local/bin/test_database_settings.py
COPY third_party_addons/ /mnt/extra-addons
COPY odoo.conf /etc/odoo/

USER root

RUN [ "chmod", "-R", "777", "/etc/odoo" ]
RUN /remove_modules_on_odoo_version.sh ${ODOO_VERSION}

EXPOSE 8069 8072
VOLUME [ "/var/lib/odoo" ]

USER odoo

ENTRYPOINT [ "/bin/bash", "odoo-entrypoint.sh" ]