from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.toolbar.toolbar import MDTopAppBar
from kivy.properties import ObjectProperty
from kivymd.uix.button.button import MDRaisedButton,MDRectangleFlatButton
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.navigationdrawer.navigationdrawer import MDNavigationDrawer,MDNavigationLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.progressbar.progressbar import MDProgressBar
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Ellipse, Rectangle
from kivy import platform
from os import walk
from kivy.metrics import dp
from kivy.properties import Clock
from kivy.core.audio import SoundLoader
from kivymd.uix.slider.slider import MDSlider
from kivymd.uix.label.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout

class MusicPlayer(MDApp):
    def __init__(self, **kwargs):
        super(MusicPlayer, self).__init__(**kwargs)

        if(platform == "android"):
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

    def build(self):
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.accent_palette = "DeepOrange"
        self.theme_cls.theme_style = "Dark"
        Builder.load_file("simplemusic.kv")
        return Demo()

class Demo(ScreenManager):
    def __init__(self, **kwargs):
        super(Demo, self).__init__(**kwargs)
        self.add_widget(MainScreen())

    def build(self):
        pass

class MainScreen(Screen):
    sideMenu = ObjectProperty()
    topMenu = ObjectProperty()
    dir_to_search = "Music/"
    files = []
    playlistSongs = []
    availableSongs = []
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.name="main_screen"
        self.sideMenu = SideMenu()
        self.topMenu = TopMenu()

        if(platform == "android"):
            self.dir_to_search = os.path.join(os.getenv('EXTERNAL_STORAGE'), 'Music/')
        else:
            self.dir_to_search = "Music/"

        self.add_widget(NavigationOptionsLayout(0.13))
        self.add_widget(TopMenu())
        #self.add_widget(self.sideMenu)
        self.list_all_files()
    
    def list_all_files(self):
        for (dirpath, dirnames, filenames) in walk(self.dir_to_search):
            self.files.extend(filenames)
            break

class TopMenu(MDTopAppBar):
    def __init__(self, **kwargs):
        super(TopMenu, self).__init__(**kwargs)
        self.pos_hint= {"top":1}
        self.title= "Navigation"
        self.elevation=2
        self.name = "menu"
        #self.left_action_items= [["menu", lambda x: self.parent.sideMenu.set_state("open")]]

class SideMenu(MDNavigationDrawer):
    def __init__(self, **kwargs):
        super(SideMenu, self).__init__(**kwargs)
        self.name="nav_drawer"
        menuContent = MenuContent()
        menuContent.nav_drawer = self
        self.add_widget(menuContent)

class NavigationOptionsLayout(MDNavigationLayout):
    def __init__(self,value, **kwargs):
        super(NavigationOptionsLayout, self).__init__(**kwargs)
        self.name = "sideMenuOptions"
        self.add_widget(OptionsScreenManager(value))

class OptionsScreenManager(ScreenManager):
    playlistScreen = None
    def __init__(self,value,  **kwargs):
        super(OptionsScreenManager, self).__init__(**kwargs)
        name = "screen_manager"
        musicList = MusicList(value,name="list_songs")
        self.add_widget(musicList)
        self.playlistScreen = PlaylistScreen(value,name="playlist")
        self.add_widget(self.playlistScreen)

class MusicList(Screen):
    musicFilesFound = None
    getParent = None
    SongItemsList = None
    def __init__(self,value, **kwargs):
        super(MusicList, self).__init__(**kwargs)
        self.size_hint=(1,1)

        scrollView = MDScrollView()
        self.SongItemsList = MDStackLayout()
        scrollView.add_widget(self.SongItemsList)
        
        self.SongItemsList.size_hint_y =1 - value
        self.SongItemsList.padding = (0,75,0,0)

        self.add_widget(scrollView)
        button = MDRectangleFlatButton()
        button.pos_hint={"right":1}
        button.text = "Playlist"
        button.bind(on_release=self.GoToPlaylist)
        self.add_widget(button)

        button2 = MDRectangleFlatButton()
        button2.pos_hint={"left":1}
        button2.text = "Load Music"
        button2.bind(on_release=self.build)
        self.add_widget(button2)

    def build(self, instance):
        self.getParent = self.parent.parent.parent
        self.musicFilesFound = self.getParent.files
        self.load_content()
    
    def GoToPlaylist(self, instance):
        self.parent.playlistScreen.build(self.getParent)
        self.parent.current="playlist"

    def load_content(self):
        for i in range(0,len(self.musicFilesFound)):
            fileName = str(self.musicFilesFound[i][0:self.musicFilesFound[i].find('.')])
            filename_extension = self.musicFilesFound[i]
            self.b=MDRectangleFlatButton(text=fileName,size_hint=(0.1,0.15))
            self.b.bind(on_press = self.add_to_playlist)
            self.SongItemsList.add_widget(self.b)

            internal_song = (fileName, filename_extension)
            self.getParent.availableSongs.append(internal_song)

    def add_to_playlist(self, instance):
        instance.disabled = True
        self.getParent.playlistSongs.append(self.find_music_in_available_songs(instance))

    def find_music_in_available_songs(self, instance):
        for i in range(0,len(self.getParent.availableSongs)):
            if(self.getParent.availableSongs[i][0] == instance.text):
                #self.current_playlist_song = i
                return self.getParent.availableSongs[i]

