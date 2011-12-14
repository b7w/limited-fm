************************************
Quick install guide
************************************

.. index:: Installation

.. _installation:

Requirements
====================================

.. index:: Requirements

| Limited works with any Python version from 2.4 to 2.7
  And with `Django framework <https://www.djangoproject.com/>`__ version 1.3.
  Python PIL, you can install it ``sudo apt-get install python-imaging``.

| You can use any django supported database server.
  It is officially works with PostgreSQL, MySQL, Oracle and SQLite.
  For more look `here <https://docs.djangoproject.com/en/1.3/topics/install/#database-installation>`__


Setting up Django
====================================

We would set up project from scratch. So we need to copy default setting file. And edit it.

.. code-block:: bash

    cd /some/../path/FileManager
    cp settings.py.smpl settings.py
    nano settings.py

| Set up database settings and others you need. Set home directory for storage, **LIMITED_ROOT_PATH**.
  For more settings look :doc:`settings.py </ref/settings>`.
  Also it good practice to set debug True.
  In this case you will see all errors in web browser.
  Do not forget to turn it False back!
  Now we have to add tables to database, and collect all static files.

.. code-block:: bash

    python manage.py syncdb --settings=settings
    python manage.py collectstatic --settings=settings


.. index:: loadpermissions
.. _installation_loadpermissions:

Permission
====================================

| Permission table is empty, you can generate and append 64 unic permissions.
  2^5 - edit, move, create, upload, http_get.
  This is very clearly, each *id+1* is a binary representation of the permission.
  For example id3, 2 == 000010.
  So it will be ease to navigate through them in Django admin.
  But if you don't want a lot of row in table, you can skip this step.
  All necessary permissions will be created on a fly.

.. code-block:: bash

    python manage.py loadpermissions

| The count of permits generating automatic from field's count.
  So if you add some fields, just run command again.
  But be carefully, all old data in table will be removed.

| Also do not forget setup `robots.txt`. You can find sample of it in docs/extra/robots.txt
  It disallow all searches robots to parse data.

.. literalinclude:: /extra/robots.txt



.. index:: Run server

Run server
====================================

| All main preference are set up.
  Now you can run test Django server.
  If you run on remote machine set ip address of this host instead of localhost.
  Also you can change port for any you like.
  
.. code-block:: bash

    python manage.py runserver localhost:8000 --settings=settings

| To run fcgi server use some thing like this shell init script.
  Copy code below or file 'doc/extra/limited.sh' to '/etc/init.d/limited'.
  And edit it for yourself.
  Usage: start | stop | restart.
  For example, *sudo service limited start*

.. index:: Init file

.. literalinclude:: /extra/limited.sh
   :language: bash

.. index:: Nginx settings

| If you use nginx, here some simple setting file for it.
  Copy code below or file 'doc/extra/nginx.conf' to '/etc/nginx/sites-available/domain.com'.
  And edit it for yourself.
  Pay attention to the *location /protected*.
  This section is to delegate file serving to nginx.
  To set up it in Limited look :ref:`here <SETTINGS_SERVE>`

.. note::  **path to fcgi.sock must be the same in both, init file and nginx settings**.

.. _nginx_settings:

.. literalinclude:: /extra/nginx.conf


| For other settings go to :doc:`here </ref/settings>`.
  If you need administration help pleas read :doc:`this </guide/administrator>`.



What to read next
====================================

| Read :doc:`administrator guide </guide/administrator>`.
  There how to configure the application and environment.
  As well as some installation parts with some details.