============
About
============

What this does
--------------
This user interface is designed for the automation of running Python programs via the concept of program control. The basic idea behind this concept is that a user can abstract their interaction with a program via the use of a control file. This control file contains nothing more than values to be sent to the program. This way a user can just select a program, and a control file with input for that program, and then press a button to set that program running. If the user decides to change their program input, they need only change the control file. This user interface provides a visual way for a user to select a Python program, and a control file to pass values to that program. A Python program being a function within a Python module file and the control file being a .txt file listing function parameter names and values to be passed to those parameters.

How to use it
-------------
`TL;DR`_ at the bottom.

To run a program using this user interface, the you, the user, must assign a minimum of three key parameters.
 - The location of a Python module
 - A function within that module
 - The location a control file

**What is a Python module?** By definition a Python module is ``"a file containing Python definitions and statements."`` For the purposes of this user interface it is simply a .py file containing function definitions (``def`` statements).

**Selecting a Module** There are two ways to select a Python module using this interface. The first, recommended, method is by pressing the file selection button on the right side of the first text field. That button will open a file browser that you can use to navigate to and select a module. Selecting a module using the file browser will automatically load that module into the interface. The second method to select a module is manually type the path of a module into the first text field and pressing the enter key.

**Selecting a Function** There are two ways to select a function within a selected module using this user interface. These two methods are similar to the two methods of selecting a module. The first, recommended, method is to open the function selection menu by pressing the ``"SELECT"`` button located to the right of the second text field. The menu will list the name and parameter names of every function within the selected module. You can then select the function you want to run from this list. The second method of selecting a function is by manually typing the function name into the second text field (note that you are not required to type parameter names into the text field).

**Wait, where's my function?** As per Python convention any functions whose name starts with the character '_' should be treated as though it is non-public. Consequently functions whose name starts with the character '_' have been filtered out of the function selection menu. Don't worry, you can still run these functions by manually typing their name into the second text field. For info visit `https://docs.python.org/3/tutorial/classes.html#tut-private <https://docs.python.org/3/tutorial/classes.html#tut-private>`_.

**Selecting a Control File** Similar to selecting, you can either select the path to a control file by pressing the file selection button which opens a file browser or by manually typing the path to the control file.

**How to format the Control File** The control file should be a .txt file that lists the parameters of a function, one parameter per line with the parameter followed by ": " and ending with the value to be passed to that parameter. For example take the function ``foobar(in_txt, out_csv).`` The control file for this function would look like this:

``in_txt: path/to/txt/foo.txt``

``out_csv: path/to/csv/bar.csv``

Notes: The inclusion of optional parameters is optional. The name of the parameter that appears before the colon does not have to match the name of a parameter in the function definition, however **ORDER MATTERS!!!** Parameters will be passed to the function in the order in which they appear, NOT BY PARAMETER NAME!!! (<- just want to reiterate that this is important). This user interface comes with tools to generate and maintain control files see `Maintaining Control Files`_.

**You're all set!** Press the run button to run the function selected.

**Notes on output:** There are two options for viewing the STDOUT of your function. The first and default option is to write all STDOUT along with what your function returns to a log file. The second option is to direct output to the text area and the bottom of the user interface this option is enabled by disabling the log file checkbox.

.. _TLDR:

TL;DR
*****************

**Select a Module** Either type the path to a .py in the first text field and press enter or select a file by pressing the file button.

**Select a Function** Either type name of a function in the second  text field  or select a function by pressing the button that says ``"SELECT"``.

**Select a Control File** Either type the path to a .txt control file in the third text field or select a file by pressing the file button.

**Press the RUN button** Press the ``RUN`` button.

.. _Maintaining control files:

Maintaining Control Files
-------------------------
Also included in this interface is a tool to auto-generate control files and an editor for control files.

**Control File Generation** Under the tab `"Generate Control Files"` is a tool for generating correctly formatted control files for all functions within a given module. Simply input the path to folder in the text area titled `"Generate Control Files Folder Location"` or select a folder by pressing the file button. Now press the `"GENERATE"` button and the program will output correctly a formatted control file for each function in the currently loaded module.

**Control File Editor** Also in this interface is tool for editing control files. Either type the path to a file in the text area titled `"Edit Control File Location"` and press enter or simply select a control file by pressing the file icon. After loading a control file, a line will appear for each parameter in the file. Each line will have the parameter name, a text area to type a value for that parameter, and a file icon that will put a file path into the text area. When you are finished editing, simply press the `"SAVE"` button and your changes will be saved to the control file.