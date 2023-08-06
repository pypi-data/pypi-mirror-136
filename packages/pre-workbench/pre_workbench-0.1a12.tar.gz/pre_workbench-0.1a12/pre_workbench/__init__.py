
import os.path
import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen, QStyleFactory

from pre_workbench import configs, guihelper
from pre_workbench.configs import SettingsSection
from pre_workbench.mainwindow import WorkbenchMain
from pre_workbench.syshelper import load_file_watch


print("PYTHONPATH = ",os.environ["PYTHONPATH"])

def run_app():
	from PyQt5.QtWidgets import QApplication

	app = QApplication(sys.argv)
	splashimg = configs.respath("icons/splash.jpg")
	splash = QSplashScreen(QPixmap(splashimg))
	splash.show()

	configs.registerOption(SettingsSection('View', 'View', 'Theme', 'Theme'),
						   "AppTheme", "Theme", "select", {"options": [(x, x) for x in QStyleFactory.keys()]},
						   "fusion", lambda key, value: app.setStyle(value))
	load_file_watch(app, os.path.join(os.path.dirname(__file__), "stylesheet.css"), lambda contents: app.setStyleSheet(contents))
	ex = WorkbenchMain()
	guihelper.MainWindow = ex
	ex.show()
	splash.finish(ex)
	# os.system("/home/mw/test/Qt-Inspector/build/qtinspector "+str(os.getpid())+" &")
	sys.exit(app.exec_())

