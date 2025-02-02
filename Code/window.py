from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QTableWidgetItem, QMenu, QTableWidget, QSizePolicy, QHeaderView, QAbstractItemView, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
import os
from PyQt5 import QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from utilities import get_network_stats, getDiskInfo, getDiskRunInfo, getProcesses, getSystemStats, kill_process, show_details, format_memory, update_system_data


class MainWindow(QWidget):
    def __init__(self, system_monitor_app):
        super().__init__()

        self.system_monitor_app = system_monitor_app
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(15)
        self.tableWidget.setHorizontalHeaderLabels(
            ['PID', 'Process Name', 'User/Owner', 'Status', 'CPU %', 'Memory', 'MB/KB',
             'Disk I/O (Read/Write)', 'Network I/O (Receive/Send)',
             'Priority', 'Threads', 'Uptime', 'Executable Path', 'Parent PID (PPID)', 'Process Type']
        )

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(
            self.open_context_menu)

        self.tableWidget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.tableWidget.setSortingEnabled(True)
        # Set the column to sort by memory (index 5 for 'Memory' column)
        memory_column_index = 5

        # Sort the table by memory in descending order (Qt.SortOrder.DescendingOrder)
        self.tableWidget.sortByColumn(
            memory_column_index, QtCore.Qt.DescendingOrder)

        # Optimize header resizing
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)

        # Set fixed column widths
        column_widths = [60, 140, 120, 80, 60, 80,     # PID, Process Name, User/Owner, Status, CPU %, Memory
                         # Disk I/O, Network I/O, GPU %, Priority, Threads, Uptime
                         70, 200, 100, 80, 90, 100,
                         300, 120, 120]
        for i, width in enumerate(column_widths):
            self.tableWidget.setColumnWidth(i, width)

        # Optionally restore vertical header (styled for minimal impact)
        self.tableWidget.verticalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setDefaultSectionSize(25)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)
        self.resize(800, 600)

        # Timer to update the process list
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_processes)
        self.timer.start(3000)  # Update every 3 second

        self.update_processes()

    def start_monitoring(self):
        self.timer.start(1000)  # Update chart every second

    def stop_monitoring(self):
        self.timer.stop()

    def update_processes(self):
        # Get the processes from the external function
        processes = getProcesses()

        self.tableWidget.setUpdatesEnabled(False)

        # Update the table in the main window with the current processes
        self.tableWidget.setRowCount(len(processes))
        for row, proc in enumerate(processes):
            # Use setData with Qt.EditRole for proper numeric sorting
            item_pid = QTableWidgetItem()
            item_pid.setData(Qt.EditRole, proc["pid"])
            self.tableWidget.setItem(row, 0, item_pid)

            self.tableWidget.setItem(row, 1, QTableWidgetItem(proc["name"]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(proc["user"]))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(proc["status"]))

            # Set CPU usage with '%' unit
            item_cpu = QTableWidgetItem()
            # Append '%' for CPU usage
            item_cpu.setData(Qt.EditRole, proc['cpu_percent'])
            self.tableWidget.setItem(row, 4, item_cpu)

            # Set memory usage with appropriate unit (e.g., MB or GB)
            item_memory = QTableWidgetItem()
            # Assuming proc["memory_unit"] contains the unit, e.g., 'MB', 'GB'
            # Add the memory unit
            item_memory.setData(
                Qt.EditRole, proc['memory'])
            self.tableWidget.setItem(row, 5, item_memory)

            self.tableWidget.setItem(
                row, 6, QTableWidgetItem(proc["memory_unit"]))

            self.tableWidget.setItem(
                row, 7, QTableWidgetItem(proc["disk_io_read_write"]))
            self.tableWidget.setItem(
                row, 8, QTableWidgetItem(proc["network_io_receive_send"]))

            self.tableWidget.setItem(
                row, 9, QTableWidgetItem(proc["priority"]))

            item_threads = QTableWidgetItem()
            item_threads.setData(Qt.EditRole, proc["threads"])
            self.tableWidget.setItem(row, 10, item_threads)

            self.tableWidget.setItem(row, 11, QTableWidgetItem(proc["uptime"]))
            self.tableWidget.setItem(
                row, 12, QTableWidgetItem(proc["executable_path"]))

            item_ppid = QTableWidgetItem()
            item_ppid.setData(Qt.EditRole, proc["parent_pid"])
            self.tableWidget.setItem(row, 13, item_ppid)

            self.tableWidget.setItem(
                row, 14, QTableWidgetItem(proc["process_type"]))

        self.tableWidget.setUpdatesEnabled(True)

    def open_context_menu(self, position):
        selected_item = self.tableWidget.itemAt(position)
        if selected_item:
            row = selected_item.row()
            pid = int(self.tableWidget.item(row, 0).text())
            process_name = self.tableWidget.item(row, 1).text()

            menu = QMenu()
            kill_action = menu.addAction("Kill")
            details_action = menu.addAction("Details")
            action = menu.exec_(self.tableWidget.mapToGlobal(position))

            if action == kill_action:
                self.kill_process(pid, process_name)
            elif action == details_action:
                self.show_process_details(pid)

    def kill_process(self, pid, process_name):
        if kill_process(pid):
            QMessageBox.information(
                self, "Process Killed",
                f"Process '{process_name}' with PID {pid} has been killed."
            )
        else:
            QMessageBox.critical(
                self, "Access Denied",
                "Unable to kill the process. Access denied. Please run the application as an administrator."
            )

    def show_process_details(self, pid):
        details = show_details(pid)
        if details:
            details_text = "\n".join(
                f"{key}: {value}" for key, value in details.items())
            QMessageBox.information(
                self, "Process Details",
                details_text
            )
        else:
            QMessageBox.warning(
                self, "Error",
                "Unable to fetch details for the process. It may no longer exist or access may be denied."
            )


class PieChartWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("System Stats Pie Charts")
        self.setGeometry(100, 100, 800, 600)

        # Set up grid layout with 2 columns
        self.layout = QGridLayout(self)
        self.layout.setSpacing(15)  # Space between charts

        # Load the stylesheet
        stylesheet_path = os.path.join(
            os.path.dirname(__file__), "piechartwindow.qss")
        self.apply_stylesheet(stylesheet_path)

        # Create a timer to update the charts every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pie_charts)
        self.timer.start(1000)  # Update every 1 second

        # Pie chart placeholders
        self.cpu_pie = None
        self.ram_pie = None
        self.disk_pie = None
        self.network_pie = None

        self.setLayout(self.layout)

    def start_chart_update(self):
        self.timer.start(1000)  # Update chart every second

    def stop_chart_update(self):
        self.timer.stop()

    def apply_stylesheet(self, stylesheet_path):
        """Apply the stylesheet from the specified file."""
        try:
            with open(stylesheet_path, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Error: Stylesheet file '{stylesheet_path}' not found.")

    def update_pie_charts(self):
        # Remove old charts to avoid overlapping
        if hasattr(self, 'layout'):
            for i in reversed(range(self.layout.count())):
                widget = self.layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()

        # Get the system stats
        system_stats = getSystemStats()
        disk_stats = getDiskInfo()
        network_stats = get_network_stats()

        # Data for the pie charts
        cpu_data = [system_stats["cpu"], 100 - system_stats["cpu"]]
        cpu_labels = ['Used', 'Free']
        self.update_chart(self.cpu_pie, "CPU Usage", cpu_data,
                          cpu_labels, "cpu", row=0, col=0)

        ram_data = [system_stats["ram_used"], system_stats["ram_free"]]
        ram_labels = ['Used', 'Free']
        self.update_chart(self.ram_pie, "RAM Usage", ram_data,
                          ram_labels, "ram", row=0, col=1)

        disk_data = [disk_stats["percent"], 100 - disk_stats["percent"]]
        disk_labels = ['Used', 'Free']
        self.update_chart(self.disk_pie, "Disk Storage",
                          disk_data, disk_labels, "disk", row=1, col=0)

        network_data = [network_stats["download"], network_stats["upload"]]
        self.update_chart(self.network_pie, "Network Activity", network_data, [
                          "Download", "Upload"], 'network', row=1, col=1)

    def update_chart(self, pie_chart, title, data, labels, chart_type, row, col):
        # Create a new figure and axis for each pie chart
        fig, ax = plt.subplots()

        # Draw the pie chart
        pie_chart = ax.pie(data, labels=labels, autopct='%1.1f%%',
                           startangle=90, colors=self.get_colors(chart_type))
        ax.set_title(title, fontsize=18, fontweight='bold',
                     color='#1e90ff')  # Title color and styling

        # Add the new pie chart to the grid layout at the specified row, col position
        canvas = FigureCanvas(fig)
        self.layout.addWidget(canvas, row, col)

        # Store the new pie chart in the class attribute to keep track of it
        setattr(self, f"{chart_type}_pie", pie_chart)

        # Close the figure to release memory
        plt.close(fig)

    def get_colors(self, chart_type):
        # Define refined and appealing colors for each chart type
        if chart_type == 'cpu':
            # Darker red for used, vibrant blue for idle
            return ['#e74c3c', '#3498db']
        elif chart_type == 'ram':
            # Vibrant orange for used, soft green for free
            return ['#f39c12', '#2ecc71']
        elif chart_type == 'disk':
            # Deep red for used, vibrant green for free
            return ['#c0392b', '#27ae60']
        elif chart_type == 'network':
            # Bright purple for download, deep blue for upload
            return ['#9b59b6', '#2980b9']
        else:
            # Default colors: vibrant green for one category, dark red for the other
            return ['#2ecc71', '#e74c3c']


class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Apply the dark theme for matplotlib
        plt.style.use('dark_background')

        # Create the graph figures and canvases with customized styles
        self.figure_cpu, self.ax_cpu = plt.subplots()
        self.canvas_cpu = FigureCanvas(self.figure_cpu)

        self.figure_ram, self.ax_ram = plt.subplots()
        self.canvas_ram = FigureCanvas(self.figure_ram)

        self.figure_disk, self.ax_disk = plt.subplots()
        self.canvas_disk = FigureCanvas(self.figure_disk)

        # Customize each graph
        self._customize_graph(self.ax_cpu, "CPU Usage (%)", "Time", "CPU %")
        self._customize_graph(
            self.ax_ram, "RAM Usage (MB)", "Time", "RAM (MB)")
        self._customize_graph(
            self.ax_disk, "Disk Usage (kB/s)", "Time", "Disk (kB/s)")

        # Set the layout for vertical arrangement of graphs
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas_cpu)
        layout.addWidget(self.canvas_ram)
        layout.addWidget(self.canvas_disk)

        # Ensure graphs stretch equally
        layout.setStretch(0, 1)  # Stretch for CPU graph
        layout.setStretch(1, 1)  # Stretch for RAM graph
        layout.setStretch(2, 1)  # Stretch for Disk graph

        self.setLayout(layout)
        self.setWindowTitle("System Graphs")

        # Timer to update graphs periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graphs)
        self.timer.start(1000)  # Update every 1 second

        # Data lists to store the values for CPU, RAM, and Disk stats
        self.cpu_data = []
        self.ram_data = []
        self.disk_data = []

    def start_graph_update(self):
        self.timer.start(1000)  # Update chart every second

    def stop_graph_update(self):
        self.timer.stop()

    def _customize_graph(self, ax, title, xlabel, ylabel):
        """Customizes the appearance of a graph."""
        ax.set_title(title, color="#1abc9c", fontsize=14, fontweight="bold")
        ax.set_xlabel(xlabel, color="#ecf0f1", fontsize=12)
        ax.set_ylabel(ylabel, color="#ecf0f1", fontsize=12)
        ax.grid(color="#34495e", linestyle="--", linewidth=0.5)
        ax.tick_params(axis="x", colors="#ecf0f1")
        ax.tick_params(axis="y", colors="#ecf0f1")

    def update_graphs(self):
        """Updates the graphs with system stats."""
        # Fetch and update system stats using the provided function
        self.cpu_data, self.ram_data, self.disk_data = update_system_data(
            self.cpu_data, self.ram_data, self.disk_data)

        # Limit the data list length
        max_data_points = 30
        self.cpu_data = self.cpu_data[-max_data_points:]
        self.ram_data = self.ram_data[-max_data_points:]
        self.disk_data = self.disk_data[-max_data_points:]

        # Update CPU graph
        self.ax_cpu.clear()
        self._customize_graph(self.ax_cpu, "CPU Usage (%)", "Time", "CPU %")
        self.ax_cpu.plot(self.cpu_data, color="#1abc9c",
                         linewidth=2, label="CPU")
        self.ax_cpu.legend(loc="upper right", fontsize=10)

        # Update RAM graph
        self.ax_ram.clear()
        self._customize_graph(
            self.ax_ram, "RAM Usage (GB)", "Time", "RAM (GB)")
        self.ax_ram.plot(self.ram_data, color="#3498db",
                         linewidth=2, label="RAM")
        self.ax_ram.legend(loc="upper right", fontsize=10)

        # Update Disk graph
        self.ax_disk.clear()
        self._customize_graph(
            self.ax_disk, "Disk Usage (kB/s)", "Time", "Disk (kB/s)")
        self.ax_disk.plot(self.disk_data, color="#e74c3c",
                          linewidth=2, label="Disk")
        self.ax_disk.legend(loc="upper right", fontsize=10)

        # Refresh canvases
        self.canvas_cpu.draw()
        self.canvas_ram.draw()
        self.canvas_disk.draw()

# Assume `update_system_data` is a function you have implemented elsewhere
# to fetch the latest CPU, RAM, and Disk data points.
