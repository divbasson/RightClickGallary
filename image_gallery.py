import os
import tkinter as tk
from tkinter import ttk, Frame, Label, Canvas, Scrollbar, VERTICAL, BOTTOM, Menu, filedialog, Checkbutton, IntVar
from PIL import Image, ImageTk
from tkinter import messagebox
from ttkthemes import ThemedTk
import sys
import ctypes
import hashlib
import shutil
import pyperclip
import logging

class ImageGallery:
    def __init__(self, root, folder_path):
        self.root = root
        self.folder_path = folder_path
        self.root.title("Image Gallery")

        # Set up logging
        logging.basicConfig(filename=os.path.join(folder_path, 'image_gallery.log'), level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # Set the window size
        self.root.geometry("1000x800")

        # Set the window icon
        icon_path = os.path.join(folder_path, 'icon.ico')
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
            # Also set the taskbar icon on Windows
            if os.name == 'nt':
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(icon_path)

        # Set the breeze theme
        style = ttk.Style()
        style.theme_use('breeze')

        # Create a canvas and a vertical scrollbar
        self.canvas = Canvas(root, bg='#f0f0f0')  # Change background to a light grey fitting for Windows 11
        self.scrollbar = Scrollbar(root, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas and add it to the canvas's window
        self.frame = Frame(self.canvas, bg='#f0f0f0')
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        # Bind the configure event to the on_frame_configure method
        self.frame.bind('<Configure>', self.on_frame_configure)

        # Pack the canvas and scrollbar, ensuring the canvas expands fully
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')

        # Bind the mouse wheel event to the on_mousewheel method
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)

        self.selected_images = set()  # Track selected images
        self.checkboxes = {}
        self.image_widgets = []
        self.image_hashes = {}

        self.load_images(folder_path)

    def load_images(self, folder_path):
        images_per_row = 6
        row, col = 0, 0
        image_count = 0

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                img_path = os.path.join(folder_path, filename)
                try:
                    image = Image.open(img_path)
                    image = image.resize((150, 150), Image.Resampling.LANCZOS)  # Resize for uniform thumbnail size
                    photo = ImageTk.PhotoImage(image=image)

                    frame = Frame(self.frame, bg='#f0f0f0', bd=2, relief='sunken', width=160, height=180)
                    frame.pack_propagate(False)  # Prevent frame from resizing to content size
                    label = Label(frame, image=photo, bg='#f0f0f0')
                    label.image = photo  # Keep a reference to avoid garbage collection
                    label.pack()

                    # Add image file name
                    fname_label = Label(frame, text=filename, bg='#f0f0f0', wraplength=150)
                    fname_label.pack()

                    # Bind right-click to show context menu
                    label.bind("<Button-3>", self.show_context_menu)

                    # Add a checkbox
                    var = IntVar()
                    checkbox = Checkbutton(frame, variable=var, bg='#f0f0f0')
                    checkbox.pack()
                    self.checkboxes[img_path] = var

                    frame.grid(row=row, column=col, padx=5, pady=5)
                    self.image_widgets.append((frame, img_path))

                    # Compute hash to find duplicates
                    image_hash = self.compute_image_hash(img_path)
                    if image_hash in self.image_hashes:
                        frame.config(bg='red')  # Highlight duplicates in red
                    else:
                        self.image_hashes[image_hash] = img_path

                    col += 1
                    image_count += 1
                    if col >= images_per_row:
                        col = 0
                        row += 1
                except Exception as e:
                    logging.error(f"Failed to load image {img_path}: {e}")

        # Display the image count
        Label(self.root, text=f"Total images: {image_count}", bg='#f0f0f0', fg='black').pack(side=BOTTOM)
        logging.info(f"Loaded {image_count} images from {folder_path}")

    def compute_image_hash(self, img_path):
        hasher = hashlib.md5()
        with open(img_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def show_context_menu(self, event):
        img_label = event.widget
        img_frame = img_label.master
        img_path = None
        for frame, path in self.image_widgets:
            if frame == img_frame:
                img_path = path
                break
        if img_path is None:
            return

        context_menu = Menu(self.root, tearoff=0)
        context_menu.add_command(label="Open in MS Paint", command=lambda: self.open_in_paint(img_path))
        context_menu.add_command(label="Copy to Clipboard", command=lambda: self.copy_to_clipboard(img_path))
        context_menu.add_command(label="Copy to New Folder", command=self.copy_selected_images)
        context_menu.add_command(label="Delete Image", command=lambda: self.delete_image(img_path))
        context_menu.add_command(label="Delete Selected Images", command=self.delete_selected_images)
        context_menu.post(event.x_root, event.y_root)

    def open_in_paint(self, img_path):
        os.system(f'mspaint "{img_path}"')
        logging.info(f"Opened {img_path} in MS Paint")

    def copy_to_clipboard(self, img_path):
        try:
            pyperclip.copy(img_path)
            messagebox.showinfo("Info", f"Copied {img_path} to clipboard")
            logging.info(f"Copied {img_path} to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")
            logging.error(f"Failed to copy {img_path} to clipboard: {e}")

    def copy_selected_images(self):
        selected_images = [path for path, var in self.checkboxes.items() if var.get() == 1]
        if not selected_images:
            messagebox.showinfo("Info", "No images selected")
            return

        target_folder = filedialog.askdirectory(title="Select Folder to Copy Images")
        if not target_folder:
            return

        for img_path in selected_images:
            shutil.copy(img_path, target_folder)

        messagebox.showinfo("Info", f"Copied {len(selected_images)} images to {target_folder}")
        logging.info(f"Copied {len(selected_images)} images to {target_folder}")

    def delete_image(self, img_path):
        try:
            os.remove(img_path)
            self.reload_gallery()
            messagebox.showinfo("Info", f"Deleted {img_path}")
            logging.info(f"Deleted {img_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete image: {e}")
            logging.error(f"Failed to delete {img_path}: {e}")

    def delete_selected_images(self):
        selected_images = [path for path, var in self.checkboxes.items() if var.get() == 1]
        if not selected_images:
            messagebox.showinfo("Info", "No images selected")
            return

        for img_path in selected_images:
            try:
                os.remove(img_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete image: {e}")
                logging.error(f"Failed to delete {img_path}: {e}")
        
        self.reload_gallery()
        messagebox.showinfo("Info", f"Deleted {len(selected_images)} images")
        logging.info(f"Deleted {len(selected_images)} images")

    def reload_gallery(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.image_widgets.clear()
        self.checkboxes.clear()
        self.image_hashes.clear()
        self.load_images(self.folder_path)

    def on_frame_configure(self, event=None):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def on_mousewheel(self, event):
        # Scroll the canvas with the mouse wheel
        self.canvas.yview_scroll(-1*(event.delta//120), 'units')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder_arg = sys.argv[1]
    else:
        folder_arg = '.'

    root = ThemedTk(theme="breeze")
    gallery = ImageGallery(root, folder_arg)
    root.mainloop()
