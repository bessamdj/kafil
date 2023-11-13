# Copyright (C) 2022 - Today: Bessam Djerad
# @author: Bessam Djerad

{
    "name": "Kafil El Yatim Addans",
    "summary": "Manage all operation off Kaflil El Yatim kkwoqcxiimpgeyed",
    "version": "14.0.1.0.1",
    "category": "",
    "author": "Get You On, Bessam Djerad",
    "website": "https://getuon.com",
    "license": "AGPL-3",
    "depends": [
        "base", "account", "stock_account", "partner_external_map", "base_geolocalize",
    ],
    "data": [
        "security/kafil_secur.xml",
        "security/ir.model.access.csv",
        'data/sequence.xml',
        "views/kafil_views.xml",
        "views/orphan_view.xml",
        "views/donation.xml",
        "views/management.xml",
        "views/collect.xml",
        "views/services_aide.xml",
        "views/inkind_aide.xml",
        "views/health_help.xml",
        "views/configuration.xml",
        "report/distribution_report.xml",
        "report/donation_report.xml",
        "report/collect_report.xml",
        "report/health_help_report.xml",
        "report/services_aide_report.xml",
        "report/inkind_aide_report.xml",
        "report/kafil_card.xml",
        "views/portal.xml"
    ],
    "installable": True,
    "application": True,
}