class PlaylistScreen(Screen):
    getParent = None
    PlaylistItemsList = None
    is_music_playing = False
    music_current_position = 0
    active_button = None
    music_Volume = 20
    musicVolume = None
    musicCurrentTime = ""
    musicTotalTime = ""

    def __init__(self, value, **kwargs):
        super(PlaylistScreen, self).__init__(**kwargs)
        
        scrollView = MDScrollView()
        self.PlaylistItemsList = MDStackLayout()
        musicInfo = MDStackLayout()

        scrollView.add_widget(self.PlaylistItemsList)
        self.PlaylistItemsList.pos_hint={"center_x":0.5, "center_y":0.5}

        self.musicCurrentTime = MDLabel(text="00:00", size_hint={0.1,0.05})
        self.musicTotalTime = MDLabel(text="00:00", pos_hint={"right":1},size_hint={0.1,0.05})
        self.musicVolume = MDSlider(size_hint={0.8,0.05})
        self.musicVolume.value = self.music_Volume
        self.musicVolume.bind(value=self.on_slider_value)
        
        musicInfo.size_hint=(1,0.2)
        musicInfo.minimum_width = 400
        musicInfo.add_widget(self.musicCurrentTime)
        musicInfo.add_widget(self.musicVolume)
        musicInfo.add_widget(self.musicTotalTime)
        
        self.PlaylistItemsList.size_hint_y =1 - value
        self.PlaylistItemsList.padding = (0,75,0,0)

        self.size_hint=(1,1)
       
        self.add_widget(scrollView)
        self.add_widget(musicInfo)

        button = MDRectangleFlatButton()
        button.pos_hint={"right":1}
        button.text = "Music List"
        button.bind(on_release=self.GoToMusicList)
        self.add_widget(button)

    def build(self, instance):
        self.getParent = instance
        self.PlaylistItemsList.clear_widgets()
        for i in range(0,len(self.getParent.playlistSongs)):
            fileName = str(self.getParent.playlistSongs[i][0])
            newPlaylistItem = PlaylistItems(fileName, i)
            newPlaylistItem.ids.playlist_Button.bind(on_release=self.PlaySong)
            self.PlaylistItemsList.add_widget(newPlaylistItem)

    def on_slider_value(self, widget, touch):
        self.music_Volume = int(widget.value)/100
        if(self.is_music_playing):
            self.playing_music.volume = self.music_Volume

    def GoToMusicList(self, instance):
        self.parent.current="list_songs"

    def PlaySong(self, instance):
        if(self.is_music_playing):
            Clock.unschedule(self.status_update)
            self.music_current_position = 0
            self.playing_music.stop()
            self.current_playlist_item.set_progressbar_value(0)

        self.is_music_playing = True
        self.playing_music_dir = self.getParent.dir_to_search + self.find_music_in_playlist(instance)
        self.playing_music = SoundLoader.load(self.playing_music_dir)

        if(self.music_Volume > 1):
            self.music_Volume = self.music_Volume /100

        self.playing_music.volume = self.music_Volume
        
        if (self.active_button != None):
            self.active_button.md_bg_color = [1,0.6,0,1]

        self.active_button = instance
        self.active_button.md_bg_color = [1,0.35,0,1]

        self.current_playlist_item = instance.parent
        self.current_playlist_item.set_max_progressbar_lenght(self.playing_music.length)
        self.musicTotalTime.text = self.get_music_time(self.playing_music.length)
        
        self.song_remaining_time = self.playing_music.length

        self.playing_music.play()
        Clock.schedule_interval(self.status_update, 1)

    def get_music_time(self, seconds):
        minutes = seconds // 60
        seconds %= 60
        return "%02i:%02i" % (minutes, seconds)

    def find_music_in_playlist(self, instance):
        for i in range(0,len(self.getParent.playlistSongs)):
            if(self.getParent.playlistSongs[i][0] == instance.text):
                self.current_playlist_song = i
                return self.getParent.playlistSongs[i][1]

    def status_update(self, instance):
        status = self.playing_music.status
        if status == 'stop':
            self.changing_music = True
            if len(self.current_playlist_item.parent.children) > self.current_playlist_item.pos_in_playlist +1:
                self.PlaySong(self.get_next_playlist_item().ids.playlist_Button)
        elif status == 'play':
            if(self.music_current_position < self.playing_music.length -1):
                self.music_current_position += 1 
                self.song_remaining_time -=1
                self.current_playlist_item.set_progressbar_value(self.music_current_position)
                self.current_playlist_item.set_songTimeLabel_value(self.music_current_position)
                self.musicCurrentTime.text=self.get_music_time(self.music_current_position)
            else:
                self.current_playlist_item.set_progressbar_value(0)
        else:
            print("Music Ended")

    def get_next_playlist_item(self):
        nextValue = (self.current_playlist_item.pos_in_playlist + 1)
        for i in range(0, len(self.current_playlist_item.parent.children)):
            if(self.current_playlist_item.parent.children[i].pos_in_playlist == nextValue):
                return self.current_playlist_item.parent.children[i]

