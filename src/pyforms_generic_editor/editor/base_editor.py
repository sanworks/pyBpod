import logging
import pkgutil

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

import pyforms_generic_editor
import pyforms_generic_editor.resources as rconf
import pyforms_generic_editor.settings as sconf
from pyforms_generic_editor.editor.generic_file_editor import GenericFileEditor
from pyforms_generic_editor.plugins import loader as plugin_loader
from pyforms_gui.basewidget import BaseWidget
from pyforms_gui.controls import control_dockwidget
from pyforms_gui.controls import control_mdiarea

logger = logging.getLogger(__name__)


class BaseEditor(BaseWidget):
	def __init__(self):
		BaseWidget.__init__(self, sconf.GENERIC_EDITOR_TITLE)

		self.mdi_area = control_mdiarea.ControlMdiArea()
		self.dock = control_dockwidget.ControlDockWidget(label='Projects', side=control_dockwidget.ControlDockWidget.SIDE_LEFT, order=1)
		self.details = control_dockwidget.ControlDockWidget(label='Details', side=control_dockwidget.ControlDockWidget.SIDE_RIGHT, order=2)

		self.dependencies = []
		self.plugins_classes = []

		self.mainmenu = [
			{'File': [
				{'Exit': self._exit_app, 'icon': QIcon(rconf.EXIT_SMALL_ICON)}
			]},
			{'Window': [
				{'Cascade all': self._option_cascade_all},
				{'Tile all': self._option_tile_all},
				'-',
				{'Show projects': self.dock.show},
				{'Show details': self.details.show},
			]},
			{'Options': [
				{'Edit user settings': self._edit_user_settings, 'icon': QIcon(rconf.USER_SETTINGS_ICON)}
			]},
			{'Help': [  # this option works for OSX also
				{'About QT': self._option_about_qt},
				{'About this project': self._option_about}
			]}
		]

		plugin_loader.install_plugins(self)  # Load plugins

		if sconf.GENERIC_EDITOR_MODEL:
			if isinstance(sconf.GENERIC_EDITOR_MODEL, str):
				c = self.__load_module(sconf.GENERIC_EDITOR_MODEL)
			else:
				c = sconf.GENERIC_EDITOR_MODEL
			self._model = c(self)

	def init_form(self):
		BaseWidget.init_form(self)

		# Loads a project automatically.
		if sconf.DEFAULT_PROJECT_PATH:
			try:
				self.model.open_project(sconf.DEFAULT_PROJECT_PATH)
			except Exception as err:
				for project in self.model.projects:
					project.close(silent=True)
				logger.warning(str(err), exc_info=True)
				self.warning("Please edit user settings.\n{0}".format(str(err)), "Invalid project path")

	def _option_close_all(self):
		self.mdi_area.value = []

	def _option_cascade_all(self):
		self.mdi_area.cascadeSubWindows()

	def _option_tile_all(self):
		self.mdi_area.tileSubWindows()

	def _option_about_qt(self):
		self.aboutQt("About Qt")

	def _option_about(self):
		plugins_info = ""
		for module in self.plugins_classes:
			try:
				version = module.__version__ if hasattr(module, '__version__') else 'Undefined'
				plugins_info += "<p>{0}: {1}</p>".format(str(module.__name__), version)
			except Exception as err:
				logger.error(str(err), exec_info=True)

		self.setWindowIcon(QIcon(rconf.APP_LOGO_ICON))
		text = """
				<html><body>
				<h2>About {gui_title}</h2>
				<p>Pyforms Generic Editor: {version}</p>
				<h3>Scientific Software Platform (Champalimaud Foundation)</h3>
				<p>The Scientific Software Platform (SWP) from the Champalimaud Foundation provides technical know-how in software engineering and high quality software support for the Neuroscience and Cancer research community at the Champalimaud Foundation. We typical work on computer vision / tracking, behavioral experiments, image registration and database management.
				<p><a href="mailto:admin.it@neuro.fchampalimaud.org">admin.it@neuro.fchampalimaud.org</a></p>
				<h3>License</h3>
				<p>This is Open Source software. We use the <a href="https://www.gnu.org/licenses/gpl.html">GNU General Public License version 3</a>.</p>
				<h3>Installed plugins</h3>
				{plugins_info}
				</body></html>
				""".format(gui_title=self.title, version=pyforms_generic_editor.__version__, plugins_info=plugins_info)
		self.about(text, "About")

	def _edit_user_settings(self):
		"""
		Open code editor window on the mdi section for the task source code.

		.. seealso::
			This event may be fired on:
				* Double click event (tree node): :py:meth:`pybpodgui_plugin.models.task.task_treenode.TaskTreeNode.node_double_clicked_event`.
				* Key press event (tree node): :py:meth:`pybpodgui_plugin.models.task.task_treenode.TaskTreeNode.node_key_pressed_event`.
		"""

		try:
			if not hasattr(self, '_user_settings_editor'):  # this only happens the first time this window is opened
				user_settings_path = pkgutil.get_loader("user_settings").get_filename()
				logger.debug("User settings path: %s", user_settings_path)
				self._user_settings_editor = GenericFileEditor(user_settings_path, "User settings editor", False)

			self.mdi_area += self._user_settings_editor
		except Exception as err:
			logger.error(err, exc_info=True)
			self.warning(str(err), "Unexpected error")

	def __load_module(self, module_name):
		modules = module_name.split('.')
		moduleclass = __import__('.'.join(modules[:-1]), fromlist=[modules[-1]])
		return getattr(moduleclass, modules[-1])

	def closeEvent(self, event):
		""" 
		Confirms exit on close
		"""

		event.accept() if self._confirm_exit() else event.ignore()

	def _exit_app(self):
		"""
		Exit app option from the menu
		"""
		if self._confirm_exit():
			QApplication.quit()

	def _confirm_exit(self):
		"""
		Prompts user to save projects changes and confirm exit
		
		:return: True to confirm exit and false otherwise
		:rtype: bool
		"""
		if self.model.is_saved():
			return True

		reply = self.question('Save all projects?', 'Save changes', buttons=['cancel','no','yes'])

		if reply=='yes':
			self.model.save_all_projects()
			return True
		elif reply=='no':
			return True
		else:
			return False

	@property
	def model(self):
		return self._model if hasattr(self, '_model') else None

	@model.setter
	def model(self, value):
		self._model = value
