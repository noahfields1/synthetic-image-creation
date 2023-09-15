import os
import tkinter as tk
from PIL import Image, ImageTk
import util
class ImageBrowser:
    def __init__(self, home_dir):
        self.home_dir = home_dir
        self.image_paths = []
        self.current_image_index = 0

        # create main window
        self.root = tk.Tk()
        self.root.title("Image Browser")

        # create search bar and button
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.root, textvariable=self.search_var)
        self.search_entry.pack(side=tk.TOP, fill=tk.X)
        self.search_button = tk.Button(self.root, text="Search", command=self.search_images)
        self.search_button.pack(side=tk.TOP)

        # create image label
        self.image_label = tk.Label(self.root)
        self.image_label.pack(side=tk.TOP)

        # create arrow buttons
        self.prev_button = tk.Button(self.root, text="<", command=self.show_prev_image)
        self.prev_button.pack(side=tk.LEFT)
        self.next_button = tk.Button(self.root, text=">", command=self.show_next_image)
        self.next_button.pack(side=tk.RIGHT)

        # create scrollbar
        self.scrollbar = tk.Scrollbar(self.root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # create listbox
        self.listbox = tk.Listbox(self.root, yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # bind events
        self.root.bind("<Left>", lambda event: self.show_prev_image())
        self.root.bind("<Right>", lambda event: self.show_next_image())
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.search_entry.bind("<Return>", lambda event: self.search_button.invoke())

        # initialize images and listbox
        self.load_images("files_clean.txt")
        self.show_image()
        self.update_listbox()

    def load_images(self,files_txt=None):
        if files_txt == None:
            self.image_paths = util.find_files_with_suffix("Xo.png")
        else:
            pathways_array = util.file_to_array(files_txt)
            pathways_array = util.remove_file_extensions(pathways_array)
            pathways_array = util.add_file_extensions(pathways_array,"Xo.png")
            self.image_paths = pathways_array
        

    def show_image(self):
        image_path = self.image_paths[self.current_image_index]
        image = Image.open(image_path)
        image = image.resize((600, 600))
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo

    def show_next_image(self):
        if self.current_image_index < len(self.image_paths) - 1:
            self.current_image_index += 1
            self.show_image()

    def show_prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.show_image()

    def search_images(self):
        query = self.search_var.get().lower()
        matches = [i for i, path in enumerate(self.image_paths) if query in path.lower()]
        if matches:
            self.current_image_index = matches[0]
            self.show_image()
            self.update_listbox()
            self.listbox.select_clear(0, tk.END)
            self.listbox.select_set(matches[0])

    def on_select(self, event):
        index = self.listbox.curselection()
        if index:
            self.current_image_index = index[0]
            self.show_image()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for path in self.image_paths:
            self.listbox.insert(tk.END, path)

def main():
    # specify the home directory here
    home_dir = './files'

    # create the ImageBrowser object and run the main loop
    browser = ImageBrowser(home_dir)
    browser.root.mainloop()

if __name__ == '__main__':
    main()
