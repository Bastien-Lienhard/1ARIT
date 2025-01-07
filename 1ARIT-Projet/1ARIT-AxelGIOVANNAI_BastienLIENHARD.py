import tkinter as tk
from tkinter import filedialog, ttk
import random
import string
import numpy as np


class Matrix:
    def __init__(self, size):
        self.size = size
        self.grille = self.generateMatrix()

    def generateMatrix(self):
        return [[0] * self.size for _ in range(self.size)]

    def generateRandomMatrix(self):
        self.grille = [
            [random.choice([0, 1]) for _ in range(self.size)] for _ in range(self.size)
        ]
        while not self.is_valid_fleissner():
            self.grille = [
                [random.choice([0, 1]) for _ in range(self.size)]
                for _ in range(self.size)
            ]

    def is_valid_fleissner(self):
        size = len(self.grille)
        new_matrix = [[0] * size for _ in range(size)]

        for i in range(size):
            for j in range(size):
                if self.grille[i][j] == 1:
                    new_i = i // 2
                    new_j = j // 2
                    if new_matrix[new_i][new_j] == 1:
                        return False
                    new_matrix[new_i][new_j] = 1

        return True

    def rotate(self, clockwise=True):
        return np.rot90(self.grille, -1 if clockwise else 1).tolist()

    def fleissner_cipher(self, text, clockwise=True):
        print(self)
        size = self.size
        text = text.replace(" ", "")
        max_length = size**2 if size % 2 == 0 else size**2 - 1

        while len(text) < max_length:
            text += random.choice(string.ascii_lowercase)

        encrypted_text = [["" for _ in range(size)] for _ in range(size)]

        for rotation in range(4):
            for i in range(size):
                for j in range(size):
                    if self.grille[i][j] == 1:
                        if not text:
                            text += random.choice(string.ascii_lowercase)
                        encrypted_text[i][j] = text[0]
                        text = text[1:]
            self.grille = self.rotate(clockwise)

        encrypted_text_str = "".join("".join(row) for row in encrypted_text)

        return encrypted_text_str

    def fleissner_decipher(self, text_blocks, clockwise=True):
        size = len(self.grille)
        max_length = size**2 if size % 2 == 0 else size**2 - 1

        text_blocks = text_blocks.split(" ")

        decrypted_text_blocks = []
        for block in text_blocks:
            grid_text = [["" for _ in range(size)] for _ in range(size)]
            text_index = 0
            for i in range(size):
                for j in range(size):
                    if size % 2 == 1 and i == size // 2 and j == size // 2:
                        continue
                    if text_index < len(block):
                        grid_text[i][j] = block[text_index]
                        text_index += 1

            decrypted_block = ""
            for rotation in range(4):
                for i in range(size):
                    for j in range(size):
                        if self.grille[i][j] == 1 and grid_text[i][j] != "":
                            decrypted_block += grid_text[i][j]
                self.grille = self.rotate(clockwise)
            decrypted_text_blocks.append(decrypted_block)

        return "".join(decrypted_text_blocks)


