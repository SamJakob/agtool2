from app.abstract import AbstractPlugin, AbstractController


class AGPlugin(AbstractPlugin):
    """
    Base class for all plugins.
    """

    def __init__(self, controller: AbstractController):
        self.controller: AbstractController = controller
        """The application controller"""
