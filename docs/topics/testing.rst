************************************
Testing project
************************************

.. index:: Testing project

.. index:: Django testing


Django testing
====================================

| Django have automated testing module.
  It is an extremely useful bug-killing tool for the modern Web developer.
  This feature will help to find bug before you run application on production.

| Limited have a lot of test. So it highly recommended to run it.
  No wonder that they have written.
  To start testing we need make some preparations.

* | Lets make another setting file. Just copy yours to 'settings2.py'.
* | Change database engine to ``django.db.backends.sqlite3`` and
    name to ``os.path.join(PROJECT_PATH,'TestDatabe.sqlite')``.
* | Assign variable :ref:`LIMITED_ROOT_PATH <SETTINGS_ROOT_PATH>`  ``PROJECT_PATH`` value.
* | Also you can change log file.

| Now let's run the tests.

.. code-block:: bash

    python manage.py test limited --settings=settings2

| After testing new 'test' direct appear. It's automatically generated data.
  You may delete it. If there are errors you will see them.
  Testing set up to stop on a first test.
  Because a lot of functions depending of more smaller.
  So if one not pass others will fall too.
  And it will be really hard to detect first bug.



.. index:: Limited testing

Limited testing
====================================

| There is some features that differ limited tests and django tests.
  Limited test moved to directory and split to files.
  It help to make easier to navigate in the tests.
  But it break possibility to test possibility test cases adn even functions.
  And another is that all of test inherit not TestCase
  but :py:class:`limited.tests.base.StorageTestCase`


.. autoclass:: limited.tests.base.StorageTestCase
    :show-inheritance:
    :members:


.. seealso:: To find out more go to official docs https://docs.djangoproject.com/en/dev/topics/testing/

  