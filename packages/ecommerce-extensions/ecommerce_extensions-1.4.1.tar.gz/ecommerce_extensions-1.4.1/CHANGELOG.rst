Change Log
==========

..
   All enhancements and patches to ecommerce-extensions will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).
   
   This project adheres to Semantic Versioning (http://semver.org/).
.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

[1.4.1] - 2022-01-25
~~~~~~~~~~~~~~~~~~~~

Changed
-------
* Update `sentry-sdk`.

[1.4.0] - 2021-08-12
~~~~~~~~~~~~~~~~~~~~

Added
-----

* Console access functionality

[1.3.1] - 2021-05-19
~~~~~~~~~~~~~~~~~~~~

Fixed
-----

* Sentry dsn integration variable

[1.3.0] - 2021-05-17
~~~~~~~~~~~~~~~~~~~~

Added
-----

* Send custom parameters for courses


[1.2.1] - 2021-05-12
~~~~~~~~~~~~~~~~~~~~

Added
-----

* Sentry configurations on apps.py


[1.2.0] - 2021-05-11
~~~~~~~~~~~~~~~~~~~~

Added
-----

* Blocks of scripts in context_processors from THEME OPTIONS in tenant options.
* Blocks of HTML in context_processors from THEME OPTIONS in tenant options.


[1.1.0] - 2021-04-06
~~~~~~~~~~~~~~~~~~~~

Fixed
-----

* returning messages for debug with the 400 responses


[1.0.2] - 2021-02-19
~~~~~~~~~~~~~~~~~~~~

Fixed
-----

* using get since the object is a dict


[1.0.1] - 2021-02-18
~~~~~~~~~~~~~~~~~~~~

Fixed
-----

* correcting the KeyError


[1.0.0] - 2021-02-09
~~~~~~~~~~~~~~~~~~~~

Added
-----

* Add new payment processor (ednx-pp).

Fixed
-----

* Remove api key from parameters dictionary in Payu.


[0.3.0] - 2020-11-18
~~~~~~~~~~~~~~~~~~~~

Added
-----

* Fomopay payment processor.

Fixed
-----

* Payu urls.

[0.2.0] - 2020-11-12
~~~~~~~~~~~~~~~~~~~~

Added
-----

* Payu payment processor.


[0.1.0] - 2020-10-21
~~~~~~~~~~~~~~~~~~~~

* Initial version
