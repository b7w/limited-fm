# -*- coding: utf-8 -*-

import os
import shutil
import stat
import sys

# START SETTINGS
DOCS_OUT_DIR = "html"
STATIC_DIR = "static"
TMP_DIRECTORY = "tmp"
TEST_SETTINGS = "settings"
CHMOD = 644
# END SETTINGS


PROJECT_PATH = os.path.realpath( os.path.dirname( __file__ ) )
MANAGE_PATH = os.path.join( PROJECT_PATH, "manage.py" )
STATIC_PATH = os.path.join( PROJECT_PATH, STATIC_DIR )
TMP_PATH = os.path.join( PROJECT_PATH, TMP_DIRECTORY )
HG_PATH = os.path.join( PROJECT_PATH, ".hg" )

__all__ = ['check', 'clear', 'docs', 'static', 'test', 'update']

# Helpers
def list_files( path, ends=None ):
    """
    Return list with full path paths to all files under ``path`` directory.
    if ``ends`` contains list of file extensions only this files will be included.
    """

    def _list_files( path, array):
        for name in os.listdir( path ):
            full_path = os.path.join( path, name )
            if os.path.isdir( full_path ):
                array = _list_files( full_path, array )
            if os.path.isfile( full_path ):
                if ends != None:
                    for ext in ends:
                        if full_path.endswith( '.' + ext ):
                            array.append( full_path )
        return array

    return _list_files( path, [] )


class CheckTry:
    """
    run ``self.func`` in try..except block and check for ImportError, Exception, else.
    At witch print ``self.import_out`` and ``self.except_out`` and ``self.success_out``
    """

    def __init__(self):
        self.func = None
        self.import_out = None
        self.except_out = None
        self.success_out = None

    def check(self):
        try:
            self.func( )
        except ImportError:
            print( self.import_out )
        except Exception:
            print( self.except_out )
        else:
            print( self.success_out )


# main commands
#  also listed in ``__all__``
def test( settings=None ):
    """
    Run limited tests.
    Arg ``settings`` is a django setting module to test with.
    """
    SETTINGS = TEST_SETTINGS
    if settings:
        SETTINGS = settings
    MANAGE_PATH = os.path.join( PROJECT_PATH, "manage.py" )
    RUN = "python -B {manage} test {app} --settings=limited.{settings}; return 0"
    clear( )
    if not os.path.exists( TMP_PATH ):
        os.mkdir( TMP_PATH )
    os.system( "clear" )
    os.system( RUN.format( manage=MANAGE_PATH, app="lviewer", settings=SETTINGS ) )
    os.system( RUN.format( manage=MANAGE_PATH, app="core", settings=SETTINGS ) )


def static( settings=None ):
    """
    Collect and gzip static files.
    Delete previous folder.
    Arg ``settings`` is a django setting module to import STATIC_ROOT.
    """

    if settings:
        django_settings = __import__( settings )
        STATIC = django_settings.STATIC_ROOT
    else:
        STATIC = STATIC_PATH
    print( "[ INFO ] Collect and gzip static " )
    os.system( "python -B {manage} collectstatic --noinput".format( manage=MANAGE_PATH ) )

    files = list_files( STATIC, ("css", "js",) )
    for item in files:
        os.system( "gzip -6 -c {0} > {0}.gz".format( item ) )
    os.system( "find {0} -type f -exec chmod {1} {{}} \;".format( STATIC_PATH, CHMOD ) )


def docs():
    """
    Build docs with sphinx
    """
    if os.path.exists( "/usr/local/bin/sphinx-build" ) or os.path.exists( "/usr/bin/sphinx-build" ):
        print( "[ INFO ] Build documentation " )
        DOCS_BUILD = "sphinx-build -b html -d {tmp} {source} {out}"
        DOCS_TMP = os.path.join( TMP_PATH, "docs" )
        DOCS_OUT_PATH = os.path.join( PROJECT_PATH, DOCS_OUT_DIR )
        DOCS_SOURCE_PATH = os.path.join( PROJECT_PATH, "docs" )
        if os.path.exists( DOCS_OUT_PATH ):
            shutil.rmtree( DOCS_OUT_PATH )
        os.system( DOCS_BUILD.format( tmp=DOCS_TMP, source=DOCS_SOURCE_PATH, out=DOCS_OUT_PATH ) )
        os.system( "find {0} -type f -exec chmod {1} {{}} \;".format( DOCS_OUT_PATH, CHMOD ) )
    else:
        print( "[ INFO ] No sphinx-build found" )


def clear():
    """
    Remove files like .pyc and .pyo
    """
    print( "[ INFO ] Clear pre compile files " )
    if os.path.exists( TMP_DIRECTORY ):
        shutil.rmtree( TMP_DIRECTORY )
    files = list_files( PROJECT_PATH, ("pyc", "pyo",) )
    for item in files:
        os.remove( item )


