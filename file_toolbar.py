from PyQt5.QtWidgets import QFileDialog
import ctypes
import os


def create_new_project(self):

    # Open a file dialog to get the name and location of the new project
    new_project_path, _ = QFileDialog.getSaveFileName(self, "New EPANET Project", "", "EPANET Map Files (*.map)")
    
    if not new_project_path:
        self.statusBar().showMessage(f"No filepath selected.")
        return  # If no path is selected, do nothing

    # Create a new EPANET project (this involves opening the toolkit and initializing a project)
    try:
        epanet_lib = ctypes.CDLL(os.path.join('epanet22_toolkit', 'epanet2.dll'))
        epanet_lib.ENinit.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
        epanet_lib.ENinit.restype = ctypes.c_int

        rpt_file = "report.rpt".encode('utf-8')
        out_file = "output.out".encode('utf-8')
        units_type = 1  # Example unitsType (you need to refer to EPANET documentation for valid types)
        headloss_type = 1
        
        result = epanet_lib.ENinit(rpt_file, out_file, units_type, headloss_type)

        # Check if the call was successful (result == 0 means success)
        if result == 0:
            print("ENinit called successfully.")
        else:
            print(f"ENinit failed with error code {result}.")
        
        # Notify the user
        self.statusBar().showMessage(f"New project created successfully: {new_project_path}")

    except Exception as e:
        # If an error occurs, show a message box
        self.statusBar().showMessage(f"Failed to create the project: {str(e)}")
    