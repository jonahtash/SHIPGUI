from functools import partial
import io
import sys
import time
import os
from inspect import getmembers, isfunction, getargspec, signature
import importlib
from multiprocessing import freeze_support
import strconv
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.rst import RstDocument
from kivy.clock import Clock, mainthread
import kivy.garden.filebrowser as filebrowser
from kivy.core.clipboard import Clipboard
from kivy.config import Config
from kivy.base import EventLoop
import kivy.garden.contextmenu
from kivy.uix.behaviors.focus import FocusBehavior

from kivymd.button import MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.label import MDLabel
from kivymd.theming import ThemeManager
from kivymd.textfields import MDTextField
from kivymd.list import MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.dialog import MDDialog
from kivymd.selectioncontrols import MDSwitch, MDCheckbox
from kivymd.tabs import MDTabbedPanel, MDTab
from kivymd.spinner import MDSpinner
from kivymd.menu import MDDropdownMenu

# A few notes on the comments in this document;
# There are a number of variables/parameters that are semantically similar
# so, just to clarify here is an explanation of what each term refers to--
# Control Program/Control Module: this is the .py file that contains Python function definitions
# these functions are the "programs" that the user intends to run
# Control Function: the function within the Control Program to be run. Selected by the user
# Control File: the control file is a .txt file that lists the values to be passed to the selected Control Function
# Control Parameters: the parameter values contained within the Control File
# Also a few abbreviations:
# mod = module
# cntrl = control
# func = function
# param = parameter


