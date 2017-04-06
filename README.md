A sample library setup. This provides a good foundation for building a re-usable library.

Note: Assume all commands in this document start from the root of the repository.

Initial setup
=============

Create a virtualenv
-------------------

In order to use your package and run the test, you will want the package installed in the local environment.

First, create a virtualenv.

`virtualenv venv`

Whenever you work on the library, you will need to activate the virtualenv.

`source venv/bin/activate`

You will also want to configure the virutalenv to look for packages from the internal artifactory.

Put the following in your venv/pip.conf

  [global]
  index-url = http://yum-1-001.shared.adm.las1.mz-inc.com:8081/artifactory/api/pypi/pypi-virtual/simple
  trusted-host = yum-1-001.shared.adm.las1.mz-inc.com

 You can also put that into your home folder to configure pip for your user globally. Just put that into ~/.pip/pip.conf


Install the git hooks
---------------------

In the .git directory, remove the existing hooks/ directory and link the hooks directory in the repo.

~~~~cd .git
rm -r hooks/
ln -s ../hooks .~~~~

General Running
===============

You will want the package installed into your local environment for testing and development. Install the package
as editable with

`pip install -e .[dev]`

This will install the package so that it is importable, but installed in a way that the code that you