class PlaylistItems(MDGridLayout):
    buttonText = ""
    progressBarValue= 0
    songTimeLabel = "00:00"
    pos_in_playlist = 0
    def __init__(self, buttonTextValue, position, **kwargs):
        super(PlaylistItems, self).__init__(**kwargs)
        self.ids.playlist_Button.text = buttonTextValue
        self.pos_in_playlist = position

    def add_circular_progressbar(self):
        # Set constant for the bar thickness
        self.ids.playlist_progressBar.thickness = 10
        # Create a direct text representation
        self.ids.playlist_progressBar.label = CoreLabel(text=self.get_music_time(0), font_size=self.ids.playlist_progressBar.thickness+5)
        # Initialise the texture_size variable
        self.ids.playlist_progressBar.texture_size = None
        # Refresh the text
        self.refresh_circular_progressbar_text()
        # Redraw on innit
        self.draw_circular_progressbar()

    def draw_circular_progressbar(self):
        with self.ids.playlist_progressBar.canvas:
            # Empty canvas instructions
            print("self.ids.playlist_progressBar.pos: " + str(self.ids.playlist_progressBar.pos))
            self.ids.playlist_progressBar.canvas.clear()
            print("self.ids.playlist_progressBar.size: " + str(self.ids.playlist_progressBar.size))
            print("self.size: " + str(self.ids.playlist_progressBar.parent.size))
            # Draw no-progress circle
            Color(0.26, 0.26, 0.26)

            Ellipse(pos=self.ids.playlist_progressBar.pos, size=self.ids.playlist_progressBar.size)

            # Draw progress circle, small hack if there is no progress (angle_end = 0 results in full progress)
            """Color(0, 1, 0)
            Ellipse(pos=self.ids.playlist_progressBar.pos, size=self.ids.playlist_progressBar.size,
                    angle_end=(0.001 if self.ids.playlist_progressBar.value_normalized == 0 else self.ids.playlist_progressBar.value_normalized*360))

            # Draw the inner circle (colour should be equal to the background)
            Color(0, 0, 0)
            Ellipse(pos=(self.ids.playlist_progressBar.pos[0] + self.ids.playlist_progressBar.thickness / 2, self.ids.playlist_progressBar.pos[1] + self.ids.playlist_progressBar.thickness / 2),
                    size=(self.ids.playlist_progressBar.size[0] - self.ids.playlist_progressBar.thickness, self.ids.playlist_progressBar.size[1] - self.ids.playlist_progressBar.thickness))

            Color(1, 1, 1, 1)
            Rectangle(texture=self.ids.playlist_progressBar.label.texture, size=self.ids.playlist_progressBar.texture_size,
                  pos=(self.ids.playlist_progressBar.size[0] / 2 - self.ids.playlist_progressBar.texture_size[0] / 2 + self.ids.playlist_progressBar.pos[0], 
                        self.ids.playlist_progressBar.size[1] / 2 - self.ids.playlist_progressBar.texture_size[1] / 2 + self.ids.playlist_progressBar.pos[1]))"""

    def refresh_circular_progressbar_text(self):
        self.ids.playlist_progressBar.label.refresh()
        self.ids.playlist_progressBar.texture_size = list(self.ids.playlist_progressBar.label.texture.size)

    def set_circular_progressbar_value(self, value):
        self.ids.playlist_progressBar.value = value
        self.ids.playlist_progressBar.label.text = self.get_music_time(value)
        self.refresh_circular_progressbar_text()
        self.draw_circular_progressbar()
    
    def set_max_progressbar_lenght(self, value):
        self.ids.playlist_progressBar.max = value

    def set_progressbar_value(self, value):
        self.ids.playlist_progressBar.value = value

    def set_songTimeLabel_value(self, value):
        self.ids.song_Time_Label.text = self.get_music_time(value)
    
    def get_music_time(self, seconds):
        minutes = seconds // 60
        seconds %= 60
        return "%02i:%02i" % (minutes, seconds)

class MenuContent(BoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

if __name__ == "__main__":
    MusicPlayer().run()