kv = '''
#:import parse_color kivy.parser.parse_color
#:import Clipboard kivy.core.clipboard.Clipboard
#: import Window kivy.core.window.Window

<ScrollBetter>
    bar_width: 7
    height: dp(150)
    scroll_type: ['bars', 'content']

    
<PopupBox>
    cols: 1
    padding: dp(48)
    spacing: 10
    id: pup_box
    BoxLayout:
        orientation: 'horizontal'
        spacing: 30
        id: ctrl_select
        height: dp(48)
        size_hint_y: None
        MDTextField:
            id: cntrl_load_path
            hint_text: "Load From Control File"
            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
        IconHover:
            on_release: app.open_dialog(cntrl_load_path)
    ScrollBetter:
        pos_hint_y: 0
        GridLayout:
            id: param_grid
            cols: 1
            row_default_height: dp(65)
            row_force_default: True
            padding: dp(18)
            size_hint_y:None
    BoxLayout:
        orientation: 'horizontal'
        spacing: 30
        height: dp(48)
        size_hint_y: None
        MDButtonFixed:
            id: func_btn
            text: "SAVE CHANGES AS"
            opposite_colors: True
            size_hint: None, None
            size: 4 * dp(48), dp(48)
            pos_hint:    {'center_x': 0, 'center_y': 0.5}
            on_release: app.save_as_params(pup_box)
        MDButtonFixed:
            id: func_btn
            text: "DONE"
            opposite_colors: True
            size_hint: None, None
            size: 4 * dp(48), dp(48)
            pos_hint: {'center_x': 1, 'center_y': 0.5}
            on_release: app.dismiss_param(pup_box)

        


<StdoutBox@TextInput>
    height: dp(20)
    readonly: True
    
<IconHover>
    icon: 'file'
    pos_hint: {'center_x': 0.75, 'center_y': 0.5}

<CtrlParamEdit>
    height: dp(48)
    size_hint_y: None
    MDLabel:
        id: param_name
        font_style: "Subhead"
        size_hint_x: .2
        pos_hint_y: 1
        canvas.before:
            Clear
            Color:
                rgba: parse_color('#E0E0E0')
            RoundedRectangle:
                pos: self.pos[0]-15, self.pos[1]+5
                size: self.size[0],self.size[1]*.75
                radius: 15, 0, 0, 15
    MDTextField:
        size_hint_x: .6
        id: param_value
        on_focus: app.set_text_focused(self)
        canvas:
            Clear
            Color:
                rgba: 1,1,1,.25
            Rectangle:
                pos: self.pos[0]-15, self.pos[1]+5
                size: self.size[0],self.size[1]*.75
    IconHover:
        on_release: app.open_dialog(param_value)
        size_hint_x: .2

        
Screen:
    id: main
    name: 'tabs'
    ContextMenu:
        id: rclick_menu
        visible: False
        ContextMenuTextItem:
            text: "Copy"
            on_release: app.clip_action(self)
        ContextMenuTextItem:
            text: "Cut"
            on_release: app.clip_action(self)
        ContextMenuTextItem:
            text: "Paste"
            on_release: app.clip_action(self)
    MDTabbedPanel:
        id: tab_panel
        tab_display_mode:'text'

        MDTab:
            name: 'control'
            text: "Control Python"
            id: main_tab

            AnchorLayout:
                id: al
                anchor_x: 'center'
                anchor_y: 'center'
                BoxLayout:
                    id: main_tab_layout
                    orientation: 'vertical'
                    padding: dp(48)
                    spacing: 10
                    BoxLayout:
                        id: control_py
                        orientation: 'horizontal'
                        spacing: 30
                        MDTextField:
                            id: param
                            line_width: control_py.minimum_width-dp(36)
                            pos_hint:{'center_x': 0.75, 'center_y': 0.5}
                            hint_text: "Select Program"
                        IconHover:
                            on_release: app.open_dialog(param,dir_path="./programs")
                        MDSpinner:
                            id: mod_spinner
                            size_hint: None, None
                            size: dp(46), dp(46)
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                            active: False
                        
                    BoxLayout:
                        orientation: 'horizontal'
                        spacing: 30
                        id: funcs_select
                        MDTextField:
                            id: func_field
                            line_width: funcs_select.minimum_width-dp(36)
                            hint_text: "Function"
                            pos_hint: {'center_x': 0.75, 'center_y': 0.5}
                        MDButtonFixed:
                            id: func_btn
                            text: "FUNCTION"
                            opposite_colors: True
                            size_hint: None, None
                            size: 4 * dp(48), dp(48)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.open_menu_thread(func_field)
                        MDSpinner:
                            id: sel_spinner
                            size_hint: None, None
                            size: dp(46), dp(46)
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                            active: False
                    BoxLayout:
                        orientation: 'horizontal'
                        spacing: 30
                        id: cntrl_select
                        MDButtonFixed:
                            id: run_btn
                            text: "SET PARAMETERS"
                            opposite_colors: True
                            size_hint: None, None
                            size: 4 * dp(48), dp(48)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.open_param_pup()
                        MDButtonFixed:
                            id: run_btn
                            text: "RUN"
                            opposite_colors: True
                            size_hint: None, None
                            size: 4 * dp(48), dp(48)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.run_param(func_field)
                            disabled: len(app.run_parameter_list)<1
                        MDSpinner:
                            id: func_spinner
                            size_hint: None, None
                            size: dp(46), dp(46)
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                            active: False
                    BoxLayout:
                        spacing: 30
                        MDCheckbox:
                            id: log_swich
                            group: 'output'
                            size_hint: None, None
                            size: dp(36), dp(48)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            active: True
                            on_release: app.switch_out(self,log_path.text, outbox)
                        MDTextField:
                            id: log_path
                            hint_text: "Log File Location"
                            line_width: funcs_select.minimum_width-dp(36)
                            pos_hint: {'center_x': 0.75, 'center_y': 0.5}
                            text: "log.txt"
                            disabled: not log_swich.active
                        IconHover:
                            on_release: app.open_dialog(log_path)
                    BoxLayout:
                        spacing: 30
                        MDCheckbox:
                            id: box_swich
                            group: 'output'
                            size_hint: None, None
                            size: dp(36), dp(48)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            active: False
                            on_release: app.switch_out(log_path,log_path.text, outbox)
                        StdoutBox:
                            id: outbox
                            disabled: not box_swich.active
                            background_disabled_normal: 'res/disabled.png'
                            background_normal: 'res/enabled.png'
                            font_name: "DejaVuSans"
        MDTab:
            name: 'ctrlfiles'
            text: "Generate Control Files"
            id: ctrl_file

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                BoxLayout:
                    id: main_tab_layout
                    orientation: 'vertical'
                    padding: dp(48)
                    spacing: 10
                    BoxLayout:
                        id: control_files
                        orientation: 'horizontal'
                        spacing: 25
                        MDTextField:
                            id: folder_field
                            line_width: control_py.minimum_width-dp(36)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            hint_text: "Generate Control Files Folder Location"
                        IconHover:
                            on_release: app.open_dialog(folder_field)
                            icon: 'folder'
                        MDButtonFixed:
                            id: folder_btn
                            text: "GENERATE"
                            opposite_colors: True
                            size_hint: None, None
                            size: 4 * dp(48), dp(48)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.create_ctrl_files(folder_field)
                        MDSpinner:
                            id: folder_spinner
                            size_hint: None, None
                            size: dp(46), dp(46)
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                            active: False
        MDTab:
            name: 'ctrlfileedit'
            text: "Control File Editor"
            id: ctrl_file
            BoxLayout:
                id: ctrl_file_edit
                orientation: 'vertical'
                padding: dp(48)
                spacing: 20
                BoxLayout:
                    id: control_files_edit
                    orientation: 'horizontal'
                    spacing: 30
                    height: dp(48)
                    MDTextField:
                        id: ctrl_edit
                        line_width: control_py.minimum_width-dp(36)
                        pos_hint:    {'center_x': 0.75, 'center_y': .75}
                        hint_text: "Edit Control File Location"
                    IconHover:
                        on_release: app.open_dialog(ctrl_edit)
                        pos_hint:    {'center_x': 0.75, 'center_y': .75}
                ScrollBetter:
                    pos_hint_y: 0
                    GridLayout:
                        id: edit_params
                        cols: 1
                        row_default_height: dp(65)
                        row_force_default: True
                        padding: dp(18)
                        size_hint_y:None
                MDButtonFixed:
                    id: save_btn
                    text: "SAVE"
                    opposite_colors: True
                    size_hint: None, None
                    size: 4 * dp(48), dp(48)
                    pos_hint: {'center_x': 0.9, 'y': 0.8}
                    on_release: app.save_ctrl(ctrl_edit,edit_params)
                
        MDTab:
            name: 'help'
            text: "Help"
            id: help_tab
            RstDocument:
                underline_color: "0277BD"
                base_font_size: 31
                text: app.my_help_text
                colors: {'background': 'FAFAFA','link': '0D47A1','paragraph': '202020ff','title': '212121','bullet': '000000ff'}



                    
            
'''

