"""
Application factory: initialize DataManager, Coordinator and MainWindow.
"""
from data.data_manager import DataManager
from core.coordinator import Coordinator
from ui.main_window import MainWindow


def create_app(db_path: str = "data/app.db"):
    dm = DataManager(db_path=db_path)
    coord = Coordinator(data_manager=dm)
    main_window = MainWindow(coordinator=coord)
    return {
        "data_manager": dm,
        "coordinator": coord,
        "main_window": main_window,
    }