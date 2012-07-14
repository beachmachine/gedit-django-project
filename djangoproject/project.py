import os
import imp
import sys
import logging

logging.basicConfig()
LOG_LEVEL = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

class DjangoProject(object):

    def __init__(self, path):
        self.set_path(path)

    def close_project(self):
        sys.path.remove(self._path)
        try:
            del os.environ['DJANGO_SETTINGS_MODULE']
        except:pass

    def activate_virtualenv(self, path):
        """
        Activates the virtualenv if necessary. Traverses the projects path up
        to the file system root and checks if 'bin/activate_this.py' exists
        in the directories. If this file is found, it gets loaded.
        """
        parent_path = os.path.dirname(path)

        if parent_path == path:
            logger.debug("No virtualenv found.")
            return

        activate_this = os.path.join(path, 'bin', 'activate_this.py')
        if not os.path.isfile(activate_this):
            self.activate_virtualenv(parent_path)
            return

        imp.load_source('activate_this', activate_this)
        logger.debug("Activated virtualenv: %s" % path)

    def get_path(self):
        """
        Return the path to the django project (where settings.py and manage.py
        are found).
        """
        return self._path

    def set_path(self, path):
        """
        Set Path

        Set the full filesystem path to where the Django project files are stored
        or raise IOError if the path does not exist or if settings.py or manage.py
        cannot be found in the path.
        """
        self.activate_virtualenv(path)

        if not os.path.exists(path):
            raise IOError("Django project directory does not exist: %s" % path)
        manage = os.path.join(path, 'manage.py')

        if not os.path.isfile(manage):
            raise IOError("Django manage file does not exist: %s" % manage)

        orig_cwd = os.getcwd()
        os.chdir(path)
        sys.path.append(path)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

        # Load the manage module, so the DJANGO_SETTINGS_MODULE environment
        # variable gets set. Loading may fail, but setting DJANGO_SETTINGS_MODULE
        # hopefully don't.
        try:
            orig_sys_argv = sys.argv
            sys.argv = ['manage.py', '--version']

            imp.load_source('__main__', manage)
            logger.debug("Loaded manage module: %s" % manage)

            sys.argv = orig_sys_argv
        except:
            raise IOError("Django manage module could not get loaded")

        # Now we try to load the settings module and get the file path.
        try:
            __import__(os.environ['DJANGO_SETTINGS_MODULE'], globals(), locals(), [], -1)
            mod_settings = sys.modules[os.environ['DJANGO_SETTINGS_MODULE']]
            settings = mod_settings.__file__
            logger.debug("Loaded settings module: %s" % settings)
        except:
            raise IOError("Django settings could not get loaded")

        self._path = path
        self._settings = settings
        self._manage = manage

        os.chdir(orig_cwd)

    def get_settings_filename(self):
        return self._settings

    def get_manage_filename(self):
        return self._manage