help_text = '''
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

'''

# set a variable to the location of the user's home directory. Used to direct file browser
user_path = os.path.expanduser("~")
# by default output stdout to a file called 'log.txt' sys.stdout is assigned to this file object in MainApp.build
# the variable is assigned here for scope
f = open('log.txt','a')



"""BEGIN UTILITY FUNCTIONS"""
"""***********************"""
# strips leading and tailing ' and " chars		
def strip_quotes(s):
    if len(s)<=1:
        return s
    if s[0] == '"' or s[0] == "'":
        s = s[1:]
    if s[-1] == '"' or s[-1] == "'":
        s = s[:-1]
    return s


def _get_diff(l1,l2):
    ret = []
    for i in range(len(l1)):
        if l1[i] != l2[i]:
            ret.append([l1[i],l2[i]])
    return ret


# used to assign stdout to output 
def set_area(text_input):
    global f
    f = TextBoxOut(TextInput())
    f.my_text_input = text_input
    sys.stdout = f


"""*********************"""
"""END UTILITY FUNCTIONS"""


class PopupBox(GridLayout):
    potat = "potato"

class ScrollBetter(ScrollView):
    potat = "potato"
    
    
# Hover effects credit https://codecalamity.com/first-steps-into-gui-design-with-kivy/
class IconHover(MDIconButton):
    def __init__(self, **kwargs):
        Window.bind(mouse_pos=self._mouse_move)
        self.hovering = BooleanProperty(False)
        self.poi = ObjectProperty(None)
        self.register_event_type('on_hover')
        self.register_event_type('on_exit')
        super(IconHover, self).__init__(**kwargs)
 
    def _mouse_move(self, *args):
        if not self.get_root_window():
            return
        is_collide = self.collide_point(*self.to_widget(*args[1]))
        if self.hovering == is_collide:
            return
        self.poi = args[1]
        self.hovering = is_collide
        self.dispatch('on_hover' if is_collide else 'on_exit')
 
    def on_hover(self):
        self.opacity = .8
 
    def on_exit(self):
        self.opacity = 1

# Hover effects credit https://codecalamity.com/first-steps-into-gui-design-with-kivy/
class MDButtonFixed(MDRaisedButton):

    def on_disabled(self, instance, value):
        if instance.disabled:
            self.opacity = 1
            instance._current_button_color = self.md_bg_color_disabled
            instance.elevation = 0
        else:
            self._current_button_color = self.md_bg_color
            instance.elevation = instance.elevation_normal

    def __init__(self, **kwargs):
        Window.bind(mouse_pos=self._mouse_move)
        self.hovering = BooleanProperty(False)
        self.poi = ObjectProperty(None)
        self.register_event_type('on_hover')
        self.register_event_type('on_exit')
        super(MDButtonFixed, self).__init__(**kwargs)
 
    def _mouse_move(self, *args):
        if not self.get_root_window():
            return
        is_collide = self.collide_point(*self.to_widget(*args[1]))
        if self.hovering == is_collide:
            return
        self.poi = args[1]
        self.hovering = is_collide
        self.dispatch('on_hover' if is_collide else 'on_exit')
 
    def on_hover(self):
        if not self.disabled:
            self.opacity = .75
 
    def on_exit(self):
        self.opacity = 1


class CtrlParamEdit(BoxLayout):
    def build(self):
        pass
    
# output class that uses a kivy TextInput as its buffer
# used to caputes stdout to a TextInput
class TextBoxOut:
    my_text_input = None
    def __init__(self,text_input):
        self.my_text_input = text_input
    def write(self, txt):
        self.my_text_input.text += txt
    def flush(self):
        self.my_text_input.text = ""
    # f.close is called at the end of main
    # in the event that the program is closed when output is to a box
    def close(self):
        potato = 'this code(||-//)'

