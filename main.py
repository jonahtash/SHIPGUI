from functools import partial
import io
import sys
import time
from os.path import expanduser

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import filebrowser

from kivymd.button import MDIconButton
from kivymd.label import MDLabel
from kivymd.theming import ThemeManager
from kivymd.textfields import MDTextField
kv = '''
#:import Toolbar kivymd.toolbar.Toolbar
#:import ThemeManager kivymd.theming.ThemeManager
#:import MDNavigationDrawer kivymd.navigationdrawer.MDNavigationDrawer
#:import NavigationLayout kivymd.navigationdrawer.NavigationLayout
#:import NavigationDrawerDivider kivymd.navigationdrawer.NavigationDrawerDivider
#:import NavigationDrawerToolbar kivymd.navigationdrawer.NavigationDrawerToolbar
#:import NavigationDrawerSubheader kivymd.navigationdrawer.NavigationDrawerSubheader
#:import MDCheckbox kivymd.selectioncontrols.MDCheckbox
#:import MDSwitch kivymd.selectioncontrols.MDSwitch
#:import MDList kivymd.list.MDList
#:import OneLineListItem kivymd.list.OneLineListItem
#:import TwoLineListItem kivymd.list.TwoLineListItem
#:import ThreeLineListItem kivymd.list.ThreeLineListItem
#:import OneLineAvatarListItem kivymd.list.OneLineAvatarListItem
#:import OneLineIconListItem kivymd.list.OneLineIconListItem
#:import OneLineAvatarIconListItem kivymd.list.OneLineAvatarIconListItem
#:import MDTextField kivymd.textfields.MDTextField
#:import MDSpinner kivymd.spinner.MDSpinner
#:import MDCard kivymd.card.MDCard
#:import MDSeparator kivymd.card.MDSeparator
#:import MDDropdownMenu kivymd.menu.MDDropdownMenu
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import colors kivymd.color_definitions.colors
#:import SmartTile kivymd.grid.SmartTile
#:import MDSlider kivymd.slider.MDSlider
#:import MDTabbedPanel kivymd.tabs.MDTabbedPanel
#:import MDTab kivymd.tabs.MDTab
#:import MDProgressBar kivymd.progressbar.MDProgressBar
#:import MDAccordion kivymd.accordion.MDAccordion
#:import MDAccordionItem kivymd.accordion.MDAccordionItem
#:import MDAccordionSubItem kivymd.accordion.MDAccordionSubItem
#:import MDThemePicker kivymd.theme_picker.MDThemePicker
#:import MDBottomNavigation kivymd.tabs.MDBottomNavigation
#:import MDBottomNavigationItem kivymd.tabs.MDBottomNavigationItem

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
            text: "Id List Generation" # Why are these not set!!!

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                ParameterTemplate:
                    OptionalParam:
                    OptionalParam:
                    FileParam:
                    StdoutBox:
                        id: out
                    MDIconButton:
                        icon: 'file'
                        pos_hint: {'center_x': 0.75, 'center_y': 0.5}
                        on_release: app.ship.print_foo()
                    MDIconButton:
                        icon: 'file'
                        pos_hint: {'center_x': 0.75, 'center_y': 0.5}
                        on_release: out.write()

        MDTab:
            name: 'pmc'
            text: 'Fetch from PMC'
            icon: "movie"

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                ParameterTemplate:
            
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
    ship = __import__("SHIP")

    theme_cls = ThemeManager()

    def build(self):
        sys.stdout = f
        return Builder.load_string(kv)

    
if __name__ == '__main__':
    MainApp().run()
    sys.stdout = sys.__stdout__
    print(f.getvalue())