def check( tag="default" ):
    """
    Check installed programs, libraries and new changes in default branch
    """
    print( "[ INFO ] Check installed programs and limited updates" )
    print( "" )
    # Easy install
    if os.path.exists( "/usr/bin/easy_install" ):
        print( "[ INFO ] Easy_install exists" )
    else:
        print( "[ INFO ] No easy_install exists" )
        print( "\t sudo apt-get install python-setuptools" )

    # Django
    def _django():
        if __import__( 'django' ).VERSION[1] < 3:
            raise

    django = CheckTry( )
    django.func = _django
    django.import_out = "[ INFO ] No django exists\n\t sudo easy_install -U django"
    django.except_out = "[ INFO ] Django 1.3 version is needed\n\t sudo easy_install -U django"
    django.success_out = "[ INFO ] Django exists"
    django.check( )

    # flup
    flup = CheckTry( )
    flup.func = lambda: __import__( "flup" )
    flup.import_out = "[ INFO ] No Python flup library exists\n\t sudo apt-get install python-flup"
    flup.success_out = "[ INFO ] Python flup library exists"
    flup.check( )

    # MySQLdb
    mysqldb = CheckTry( )
    mysqldb.func = lambda: __import__( "MySQLdb" )
    mysqldb.import_out = "[ INFO ] No Python MySQLdb library exists\n\t sudo apt-get install python-mysqldb"
    mysqldb.success_out = "[ INFO ] Python MySQLdb library exists"
    mysqldb.check( )

    # Psycopg
    psycopg = CheckTry( )
    psycopg.func = lambda: __import__( "psycopg2" )
    psycopg.import_out = "[ INFO ] No Python Psycopg library exists\n\t sudo apt-get install python-psycopg2"
    psycopg.success_out = "[ INFO ] Python Psycopg library exists"
    psycopg.check( )

    # PIL
    pil = CheckTry( )
    pil.func = lambda: __import__( "PIL" )
    pil.import_out = "[ INFO ] No Python image library exists\n\t sudo apt-get install python-imaging"
    pil.success_out = "[ INFO ] Python image library exists"
    pil.check( )

    # Sphinx
    if os.path.exists( "/usr/local/bin/sphinx-build" ) or os.path.exists( "/usr/bin/sphinx-build" ):
        print( "[ INFO ] Sphinx-build exists" )
    else:
        print( "[ INFO ] No sphinx-build exists" )
        print( "\t sudo apt-get install python-sphinx" )
        print( "\t sudo easy_install -U sphinx" )

    #Settings file permissions
    files = []
    for item in os.listdir( PROJECT_PATH ):
        full_path = os.path.join( PROJECT_PATH, item )
        if os.path.isfile( full_path ) and 'setting' in item.lower( ):
            mode = os.stat( full_path ).st_mode
            # other
            if bool( mode & stat.S_IROTH ) and bool( mode & stat.S_IROTH ):
                files.append( item )
    if files == []:
        print( "[ INFO ] Settings file permissions right" )
    else:
        print( "[ INFO ] Settings file permissions not right" )
        for file in files:
            print( "\t Other can read file '{0}'".format( file ) )

    # HG updates
    print( "" )
    RUN = "hg incoming --branch {branch} --template '{{rev}} {{desc|firstline}}\n'; return 0"
    RUN2 = "hg log -l 5 --template '{{rev}} {{desc|firstline}}\n'"
    if os.path.exists( HG_PATH ):
        print( "[ INFO ] LimitedFM updates" )
        os.system( RUN.format( branch=tag ) )
        print( "" )
        print( "[ INFO ] LimitedFM hg log" )
        os.system( RUN2.format( ) )
    else:
        print( "[ INFO ] No mercurial vcs exists, can't check for updates" )


def update( tag="default", settings=None ):
    """
    Pull/up ``tag`` version, collect static, build docs
    """
    print( "[ INFO ] Update project " )
    clear( )

    if os.path.exists( HG_PATH ):
        os.system( "hg pull" )
        os.system( "hg up {commit}".format( commit=tag ) )

    static( settings=settings )
    docs( )


def usage():
    """
    Print usage for commands
    """
    print( "It is a small helper to install and run LimitedFM" )
    print( "Usage: python fabfile.py command [arg arg2]" )
    print( "Usage: fab command[:arg,arg2] command .." )
    print( "" )
    module = sys.modules[__name__]
    for item in __all__:
        attr = module.__dict__[item]
        print( "{name} {doc}".format( name=item, doc=attr.__doc__ ) )
    sys.exit( )


def main():
    module = sys.modules[__name__]
    if len( sys.argv ) == 1:
        usage( )
    else:
        name = sys.argv[1]
        if name not in __all__:
            usage( )
        args = sys.argv[2:]
        func = module.__dict__[name]
        func( *args )

if __name__ == "__main__":
    main( )