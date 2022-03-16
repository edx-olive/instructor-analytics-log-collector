Change Log
__________

..
   All enhancements and patches to rg instructor analytics will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

[Fix] - 2022-03-16
~~~~~~~~~~~~~~~~~~
* Make the Student Step pipeline MFE compatible

  * this is a part of the Student Step pipeline fix for MFE
  * https://youtrack.raccoongang.com/issue/RGOeX-991

[v3.3.1] - 2021-12-01
~~~~~~~~~~~~~~~~~~~~~
* Fix data included to the package.
* Fix styling issues.

[v3.3.0] - 2021-10-21
~~~~~~~~~~~~~~~~~~~~~
* Feature Add support for live events

[v3.2.0] - 2021-07-29
~~~~~~~~~~~~~~~~~~~~~
* Feature Add support for tracking logs in object storages:
   - S3 service
   - Azure Blob service


[v3.1.0] - 2021-07-08
~~~~~~~~~~~~~~~~~~~~~
* Feature Add Installable App Options
* Docs: GitLab MR Template is added

[v3.0.0] - 2021-06-17 (Koa+ only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Full migration from Py2 to Py3, Py2 based OeX releases are not supported.
* Fix MySQL Operational Error storing 4 byte unicode
  `YouTrack issue RGA-242 <https://youtrack.raccoongang.com/issue/RGA-242?p=RGA2-424>`_
  (temporary workaround is added together with `FIXME` flag)


[Documentation|Enhancement] - 2021-06-16
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* CHANGELOG is added!

* For the upcoming logs please use the following tags:
   * Feature
   * Enhancement
   * Fix
   * Documentation
