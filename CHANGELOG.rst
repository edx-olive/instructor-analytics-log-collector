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
