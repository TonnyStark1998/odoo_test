ARG ODOO_VERSION=16.0
ARG ODOO_EDITION=ce
ARG ODOO_ENVIRONMENT=dev

FROM odoo:${ODOO_VERSION}

LABEL com.accounterprise.owner="Accounterprise SRL <contabilidad@accounterprise.com>" \
      com.accounterprise.author="Samuel Luciano <sluciano@accounterprise.com>" \
      version=1.0 \
      description="Customizaciones implementadas al ERP Odoo\
        por el equipo de TI de Accounterprise SRL para la adaptación\
        a las leyes fiscales de la República Dominicana.\
        (c) 2024 Copyright. Todos los derechos reservados."

ENV ODOO_EDITION=${ODOO_EDITION} \
    ODOO_ENVIRONMENT=${ODOO_ENVIRONMENT} \
    DB_NAME= \
    ODOO_CONFIG_FILE='/etc/odoo/odoo.conf' \
    ODOO_INITIAL_MODULES= \
    ODOO_UPDATE_MODULES= \
    ODOO_ADDONS_PATH='/mnt/extra-addons' \
    USE_DEFAULT_ADDONS_PATH='y' \
    MAX_RETRIES= \
    SLEEP_TIME=

# hadolint ignore=DL3013
RUN pip3 install --no-cache-dir \
    psycopg2 \
    python-barcode

COPY .ops/scripts/odoo-entrypoint.sh /
COPY .ops/scripts/test_database_settings.py /usr/local/bin/test_database_settings.py
COPY conf/odoo.conf /etc/odoo/odoo.conf
COPY addons/${ODOO_VERSION} ${ODOO_ADDONS_PATH}/${ODOO_VERSION}

EXPOSE 8069 8072

VOLUME /var/lib/odoo

USER odoo

ENTRYPOINT [ "/bin/bash", "odoo-entrypoint.sh" ]
