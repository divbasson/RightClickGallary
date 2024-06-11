import os
from tkinter import Tk, Frame, Label
from PIL import Image, ImageTk

class ImageGallery:
    def __init__(self, root, folder_path):
        self.root = root
        self.root.title("Image Gallery")
        
        # Set the window to be a square
        self.window_size = 1000  # Assuming each thumbnail is 100x100, 10 thumbnails per row/column
        self.root.geometry(f"{self.window_size}x{self.window_size}")
        
        self.frame = Frame(root)
        self.frame.pack()
        
        self.load_images(folder_path)
    
    def load_images(self, folder_path):
        images_per_row = 10
        row, col = 0, 0
        
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                img_path = os.path.join(folder_path, filename)
                image = Image.open(img_path)
                image.thumbnail((100, 100))  # Resize for thumbnail
                photo = ImageTk.PhotoImage(image=image)
                
                label = Label(self.frame, image=photo)
                label.image = photo  # Keep a reference to avoid garbage collection
                label.grid(row=row, column=col)
                
                col += 1
                if col >= images_per_row:
                    col = 0
                    row += 1

if __name__ == "__main__":
    import sys
    folder_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    root = Tk()
    gallery = ImageGallery(root, folder_path)
    root.mainloop()
