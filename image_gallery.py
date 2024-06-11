import os
import webbrowser
from tkinter import Tk, Frame, Label, Canvas, Scrollbar, VERTICAL, BOTTOM
from PIL import Image, ImageTk

class ImageGallery:
    def __init__(self, root, folder_path):
        self.root = root
        self.root.title("Image Gallery")
        
        # Set the window size
        self.root.geometry("800x600")
        
        # Create a canvas and a vertical scrollbar
        self.canvas = Canvas(root, bg='black')
        self.scrollbar = Scrollbar(root, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create a frame inside the canvas and add it to the canvas's window
        self.frame = Frame(self.canvas, bg='black')
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')
        
        # Bind the configure event to the on_frame_configure method
        self.frame.bind('<Configure>', self.on_frame_configure)
        
        # Pack the scrollbar and canvas
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        self.load_images(folder_path)
    
    def load_images(self, folder_path):
        images_per_row = 10
        row, col = 0, 0
        image_count = 0
        
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                img_path = os.path.join(folder_path, filename)
                image = Image.open(img_path)
                image.thumbnail((100, 100))  # Resize for thumbnail
                photo = ImageTk.PhotoImage(image=image)
                
                label = Label(self.frame, image=photo, bg='black')
                label.image = photo  # Keep a reference to avoid garbage collection
                label.grid(row=row, column=col)
                
                # Bind the click event to the open_image function
                label.bind('<Button-1>', lambda e, img_path=img_path: self.open_image(img_path))
                
                col += 1
                image_count += 1
                if col >= images_per_row:
                    col = 0
                    row += 1

        # Display the image count
        Label(self.root, text=f"Total images: {image_count}", bg='black', fg='white').pack(side=BOTTOM)

    def open_image(self, img_path):
        # Open the image file with the default application
        webbrowser.open(img_path)

    def on_frame_configure(self, event=None):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

if __name__ == "__main__":
    import sys
    folder_arg = sys.argv[1] if len(sys.argv) > 1 else '.'
    root = Tk()
    gallery = ImageGallery(root, folder_arg)
    root.mainloop()
