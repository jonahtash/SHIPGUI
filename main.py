from functools import partial
import io
import sys
import time
from os.path import expanduser
from inspect import getmembers, isfunction, getargspec, signature
from importlib import import_module
from multiprocessing import freeze_support
import strconv

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import filebrowser

from kivymd.button import MDIconButton, MDRaisedButton
from kivymd.label import MDLabel
from kivymd.theming import ThemeManager
from kivymd.textfields import MDTextField
from kivymd.list import MDList, OneLineListItem
from kivymd.dialog import MDDialog
from kivymd.selectioncontrols import MDSwitch, MDCheckbox
from kivymd.tabs import MDTabbedPanel, MDTab

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
# param = parameters

kv = '''

<StdoutBox@TextInput>
    height: dp(20)
    readonly: True
	

	
Screen:
    id: main
    name: 'tabs'
    MDTabbedPanel:
        id: tab_panel
        tab_display_mode:'text'

        MDTab:
            name: 'txts'
            text: "Control Python"
            id: main_tab

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                BoxLayout:
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
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            hint_text: "Program Control File Location"
                            text: "SHIP.py"
                        MDIconButton:
                            icon: 'file'
                            pos_hint: {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.open_dialog(param)
                        
                    BoxLayout:
                        orientation: 'horizontal'
                        spacing: 30
                        id: funcs_select
                        MDTextField:
                            id: func_field
                            line_width: funcs_select.minimum_width-dp(36)
                            hint_text: "Function"
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                        MDRaisedButton:
                            text: "SELECT"
                            opposite_colors: True
                            size_hint: None, None
                            size: 4 * dp(48), dp(48)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.open_menu(func_field)
                    BoxLayout:
                        orientation: 'horizontal'
                        spacing: 30
                        id: cntrl_select
                        MDTextField:
                            id: cntrl_path
                            hint_text: "Parameter Control File Location"
                            line_width: funcs_select.minimum_width-dp(36)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            text: "cntrl.txt"
                        MDIconButton:
                            icon: 'file'
                            pos_hint: {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.open_dialog(cntrl_path)
                        MDRaisedButton:
                            text: "RUN"
                            opposite_colors: True
                            size_hint: None, None
                            size: 4 * dp(48), dp(48)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.run_param(cntrl_path.text,func_field)
                    BoxLayout:
                        spacing: 30
                        MDCheckbox:
                            id: log_swich
                            size_hint:    None, None
                            size:        dp(36), dp(48)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            active: True
                            on_release: app.switch_out(self,log_path.text, outbox)
                        MDTextField:
                            id: log_path
                            hint_text: "Log File Location"
                            line_width: funcs_select.minimum_width-dp(36)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            text: "log.txt"
                            disabled: not log_swich.active
                        MDIconButton:
                            icon: 'file'
                            pos_hint: {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.open_dialog(log_path)

					StdoutBox:
						id: outbox
						disabled: log_swich.active
						background_disabled_normal: 'res/disabled.png'
						background_normal: 'res/enabled.png'
						font_name: "DejaVuSans" 
                    
                    

                    
            
'''
# set a variable to the location of the user's home directory. Used to direct file browser
user_path = expanduser("~")
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
    # default control program: SHIP.py
    cnrtl_mod = import_module("SHIP")
    # list of the functions within the control programs
    # stored in tuples of ("func_name_as_string", <ref_to_func>)
    cnrtl_funcs = [o for o in getmembers(cnrtl_mod) if isfunction(o[1])]
    # used for kivy themeing
    theme_cls = ThemeManager()

    # on_release event for checkbox controlling output location
    # when the check box is active (checked) std is directed to a log file whose location is given by a text field
    # if the box is not active, have std go to a TextInput at the bottom of the app
    def switch_out(self, button, log_path, area):
        global f
        if button.active:
            f=open(log_path,'a')
            sys.stdout = f
        else:
            set_area(area)

    # used to switch module control program
    # called when new file is chosen for control program (first TextField)
    def set_mod(self,mod_path):
        # add the location of the control program to path so that it can be imported
        path_a = mod_path.text.split('\\')
        sys.path.insert(0, path_a[:-1])
        try:
            # import module and it to cnrtl_mod field
            self.cnrtl_mod =  import_module(path_a[-1].split('.')[0])
            # reassign list of functions to functions within new module
            self.cnrtl_funcs = [o for o in getmembers(self.cnrtl_mod) if isfunction(o[1])]
        except Exception as e:
            # if there is an error loading the module selected, use a dialog to display the error
            # most calls will likely be when the user selects a file that is not a module
            content = MDLabel(font_style='Body1',theme_text_color='Secondary',text="Error loading: "+path_a[-1].split('.')[0]+"\n"+str(e),size_hint_y=None,valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title="Module Error",content=content,size_hint=(.8, None),height=dp(200),auto_dismiss=False)
            self.dialog.add_action_button("DISMISS",action=lambda *x: self.dialog.dismiss())
            self.dialog.open()
            # when the import fails reset the text in the control file path textfield
            # avoids the confusion of the file selected not importing but the file name appearing in the text field
            # implying that it is the current control program 
            mod_path.text = ""
            # reset list of funcs
            self.cnrtl_funcs = []

        
    """BEGIN FILE BROWESER FUNCTIONS"""
    """*****************************"""
    # These functios are used to control the selection of file paths using FileBrowser objects

    # called when a button used to select a file is pressed
    # takes in a reference to a textfield that a file path will be written to on sucessful file selection
    def open_dialog(self,textfield):
        # make filebroswer open to current path
        fb = filebrowser.FileBrowser(select_string='Select',favorites=[(user_path, 'Documents')],path=".")
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
            field.text = instance.path
        # close popup
        pup.dismiss()
        # if the textfield that has be written to is the control program testfield, then also load in module from file selected
        if field.hint_text == "Program Control File Location":
            self.set_mod(field)

    # just use the success function
    def _fbrowser_submit(self, field, pup,instance):
        self._fbrowser_success(field, pup, instance)
    """***************************"""
    """END FILE BROWESER FUNCTIONS"""   

    # used to write to selected func textfield when a function name is selected from popup list
    # called on on_touch_down event
    def write_to_field(self,a,b,tf,text):
        a.text =b
        tf.parent.parent.parent.parent.parent.dismiss()

    # opens func selection popup from list of funcs in control program module
    # called when "Select" button is pressed
    def open_menu(self,tf):
        # make KivyMd list
        menu_list = MDList(id = 'func_list')
        sv= ScrollView()
        sv.add_widget(menu_list)
        # go through funcs in control mod and add names with parameters to list
        if len(self.cnrtl_funcs)==0:
            self.open_final_msg("Program Error", "No functions found")
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
                # make func_string into menu list item and add to menu
                menu_list.add_widget(OneLineListItem(text=func_string,on_touch_down=partial(self.write_to_field, tf,func_string)))
        # make and open popup with list    
        pu = Popup(id='funcs',title='Function Selector',title_color=[255, 255, 255, 1],content=sv,size_hint=(None, None), size=(800, 500),auto_dismiss=False,background="res/back.png",)
        pu.open()

    # takes func and args as array and passes them to func using *    
    def func_wrapper(self,function, args):
        return function(*args)

    """BEGIN RUN PARAM CHAIN"""
    """*********************"""  
    # runs func name that is in the function text field
    # note that this function, run_param, is broken into 3 pieces
    # this is the result of conditional checks that must be met in order for the function to run properly
    # these checks are determined by user input in the form of selecting dialog options

    # cntrl_path is the file path of the txt conatining parameters to be passed
    # function_text is a reference to the MDTextField that contains function names
    def run_param(self,cntrl_path,function_text_field):
        # func_name string that conmes before ( in the function_text_field
        func_name = function_text_field.text.split('(')[0]
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
            num_params = sum(1 for line in open(cntrl_path))
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
            self.open_too('many',params,cntrl_path,func)
    
        elif num_params < len(params):
            # too few
            # open dialog to give user option to continue
            self.open_too('few',params,cntrl_path,func)
        else:
            # just right
            # continue execution
            self.__cont_run_param(params,cntrl_path,func)
            
    # next block of run_param function
    # assumes that parameter number discrepencies have been resolved or user has chosen to ignore
    def __cont_run_param(self,params,cntrl_path,func):
        c = 0
        # 2 lsits of blanks size of # of contrl params params
        # first values given by cntrl file (thing after ':')
        run_params = [None] * len(params)
        # second param names in file (thing before ':')
        run_params_names = [None] * len(params)
        # read through control file
        for p in open(cntrl_path,'r'):
            if(c<len(params)):
                # add param value to run_params
                run_params[c] = strconv.convert(strip_quotes(p[p.index(':')+1:].strip()))
                # add param name to run_param_names
                run_params_names[c] = p.split(':')[0].strip()
                c+=1
            else:
                break
        # get list of difference between
        # list of param names in cntrl function definition and param names in cntrl file
        diffs = _get_diff(params,run_params_names)
        if len(diffs)>0:
            # if there are differences, display them to the user and ask if they want to continue
            self.open_diffs(diffs,func,run_params)
        else:
            # no differences, then just continue
           self.__finish_run_param(func,run_params,"Placehodler")
        
    # final block of run_param
    # assumes all parameter name discrepencies have been solved
    def __finish_run_param(self,func,run_params,placeholder):
        try:
            # use func_wrapper to pass params to cntrl function as list
            # run the function and print the result
            print(self.func_wrapper(func,run_params))
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
    def open_too(self,text,params,cntrl_path,func):
        # text either many or few, so text reads "Too (many or few) arguents"
        content = MDLabel(font_style='Body1',theme_text_color='Secondary',text="Too "+text+" arguments. Is this OK?",size_hint_y=None,valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="Program Error",content=content,size_hint=(.8, None),height=dp(200),auto_dismiss=False)
        # if yes call next function in run_param chain
        self.dialog.add_action_button("YES",action=lambda *x: self.dialog.dismiss(force=True,animation=False) and self.__cont_run_param(params,cntrl_path,func))
        # else end the chain
        self.dialog.add_action_button("NO",action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    # called from run param
    # displays name differnces in ctrnl params and cntrl func params
    # has user choose to continue
    def open_diffs(self,diffs,func,run_params):
        # build dia_text to list two columns
        # expected param name and param name recieved from cntrl file
        dia_text = "Unexepcted parameter names recieved:\nEXPECTED     RECEIVED"
        for r in diffs:
            # formats so that the cols maintain a somewhat uniform width
            dia_text+="\n"+"{:17}{}".format(str(r[0]),str(r[1]))
        dia_text+="\n\nWould you like to continue?"
        content = MDLabel(font_style='Body1',theme_text_color='Secondary',text=dia_text,size_hint_y=None,valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="Parameter Error",content=content,size_hint=(.8, None),height=dp(350),auto_dismiss=False)
        # if finish call next function in run_param chain
        # intermediary function used to create a .5 sec pause so that the dialog close animation has time to finish
        self.dialog.add_action_button("YES, CONTINUE",action=lambda *x: self.__pass_run(func,run_params))
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
    def open_final_msg(self,title, txt):
        # binds given title and text of message to dialog
        content = MDLabel(font_style='Body1',theme_text_color='Secondary',text=txt,size_hint_y=None,valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title=title,content=content,size_hint=(.8, None),height=dp(200),auto_dismiss=False)
        # only option is to dismiss
        self.dialog.add_action_button("Dismiss",action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    """********************"""
    """END DIALOG FUNCTIONS"""

    # function called on every key down event in the app
    # used to check if enter key is pressed
    # handles actions accordingly
    def key_action(self, *args):
        #if key pressed is enter key (key code 13)
        if args[1]==13:
            # if the Control Module textfield is currently foucused
            if self.root.ids["param"].focused:
                # set mod to value in txtfield
                self.set_mod(self.root.ids["param"])
    # app build function            
    def build(self):
        # bind key down events to call key_action func
        Window.bind(on_key_down=self.key_action)
        # set std to logfile
        sys.stdout = f
        # build the app form kv string
        return Builder.load_string(kv)


if __name__ == '__main__':
    # multiprocessing io
    freeze_support()
    # open the app
    MainApp().run()
    # after the app closes, set stdout to its original state and close the current capture buffer
    sys.stdout = sys.__stdout__
    f.close()
