#!/usr/bin/env python3

import menu
import os

import tkinter as tk
import tkinter.font as tkfont
import tkinter.messagebox as tkmsg


class MainWindow():
    def __init__(self):
        self.__make_window()
        self.__load_content()
        self.__make_path_frame()
        self.__make_main_canvas()
        self.show_content()

    def __make_window(self):
        self.window = tk.Tk()
        self.window.title('North Typical Heavy Extended Mount Explorer')
        self.window.resizable(width=True, height=True)
        self.window.config(background='#00E5E5')
        self.window.geometry('1280x720')
        self.window.minsize(width=self.window.winfo_screenwidth() // 4,
                            height=self.window.winfo_screenheight() // 4)
        self.window.bind('<Button-1>', self.__unpost)

    def __load_content(self):
        self.font = tkfont.Font(family='Arial')
        self.font.configure(size=11)
        self.image = {'dirs': [tk.PhotoImage(file='share/folder_rest.png'),
                      tk.PhotoImage(file='share/folder_open.png')],
                      'files': [tk.PhotoImage(file='share/file_rest.png'),
                                tk.PhotoImage(file='share/file_open.png')],
                      'unrec': [tk.PhotoImage(file='share/unknown_rest.png'),
                                tk.PhotoImage(file='share/unknown_open.png')],
                      'rest': [tk.PhotoImage(file='share/back.png'),
                               tk.PhotoImage(file='share/disk.png')]}

    def __make_path_frame(self):
        path_frame = tk.Frame(self.window)
        path_frame.configure(background='#00E5E5')
        path_frame.pack()

        path_font = tkfont.Font(family='Arial')
        path_font.configure(size=12, weight='bold')

        path_button = tk.Button(path_frame)
        path_button.configure(font=path_font, text='Go to path...')
        path_button.configure(width=10, height=1)
        path_button.configure(bg='blue', fg='white')
        path_button.configure(activebackground='red')
        path_button.pack(padx=10, pady=5, side='left')

        self.path_tree = set()
        self.path_str = tk.StringVar(value='/')
        self.path_last = tk.StringVar(value='/')
        self.path_box = tk.Entry(path_frame)
        self.path_box.configure(textvariable=self.path_str)
        self.path_box.configure(width=80, justify='center')
        self.path_box.configure(bg='#84FCFC', fg='#115F15')
        self.path_box.pack(pady=10)

        def goto_f5(event=tk.Event()):
            path = self.path_last.get()
            return self.__goto_dir(event, path)
        self.window.bind('<F5>', goto_f5)

        def goto_return(event=tk.Event()):
            path = self.path_str.get()
            return self.__goto_dir(event, path)
        self.window.bind('<Return>', goto_return)
        path_button.configure(command=goto_return)

    def __make_main_canvas(self):
        self.name = {'left': [], 'right': []}
        self.icon = {'left': [], 'right': []}
        self.frame = {'left': tk.Frame(), 'right': tk.Frame()}
        scroll_ver = {'left': tk.Scrollbar(), 'right': tk.Scrollbar()}
        scroll_hor = {'left': tk.Scrollbar(), 'right': tk.Scrollbar()}
        self.cframe = {'left': tk.Frame(), 'right': tk.Frame()}
        self.canvas = {'left': tk.Canvas(), 'right': tk.Canvas()}

        frame_side = ['left', 'right']
        frame_fill = {'left': 'y', 'right': 'both'}
        canvas_width = {'left': 300, 'right': self.window.winfo_screenwidth()}

        for i in frame_side:
            self.frame[i] = tk.Frame(self.window)
            self.frame[i].configure(background='#00E5E5')
            self.frame[i].pack(side=i, fill=frame_fill[i], expand=True)
            scroll_ver[i] = tk.Scrollbar(self.frame[i])
            scroll_hor[i] = tk.Scrollbar(self.frame[i])
            scroll_ver[i].configure(orient='vertical')
            scroll_hor[i].configure(orient='horizontal')
            self.canvas[i] = tk.Canvas(self.frame[i])
            self.canvas[i].configure(borderwidth=0, background='#84FCFC')
            self.canvas[i].configure(height=self.window.winfo_screenheight())
            self.canvas[i].configure(yscrollcommand=scroll_ver[i].set)
            self.canvas[i].configure(xscrollcommand=scroll_hor[i].set)
            self.canvas[i].configure(width=canvas_width[i])

            def scrollup(event, sign=-1, index=i):
                return self.__mousewheel(event, sign, index)

            def scrolldown(event, sign=1, index=i):
                return self.__mousewheel(event, sign, index)
            self.canvas[i].bind('<Button-4>', scrollup)
            self.canvas[i].bind('<Button-5>', scrolldown)
            scroll_ver[i]['command'] = self.canvas[i].yview
            scroll_hor[i]['command'] = self.canvas[i].xview
            scroll_hor[i].pack(side='bottom', fill='x')
            self.cframe[i] = tk.Frame(self.canvas[i])
            self.cframe[i].configure(background='#84FCFC')
            scroll_ver[i].pack(side=i, fill='y')
            self.canvas[i].pack(side=i, fill='both', expand=True)
            self.canvas[i].create_window(
                (0, 0), window=self.cframe[i], anchor='nw')

        self.menu = menu.Menu(self.window)
        self.canvas_menu = menu.CanvasMenu(self, self.cframe['right'])
        self.canvas['right'].bind('<Button-3>', self.canvas_menu.show)
        self.item_menu = menu.ItemMenu(self, self.cframe['right'])
        self.window.bind('<Control-z>', self.item_menu.cancel)
        self.window.bind('<Control-Z>', self.item_menu.cancel)
        self.window.bind('<Control-v>', self.item_menu.copy_item)
        self.window.bind('<Control-V>', self.item_menu.copy_item)
        self.window.bind('<Control-d>', self.item_menu.move_item)
        self.window.bind('<Control-D>', self.item_menu.move_item)

    def __get_content(self, path):
        item_list = {'dirs': [], 'files': [], 'unrec': []}
        if path != '/':
            path += '/'
        for item in os.listdir(path):
            path_s = path + item
            if os.path.isdir(path_s):
                item_list['dirs'].append({'path': path_s, 'name': item})
            elif os.path.isfile(path_s):
                item_list['files'].append({'path': path_s, 'name': item})
            else:
                item_list['unrec'].append({'path': path_s, 'name': item})

        for i in item_list:
            item_list[i] = sorted(item_list[i], key=lambda d: d['name'])
        return item_list

    def __update_frame(self, index):
        new_size = 0
        for i in self.item_list[index]:
            new_size += len(self.item_list[index][i])

        while len(self.name[index]) < new_size:
            size = len(self.name[index])
            self.name[index].append(tk.Label(self.cframe[index]))
            self.name[index][size].configure(font=self.font)
            self.name[index][size].configure(bg='#84FCFC', cursor='hand2')
            self.name[index][size].grid(row=size, column=1, sticky='w')
            self.icon[index].append(tk.Label(self.cframe[index]))
            self.icon[index][size].configure(bg='#84FCFC', cursor='hand2')
            self.icon[index][size].grid(row=size, column=0)
            self.icon[index][size].bind('<Button-3>', self.item_menu.show)

        for widget in self.cframe[index].winfo_children():
            widget.unbind('<Button-1>')
            widget.unbind('<Button-3>')
            widget.configure(fg='#000000')
            widget.grid_remove()

    def __draw_tree(self):
        self.__update_frame('left')

        row = 0
        for i in self.item_list['left']:
            for item in self.item_list['left'][i]:
                self.name['left'][row].configure(text=item['name'])
                self.name['left'][row].grid()

                open = os.access(item['path'], os.R_OK)
                self.icon['left'][row].configure(
                    image=self.image['dirs'][open])

                if i == 'dirs':
                    shift = '>'
                    if item['path'] != '/':
                        shift = '   ' * item['path'].count('/') + '>'
                    self.name['left'][row].configure(text=shift + item['name'])
                elif i == 'disks':
                    self.icon['left'][row].configure(
                        image=self.image['rest'][1])
                self.icon['left'][row].grid()

                def menu(event, name=item):
                    return self.item_menu.show(event, name)
                self.name['left'][row].bind('<Button-3>', menu)
                self.icon['left'][row].bind('<Button-3>', menu)

                def goto(event, path=item['path']):
                    return self.__goto_dir(event, path)
                self.name['left'][row].bind('<Button-1>', goto)

                def remove(event, path=item['path']):
                    return self.__remove_set(event, path)
                self.icon['left'][row].bind('<Button-1>', remove)

                row += 1
        self.cframe['left'].update()
        self.canvas['left'].configure(
            scrollregion=self.canvas['left'].bbox("all"))

    def __draw_content(self):
        self.__update_frame('right')

        row = 0
        for i in self.item_list['right']:
            for item in self.item_list['right'][i]:
                self.name['right'][row].configure(text=item['name'])
                self.name['right'][row].grid()

                if item['name'] == '--UP--':
                    self.icon['right'][row].configure(
                        image=self.image['rest'][0])
                else:
                    open = os.access(item['path'], os.R_OK)
                    self.icon['right'][row].configure(
                        image=self.image[i][open])

                    def menu(event, name=item):
                        return self.item_menu.show(event, name)
                    self.name['right'][row].bind('<Button-3>', menu)
                    self.icon['right'][row].bind('<Button-3>', menu)
                self.icon['right'][row].grid()

                if i == 'dirs':
                    def goto(event, path=item['path']):
                        return self.__goto_dir(event, path)
                    self.name['right'][row].bind('<Button-1>', goto)
                    self.icon['right'][row].bind('<Button-1>', goto)
                elif i == 'files' and os.access(item['path'], os.X_OK):
                    def exec(event, path=item['path']):
                        return os.system(path)
                    self.name['right'][row].configure(fg='#EE204D')
                    self.name['right'][row].bind('<Button-1>', exec)
                    self.icon['right'][row].bind('<Button-1>', exec)

                row += 1
        self.cframe['right'].update()
        self.canvas['right'].configure(
            scrollregion=self.canvas['right'].bbox('all'))

    def show_content(self):
        self.item_list = {'left': {'dirs': [], 'user': [], 'disks': []},
                          'right': {'dirs': [], 'files': [], 'unrec': []}}

        self.item_list['left']['dirs'] = [{'path': '/', 'name': 'ROOT'}]
        for fol in self.path_tree:
            self.item_list['left']['dirs'] += self.__get_content(fol)['dirs']
        self.item_list['left']['dirs'] = sorted(
            self.item_list['left']['dirs'], key=lambda d: d['path'])
        self.item_list['left']['user'].append({'path': os.path.abspath(
            os.path.expanduser('~')), 'name': 'User'})
        self.item_list['left']['disks'] += self.__get_content('/mnt')['dirs']
        self.__draw_tree()

        self.item_list['right'] = self.__get_content(self.path_str.get())
        if self.path_str.get() != '/':
            self.item_list['right']['dirs'].insert(
                0, {'path': self.path_str.get() + '/../', 'name': '--UP--'})
        self.__draw_content()

    def __goto_dir(self, event, path):
        if not os.path.exists(path):
            self.canvas_menu.warn('Warning', 'Incorrect path')
            return
        if not os.access(path, os.R_OK):
            self.canvas_menu.warn('Warning', 'Permission denied')
            return

        path = os.path.abspath(os.path.expanduser(path))
        self.path_str.set(path)
        self.path_last.set(path)
        if path != '/':
            while path != '/':
                path = os.path.abspath(os.path.join(path, os.pardir))
                self.path_tree.add(path)

        self.show_content()
        self.canvas['right'].focus_set()

    def __remove_set(self, event, path):
        new_tree = {elem for elem in self.path_tree if elem.find(path) == -1}
        if len(new_tree) == len(self.path_tree):
            if not os.access(path, os.R_OK):
                self.canvas_menu.warn('Warning', 'Permission denied')
                return
            while True:
                new_tree.add(path)
                if path == '/':
                    break
                path = os.path.abspath(os.path.join(path, os.pardir))
        self.path_tree = new_tree
        self.show_content()

    def __mousewheel(self, event, sign, index):
        self.canvas[index].yview_scroll(sign, "units")

    def __unpost(self, event):
        event.widget.focus_set()
        self.canvas_menu.unpost()
        self.item_menu.unpost()
