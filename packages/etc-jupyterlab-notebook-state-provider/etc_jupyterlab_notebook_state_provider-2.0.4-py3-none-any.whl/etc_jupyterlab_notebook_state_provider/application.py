from .handlers import RouteHandler
from jupyter_server.extension.application import ExtensionApp
# import pprint

class ETCJupyterLabNotebookStateProviderApp(ExtensionApp):

    name = "etc_jupyterlab_notebook_state_provider"
    # default_url = "/etc-jupyterlab-notebook-state-provider"
    # load_other_extensions = True
    # file_url_prefix = "/render"

    # def initialize_settings(self):

    #     try:
    #         self.log.info(f"ETCJupyterLabNotebookStateProviderApp.config {pprint.pformat(self.config)}")
    #     except Exception as e:
    #         self.log.error(str(e))

    # def initialize_settings(self):
    #     self.log.info(f"Config {self.config}")

    def initialize_handlers(self):

        self.handlers.extend([(r'/etc-jupyterlab-notebook-state-provider/(.*)', RouteHandler)])

