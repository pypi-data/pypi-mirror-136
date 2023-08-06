import os
from gi.repository import Gtk, Gio

class SelectFolder(Gtk.FileChooserDialog):
    def __init__(self, parent, init_path: str = os.path.expanduser('~'), select_multiple: bool = False):
        super().__init__(transient_for=parent, use_header_bar=True)
        self.parent = parent
        self.select_multiple = select_multiple

        self.set_action(action=Gtk.FileChooserAction.SELECT_FOLDER)
        title = 'Select folder'
        self.set_title(title=title)
        self.set_modal(modal=True)
        self.set_select_multiple(select_multiple=self.select_multiple)
        self.connect('response', self.dialog_response)
        self.set_current_folder(
            init_path
        )

        self.add_buttons(
            '_Cancel', Gtk.ResponseType.CANCEL,
            '_Select', Gtk.ResponseType.OK
        )
        btn_select = self.get_widget_for_response(
            response_id=Gtk.ResponseType.OK,
        )
        btn_select.get_style_context().add_class(class_name='suggested-action')

        btn_cancel = self.get_widget_for_response(
            response_id=Gtk.ResponseType.CANCEL,
        )
        btn_cancel.get_style_context().add_class(class_name='destructive-action')

        self.show()

    def dialog_response(self, widget, response):
        if response == Gtk.ResponseType.OK:
            if self.select_multiple:
                ...
                # gliststore = self.get_files()
            else:
                glocalfile = self.get_file()
                self.parent.savepath = glocalfile.get_path()
        elif response == Gtk.ResponseType.CANCEL:
            ...
        widget.close()
