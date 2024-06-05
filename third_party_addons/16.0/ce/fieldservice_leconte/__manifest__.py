{
    "name": "Field Service - Leconte",
    "version": "16.0.1.14.1",
    "category": "Field Service",
    "depends": ["fieldservice", 'fieldservice_project', 'sale'],
    "data": [
        "views/fsm_order.xml",
        "views/project_views.xml",
        "views/product_template_views.xml",
        "views/fsm_brand_views.xml",
        "views/fsm_equipment_views.xml",
        "security/ir.model.access.csv",
        "security/groups_leconte.xml",
        "data/cron_data.xml",
        "data/fsm_stages_data.xml"
    ],
    "license": "AGPL-3",
}
