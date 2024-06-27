# [LabelmeToMaskApp](https://github.com/li-jin-1998/LabelmeToMaskApp)

To generate a project description for your LabelmeToMaskApp, here's a structured outline you can use:

---

**Project Description: LabelmeToMaskApp**

**Overview:**
LabelmeToMaskApp is a versatile desktop application designed to streamline the conversion process of Labelme annotations into corresponding image masks. Built using PyQt5, the application provides a user-friendly interface for managing datasets, configuring directories, and executing conversion tasks efficiently.

**Key Features:**
1. **Conversion Functionality:** Converts Labelme JSON annotations to image masks with customizable class mappings.
   
2. **Directory Management:** Allows users to browse, select, and confirm directories for data input and output.
   
3. **Dataset Handling:** Supports creation, deletion, and opening of dataset directories directly from the application.
   
4. **User Interface:** Offers an intuitive GUI with progress bars, runtime indicators, and error handling for smooth operation.
   
5. **Configuration Persistence:** Saves user preferences such as default directories, window size, and position using a JSON configuration file.

**Technologies Used:**
- **Python:** Core language for application logic and backend processing.
- **PyQt5:** GUI framework for creating the interactive user interface.
- **OpenCV (cv2):** Image processing library for handling image and mask generation.
- **NumPy:** Used for efficient numerical operations on arrays, especially in image manipulation.
- **PyInstaller:** Tool used for packaging the application into a single executable file (.exe) for easy distribution.

**PyInstaller Installation Guide:**
```
pyinstaller --clean main.spec
```


**Usage Scenario:**
LabelmeToMaskApp is ideal for researchers and developers working with labeled image datasets, enabling them to quickly transform Labelme annotations into machine-readable formats like image masks. By simplifying the conversion process and providing robust directory management, it enhances productivity in preparing data for machine learning tasks.

**Future Enhancements:**
Future updates may include:
- Batch processing capabilities for handling large datasets more efficiently.
- Enhanced error logging and reporting features for better troubleshooting.

**Conclusion:**
LabelmeToMaskApp empowers users to convert Labelme annotations to image masks effortlessly, ensuring compatibility and efficiency in data preprocessing tasks. With its intuitive interface and robust functionality, it caters to both novice and experienced users in the field of computer vision and machine learning.