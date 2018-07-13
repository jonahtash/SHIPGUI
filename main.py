from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
import filebrowser

from kivymd.bottomsheet import MDListBottomSheet, MDGridBottomSheet
from kivymd.button import MDIconButton
from kivymd.date_picker import MDDatePicker
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch, BaseListItem
from kivymd.material_resources import DEVICE_TYPE
from kivymd.navigationdrawer import MDNavigationDrawer, NavigationDrawerHeaderBase
from kivymd.selectioncontrols import MDCheckbox
from kivymd.snackbar import Snackbar
from kivymd.theming import ThemeManager
from kivymd.time_picker import MDTimePicker
from kivymd.textfields import MDTextField
from kivymd.button import MDRaisedButton
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



<Param@BoxLayout>:
    orientation: 'horizontal'
    spacing: 30
    MDTextField:
        line_width: root.minimum_width-dp(36)
        pos_hint:    {'center_x': 0.75, 'center_y': 0.5}
        hint_text: "Parameter"
    MDIconButton:
        icon: 'file'
        pos_hint: {'center_x': 0.25, 'center_y': 0.8}
        on_release: app.open_dialog()
        

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
    name: 'tabs'
    MDTabbedPanel:
        id: tab_panel
        tab_display_mode:'text'

        MDTab:
            name: 'music'
            text: "Music" # Why are these not set!!!
            icon: "playlist-play"

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                ParameterTemplate:
                    OptionalParam:
                    OptionalParam:
                    Param

        MDTab:
            name: 'movies'
            text: 'Movies'
            icon: "movie"

            AnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                ParameterTemplate:
                    Param
                    FileChooserListView:
                        path: './'
                        on_selection: app.file_select(self.selection,self)
            
'''

user_path = "C:/Users/jnt11/"

class MainApp(App):
    theme_cls = ThemeManager()
    def load(self, path, selection):
        print(path,  selection)
    def build(self):
        return Builder.load_string(kv)
    def file_select(self,selection,f):
        print("selected: %s" % selection)
    def open_dialog(self):
        fc = FileChooserListView(path="./")
        fb = filebrowser.FileBrowser(select_string='Select',
                                  favorites=[(user_path, 'Documents')])
        tf = MDTextField(hint_text="wink wink")
        bl = BoxLayout(orientation = 'vertical')
        bl.add_widget(fb)
        bl.add_widget(tf)
        pu = Popup(id='file_chooser_dialog',title='Test popup',content=bl,size_hint=(None, None), size=(800, 500),auto_dismiss=False)
        fb.bind(on_success=self._fbrowser_success,
                         on_canceled=pu.dismiss,
                         on_submit=self._fbrowser_submit)
        pu.open()
    def _fbrowser_canceled(self, instance):
        print('cancelled, Close self.')

    def _fbrowser_success(self, instance):
        print(instance.selection)

    def _fbrowser_submit(self, instance):
        print(instance.selection)
if __name__ == '__main__':
    MainApp().run()
