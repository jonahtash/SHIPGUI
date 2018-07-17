from functools import partial
import io
import sys
import time
from os.path import expanduser
from inspect import getmembers, isfunction, getargspec
from importlib import import_module
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
import filebrowser

from kivymd.button import MDIconButton
from kivymd.label import MDLabel
from kivymd.theming import ThemeManager
from kivymd.textfields import MDTextField
from kivymd.menu import MDDropdownMenu, MDMenuItem
from kivymd.list import MDList, OneLineListItem
kv = '''
#:import MDSwitch kivymd.selectioncontrols.MDSwitch
#:import MDTextField kivymd.textfields.MDTextField
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import colors kivymd.color_definitions.colors
#:import MDTabbedPanel kivymd.tabs.MDTabbedPanel
#:import MDTab kivymd.tabs.MDTab
#:import MDMenuItem kivymd.menu.MDMenuItem
#:import MDDropdownMenu kivymd.menu.MDDropdownMenu
#:import MDRaisedButton kivymd.button.MDRaisedButton


<StdoutBox@TextInput>
    readonly: True


<FileParam@BoxLayout>:
    orientation: 'horizontal'
    spacing: 30
    MDTextField:
        id: param
        line_width: root.minimum_width-dp(36)
        pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
        hint_text: "Parameter"
    MDIconButton:
        icon: 'file'
        pos_hint: {'center_x': 0.75, 'center_y': 0.5}
        on_release: root.open_dialog(param)

<OptionalFileParam@BoxLayout>:
    orientation: 'horizontal'
    spacing: 30
    
    MDSwitch:
        id: s1
        size_hint:    None, None
        size:        dp(36), dp(48)
        pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
        _active:        False
    MDTextField:
        id: param
        line_width: root.minimum_width-dp(36)
        pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
        hint_text: "Optional Parameter"
        disabled: not s1.active
    MDIconButton:
        icon: 'file'
        pos_hint: {'center_x': 0.75, 'center_y': 0.5}
        on_release: root.open_dialog(param)
   

<OptionalParam@BoxLayout>:
    orientation: 'horizontal'
    spacing: 30
    
    MDSwitch:
        id: s1
        size_hint:    None, None
        size:        dp(36), dp(48)
        pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
        _active:        False
    MDTextField:
        id: param
        line_width: root.minimum_width-dp(36)
        pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
        hint_text: "Optional Parameter"
        disabled: not s1.active
        
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
                        MDIconButton:
                            icon: 'file'
                            pos_hint: {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.open_dialog(param)
                        MDRaisedButton:
                            text: "SUBMIT"
                            opposite_colors: True
                            size_hint: None, None
                            size: 4 * dp(48), dp(48)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.set_mod(param.text)
                        
                    BoxLayout:
                        orientation: 'horizontal'
                        spacing: 30
                        id: funcs_select
                        MDTextField:
                            id: textf
                            line_width: funcs_select.minimum_width-dp(36)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                        MDRaisedButton:
                            text: "SELECT"
                            opposite_colors: True
                            size_hint: None, None
                            size: 4 * dp(48), dp(48)
                            pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
                            on_release: app.open_menu(textf)
                    FileParam:
                    
                    

                    
            
'''

user_path = expanduser("~")

class FileParam(BoxLayout):
    def open_dialog(self,textfield):
        fb = filebrowser.FileBrowser(select_string='Select',
                                  favorites=[(user_path, 'Documents')])
        bl = BoxLayout(orientation = 'vertical')
        bl.add_widget(fb)
        pu = Popup(id='file_chooser_dialog',title='File Selection',content=bl,size_hint=(None, None), size=(800, 500),auto_dismiss=False)
        fb.bind(on_success=partial(self._fbrowser_success, textfield, pu),
                         on_canceled=pu.dismiss,
                         on_submit=partial(self._fbrowser_submit, textfield, pu))
        pu.open()
    def _fbrowser_canceled(self, instance):
        print('placeholder func ||-//')

    def _fbrowser_success(self, field, pup, instance):
        if len(instance.selection)>0:
            field.text =instance.selection[0]
        else:
            field.text = instance.path
        pup.dismiss()

    def _fbrowser_submit(self, field, pup,instance):
        self._fbrowser_success(field, pup, instance)

class StdoutBox(TextInput):
    def build(self):
        self.bind(readonly = True)
    def write(self):
        global text_area
        text_area = self
        write_to_area()


f = io.StringIO()
text_area = None
def write_to_area():
    global f
    text_area.text = text_area.text + f.getvalue()
    f.truncate(0)
    f.seek(0)


class MainApp(App):
    cnrtl_mod = import_module("numpy")
    def set_mod(self,mod_path):
        path_a = mod_path.split('\\')
        sys.path.insert(0, path_a[:-1])
        self.cnrtl_mod =  import_module(path_a[-1].split('.')[0])
    def open_dialog(self,textfield):
        fb = filebrowser.FileBrowser(select_string='Select',
                                  favorites=[(user_path, 'Documents')])
        bl = BoxLayout(orientation = 'vertical')
        bl.add_widget(fb)
        pu = Popup(id='file_chooser_dialog',title='File Selection',content=bl,size_hint=(None, None), size=(800, 500),auto_dismiss=False)
        fb.bind(on_success=partial(self._fbrowser_success, textfield, pu),
                         on_canceled=pu.dismiss,
                         on_submit=partial(self._fbrowser_submit, textfield, pu))
        pu.open()
    def _fbrowser_canceled(self, instance):
        print('placeholder func ||-//')

    def _fbrowser_success(self, field, pup, instance):
        if len(instance.selection)>0:
            field.text =instance.selection[0]
        else:
            field.text = instance.path
        pup.dismiss()

    def _fbrowser_submit(self, field, pup,instance):
        self._fbrowser_success(field, pup, instance)
    theme_cls = ThemeManager()
    def write_to_field(self,a,b,tf,text):
        a.text =b
        tf.parent.parent.parent.parent.parent.dismiss()
    def open_menu(self,tf):
        menu_list = MDList(id = 'reee')
        sv= ScrollView()
        sv.add_widget(menu_list)
        for func in [o for o in getmembers(self.cnrtl_mod) if isfunction(o[1])]:
            func_string = func[0]+'('+', '.join(getargspec(func[1]).args)+')'
            menu_list.add_widget(OneLineListItem(text=func_string,on_touch_down=partial(self.write_to_field, tf,func_string)))
            
        pu = Popup(id='funcs',title='Function Selector',title_color=[255, 255, 255, 1],content=sv,size_hint=(None, None), size=(800, 500),auto_dismiss=False,background="back.png",)
        pu.open()

    def build(self):
        sys.stdout = f
        return Builder.load_string(kv)

    
if __name__ == '__main__':
    MainApp().run()
    sys.stdout = sys.__stdout__
    print(f.getvalue())
