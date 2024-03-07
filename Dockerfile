ARG ODOO_VERSION

FROM odoo:${ODOO_VERSION:-16.0}
MAINTAINER "Samuel Luciano <sluciano@accounterprise.com>"

LABEL com.accounterprise.owner="Accounterprise SRL <contabilidad@accounterprise.com>" \
    com.accounterprise.author="Samuel Luciano <sluciano@accounterprise.com>" \
    version=1.0 \
    description="Customizaciones implementadas al ERP Odoo\
        por el equipo de TI de Accounterprise SRL para la adaptación\
        a las leyes fiscales de la República Dominicana.\
        (c) 2024 Copyright. Todos los derechos reservados."

ENV ODOO_EDITION=ce \
    ODOO_ENVIRONMENT=dev \
    DATABASE_NAME= \
    ODOO_CONFIG_FILE=/etc/odoo/odoo.conf\
    ODOO_INITIAL_MODULES= \
    USE_DEFAULT_ADDONS_PATH=y \
    MAX_RETRIES= \
    SLEEP_TIME=

COPY odoo-entrypoint.sh /
COPY remove_modules_on_odoo_version.sh /
COPY test_database_settings.py /usr/local/bin/test_database_settings.py
COPY third_party_addons/ /mnt/extra-addons
COPY conf/odoo.conf /etc/odoo/

USER root

RUN [ "chmod", "-R", "777", "/etc/odoo" ]
RUN /remove_modules_on_odoo_version.sh ${ODOO_VERSION}

EXPOSE 8069 8072
VOLUME [ "/var/lib/odoo" ]

USER odoo

ENTRYPOINT [ "/bin/bash", "odoo-entrypoint.sh" ]