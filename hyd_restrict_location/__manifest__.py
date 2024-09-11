{
    "name": "Set warehouseman [responsible] for location",
    "summary": """ Set the warehousemen on a location who are the only"""
    """  one to done a every picking from/to that location """,
    "description": """
        Sometimes u don't want all user group warehouse to do
        transfert on certains location.

        Example:
        You can restrict move in destination or from inventory loss location
         to a user list. In this case, only them can do picking from/to
        inventory location like when we do inventory.
    """,
    "author": "HyD Freelance",
    "website": "http://",
    "category": u"Warehouse",
    "version": "15.0.0.1.2",
    "license": "AGPL-3",
    # any module necessary for this one to work correctly
    "depends": ["stock"],
    # always loaded
    "data": [
        # data
        # views
        "views/stock_location_views.xml",
        # workflow
        # security
        # reports
    ],
    # only loaded in demonstration mode
    "demo": [],
    "installable": True,
    "price": 0,
    "currency": "EUR",
    "images": ["static/images/main_screenshot.jpg"],
}
