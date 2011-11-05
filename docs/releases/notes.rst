************************************
Release notes
************************************

.. index:: Release notes

| Release notes for the official Limited FM releases.
  Each release note will tell you what’s new in each version,
  and will also describe any backwards-incompatible changes made in that version.



.. index:: Release notes 1.0

1.0 release
====================================


1.0.1
------------------------------------

| **Info notes**. History now store all changed files in database. In ``name`` field in comma separated way.
  The filed need to be updated to 1024 max length.
  With this feature, history link following highlight all changed files.

| **Fix errors**.
  Tread auto join after start;
  Upload restriction in Opera;
  Wrong upload names in history if the same name exists;
  Fix *ObjectDoesNotExist* if try to download/upload from lib that not in users home.
