#!/usr/bin/env python3

import tkinter as tk
import os
import shutil

import tkinter.messagebox as tkmsg
import tkinter.simpledialog as tkdialog

stack = []


class Menu():
    def __init__(self, window):
        self.window = window

        self.tmp = '/tmp/.ntheme/'
        if not os.path.exists(self.tmp):
            os.makedirs(self.tmp)

    def empty(self):
        pass

    def warn(self, *args):
        tkmsg.showwarning(*args)

    def oper_2(self, exec, *args, err, **kwargs):
        try:
            exec(*args)
        except:
            err(*tuple(kwargs.values()))

    def get_name(self, dialog):
        name = ''
        while not name:
            name = tkdialog.askstring(dialog[0], 'Name:')
            if not name:
                self.warn('Warning', 'Empty name')
            elif os.path.exists(self.window.path_str.get() + name):
                self.warn('Warning', 'Object already exists')
                name = ''
        return name

    def inner_move(self, source, final, dialog):
        msg = {'title': 'Warning', 'message': dialog}
        self.oper_2(shutil.move, source, final, err=self.warn, **msg)
        self.window.show_content()

    def cancel(self, event=tk.Event()):
        if len(stack) > 0:
            stack[-1][0](stack[-1][1],
                         stack[-1][2], 'Cannot cancel')
            stack.pop()


class CanvasMenu(Menu, tk.Menu):
    def __init__(self, window, parent):
        Menu.__init__(self, window)
        tk.Menu.__init__(self, parent, tearoff=0)

        self.add_command(label='New file...', command=self.make_file)
        self.add_command(label='New folder...', command=self.make_dir)
        self.add_separator()

    def make_file(self):
        name = self.__get_name('Creating a file...')
        path = self.window.path_str.get() + '/'

        def exec():
            open(self.window.path_str.get() + '/' + name, 'w').close()
        msg = {'title': 'Warning', 'message': 'Unable to create a file!'}
        self.oper_2(exec, err=self.warn, **msg)
        self.window.show_content()
        stack.append([self.inner_move, path + name, self.tmp])

    def make_dir(self):
        name = self.__get_name('Creating a directory...')
        path = self.window.path_str.get() + '/'
        msg = {'title': 'Warning', 'message': 'Unable to create a folder!'}
        self.oper_2(os.makedirs, path + name, err=self.warn, **msg)
        self.window.show_content()
        stack.append([self.inner_move, path + name, self.tmp])

    def __get_name(self, dialog):
        name = ''
        while not name:
            name = tkdialog.askstring(dialog[0], 'Name:')
            if not name:
                self.warn('Warning', 'Empty name')
            elif os.path.exists(self.window.path_str.get() + '/' + name):
                self.warn('Warning', 'Object already exists')
                name = ''
        return name

    def show(self, event):
        self.oper_2(self.delete, 'Paste moved...', err=self.empty)
        self.oper_2(self.delete, 'Paste copied...', err=self.empty)
        self.oper_2(self.delete, 'Cancel...', err=self.empty)
        if self.window.item_menu.copy_str['path'] != '':
            self.add_command(label='Paste copied...',
                             command=self.window.item_menu.copy_item)
        if self.window.item_menu.move_str['path'] != '':
            self.add_command(label='Paste moved...',
                             command=self.window.item_menu.move_item)
        if len(stack) > 0:
            self.add_command(label='Cancel...',
                             command=self.window.item_menu.cancel)
        self.post(event.x_root, event.y_root)
        self.window.item_menu.unpost()


class ItemMenu(Menu, tk.Menu):
    def __init__(self, window, parent):
        Menu.__init__(self, window)
        tk.Menu.__init__(self, parent, tearoff=0)
        self.window = window
        self.copy_str = {'path': '', 'name': ''}
        self.move_str = {'path': '', 'name': ''}
        self.add_command(label='Rename...', command=self.__rename_item)
        self.add_command(label='Copy...', command=self.copy_fill)
        self.add_command(label='Cut...', command=self.move_fill)
        self.add_separator()
        self.add_command(label='Remove...', command=self.__delete_item)

    def __del__(self):
        if os.path.exists(self.tmp):
            shutil.rmtree(self.tmp)

    def copy_fill(self):
        self.copy_str = self.item

    def move_fill(self):
        self.move_str = self.item

    def __delete_item(self):
        if not tkmsg.askyesno('Confirmation', 'Are you sure you want to delete?'):
            return
        if self.__check_path(self.item['path'], ''):
            return
        self.inner_move(self.item['path'], self.tmp +
                        self.item['name'], 'Cannot delete')
        stack.append([self.inner_move, self.tmp +
                      self.item['name'], self.item['path']])

    def __rename_item(self):
        name = self.get_name('Renaming a file...')
        path = self.window.path_str.get() + '/'
        self.__check_path(self.item['path'], path + name)
        self.inner_move(self.item['path'], path + name, 'Cannot rename item')
        stack.append([self.inner_move, path + name, self.item['path']])

    def move_item(self, event=tk.Event()):
        if self.move_str['path'] == '':
            return
        path = self.window.path_str.get() + '/' + self.move_str['name']
        if self.__check_path(self.move_str['path'], path):
            return
        self.inner_move(self.move_str['path'], path, 'Cannot move item')
        self.move_str = {'path': '', 'name': ''}
        stack.append([self.inner_move, path, self.item['path']])

    def copy_item(self, event=tk.Event()):
        if self.copy_str['path'] == '':
            return
        path = self.window.path_str.get() + '/' + self.copy_str['name']
        if self.__check_path(self.copy_str['path'], path):
            return
        self.__inner_copy(self.copy_str['path'], path)
        stack.append([self.inner_move, path, self.tmp])

    def __inner_copy(self, source, final):
        msg = {'title': 'Warning', 'message': 'Cannot copy'}

        def exec():
            self.oper_2(shutil.copytree, source, final, err=self.warn, **msg)
        self.oper_2(shutil.copy2, source, final, err=exec)
        self.window.show_content()

    def __check_path(self, source, final):
        if not os.path.exists(source):
            self.warn('Warning', 'Source object does not exist')
            return True
        if os.path.exists(final):
            self.warn('Warning', 'Final object already exists')
            return True

    def show(self, event, name):
        self.post(event.x_root, event.y_root)
        self.window.canvas_menu.unpost()
        self.item = name
