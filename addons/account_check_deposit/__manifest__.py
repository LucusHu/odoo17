{
    "name": "Account Check Deposit",
    "version": "1.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Manage deposit of checks to the bank",
    # "author": "Akretion, Tecnativa, Odoo Community Association (OCA)",
    "author": "Lucas",
    # "description": "Your Description",
    "website": "https://github.com/OCA/account-financial-tools",
    "depends": ["account"],
    "development_status": "Mature",
    "data": [
        "security/ir.model.access.csv",
        "security/check_deposit_security.xml",
        "data/sequence.xml",
        "views/account_check_deposit_view.xml",
        "views/account_move_line_view.xml",
        "report/report.xml",
        "report/report_checkdeposit.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
