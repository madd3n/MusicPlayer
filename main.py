from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from os import walk
from kivy.core.audio import SoundLoader
from kivy import platform
from kivy.properties import Clock

class GridLayoutExample(StackLayout):
    sound = None
    def __init__(self, **kwargs):
        super(GridLayoutExample, self).__init__(**kwargs)

        #   Create Buttons
        play_music1_button = Button(text="music1", size_hint=(None,None), size=(dp(100),dp(120)))
        play_gms_button = Button(text="GMS", size_hint=(None,None), size=(dp(100),dp(120)))
        stop_button = Button(text="Stop", size_hint=(None,None), size=(dp(100),dp(120)))
        
        #   Bind events to buttons
        play_music1_button.bind(on_press=self.play_music1_sound)
        play_gms_button.bind(on_press=self.play_gms_sound)
        stop_button.bind(on_press=self.stop_sound)
        
        #   Add widgets to screen
        self.add_widget(play_music1_button)
        self.add_widget(play_gms_button)
        self.add_widget(stop_button)

    def play_music1_sound(self, dt):
        self.sound = SoundLoader.load(os.path.join(os.getenv('EXTERNAL_STORAGE'), 'Music/music1.wav'))
        self.sound.play()
    
    def play_gms_sound(self, dt):
        self.sound = SoundLoader.load('/storage/emulated/0/Download/Music/galaxy.wav')
        self.sound.play()
        
    def stop_sound(self, dt):
        self.sound.stop()

class SimpleMusicApp(App):
    pass

if __name__ == "__main__":
    SimpleMusicApp().run()

