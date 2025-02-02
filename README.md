# CrossTaskManager  

CrossTaskManager is a cross-platform desktop task management application built with PyQt5. It provides users with real-time system monitoring through an intuitive and visually appealing interface. The application features interactive tables, pie charts, and graphs to visualize system resource usage.

---

## Features  

### 1. **Main Tab**  
- Displays a table with all major system processes.
- **Functions:**  
  - **Sorting:** Click on any column header (like Memory) to sort processes in ascending order; click again for descending order.  
  - **Process Management:**  
    - **Kill:** Right-click on any process to terminate it.  
    - **More Details:** Opens a window showing detailed information about the selected process.  

### 2. **Piecharts Tab**  
- Displays live system information using pie charts:  
  - **Storage Usage**  
  - **Network (Download and Upload)**  
  - **CPU Usage (Idle/Active)**  
  - **Memory Usage**  

### 3. **Graphs Tab**  
- Displays dynamic system performance graphs:  
  - **CPU Usage Graph**  
  - **Memory Usage Graph**  
  - **Disk Read/Write Graph**  

---

## Code Structure  

![image](https://github.com/user-attachments/assets/e164d16f-5abe-42ff-992c-9a86b0973e7d)

- **Classes:** Separate classes for each tab and the main application interface.  
- **Utilities:** A dedicated module for gathering and processing system information.  

---

## How to Build the Application  

To build the application using `PyInstaller`, ensure that you include all styling and icon files for a complete build.  

### Build Command:  
```bash
pyinstaller --onefile --windowed --add-data "styles.qss" --add-data "piechartwindow.qss" --add-data "styles.qss" --add-data "logo.png" --add-data "logo.ico" main.py
```

---

## Installation  

1. Clone the repository:  
   ```bash
   git clone https://github.com/ZakriaComputerEngineer/CrossTaskManager.git
   cd CrossTaskManager
   ```  
2. Install dependencies:  
   ```bash
   pip install PyQt5 psutil matplotlib
   ```  
3. Run the application:  
   ```bash
   python main.py
   ```

---

## Screenshots  

![image](https://github.com/user-attachments/assets/d3245282-5cfb-43b1-a226-adb8e4c6b514)
![image](https://github.com/user-attachments/assets/55bbc649-83b4-4296-9855-6d71c7a08981)
![image](https://github.com/user-attachments/assets/df563f4f-805e-4278-b768-2bf8f523215d)

---
