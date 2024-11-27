import json
import os
import arabic_reshaper
from bidi.algorithm import get_display
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import LabelBase
from kivy.uix.image import Image
from kivy.uix.screenmanager import SlideTransition
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget


# Function to get the correct path for assets
def get_asset_path(asset_name):
    # Get the current directory (InterLexiArabicApp folder)
    current_dir = os.path.dirname(__file__)

    # Construct path for assets (fonts, images, etc.) from the current directory
    asset_path = os.path.join(current_dir, 'assets', asset_name)
    
    # Return the absolute path
    return os.path.abspath(asset_path)

# Load JSON data
def load_json_data():
    json_file_path = get_asset_path('data.json')
    with open(json_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Register the Arabic font globally
LabelBase.register(name='Arial', fn_regular=get_asset_path('fonts/arial.ttf'))

# Function to reshape and apply bidi algorithm to Arabic text
def reshape_and_bidi(text):
    reshaped_text = arabic_reshaper.reshape(text)  # Reshape the Arabic text
    return get_display(reshaped_text)  # Apply bidi algorithm to ensure correct text display

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # Layout to hold everything
        layout = FloatLayout()

        # Add logo image and center it on the screen
        logo = Image(source=get_asset_path('logo/logo.png'), size_hint=(None, None), size=(200, 200))
        # Center the logo and give it some padding from the top
        logo.pos_hint = {'center_x': 0.5, 'center_y': 0.75}
        layout.add_widget(logo)

        # Add title and position it just below the logo, centered horizontally
        title = Label(text="InterLexi Arabic", font_size=30, size_hint=(None, None), height=50)
        # Center the title horizontally and position it below the logo
        title.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
        layout.add_widget(title)

        # Button to go to Table of Contents, centered horizontally
        toc_button = Button(text="Go to Table of Contents", font_size=20, size_hint=(None, None), height=50)
        # Center the button horizontally and position it below the title
        toc_button.pos_hint = {'center_x': 0.5, 'center_y': 0.45}
        toc_button.bind(on_press=self.go_to_toc)
        layout.add_widget(toc_button)

        # Add layout to the screen
        self.add_widget(layout)

    def go_to_toc(self, instance):
        # Set transition for left to right sliding
        self.manager.transition = SlideTransition(direction='left')  # Left to right transition
        
        # Navigate to Table of Contents screen
        self.manager.current = 'toc'

class TOCScreen(Screen):
    def __init__(self, **kwargs):
        super(TOCScreen, self).__init__(**kwargs)

        # Load JSON content
        data = load_json_data()

        # Layout for TOC
        layout = BoxLayout(orientation='vertical', padding=10)

        # Add a label for the title
        title = Label(text="Table of Contents", font_size=25, size_hint=(1, None), height=50, halign='center', font_name='Arial')
        layout.add_widget(title)

        # Scrollable list of topics
        scroll_view = ScrollView()

        # Create a grid to hold the buttons for each topic
        grid = GridLayout(cols=1, padding=10, spacing=10, size_hint=(None, None), height=self.get_height(data))

        for topic in data['topics']:
            button = Button(text=reshape_and_bidi(topic['name']), size_hint_y=None, height=50, font_size=18, font_name='Arial')
            button.bind(on_press=lambda instance, topic=topic: self.go_to_topic(instance, topic))
            grid.add_widget(button)

        scroll_view.add_widget(grid)
        layout.add_widget(scroll_view)

        # Back button at the bottom
        back_button = Button(text="Back", size_hint=(None, None), size=(200, 50))
        back_button.bind(on_press=self.back_to_main)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def get_height(self, data):
        # Dynamically calculate the height based on the number of topics
        return len(data['topics']) * 60  # 60 is the height of each button

    def go_to_topic(self, instance, topic):
        # Pass the topic data to the topic screen
        self.manager.current = f"topic_{topic['id']}"
        topic_screen = self.manager.get_screen(f"topic_{topic['id']}")
        topic_screen.load_topic_data(topic)

    def back_to_main(self, instance):
        # Navigate back to the Main screen
        self.manager.transition = SlideTransition(direction='right')  # Slide from right (backwards transition)
        self.manager.current = 'main'


class TopicScreen(Screen):
    def __init__(self, topic_id, **kwargs):
        super(TopicScreen, self).__init__(**kwargs)
        self.topic_id = topic_id

        # Layout for displaying topic content
        layout = BoxLayout(orientation='vertical', padding=10)

        # Add a label for the title of the topic
        self.title_label = Label(text="", font_size=30, size_hint=(1, None), height=50, halign='center', font_name='Arial')
        layout.add_widget(self.title_label)

        # Scrollable list of phrases
        self.scroll_view = ScrollView()

        # Layout for the phrases (each phrase is a label)
        self.phrase_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.phrase_layout.bind(minimum_height=self.phrase_layout.setter('height'))

        self.scroll_view.add_widget(self.phrase_layout)
        layout.add_widget(self.scroll_view)

        # Back button at the bottom
        back_button = Button(text="Back", size_hint=(None, None), size=(200, 50))
        back_button.bind(on_press=self.back_to_toc)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def load_topic_data(self, topic):
        # Set the title of the topic
        self.title_label.text = reshape_and_bidi(topic['name'])

        # Clear any previous content in the phrase layout
        self.phrase_layout.clear_widgets()

        # Add phrases for this topic
        for phrase in topic['phrases']:
            phrase_label = Label(text=f"{phrase['translation']} = {reshape_and_bidi(phrase['text'])} ", font_size=40, size_hint_y=None, height=40, font_name='Arial')
            self.phrase_layout.add_widget(phrase_label)

    def back_to_toc(self, instance):
        # Navigate back to the Table of Contents screen
        self.manager.transition = SlideTransition(direction='right')  # Slide from right (backwards transition)
        self.manager.current = 'toc'


class InterLexiArabicApp(App):
    def build(self):
        self.sm = ScreenManager()

        # Add screens to the manager
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(TOCScreen(name='toc'))

        # Dynamically create Topic screens based on the JSON
        data = load_json_data()
        for topic in data['topics']:
            topic_screen = TopicScreen(topic['id'], name=f"topic_{topic['id']}")
            self.sm.add_widget(topic_screen)

        return self.sm

if __name__ == '__main__':
    InterLexiArabicApp().run()
