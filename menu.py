#!/usr/bin/env python3

import tkinter as tk
import os
import shutil

import tkinter.messagebox as tkmsg
import tkinter.simpledialog as tkdialog


class Menu():
    def __init__(self, window):
        self.window = window

    def empty(self):
        pass

    def warn(self, *args):
        tkmsg.showwarning(*args)

    def oper_2(self, exec, *args, err, **kwargs):
        try:
            exec(*args)
        except:
            err(*tuple(kwargs.values()))

    def operate(self, exec, *args):
        self.oper_2(exec=exec, args=args, err=self.warn,
                    title='Warning', message='Error')

    def get_name(self, dialog):
        name = ''
        while not name:
            name = tkdialog.askstring(dialog[0], "Name:")
            if not name:
                tkmsg.showwarning("Warning", "Empty name")
            elif os.path.exists(self.window.path_str.get() + name):
                tkmsg.showwarning("Warning", "Object already exists")
                name = ''
        return name


class CanvasMenu(Menu, tk.Menu):
    def __init__(self, window, parent):
        Menu.__init__(self, window)
        tk.Menu.__init__(self, parent, tearoff=0)

        self.add_command(label="New file...", command=self.make_file)
        self.add_command(label="New folder...", command=self.make_dir)

    def make_file(self):
        name = self.__get_name("Creating a file...")

        def exec():
            open(self.window.path_str.get() + name, 'w').close()
        msg = {'title': 'Warning', 'message': 'Unable to create a file!'}
        self.oper_2(exec, err=self.warn, **msg)
        self.window.show_content()

    def make_dir(self):
        path = self.window.path_str.get() + self.__get_name("Creating a directory...")
        msg = {'title': 'Warning', 'message': 'Unable to create a folder!'}
        self.oper_2(os.makedirs, path, err=self.warn, **msg)
        self.window.show_content()

    def __get_name(self, dialog):
        name = ''
        while not name:
            name = tkdialog.askstring(dialog[0], "Name:")
            if not name:
                self.warn('Warning', 'Empty name')
            elif os.path.exists(self.window.path_str.get() + name):
                self.warn('Warning', 'Object already exists')
                name = ''
        return name

    def popup_menu(self, event):
        self.oper_2(self.delete, "Paste moved...", err=self.empty)
        self.oper_2(self.delete, "Paste copied...", err=self.empty)
        if self.window.item_menu.copy_str[1] != '':
            self.add_command(label='Paste copied...',
                             command=self.window.item_menu.copy_item)
        if self.window.item_menu.move_str[1] != '':
            self.add_command(label='Paste moved...',
                             command=self.window.item_menu.move_item)
        self.post(event.x_root, event.y_root)
        self.window.item_menu.unpost()


class ItemMenu(tk.Menu, Menu):
    def __init__(self, window, parent):
        super(ItemMenu, self).__init__(parent, tearoff=0)
        self.window = window
        self.copy_str = ['', '']
        self.move_str = ['', '']
        self.add_command(label="Rename...", command=self.rename_item)
        self.add_command(label="Copy...", command=self.copy_fill)
        self.add_command(label="Cut...", command=self.move_fill)
        self.add_separator()
        self.add_command(label="Remove :(", command=self.delete_item)

    def copy_fill(self):
        self.copy_str = [self.window.path_str.get() + self.item, self.item]

    def move_fill(self):
        self.move_str = [self.window.path_str.get() + self.item, self.item]

    def delete_item(self, event=tk.Event()):
        if not tkmsg.askyesno('Confirmation', 'Are you sure you want to delete_item?'):
            return

        path = self.window.path_str.get() + self.item
        if self.__check_path(path, ''):
            return
        msg = {'title': 'Warning', 'message': 'Cannot delete'}

        def exec():
            self.oper_2(shutil.rmtree, path, err=self.warn, **msg)
        self.oper_2(os.remove, path, err=exec)

        self.window.show_content()

    def rename_item(self, event=tk.Event()):
        name = self.get_name("Renaming a file...")
        path = self.window.path_str.get()
        self.__check_path(path + self.item, path + name)
        self.__inner_move(path + self.item, path + name, 'Cannot rename item')

    def move_item(self, event=tk.Event()):
        path = self.window.path_str.get() + self.move_str[1]
        if self.__check_path(self.copy_str[0], path):
            return
        self.__inner_move(self.move_str[0], path, 'Cannot move item')

    def copy_item(self, event=tk.Event()):
        c_str = self.copy_str
        path = self.window.path_str.get() + c_str[1]
        if self.__check_path(self.copy_str[0], path):
            return
        msg = {'title': 'Warning', 'message': 'Cannot copy'}

        def exec():
            self.oper_2(shutil.copytree, c_str[0], path, err=self.warn, **msg)
        self.oper_2(shutil.copy2, c_str[0], path, err=exec)
        self.window.show_content()

    def __check_path(self, source, final):
        if not os.path.exists(source):
            self.warn('Warning', 'Source object does not exist')
            return True
        if os.path.exists(final):
            self.warn('Warning', 'Final object already exists')
            return True

    def __inner_move(self, source, final, dialog):
        msg = {'title': 'Warning', 'message': dialog}
        self.oper_2(os.rename, source, final, err=self.warn, **msg)
        self.window.show_content()

    def popup_menu(self, event, name):
        self.post(event.x_root, event.y_root)
        self.window.canvas_menu.unpost()
        self.item = name
