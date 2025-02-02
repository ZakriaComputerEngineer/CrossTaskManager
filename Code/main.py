import sys
import os
from window import PieChartWindow, GraphWindow, MainWindow
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget


class SystemMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("System Monitor Application")
        self.setGeometry(100, 100, 1200, 800)

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'logo.png'))

        # Load the stylesheet
        stylesheet_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        self.apply_stylesheet(stylesheet_path)

        # Create the main tab widget
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        # Initialize the MainWindow, PieChartWindow, and GraphWindow
        self.main_window = MainWindow(self)
        self.piechart_window = PieChartWindow()
        self.graph_window = GraphWindow()

        # Add the windows to the tab widget
        self.tabs.addTab(self.main_window, "Processes")
        self.tabs.addTab(self.piechart_window, "Charts")
        self.tabs.addTab(self.graph_window, "Graphs")

        # Connect the tab change signal to handle tab focus change
        self.tabs.currentChanged.connect(self.on_tab_change)

    def on_tab_change(self, index):
        # Stop tasks for all tabs
        self.stop_all_tabs()

        # Start tasks only for the active tab
        if index == 0:  # "Processes" tab
            self.main_window.start_monitoring()
        elif index == 1:  # "Charts" tab
            self.piechart_window.start_chart_update()
        elif index == 2:  # "Graphs" tab
            self.graph_window.start_graph_update()

    def stop_all_tabs(self):
        # Stop all monitoring and updating tasks
        self.main_window.stop_monitoring()
        self.piechart_window.stop_chart_update()
        self.graph_window.stop_graph_update()

    def apply_stylesheet(self, stylesheet_path):
        """Apply the stylesheet from the specified file."""
        try:
            with open(stylesheet_path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Error: Stylesheet file '{stylesheet_path}' not found.")

    def switch_to_charts(self):
        # Switch to the charts view
        self.tabs.setCurrentIndex(1)  # Index 1 corresponds to the Charts tab

    def switch_to_graphs(self):
        # Switch to the graphs view
        self.tabs.setCurrentIndex(2)  # Index 2 corresponds to the Graphs tab


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMonitorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SystemMonitorApp()
    window.show()
    sys.exit(app.exec_())
