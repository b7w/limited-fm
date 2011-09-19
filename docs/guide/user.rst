************************************
User guide
************************************

.. index:: User guide

Page layout
====================================

.. index:: Page layout

| Every page have the same layout. On the left side a column of widgets.
  In the center we have the table with file libs or a files. On the top we can see panel.
  The right panels side contains the title of the resource and path to the current page
  The path start with link to home page and next all previous directories you entered.
  Also the last name is name of current directory, but it isn't a link.
  The left panels side contains greeting and a login link.
  A slightly below the reference to feed back is situated.
  To learn more about feed back go :doc:`click </feedback>`.

.. |success.png| image:: /_static/actions/create.png
.. |error.png| image:: /_static/actions/delete.png

.. index:: Messages

| Directly below this panel messages are displayed.
  It can be error messages - |error.png|, or success message - |success.png|.
  They all differs by icons. The colour of background is one - pale yellow.
  


Login page
====================================

.. index:: Login page

| Login page is very simple. You just need to write you *login name* and *password*.
  If you forget to fill in some fields the error *'This field is required'* will be displayed.
  Also if you incorrectly fill in your password and/or login error
  '*Please enter a correct username and password*' will be displayed.
  Note that both fields are case-sensitive.
  After login you will be redirect to page from witch you come.
  To verify are you login or not just look at the greeting, there should be your nickname.



Home page
====================================

.. index:: Home page

| Every user even Anonymous have his home page.
  Where all available file libs are located.
  There may be one or two blocks of file libs.
  If you not login you only see one block *'file libraries'*.
  In either case, you see *'{User name} file libraries'*  and *'Anonymous file libraries'*.
  In each row there are name and description on the right and links to trash and history pages on the left.
  To go to the file lib page, just click anywhere on the line, except places next to trash and history links.

File lib page
====================================

.. index:: File lib page

| File lib page contain table with files and actions, and some other info.
  All in all there are 3 columns: file name, permitted actions, size and modified time.
  Lets start from the end. Time is not needed explanation.
  Size, if it is a file the size will be displayed.
  It is because to check directory size is long work.
  Permissions. All permits display like icons.
  But you can hover cursor to the icon and short description will be raise.
  Here all action icons.

.. |down.png| image:: /_static/actions/down.png
.. |zip.png| image:: /_static/actions/zip.png
.. |rename.png| image:: /_static/actions/rename.png
.. |move.png| image:: /_static/actions/move.png
.. |create.png| image:: /_static/actions/create.png
.. |delete.png| image:: /_static/actions/delete.png

.. index:: Actions

* | |down.png| - Download file or directory.
    File start downloading to your computer after you click it.
    But directories can raise message to wait.
    It is because server have to archive directory first.
    So wait a minute and click to download again.

* | |zip.png| - Zip file or directory. If it is already archived it will be unziped.
    Archiving is a long operation so you need to wait a little.
    The archived name '.zip' extension will be added.
    If the such name already exists, new name will look something like this *file name[n].zip*

* | |rename.png| - Rename file or directory. After click on a icon the text box will appear.
    Enter new name and click *ok*. Do not use special chars like '/'.
    If the file already exists the error show up.

* | |move.png| - Move file or directory. After click on a icon the text box will appear.
    There are some trick. If you want to copy object ant indicate absolute path to directory,
    just add slash to the beginning of string. Like this */some/path*.
    If you want to start from the directory where you are, write something like this *some/path*.
    Also you can start path with *../* to step one directory back.
    For example if you in */some/path* and you want to walk into */some/path2*.
    Write to the text filed *../path2* or absolute */some/path2*.
    And then click *ok*.
  
* | |create.png| - Some times you need to share some file or even a folder with someone.
    But you don't want to give him your login and password.
    In this case limited have cool feature - direct link.
    Just click on this action and copy link from shown message.
    Now you can get files just following this link.
    But there is one restriction, link acts during some time (a week by default).
    If you forget link, click again. The system detect automatically to create new or show you old.

* | |delete.png| - Delete file or folder. In fact, no objects deleted.
    All files move to trash bin. From witch you can easily move it back or remove completely.
    to read more about trash page go :ref:`here <trash_page>`.


History page
====================================

.. index:: History page

Turn you brain OFF :-)  The documentation is not ready yet


Trash page
====================================

.. index:: Trash page

.. _trash_page:

Relax, take a cup of tee :-)  The documentation is not ready yet