class MainApp(App):
    # the control program
    # default control program: None
    #cnrtl_mod = importlib.import_module("SHIP")
    cnrtl_mod = None
    # list of the functions within the control programs
    # stored in tuples of ("func_name_as_string", <ref_to_func>)
    #cnrtl_funcs = [o for o in getmembers(cnrtl_mod) if isfunction(o[1])]
    cnrtl_funcs = []
    # used for kivy themeing
    theme_cls = ThemeManager()
    # make help accessable to kv objects
    global help_text
    my_help_text = help_text

    text_fields = ['func_field','param','cntrl_path','log_path','folder_field','ctrl_edit']

    text_focused = None

    screen_popup = None


    # on_release event for checkbox controlling output location
    # when the check box is active (checked) std is directed to a log file whose location is given by a text field
    # if the box is not active, have std go to a TextInput at the bottom of the app
    def switch_out(self, button, log_path, area):

        global f
        if self.root.ids['log_swich'].active:
            f=open(log_path,'a')
            sys.stdout = f
        elif self.root.ids['box_swich'].active:
            set_area(area)
        else:
            sys.stdout=sys.__stdout__

    def set_text_focused(self, textf):
        self.text_focused = textf
    
    # used to switch module control program
    # called when new file is chosen for control program (first TextField)
    def set_mod(self,mod_path):
        path_a = mod_path.text.split('\\')
        try:  
            # add path to file selected to sys.path
            sys.path.append("\\".join(path_a[:-2]))
            # import module and it to cnrtl_mod field
            self.cnrtl_mod = importlib.import_module(path_a[-1].split('.')[0])
            # reassign list of functions to functions within new module
            self.cnrtl_funcs = [o for o in getmembers(self.cnrtl_mod) if isfunction(o[1])]
            self.root.ids.param.error=False
        except Exception as e:
            # if there is an error loading the module selected, use a dialog to display the error
            # most calls will likely be when the user selects a file that is not a module
            self.open_final_msg("Module Error","Error loading: "+path_a[-1].split('.')[0]+"\n"+str(e))
            # when the import fails reset the text in the control file path textfield
            # avoids the confusion of the file selected not importing but the file name appearing in the text field
            # implying that it is the current control program 
            mod_path.text = ""
            # reset list of funcs
            self.cnrtl_funcs = []
            self.cnrtl_mod = None
        self.root.ids['mod_spinner'].active = False
        self.toggle_btns()


    def create_ctrl_files(self,folder_field):
        self.root.ids['folder_spinner'].active = True
        self.root.ids['folder_spinner'].disabled = True
        threading.Thread(target=self._create_ctrl_files_pass,args=(folder_field,)).start()

    def _create_ctrl_files_pass(self,folder_field):
        if not self.cnrtl_mod:
            self.open_final_msg("Module Error","No Module Loaded")
            self.root.ids['folder_spinner'].active = False
            self.root.ids['folder_spinner'].disabled = False
            return
        if len(folder_field.text)>0:
            if not os.path.exists(folder_field.text):
                try:
                    os.makedirs(folder_field.text)
                except Exception as e:
                    self.open_final_msg("Folder Error","Unable to create folder "+folder_field.text+"\n"+str(e))
                    self.root.ids['folder_spinner'].active = False
                    self.root.ids['folder_spinner'].disabled = False
                    return
            if not os.path.isdir(folder_field.text):
                self.open_final_msg("Folder Error","Selected path is not directory.")
                self.root.ids['folder_spinner'].active = False
                self.root.ids['folder_spinner'].disabled = False
                return
            for func in self.cnrtl_funcs:
                if func[0][0] != '_':
                    try:
                        cf = open(os.path.join(folder_field.text,func[0]+"_ctrl.txt"),'w')
                        argspec= getargspec(func[1])
                        if argspec[0]:
                            for arg in argspec[0]:
                                cf.write(arg+": \n")
                        if argspec[1]:
                            cf.write(argspec[1]+": \n")
                        if argspec[2]:
                            cf.write(argspec[2]+": \n")
                        if argspec[0] or argspec[1] or argspec[2]:
                            cf.truncate(cf.tell()-1)
                        cf.close()
                    except Exception as e:
                        self.open_final_msg("File Error","Unable to create control file "+func[0]+"_ctrl.txt\n"+str(e))
                        self.root.ids['folder_spinner'].active = False
                        self.root.ids['folder_spinner'].disabled = False
                        return
        else:
            self.open_final_msg("File Error", "No folder selected")
            self.root.ids['folder_spinner'].active = False
            self.root.ids['folder_spinner'].disabled = False
            
        self.open_final_msg("Success","Control files created successfully.","Ok")
        self.root.ids['folder_spinner'].active = False
        self.root.ids['folder_spinner'].disabled = False

    def create_ctrl_edit(self,ctrl_path,box):
        cf = []
        box.clear_widgets()
        try:
            cf = open(ctrl_path.text,'r')
        except Exception as e:
            self.open_final_msg("File Error","Unable to open control file "+ctrl_path.text+"\n"+str(e))
            return
        if os.stat(ctrl_path.text).st_size==0:
            self.open_final_msg("File Error","Control file empty")
            return
        c=0
        for line in cf:
            line = line.strip()
            if line:
                try:
                    param_box= CtrlParamEdit()
                    param_box.children[1].text=strip_quotes(line[line.index(':')+1:].strip())
                    param_box.children[2].text=line.split(':')[0].strip()
                    box.add_widget(param_box)
                    c+=1
                except Exception as e:
                    self.open_final_msg("File Error","Malformed control file")
                    print(str(e))
                    return
        box.size[1] = sum([dp(65) for c in box.children])+20
    def save_ctrl(self,ctrl_path,box):
        if len(ctrl_path.text)<1:
            self.open_final_msg("File Error","No file selected.")
            return
        if not box.children:
            self.open_final_msg("File Error","No file loaded.")
            return       
        towrite=[]
        for param_box in box.children:
            towrite.append(param_box.children[2].text+": "+param_box.children[1].text+"\n")
        try:
            cf = open(ctrl_path.text,'w')
            cf.writelines(towrite[::-1])
            cf.truncate(cf.tell()-1)
            cf.close()
            self.open_final_msg("Success","File saved successfully.","Ok")
        except Exception as e:
            self.open_final_msg("File Error","Unable to save control file "+ctrl_path.text+"\n"+str(e))
            return

        
    """BEGIN FILE BROWESER FUNCTIONS"""
    """*****************************"""
    # These functios are used to control the selection of file paths using FileBrowser objects

    # called when a button used to select a file is pressed
    # takes in a reference to a textfield that a file path will be written to on sucessful file selection
    def open_dialog(self,textfield,dir_path=".",btn_text="Select"):
        # make filebroswer open to current path
        fb = filebrowser.FileBrowser(favorites=[(user_path, 'Documents')],path=dir_path,select_string=btn_text)
        fb.ids.splitter.strip_size = '3pt'
        fb.ids.splitter.children[1].bar_width= 7
        fb.ids.splitter.children[1].scroll_type= ['bars', 'content']
        fb.ids.list_view.ids.layout.ids.scrollview.bar_width= 7
        fb.ids.list_view.ids.layout.ids.scrollview.scroll_type= ['bars', 'content']
        fb.ids.icon_view.ids.layout.ids.scrollview.scroll_type= ['bars', 'content']
        fb.ids.icon_view.ids.layout.ids.scrollview.bar_width= 7
        pu = Popup(id='file_chooser_dialog',title='File Selection',content=fb,size_hint=(None, None), size=(800, 500),auto_dismiss=False)
        # bind _success and _submit functions. On cancel call popup.dismiss (close the popup)
        fb.bind(on_success=partial(self._fbrowser_success, textfield, pu),on_canceled=pu.dismiss,on_submit=partial(self._fbrowser_submit, textfield, pu))
        pu.open()

    # currently unused but conventional name for func to be called on file broswer cancel- keeping in case needed later    
    def _fbrowser_canceled(self, instance):
        placeholder = "placeholder func ||-//"
        
    # on success set text to either current file broswer directory or file file chosen if avaible
    def _fbrowser_success(self, field, pup, instance):
        # if a file has been chosen
        if len(instance.selection)>0:
            field.text =instance.selection[0]
        else:
            # no file chosen, so path selected
            field.text = os.path.join(instance.path,instance.filename)
        # close popup
        pup.dismiss()
        # if the textfield that has be written to is the control program testfield, then also load in module from file selected
        if field.hint_text == "Select Program":
            self.root.ids['mod_spinner'].active = True
            self.toggle_btns()
            threading.Thread(target=self.set_mod, args=(field,)).start()
        if field.hint_text == self.root.ids.ctrl_edit.hint_text:
            self.create_ctrl_edit(field,self.root.ids.edit_params)
        if field.hint_text == "ctrl_location":
            self.save_ctrl(MDTextField(text=field.text),self.screen_popup.children[0].children[0].children[0].ids['param_grid'])
        if field.hint_text == "Load From Control File":
            cf = None
            try:
                cf = open(instance.selection[0],'r')
                for child in self.screen_popup.children[0].children[0].children[0].ids['param_grid'].children[::-1]:
                    line = cf.readline().strip()
                    if line:
                        child.children[1].text=strip_quotes(line[line.index(':')+1:].strip())
            except Exception as e:
                self.open_final_msg("File Error","Unable to open control file "+instance.selection[0]+"\n"+str(e))
                return
    

    # just use the success function
    def _fbrowser_submit(self, field, pup,instance):
        self._fbrowser_success(field, pup, instance)
    """***************************"""
    """END FILE BROWESER FUNCTIONS"""   

    # used to write to selected func textfield when a function name is selected from popup list
    # called on on_touch_down event

    def dismiss_param(self,popup):
        self.run_parameter_list=[]
        for child in popup.children[1].children[0].children[::-1]:
            if child.children[1].text:
                self.run_parameter_list.append(strconv.convert(child.children[1].text))
        if self.run_parameter_list:
            self.root.ids['run_btn'].disabled = False
        self.screen_popup.dismiss()

    def save_as_params(self,pup_box):
        tf= MDTextField(hint_text="ctrl_location")
        self.open_dialog(tf,btn_text="Save")

    params = []
    run_parameter_list = []
    def open_param_pup(self):
        pup_box = PopupBox()
        box = pup_box.ids['param_grid']
        for param in self.params:
            try:
                param_box= CtrlParamEdit()
                param_box.children[2].text=param
                box.add_widget(param_box)
            except Exception as e:
                self.open_final_msg("File Error","Malformed control file")
                print(str(e))
                return
        box.size[1] = sum([dp(65) for c in box.children])+20
        pu = Popup(id='pup_params',title='Parameter Editor',title_color=[255, 255, 255, 1],content=pup_box,size_hint=(None, None), size=(800, 500),auto_dismiss=False,background="res/back.png",)
        self.screen_popup = pu
        pu.open()

    def write_to_field(self,tf,txt,params,callback,touch):
        self.screen_popup.dismiss()
        self.params = params
        tf.text=txt
        return False

    def open_menu_thread(self,tf):
        self.root.ids['sel_spinner'].active = True
        self.toggle_btns()
        t = threading.Thread(target=self.open_menu, args=(tf,))
        t.start()
        t.join()

    # opens func selection popup from list of funcs in control program module
    # called when "Select" button is pressed
    def open_menu(self,tf):
        # make KivyMd list
        menu_list = MDList(id = 'func_list')
        sv= ScrollBetter(scroll_wheel_distance=35)
        sv.add_widget(menu_list)
        # go through funcs in control mod and add names with parameters to list
        if not self.cnrtl_mod:
            self.open_final_msg("Program Error", "No module loaded")
            self.root.ids['sel_spinner'].active = False
            self.toggle_btns()
            return
        if len(self.cnrtl_funcs)==0:
            self.open_final_msg("Program Error", "No functions found")
            self.root.ids['sel_spinner'].active = False
            self.toggle_btns()
            return
        for func in self.cnrtl_funcs:
            # check if function is private (name starts with '_' by Python convention)
            if not func[0][0] == '_':
                # make string "func_name(list,of,params)"
                func_string = func[0]+'('
                for param in signature(func[1]).parameters.values():
                    # if parameter has default value display that in the function string
                    if param.default and not param.default is param.empty:
                        func_string+= param.name+"="+str(param.default)+", "
                    else:
                        func_string+= param.name+", "
                func_string = func_string.strip()[:-1]+")"
                params = getargspec(func[1])[0]
                # make func_string into menu list item and add to menu
                if len(func_string)<110:
                    menu_list.add_widget(OneLineListItem(text=func_string,on_touch_down=partial(self.write_to_field, tf,func_string,params)))
                elif len(func_string)<220:
                    menu_list.add_widget(TwoLineListItem(text=func_string,on_touch_down=partial(self.write_to_field, tf,func_string,params)))
                else:
                    menu_list.add_widget(ThreeLineListItem(text=func_string,on_touch_down=partial(self.write_to_field,tf,func_string,params)))

        Clock.schedule_once(partial(self.__cont_open_menu,sv),0)
        
    def __cont_open_menu(self,sv,ph):
        # make and open popup with list    
        pu = Popup(id='funcs_menu',title='Function Selector',title_color=[255, 255, 255, 1],content=sv,size_hint=(None, None), size=(800, 500),auto_dismiss=False,background="res/back.png",)
        self.screen_popup = pu
        pu.open()
        self.root.ids['sel_spinner'].active = False
        self.toggle_btns()
    # takes func and args as array and passes them to func using *    
    def func_wrapper(self,function, args):
        ret = None
        try:
            ret= function(*args)
            print(ret)
        except Exception as e:
            print("Function threw error:\n"+str(e))
        Clock.schedule_once(self.toggle_loading,0)
        return ret

    def toggle_btns(self):
        for btn in ['run_btn','func_btn']:
            self.root.ids[btn].disabled = not self.root.ids[btn].disabled
            
    def toggle_loading(self,call):
        self.root.ids['func_spinner'].active = not self.root.ids['func_spinner'].active
        self.toggle_btns()
    """BEGIN RUN PARAM CHAIN"""
    """*********************"""  
    # runs func name that is in the function text field
    # note that this function, run_param, is broken into 3 pieces
    # this is the result of conditional checks that must be met in order for the function to run properly
    # these checks are determined by user input in the form of selecting dialog options

    # cntrl_path is the file path of the txt conatining parameters to be passed
    # function_text is a reference to the MDTextField that contains function names
    def run_param(self,function_text_field):
        # func_name string that conmes before ( in the function_text_field
        func_name = function_text_field.text.split('(')[0]
        if len(func_name)<1:
            self.open_final_msg("Program Error", "No function selected")
            return
        # get reference to function with name func_name by searching through list of funcs in module
        func = [o[1] for o in self.cnrtl_funcs if func_name==o[0]]
        # params to be filled with the parameter name within the selected function
        params = []
        # if a function was found in the list of functions
        if len(func)>0:
            # variable func is currently a list of 1 elem.
            # if the function was found set the varible to that elem. (reference to function)
            func = func[0]
            # set params to list of function params
            params = getargspec(func).args
        else:
            # if no functions of name in text field found, display this to user and exit
            self.open_final_msg("Program Error", "Error: Function \""+func_name+"\" not found")
            return
        
        num_params = 0
        try:
            # set the number of cntrl params to the number of params in cntrl file
            num_params = len(self.run_parameter_list)
        except Exception as e:
            # if for any reason the control file could not be opened, display the error to the user and exit
            self.open_final_msg("File Error", "Error opening file:\n"+str(e))
            return

        # now switch on the number of cntrl params vs. the number of params in cntrl func definition
        # it is possible that the number of cntrl params is different than the cntrl func params, but execution is still desired
        # optional params, etc.
        if num_params > len(params):
            # too many
            # open dialog to give user option to continue
            self.open_too('many',params,func)
    
        elif num_params < len(params):
            # too few
            # open dialog to give user option to continue
            self.open_too('few',params,func)
        else:
            # just right
            # continue execution
            self.__cont_run_param(func)
            
    # next block of run_param function
    # assumes that parameter number discrepencies have been resolved or user has chosen to ignore

    @mainthread
    def __cont_run_param(self,func):
        Clock.schedule_once(self.toggle_loading,.25)
        try:
            # use func_wrapper to pass params to cntrl function as list
            # run the function and print the result
            threading.Thread(target=self.func_wrapper, args=(func,self.run_parameter_list,)).start()
        except Exception as e:
            # if the function throws an error, output the error
            print("Function threw error:\n"+str(e))

    """*******************"""
    """END RUN PARAM CHAIN"""
    


    """BEGIN DIALOG FUNCTIONS"""
    """**********************"""
    # Each function in this block is used in the displaying of options to the user via dialogs

    # called from run param
    # has user choose to continue if the # of contrl params != # params in cntrl func definition
    def open_too(self,text,params,func):
        # text either many or few, so text reads "Too (many or few) arguents"
        content = MDLabel(font_style='Body1',theme_text_color='Secondary',text="Too "+text+" arguments. Is this OK?",size_hint_y=None,valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="Program Error",content=content,size_hint=(.8, None),height=dp(200),auto_dismiss=False)
        # if yes call next function in run_param chain
        self.dialog.add_action_button("YES",action=lambda *x: self.dialog.dismiss(force=True,animation=False) and self.__cont_run_param(func))
        # else end the chain
        self.dialog.add_action_button("NO",action=lambda *x: self.dialog.dismiss())
        self.dialog.open()


    # run a given function after waiting period in seconds time
    def __schedule(self,function,time,placeholder):
        Clock.schedule_once(function,time)

    def __pass_run(self,func,run_params):
        # bind the schedule to dialog dismiss event
        # this has the app wait .5 sec after the dialog is dismissed to execute the next func in the run_param chain
        self.dialog.bind(on_dismiss=partial(self.__schedule, partial(self.__finish_run_param,func,run_params),.5))
        self.dialog.dismiss(force=True,animation=False)
        
    # called when a dialog message is final
    # i.e. the function running ends after this dialog is opened
    # typically called for fatal error when setting up cntrl func,
    # Module not found, cntrl file not found, etc.
    def open_final_msg(self,title,txt,btn_text="Dismiss"):
        # binds given title and text of message to dialog
        content = MDLabel(font_style='Body1',theme_text_color='Secondary',text=txt,size_hint_y=None,valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title=title,content=content,size_hint=(.8, None),height=dp(200),auto_dismiss=False)
        # only option is to dismiss
        self.dialog.add_action_button(btn_text,action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    """********************"""
    """END DIALOG FUNCTIONS"""


    """BEGIN STARTUP FUNCTIONS"""
    """***********************"""
    # function called on every key down event in the app
    # used to check if enter key is pressed
    # handles actions accordingly
    def key_action(self, *args):
        #if key pressed is enter key (key code 13)
        if args[1]==13:
            # if the Control Module textfield is currently foucused
            if self.root.ids['param'].focused:
                # set mod to value in txtfield
                # uses thread to keep ui from freezing
                self.root.ids['mod_spinner'].active = True
                self.toggle_btns()
                threading.Thread(target=self.set_mod, args=(self.root.ids["param"],)).start()

            if self.root.ids['folder_field'].focused:
                self.root.ids['folder_spinner'].active = not self.root.ids['folder_spinner'].active
                self.root.ids['folder_spinner'].disabled = not self.root.ids['folder_spinner'].disabled 
                threading.Thread(target=self.create_ctrl_files, args=(self.root.ids['folder_field'],)).start()
            if self.root.ids['ctrl_edit'].focused:
                self.create_ctrl_edit(self.root.ids.ctrl_edit,self.root.ids.edit_params)
                                  
    def on_start(self, **kwargs):
        self.load_configure()

    def on_touch_down(self, window, touch):
        if not self.root.ids['rclick_menu'].collide_point(*touch.pos):
            self.root.ids['rclick_menu'].hide()
        else:
            FocusBehavior.ignored_touch.append(touch)
        if touch.button == 'right':
            FocusBehavior.ignored_touch.append(touch)
            self.root.ids.rclick_menu.show(*touch.pos)
            return True

    def clip_action(self,clip_item):
        self.root.ids['rclick_menu'].hide()
        if self.text_focused and self.text_focused.focused:
            self.clip_interact(self.text_focused,clip_item.text)
            return
        for field in self.text_fields:
            fld = self.root.ids[field]
            if fld.focused:
                self.clip_interact(fld,clip_item.text)


    def clip_interact(self,fld,action):
        if action == "Paste":
            if fld.selection_text:
                a = fld.selection_from if fld.selection_from<fld.selection_to else fld.selection_to
                z = fld.selection_from if fld.selection_from>fld.selection_to else fld.selection_to 
                fld.text = fld.text[:a]+Clipboard.paste()+fld.text[z:]
            else:
                fld.text = fld.text[:fld.cursor_index()]+Clipboard.paste()+fld.text[fld.cursor_index():]                

        if action == "Copy":
            Clipboard.copy(fld.selection_text)

        if action == "Cut":
            if fld.selection_text:
                a = fld.selection_from if fld.selection_from<fld.selection_to else fld.selection_to
                z = fld.selection_from if fld.selection_from>fld.selection_to else fld.selection_to 
                Clipboard.copy(fld.selection_text)
                fld.text = fld.text[:a]+fld.text[z:]
            else:
                Clipboard.copy("")

                
    def load_configure(self):
        try:
            conf = open('conf.ini','r')
            val_dict = {}
            for line in conf:
                line_split = line.strip().split('=')
                val_dict[line_split[0].strip()] = line_split[1].strip()
            if val_dict.get('default_module'):
                self.root.ids['param'].text = val_dict.get('default_module')
            
            if(len(self.root.ids['param'].text)>0):
                self.toggle_btns()
                self.set_mod(self.root.ids['param'])
            if val_dict.get('default_function'):
                self.root.ids['func_field'].text=val_dict.get('default_function')
            if val_dict.get('default_control'): 
                do = "nothing"
                #self.root.ids['cntrl_path'].text=val_dict.get('default_control')
            if val_dict.get('default_log'):
                self.root.ids['log_path'].text=val_dict.get('default_log')
            
        except Exception as e:
            # if for any reason the config file could not be opened, display the error to the user and exit
            self.open_final_msg("File Error", "Error loading config file:\n"+str(e))
            return
        
    # app build function            
    def build(self):
        # bind key down events to call key_action func
        Window.bind(on_key_down=self.key_action,on_touch_down=self.on_touch_down)
        # set std to logfile
        sys.stdout = f
        # build the app form kv string
        Config.set('input', 'mouse', 'mouse,disable_multitouch')
        self.theme_cls.theme_style = 'Light'
        return Builder.load_string(kv)

    """*********************"""
    """END STARTUP FUNCTIONS"""
    

if __name__ == '__main__':
    # multiprocessing io
    freeze_support()
    # open the app
    MainApp().run()
    # after the app closes, set stdout to its original state and close the current capture buffer
    sys.stdout = sys.__stdout__
    f.close()
