=====================
Base Field Deprecated
=====================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:f7f7c06c5575251f1039635cc7a00d07cbba1249af41fe9055a7adf0166f0555
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fserver--ux-lightgray.png?logo=github
    :target: https://github.com/OCA/server-ux/tree/15.0/base_field_deprecated
    :alt: OCA/server-ux
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/server-ux-15-0/server-ux-15-0-base_field_deprecated
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/server-ux&target_branch=15.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module adds the deprecated field to the Odoo field itself based on the value set to the Python field.
This can be useful to determine which are the declared deprecated fields in a fast way.

**Table of contents**

.. contents::
   :local:

Usage
=====

#. By setting **deprecated=True** to a declared field, the Odoo field will inherit the value and it will be stored at the database level.
#. For instance:
    #. If we have the following field: test_field = fields.Boolean(deprecated=True).
    #. By looking at the instance that saves the information of the Python field on the **ir.model.fields** model, the deprecated attribute will be set there, just like copied, store, computed, among others.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-ux/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/server-ux/issues/new?body=module:%20base_field_deprecated%0Aversion:%2015.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* ForgeFlow

Contributors
~~~~~~~~~~~~

* `ForgeFlow S.L. <https://www.forgeflow.com>`_:

  * Guillem Casassas <guillem.casassas@forgeflow.com>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

.. |maintainer-GuillemCForgeFlow| image:: https://github.com/GuillemCForgeFlow.png?size=40px
    :target: https://github.com/GuillemCForgeFlow
    :alt: GuillemCForgeFlow

Current `maintainer <https://odoo-community.org/page/maintainer-role>`__:

|maintainer-GuillemCForgeFlow| 

This module is part of the `OCA/server-ux <https://github.com/OCA/server-ux/tree/15.0/base_field_deprecated>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
