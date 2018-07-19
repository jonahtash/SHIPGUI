from functools import partial
import io
import sys
import time
from os.path import expanduser
from inspect import getmembers, isfunction, getargspec
from importlib import import_module
from multiprocessing import freeze_support
import strconv

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import filebrowser

from kivymd.button import MDIconButton
from kivymd.label import MDLabel
from kivymd.theming import ThemeManager
from kivymd.textfields import MDTextField
from kivymd.list import MDList, OneLineListItem
from kivymd.dialog import MDDialog
kv = '''
#:import MDSwitch kivymd.selectioncontrols.MDSwitch
#:import MDTextField kivymd.textfields.MDTextField
#:import MDTabbedPanel kivymd.tabs.MDTabbedPanel
#:import MDTab kivymd.tabs.MDTab
#:import MDRaisedButton kivymd.button.MDRaisedButton
#:import MDCheckbox kivymd.selectioncontrols.MDCheckbox

<StdoutBox@TextInput>
    height: dp(20)
    readonly: True
	
<ParameterTemplate@BoxLayout>:
    orientation: 'vertical'
    padding: dp(48)
    spacing: 10
	
Screen:
    id: main
    name: 'tabs'
    MDTabbedPanel:
        id: tab_panel
        tab_display_mode:'text'

        MDTab:
            name: 'txts'
            text: "Id List Generation"
            id: main_tab

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                ParameterTemplate:
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
                            text: 'sort_url(id_txt, out_csv, num_threads)'
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
                            on_release: app.run_param(cntrl_path.text,func_field,outbox)
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

user_path = expanduser("~")
f = open('log.txt','w')

def set_area(ti):
    global f
    f = TextBoxOut(TextInput())
    f.my_in = ti
    sys.stdout = f

class TextBoxOut:
    my_in = None
    def __init__(self,text_input):
        self.my_in = text_input
    def write(self, txt):
        self.my_in.text += txt
    def flush(self):
        self.my_in.text = ""
    #f.close is called at the end of main
    #in the event that the program is closed when output is to a box
    def close(self):
        potato = 'this code(||-//)'

		
class StdoutBox(TextInput):
    def build(self):
        global text_area
        text_area = self
    def write(self):
        global text_area
        text_area = self
        write_to_area()


class MainApp(App):
    cnrtl_mod = import_module("SHIP")
    cnrtl_funcs = [o for o in getmembers(cnrtl_mod) if isfunction(o[1])]
    theme_cls = ThemeManager()

    
    def switch_out(self, button, log_path, area):
        global f
        if button.active:
            f=open(log_path,'w')
            sys.stdout = f
        else:
            set_area(area)

            
    def set_mod(self,mod_path):
        path_a = mod_path.text.split('\\')
        sys.path.insert(0, path_a[:-1])
        try:
            self.cnrtl_mod =  import_module(path_a[-1].split('.')[0])
            self.cnrtl_funcs = [o for o in getmembers(self.cnrtl_mod) if isfunction(o[1])]
        except Exception as e:
            content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text="Error loading: "+path_a[-1].split('.')[0]+"\n"+str(e),
                          size_hint_y=None,
                          valign='top')
            content.bind(texture_size=content.setter('size'))
            self.dialog = MDDialog(title="Module Error",
                               content=content,
                               size_hint=(.8, None),
                               height=dp(200),
                               auto_dismiss=False)

            self.dialog.add_action_button("DISMISS",
                                      action=lambda *x: self.dialog.dismiss())
            self.dialog.open()
            mod_path.text = ""

        
    """BEGIN FILE BROWESER FUNCTIONS"""        
    def open_dialog(self,textfield):
        fb = filebrowser.FileBrowser(select_string='Select',
                                  favorites=[(user_path, 'Documents')],path=".")
        bl = BoxLayout(orientation = 'vertical')
        bl.add_widget(fb)
        pu = Popup(id='file_chooser_dialog',title='File Selection',content=bl,size_hint=(None, None), size=(800, 500),auto_dismiss=False)
        fb.bind(on_success=partial(self._fbrowser_success, textfield, pu),
                         on_canceled=pu.dismiss,
                         on_submit=partial(self._fbrowser_submit, textfield, pu))
        pu.open()
        
    def _fbrowser_canceled(self, instance):
        placeholder = "placeholder func ||-//"
        

    def _fbrowser_success(self, field, pup, instance):
        if len(instance.selection)>0:
            field.text =instance.selection[0]
        else:
            field.text = instance.path
        pup.dismiss()
        if field.hint_text == "Program Control File Location":
            self.set_mod(field)


    def _fbrowser_submit(self, field, pup,instance):
        self._fbrowser_success(field, pup, instance)

    """END FILE BROWESER FUNCTIONS"""   

	
    def write_to_field(self,a,b,tf,text):
        a.text =b
        tf.parent.parent.parent.parent.parent.dismiss()

        
    def open_menu(self,tf):
        menu_list = MDList(id = 'reee')
        sv= ScrollView()
        sv.add_widget(menu_list)
        for func in self.cnrtl_funcs:
            if not func[0][0] == '_':
                func_string = func[0]+'('+', '.join(getargspec(func[1]).args)+')'
                menu_list.add_widget(OneLineListItem(text=func_string,on_touch_down=partial(self.write_to_field, tf,func_string)))
            
        pu = Popup(id='funcs',title='Function Selector',title_color=[255, 255, 255, 1],content=sv,size_hint=(None, None), size=(800, 500),auto_dismiss=False,background="res/back.png",)
        pu.open()

        
    def func_wrapper(self,function, args):
        return function(*args)

    def run_param(self,cntrl_path,function_text_field,outputbox):
        func_name = function_text_field.text.split('(')[0]
        func = [o[1] for o in self.cnrtl_funcs if func_name==o[0]]
        params = []
        if len(func)>0:
            func = func[0]
            params = getargspec(func).args
        else:
            self.open_final_msg("Program Error", "Error: Function \""+func_name+"\" not found")
            return

        num_params = 0
        try:
            num_params = sum(1 for line in open(cntrl_path))
        except Exception as e:
            self.open_final_msg("File Error", "Error opening file:\n"+str(e))
            return
            
        if num_params > len(params):
            self.open_too('many',params,cntrl_path,func)
    
        elif num_params < len(params):
            self.open_too('few',params,cntrl_path,func)
        else:
            self.__cont_run_params(params,cntrl_path,func)

    def __cont_run_params(self,params,cntrl_path,func):
        c = 0
        run_params = [None] * len(params)
        run_params_names = [None] * len(params)
        for p in open(cntrl_path,'r'):
            if(c<len(params)):
                run_params[c] = strconv.convert(strip_quotes(p[p.index(':')+1:].strip()))
                run_params_names[c] = p.split(':')[0].strip()
                c+=1
            else:
                break
        diffs = _get_diff(params,run_params_names)
        if len(diffs)>0:
            self.open_diffs(diffs,func,run_params)
        else:
           self.__finish_run_params(func,run_params)
        

    def __finish_run_params(self,func,run_params,placeholder):
        try:
            print(self.func_wrapper(func,run_params))
        except Exception as e:
            print("Function threw error:\n"+str(e))
            

    def open_too(self,text,params,cntrl_path,func):
        content = MDLabel(font_style='Body1',theme_text_color='Secondary',text="Too "+text+" arguments. Is this OK?",size_hint_y=None,valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="Program Error",content=content,size_hint=(.8, None),height=dp(200),auto_dismiss=False)
        self.dialog.add_action_button("YES",action=lambda *x: self.dialog.dismiss(force=True,animation=False) and self.__cont_run_params(params,cntrl_path,func))
        self.dialog.add_action_button("NO",action=lambda *x: self.dialog.dismiss())
        self.dialog.open()


    def open_diffs(self,diffs,func,run_params):
        dia_text = "Unexepcted parameter names recieved:\nEXPECTED     RECEIVED"
        for r in diffs:
            dia_text+="\n"+"{:17}{}".format(str(r[0]),str(r[1]))
        dia_text+="\n\nWould you like to continue?"
        content = MDLabel(font_style='Body1',theme_text_color='Secondary',text=dia_text,size_hint_y=None,valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="Parameter Error",content=content,size_hint=(.8, None),height=dp(350),auto_dismiss=False)
        self.dialog.add_action_button("YES, CONTINUE",action=lambda *x: self.__pass_run(func,run_params))
        self.dialog.add_action_button("NO",action=lambda *x: self.dialog.dismiss())
        self.dialog.open()
    
    def __schedule(self,function,time,placeholder):
        Clock.schedule_once(function,time)
    def __pass_run(self,func,run_params):
        self.dialog.bind(on_dismiss=partial(self.__schedule, partial(self.__finish_run_params,func,run_params),.5))
        self.dialog.dismiss(force=True,animation=False)
        

    def open_final_msg(self,title, txt):
        content = MDLabel(font_style='Body1',theme_text_color='Secondary',text=txt,size_hint_y=None,valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title=title,
                           content=content,
                           size_hint=(.8, None),
                           height=dp(200),
                           auto_dismiss=False)

        self.dialog.add_action_button("Dismiss",
                                  action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    def build(self):
        sys.stdout = f
        return Builder.load_string(kv)
		
		
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

if __name__ == '__main__':
    freeze_support()
    MainApp().run()
    sys.stdout = sys.__stdout__
    f.close()