class Interface:
    def __init__(self, size):
        self.size = size
        self.matrix = Matrix(size)
        self.window_size = 800
        self.cell_size = self.window_size // self.size
        self.canvas_size = self.cell_size * self.size
        self.window = tk.Tk()
        self.window.title("Fleissner Cipher")
        self.window.configure(bg="#2D2D2D")
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.geometry(f"{self.canvas_size+70}x{self.canvas_size+200}")
        self.window.update_idletasks()
        self.window_width = self.window.winfo_width()
        self.window_height = self.window.winfo_height()
        self.position_right = int(
            self.window.winfo_screenwidth() / 2 - self.window_width / 2
        )
        self.position_down = int(
            self.window.winfo_screenheight() / 2 - self.window_height / 2
        )
        self.window.geometry(
            "+{}+{}".format(self.position_right, self.position_down))
        self.grid_canvas = tk.Canvas(
            self.window, bg="#4D4D4D", width=self.canvas_size, height=self.canvas_size
        )
        self.grid_canvas.grid(row=0, column=0, sticky="nsew")
        self.grid_canvas.bind(
            "<Button-1>", lambda event: self.cell_clicked(event))
        self.grid = self.matrix.generateMatrix()
        self.draw_grid()
        self.right_frame = tk.Frame(self.window, bg="#2D2D2D")
        self.right_frame.grid(row=0, column=2, sticky="nsew")
        self.button_bg = "#2D2D2D"
        self.button_fg = "white"
        self.text_field_bg = "#2D2D2D"
        self.text_field_fg = "white"
        self.menu_bg = "#2D2D2D"
        self.menu_fg = "white"
        style = ttk.Style()
        style.configure(
            "BW.TCheckbutton",
            foreground="white",
            background="#2D2D2D",
            bordercolor="white",
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "BW.TButton",
            foreground="#2D2D2D",
            background="#2D2D2D",
            bordercolor="white",
            relief="solid",
            borderwidth=1,
        )
        self.clock_var = tk.IntVar()
        self.create_var = tk.IntVar()
        self.save_button = ttk.Button(
            self.right_frame, text="Save", command=self.save, style="BW.TButton"
        )
        self.save_button.grid(row=0, column=0, sticky="ew")
        self.load_button = ttk.Button(
            self.right_frame,
            text="Load",
            command=self.load_and_update,
            style="BW.TButton",
        )
        self.load_button.grid(row=1, column=0, sticky="ew")
        self.random_button = ttk.Button(
            self.right_frame,
            text="Random",
            command=self.random_and_update,
            style="BW.TButton",
        )
        self.random_button.grid(row=2, column=0, sticky="ew")
        self.create_checkbox = ttk.Checkbutton(
            self.right_frame,
            text="Create",
            variable=self.create_var,
            style="BW.TCheckbutton",
        )
        self.create_checkbox.grid(row=3, column=0, sticky="ew")
        self.clear_text = tk.Text(
            self.window,
            height=5,
            width=75,
            bg=self.text_field_bg,
            fg=self.text_field_fg,
        )
        self.clear_text.grid(row=1, column=0)
        self.button_frame = tk.Frame(self.window, bg="#2D2D2D")
        self.button_frame.grid(row=2, column=0)
        self.clock_checkbox = ttk.Checkbutton(
            self.button_frame,
            text="Clock",
            variable=self.clock_var,
            style="BW.TCheckbutton",
        )
        self.clock_checkbox.grid(row=0, column=3, sticky="ew")
        self.cipher_button = ttk.Button(
            self.button_frame,
            text="Cipher",
            command=self.cipher_and_update,
            style="BW.TButton",
        )
        self.cipher_button.grid(row=0, column=0)
        self.decipher_button = ttk.Button(
            self.button_frame,
            text="Decipher",
            command=self.decipher_and_update,
            style="BW.TButton",
        )
        self.decipher_button.grid(row=0, column=1)
        self.clear_button = ttk.Button(
            self.button_frame, text="Clear", command=self.clearText, style="BW.TButton"
        )
        self.clear_button.grid(row=0, column=2)
        self.clear_button.grid(row=0, column=2)
        self.cipher_text = tk.Text(
            self.window,
            height=5,
            width=75,
            bg=self.text_field_bg,
            fg=self.text_field_fg,
        )
        self.cipher_text.grid(row=3, column=0)

    def draw_grid(self):
        for i in range(self.matrix.size):
            for j in range(self.matrix.size):
                x1 = i * self.cell_size
                y1 = j * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "#2D2D2D" if self.matrix.grille[i][j] == 0 else "black"
                self.grid_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline="#9695FF"
                )

    def cell_clicked(self, event):
        if self.create_var.get() == 0:
            return

        i = event.y // self.cell_size
        j = event.x // self.cell_size
        if self.matrix.grille[i][j] == 1:
            return

        self.matrix.grille[i][j] = 1
        color = "#4D4D4D" if self.matrix.grille[i][j] == 0 else "black"
        x1 = j * self.cell_size
        y1 = i * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        event.widget.create_rectangle(
            x1, y1, x2, y2, fill=color, outline="#9695FF")

        for _ in range(3):
            self.matrix.grille = self.matrix.rotate()
            i, j = j, self.matrix.size - 1 - i
            x1 = j * self.cell_size
            y1 = i * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            event.widget.create_rectangle(
                x1, y1, x2, y2, fill="gray", outline="#9695FF"
            )

        self.matrix.grille = self.matrix.rotate()

    def cipher_and_update(self):
        text = self.clear_text.get("1.0", "end-1c")
        ciphered_text = self.matrix.fleissner_cipher(
            text, bool(self.clock_var.get()))
        self.cipher_text.delete("1.0", "end")
        self.cipher_text.insert("1.0", ciphered_text)

    def decipher_and_update(self):
        text = self.cipher_text.get("1.0", "end-1c")
        deciphered_text = self.matrix.fleissner_decipher(
            text, bool(self.clock_var.get())
        )
        self.clear_text.delete("1.0", "end")
        self.clear_text.insert("1.0", deciphered_text)

    def clearText(self):
        self.clear_text.delete("1.0", "end")
        self.cipher_text.delete("1.0", "end")

    def random_and_update(self):
        self.matrix.generateRandomMatrix()
        self.grid_canvas.delete("all")
        for i in range(self.matrix.size):
            for j in range(self.matrix.size):
                x1 = i * self.cell_size
                y1 = j * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "#2D2D2D" if self.matrix.grille[i][j] == 0 else "black"
                self.grid_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline="#9695FF"
                )

    def save(self):
        filename = filedialog.asksaveasfilename(
            initialdir="Saves",
            title="Select file",
            filetypes=(("text files", "*.txt"), ("all files", "*.*")),
        )
        if filename:
            if not filename.endswith(".txt"):
                filename += ".txt"
            with open(filename, "w") as f:
                for row in self.matrix.grille:
                    f.write("".join(map(str, row)) + "\n")

    def load_and_update(self):
        filename = filedialog.askopenfilename(
            initialdir="Saves",
            title="Select file",
            filetypes=(("text files", "*.txt"), ("all files", "*.*")),
        )
        if filename:
            with open(filename, "r") as f:
                loaded_grid = [list(map(int, list(line.strip())))
                               for line in f]
            self.matrix.grille = loaded_grid
            self.matrix.size = len(self.matrix.grille)

            self.window_size = 800
            self.cell_size = self.window_size // self.matrix.size
            self.canvas_size = self.cell_size * self.matrix.size
            self.grid_canvas.config(
                width=self.canvas_size, height=self.canvas_size)

            self.grid_canvas.delete("all")
            for i in range(self.matrix.size):
                for j in range(self.matrix.size):
                    x1 = j * self.cell_size
                    y1 = i * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    color = "#2D2D2D" if self.matrix.grille[i][j] == 0 else "black"
                    self.grid_canvas.create_rectangle(
                        x1, y1, x2, y2, fill=color, outline="#9695FF"
                    )


def ask_grid_size():
    root = tk.Tk()
    root.configure(bg="#2D2D2D")

    grid_size = tk.StringVar()

    def submit_and_continue(event=None):
        size = int(grid_size.get())
        root.destroy()
        Interface(size)

    label = tk.Label(root, text="Taille de la matrice :",
                     bg="#2D2D2D", fg="white")
    label.pack()

    entry = tk.Entry(
        root, textvariable=grid_size, bg="#2D2D2D", fg="white", insertbackground="white"
    )
    entry.pack()
    entry.focus_set()

    style = ttk.Style()
    style.configure(
        "BW.TButton",
        foreground="#2D2D2D",
        background="#2D2D2D",
        bordercolor="white",
        relief="solid",
        borderwidth=1,
    )

    button = ttk.Button(
        root, text="Submit", command=submit_and_continue, style="BW.TButton"
    )

    button.pack()

    root.bind("<Return>", submit_and_continue)

    root.update_idletasks()

    window_width = 200
    window_height = 75
    position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
    root.geometry(
        "{}x{}+{}+{}".format(window_width, window_height,
                             position_right, position_down)
    )
    root.title("Size")

    root.mainloop()


ask_grid_size()
