#!/usr/bin/env python3

import menu
import os

import tkinter as tk
import tkinter.font as tkfont
import tkinter.messagebox as tkmsg


class MainWindow():
    def __init__(self):
        self.__make_window()
        self.__load_images()
        self.__make_path_frame()
        self.__make_main_canvas()
        self.__add_labels(1, 100)
        self.show_content()

    def __make_window(self):
        self.window = tk.Tk()
        self.window.title("North Typical Heavy Extended Mount Explorer")
        self.window.resizable(width=True, height=True)
        self.window.config(background='#00E5E5')
        self.window.geometry('1280x720')
        self.window.minsize(width=self.window.winfo_screenwidth() // 4,
                            height=self.window.winfo_screenheight() // 4)
        self.window.bind('<F5>', self.show_content)
        self.window.bind('<Button-1>', self.__focus)

        self.content_font = tkfont.Font(family="Arial")
        self.content_font.configure(size=11)

    def __load_images(self):
        self.image = [tk.PhotoImage(file="img/folder_rest.png"),
                      tk.PhotoImage(file="img/folder_open.png"),
                      tk.PhotoImage(file="img/file_rest.png"),
                      tk.PhotoImage(file="img/file_open.png"),
                      tk.PhotoImage(file="img/unknown_rest.png"),
                      tk.PhotoImage(file="img/unknown_open.png"),
                      tk.PhotoImage(file="img/back.png"),
                      tk.PhotoImage(file="img/disk.png")]

    def __make_path_frame(self):
        path_frame = tk.Frame(self.window)
        path_frame.configure(background='#00E5E5')
        path_frame.pack()

        path_font = tkfont.Font(family="Arial")
        path_font.configure(size=12, weight='bold')

        path_button = tk.Button(path_frame)
        path_button.configure(command=self.show_content)
        path_button.configure(font=path_font, text="Go to path...")
        path_button.configure(width=10, height=1)
        path_button.configure(bg='blue', fg='white')
        path_button.configure(activebackground='red')
        path_button.pack(padx=10, pady=5, side='left')

        self.path_str = tk.StringVar(value='/')
        self.path_last = tk.StringVar(value='/')
        self.path_box = tk.Entry(path_frame)
        self.path_box.bind('<Return>', self.show_content)
        self.path_box.configure(textvariable=self.path_str)
        self.path_box.configure(width=80, justify='center')
        self.path_box.configure(bg='#84FCFC', fg='#115F15')
        self.path_box.pack(pady=10)

    def __make_main_canvas(self):
        self.name = [[], []]
        self.icon = [[], []]
        self.frame = [tk.Frame(self.window) for i in range(2)]
        scroll_ver = []
        scroll_hor = []
        self.cframe = []
        self.canvas = []

        for i in range(2):
            self.frame[i].configure(background='#00E5E5')
            scroll_ver.append(tk.Scrollbar(self.frame[i]))
            scroll_hor.append(tk.Scrollbar(self.frame[i]))
            scroll_ver[i].configure(orient="vertical")
            scroll_hor[i].configure(orient="horizontal")
            self.canvas.append(tk.Canvas(self.frame[i]))
            self.canvas[i].configure(borderwidth=0, background='#84FCFC')
            self.canvas[i].configure(height=self.window.winfo_screenheight())
            self.canvas[i].configure(yscrollcommand=scroll_ver[i].set)
            self.canvas[i].configure(xscrollcommand=scroll_hor[i].set)
            scroll_ver[i]["command"] = self.canvas[i].yview
            scroll_hor[i]["command"] = self.canvas[i].xview
            scroll_hor[i].pack(side='bottom', fill='x')
            self.cframe.append(tk.Frame(self.canvas[i]))
            self.cframe[i].configure(background='#84FCFC')

        self.canvas[0].configure(width=200)
        self.canvas[1].configure(width=self.window.winfo_screenwidth())

        self.canvas_menu = menu.CanvasMenu(self, self.cframe[1])
        self.canvas[1].bind('<Button-3>', self.canvas_menu.popup_menu)
        self.item_menu = menu.ItemMenu(self, self.cframe[1])

        self.frame[0].pack(side='left')
        self.frame[1].pack(fill='both', expand=True)
        scroll_ver[0].pack(side='left', fill='y')
        scroll_ver[1].pack(side='right', fill='y')
        self.canvas[0].pack(side='left', fill='both', expand=True)
        self.canvas[1].pack(side='right', fill='both', expand=True)
        for i in range(2):
            self.canvas[i].create_window(
                (0, 0), window=self.cframe[i], anchor="nw")

    def __get_content(self, path):
        content_list = [list() for i in range(3)]
        for item in os.listdir(path):
            if os.path.isdir(path + item):
                content_list[0].append(item)
            elif os.path.isfile(path + item):
                content_list[1].append(item)
            else:
                content_list[2].append(item)

        for item in content_list:
            item.sort()
        return content_list

    def __update_path(self, event):
        path = os.path.expanduser(self.path_str.get())
        if len(path) >= 2 and path[0:2] == '..':
            old_path = [i for i in self.path_last.get().split('/') if i]
            path = '/'+'/'.join(old_path[:-1]) + path[2:]
        elif len(path) >= 1 and path[0] == '.':
            path = self.path_last.get() + path[1:]

        path = os.path.abspath(path + '///')
        if not os.access(path, os.R_OK):
            print(f"Cannot open {path}\n", end='')
            return True

        if hasattr(event, 'keysym') and event.keysym == 'Return':
            self.window.focus_set()

        if path != '/':
            path = path + '/'
        self.path_str.set(path)
        self.path_last.set(path)
        return False

    def __add_labels(self, index, new_size):
        size = len(self.name[index])
        while size < new_size:
            self.name[index].append(tk.Label(self.cframe[index]))
            self.name[index][size].configure(font=self.content_font)
            self.name[index][size].configure(bg='#84FCFC', cursor='hand2')
            self.name[index][size].grid(row=size, column=1, sticky='w')
            self.icon[index].append(tk.Label(self.cframe[index]))
            self.icon[index][size].configure(bg='#84FCFC', cursor='hand2')
            self.icon[index][size].grid(row=size, column=0)
            self.icon[index][size].bind(
                '<Button-3>', self.item_menu.popup_menu)
            size += 1

    def __draw_content(self, content_list):
        for l in range(2):
            size = 0
            for j in range(3):
                size += len(content_list[l][j])
            self.__add_labels(l, size)
            for widget in self.cframe[l].winfo_children():
                widget.unbind('<Button-1>')
                widget.unbind('<Button-3>')
                widget.grid_remove()

            row = 0
            for i in range(3):
                for item in content_list[l][i]:
                    self.name[l][row].configure(text=item)
                    self.name[l][row].grid()

                    fpath = self.path_str.get() + item
                    if l == 0:
                        self.icon[l][row].configure(image=self.image[7])
                        fpath = item
                        if row > 1:
                            fpath = '/mnt/' + item
                    elif l == 1 and item == '../':
                        self.icon[l][row].configure(image=self.image[6])
                    else:
                        open = os.access(self.path_str.get() + item, os.R_OK)
                        open = int(open) + i * 2
                        self.icon[l][row].configure(image=self.image[open])

                        def menu(event, name=item):
                            return self.item_menu.popup_menu(event, name)
                        self.name[l][row].bind('<Button-3>', menu)
                        self.icon[l][row].bind('<Button-3>', menu)
                    self.icon[l][row].grid()

                    if i == 0:
                        def goto(event, path=fpath):
                            return self.__goto_dir(event, path)
                        self.name[l][row].bind('<Button-1>', goto)
                        self.icon[l][row].bind('<Button-1>', goto)
                    row += 1
            self.cframe[l].update()
            self.canvas[l].configure(scrollregion=self.canvas[l].bbox("all"))

    def show_content(self, event=tk.Event()):
        if self.__update_path(event):
            return
        content_list = [[], []]
        content_list[0] = [['/', os.path.expanduser('~')], [], []]
        content_list[0][0] += self.__get_content('/mnt/')[0]
        content_list[1] = self.__get_content(self.path_str.get())
        if self.path_str.get() != '/':
            content_list[1][0].insert(0, '../')

        self.__draw_content(content_list)

    def __goto_dir(self, event, path):
        if not os.access(path, os.R_OK):
            tkmsg.showwarning("Warning", "Permission denied")
            return
        self.path_str.set(path)
        self.show_content()

    def __focus(self, event=tk.Event()):
        event.widget.focus_set()
        self.canvas_menu.unpost()
        self.item_menu.unpost()
