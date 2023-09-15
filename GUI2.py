import tkinter as tk
import yaml
from PIL import Image, ImageTk
import os

class ImageGUI:
    def __init__(self, image_directory):
        self.image_directory = image_directory
        self.images = []
        self.image_info = []  # list to store information about each image
        self.current_index = 0
        self.image_size = (480, 480)
        self.window = tk.Tk()
        self.window.title("Image Viewer")
        self.load_images()
        self.create_widgets()

    def load_images(self):
        for model in os.listdir(self.image_directory):
            if model == ".DS_Store":
                continue
            for branch in os.listdir(self.image_directory + '/' + model):
                if branch == ".DS_Store":
                    continue
                full_image_dir = self.image_directory + '/' + model + '/' + branch
                for filename_X in os.listdir(full_image_dir):
                    if filename_X.endswith("X.png"):
                        filename_Y = filename_X.replace("X","Y")
                        filename_Yc = filename_X.replace("X","Yc")
                        yaml_pathway = "./files/" + model + "/" + branch + "/" + filename_X[0:-6] + ".yaml"
                        with open(yaml_pathway, 'r') as file:
                            data = yaml.safe_load(file)
                        radius = str(data[7]['radius'])
                        ratio = str(round(data[10]['ratio (circum^2/area)'],2))

                        img = Image.open(os.path.join(full_image_dir, filename_X)).resize(self.image_size)
                        self.images.append(ImageTk.PhotoImage(img))
                        self.image_info.append("Model: " + model + "\nBranch: " + branch + "\nImage: " + filename_X[0:-6])  # add the filename as image info

                        img = Image.open(os.path.join(full_image_dir, filename_Yc)).resize(self.image_size)
                        self.images.append(ImageTk.PhotoImage(img))
                        self.image_info.append("Model: " + model + "\nBranch: " + branch + "\nImage: " + filename_Yc[0:-7] + "\nradius: " + radius + "\nratio: " + ratio)  # add the filename as image info

                        img = Image.open(os.path.join(full_image_dir, filename_Y)).resize(self.image_size)
                        self.images.append(ImageTk.PhotoImage(img))
                        self.image_info.append("Model: " + model + "\nBranch: " + branch + "\nImage: " + filename_Y[0:-6])  # add the filename as image info
    """
    def load_images(self):
        for root, dirs, files in os.walk(self.image_directory):
            for file in files:
                if file.endswith((".jpg", ".png")):
                    path = os.path.join(root, file)
                    image = Image.open(path).resize((300, 300))
                    self.images.append(ImageTk.PhotoImage(image))
                    self.image_info.append(file)  # add the filename as image info
    """
    def create_widgets(self):
        self.previous_button = tk.Button(self.window, text="Previous", command=self.show_previous_images)
        self.previous_button.pack(side="left")
        self.next_button = tk.Button(self.window, text="Next", command=self.show_next_images)
        self.next_button.pack(side="right")
        self.image_labels = []
        self.info_labels = []  # list to store information labels
        for i in range(3):
            frame = tk.Frame(self.window)
            frame.pack(side="left", pady=10)
            label = tk.Label(frame, image=self.images[i])
            label.pack(side="top")
            self.image_labels.append(label)
            info_label = tk.Label(frame, text=self.image_info[i])  # create a label for image info
            info_label.pack(side="bottom")
            self.info_labels.append(info_label)

    def show_previous_images(self):
        if self.current_index >= 3:
            self.current_index -= 3
            for i in range(3):
                self.image_labels[i].config(image=self.images[self.current_index + i])
                self.info_labels[i].config(text=self.image_info[self.current_index + i])  # update info label text

    def show_next_images(self):
        if self.current_index + 3 < len(self.images):
            self.current_index += 3
            for i in range(3):
                self.image_labels[i].config(image=self.images[self.current_index + i])
                self.info_labels[i].config(text=self.image_info[self.current_index + i])  # update info label text

    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    gui = ImageGUI("/Users/noah/Desktop/image-data-creation/files")
    gui.run()
