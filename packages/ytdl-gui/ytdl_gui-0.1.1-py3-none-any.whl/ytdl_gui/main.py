import os
import sys
from typing import Dict, List

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject
from gi.repository import Gtk, Gio

from ytdl_gui.youtube import YTDL_Controller, validate_link, convert_link
from ytdl_gui.dialog import SelectFolder
from ytdl_gui.const import *

class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Youtube Downloader")
        self.set_default_size(WIDTH, HEIGHT)
        self.controller = YTDL_Controller(self)
        self.savepath = os.path.expanduser('~')

        GObject.signal_new('hook', self, GObject.SignalFlags.RUN_LAST,
                           GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        download_button = Gtk.Button(label='Download')
        download_button.connect('clicked', self.download_all)
        savepath_button = Gtk.Button(label='Save path')
        savepath_button.connect('clicked', self.select_savepath)

        self.formats = {'Best Audio + Video': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio', 'Best': 'best', 'Best Video': 'bestvideo', 'Best Audio': 'bestaudio', 'Worst': 'worst', 'Worst Video': 'worstvideo', 'Worst Audio': 'worstaudio', 'Worst vid + Best Audio': 'worstvideo[ext=mp4]+bestaudio[ext=m4a]/worstvideo+bestaudio', 'Best vid + Worst Audio': 'bestvideo[ext=mp4]+worstaudio[ext=m4a]/bestvideo+worstaudio',}
        self.format_dropdown = Gtk.ComboBoxText()
        for format_text in self.formats.keys():
            self.format_dropdown.append(format_text, format_text)

        self.url_liststore = Gtk.ListStore.new([GObject.TYPE_STRING, GObject.TYPE_STRING])
        self.url_treeview = Gtk.TreeView.new_with_model(self.url_liststore)
        self.url_treeview.set_hexpand(True)
        self.url_treeview.set_vexpand(True)
        self.url_treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.url_treeview.set_headers_visible(True)
        self.url_treeview.set_reorderable(True)
        self.videoid_to_index_dict: Dict[str, int] = {}

        cols = ('URL', 'Status')
        for column_index, column_title in enumerate(cols):
            cell_render = Gtk.CellRendererText.new()
            cell_render.set_property('editable', 'false')
            
            treeview_column = Gtk.TreeViewColumn(
                title=column_title,
                cell_renderer=cell_render,
                text=column_index,
            )

            self.url_treeview.append_column(column=treeview_column)

        add_url_button = Gtk.Button(label='Add URL')
        add_url_button.connect('clicked', self.add_url)

        self.url_entry = Gtk.Entry()
        self.status_lbl = Gtk.Label(label='Press download to start downloading')

        box.pack_start(savepath_button, False, False, 0)
        box.pack_start(self.url_entry, False, False, 0)
        box.pack_start(add_url_button, False, False, 0)
        box.pack_start(self.url_treeview, True, True, 0)
        box.pack_start(download_button, False, False, 0)
        box.pack_start(self.format_dropdown, False, False, 0)
        box.pack_start(self.status_lbl, False, False, 0)

        self.add(box)
        self.show_all()
        self.connect('hook', self.handle_hook)

    def add_url(self, _button):
        text: str = self.url_entry.get_text()
        urls: List[str] = text.splitlines()
        for url in urls:
            video_id: str = convert_link(url)
            if validate_link(url):
                index = len(self.url_liststore)
                self.url_liststore.insert_with_valuesv(-1, (0, 1), (url, 'Waiting', ))
                self.url_entry.set_text('')
                self.videoid_to_index_dict[video_id] = index

    def select_savepath(self, _button):
        SelectFolder(parent=self, init_path=self.savepath, select_multiple=False)

    def handle_hook(self, _window, data):
        url: str = data['info_dict']['webpage_url']
        video_id: str = convert_link(url)
        index: int = self.videoid_to_index_dict[video_id]
        if data['status'] == 'finished':
            self.url_liststore[index][1] = 'Done downloading'
        elif data['status'] == 'downloading':
            self.url_liststore[index][1] = f'Downloading: {data["_percent_str"]}'

    def download_all(self, _button):
        formats = self.formats[self.format_dropdown.get_active_text()]
        for row in self.url_liststore:
            url = row[0]
            self.controller.download_threaded(url, formats, self.savepath)


class App(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(
            self, application_id='app.test.id', flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect('activate', self.on_activate)

    def on_activate(self, *_data):
        self.window = Window()
        self.add_window(self.window)


def main():
    app = App()
    app.run(None)


if __name__ == '__main__':
    sys.exit(main())
