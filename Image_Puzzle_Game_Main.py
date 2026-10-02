import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import random


class Tile:

    def __init__(self, image, correct_pos):
        self.original_image = image
        self.correct_pos = correct_pos
        self.current_pos = correct_pos
        self.rotation = 0
        self.flip_direction = None
        self.tk_image = None

    def turn_piece(self, angle=90):
        self.rotation = (self.rotation + angle) % 360

    def mirror_piece(self, direction="horizontal"):
        if self.flip_direction is None:
            self.flip_direction = direction
        else:
            self.flip_direction = (
                None if self.flip_direction == direction else direction
            )

    def restore_original_state(self):
        self.current_pos = self.correct_pos
        self.rotation = 0
        self.flip_direction = None

    def prepare_image_for_display(self):
        img = self.original_image.copy()

        if self.flip_direction == "horizontal":
            img = cv2.flip(img, 1)
        elif self.flip_direction == "vertical":
            img = cv2.flip(img, 0)

        if self.rotation == 90:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif self.rotation == 180:
            img = cv2.rotate(img, cv2.ROTATE_180)
        elif self.rotation == 270:
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        return img

    def is_in_the_right_spot(self):
        return (
            self.current_pos == self.correct_pos
            and self.rotation == 0
            and self.flip_direction is None
        )


class GamePiece(Tile):

    def __init__(self, image, correct_pos, hint_text=""):
        super().__init__(image, correct_pos)
        self.hint_text = hint_text

    def tell_me_about_this_piece(self):
        return f"GamePiece Hint: {self.hint_text}"


class PuzzleGame:

    def __init__(self, root):
        self.root = root
        self.root.title("Scrambled Image Puzzle")

        self.grid_size_var = tk.IntVar(value=3)
        self.tiles = []
        self.selected_index = None
        self.moves = 0
        self.hints_remaining = 3
        self.active_hint_tile = None
        self.game_over = False
        self.canvas_size = 350
        self.original_tk_img = None

        self.build_the_interface()

    def build_the_interface(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(control_frame, text="Grid Size:").pack(side=tk.LEFT, padx=5)
        for size in (3, 4, 5):
            tk.Radiobutton(
                control_frame,
                text=f"{size}x{size}",
                variable=self.grid_size_var,
                value=size,
            ).pack(side=tk.LEFT)

        tk.Button(
            control_frame,
            text="Load Image",
            command=self.choose_and_load_a_photo,
        ).pack(side=tk.LEFT, padx=10)

        self.hint_btn = tk.Button(
            control_frame,
            text="Hint (3 left)",
            command=self.give_the_player_a_clue,
            state=tk.DISABLED,
        )
        self.hint_btn.pack(side=tk.LEFT, padx=5)

        self.solve_btn = tk.Button(
            control_frame,
            text="Solve",
            command=self.instantly_solve_everything,
            state=tk.DISABLED,
        )
        self.solve_btn.pack(side=tk.LEFT, padx=5)

        stats_frame = tk.Frame(control_frame)
        stats_frame.pack(side=tk.RIGHT, padx=10)

        self.move_label = tk.Label(
            stats_frame, text="Moves: 0", font=("Arial", 10, "bold")
        )
        self.move_label.pack(anchor=tk.E)

        self.incorrect_label = tk.Label(
            stats_frame,
            text="Incorrect: 0",
            font=("Arial", 10, "bold"),
            fg="red",
        )
        self.incorrect_label.pack(anchor=tk.E)

        display_frame = tk.Frame(self.root)
        display_frame.pack(padx=10, pady=5)

        left_box = tk.LabelFrame(display_frame, text="Original Reference")
        left_box.pack(side=tk.LEFT, padx=5)
        self.ref_canvas = tk.Canvas(
            left_box,
            bg="darkgray",
            width=self.canvas_size,
            height=self.canvas_size,
        )
        self.ref_canvas.pack()

        right_box = tk.LabelFrame(display_frame, text="Interactive Puzzle")
        right_box.pack(side=tk.LEFT, padx=5)
        self.puzzle_canvas = tk.Canvas(
            right_box,
            bg="darkgray",
            width=self.canvas_size,
            height=self.canvas_size,
        )
        self.puzzle_canvas.pack()

        self.puzzle_canvas.bind("<Button-1>", self.on_tile_clicked)
        self.puzzle_canvas.bind("<Shift-Button-1>", self.on_tile_flipped)
        self.puzzle_canvas.bind("<Button-3>", self.on_tile_rotated)

        instr = (
            "Left Click: Select/Swap | Shift + Click: Flip | Right Click: Rotate"
        )
        tk.Label(self.root, text=instr, font=("Arial", 8, "italic")).pack(
            side=tk.BOTTOM, pady=5
        )

    def choose_and_load_a_photo(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.png *.bmp")]
        )
        if not path:
            return

        grid_size = self.grid_size_var.get()
        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Error", "Could not load image.")
            return

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        processed_img = self.fit_image_to_grid(img, grid_size)

        pil_ref = Image.fromarray(processed_img)
        self.original_tk_img = ImageTk.PhotoImage(image=pil_ref)

        self.slice_image_into_pieces(processed_img, grid_size)
        self.mix_up_the_puzzle_pieces(grid_size)

        (
            self.moves,
            self.hints_remaining,
            self.active_hint_tile,
            self.selected_index,
            self.game_over,
        ) = (0, 3, None, None, False)

        self.hint_btn.config(
            state=tk.NORMAL, text=f"Hint ({self.hints_remaining} left)"
        )
        self.solve_btn.config(state=tk.NORMAL)
        self.refresh_the_screen()

    def fit_image_to_grid(self, img, grid_size):
        h, w, _ = img.shape
        scale = self.canvas_size / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h))

        tile_w, tile_h = new_w // grid_size, new_h // grid_size
        crop_w, crop_h = tile_w * grid_size, tile_h * grid_size

        start_x, start_y = (new_w - crop_w) // 2, (new_h - crop_h) // 2
        img = img[start_y : start_y + crop_h, start_x : start_x + crop_w]

        pad_h, pad_w = (self.canvas_size - crop_h) // 2, (
            self.canvas_size - crop_w
        ) // 2
        return cv2.copyMakeBorder(
            img,
            pad_h,
            pad_h,
            pad_w,
            pad_w,
            cv2.BORDER_CONSTANT,
            value=[240, 240, 240],
        )

    def slice_image_into_pieces(self, img, grid_size):
        self.tiles = []
        h, w, _ = img.shape
        th, tw = h // grid_size, w // grid_size

        for r in range(grid_size):
            for c in range(grid_size):
                y, x = r * th, c * tw
                tile_img = img[y : y + th, x : x + tw]
                self.tiles.append(
                    GamePiece(
                        tile_img,
                        (r, c),
                        f"Target: Row {r + 1}, Col {c + 1}",
                    )
                )

    def mix_up_the_puzzle_pieces(self, grid_size):
        if not self.tiles:
            return
        scale_map = {3: 6, 4: 12, 5: 20}
        num_actions = scale_map.get(grid_size, grid_size * 4)

        for _ in range(num_actions):
            action = random.choice(["swap", "rotate", "flip"])
            if action == "swap":
                idx1, idx2 = random.sample(range(len(self.tiles)), 2)
                (
                    self.tiles[idx1].current_pos,
                    self.tiles[idx2].current_pos,
                ) = (
                    self.tiles[idx2].current_pos,
                    self.tiles[idx1].current_pos,
                )
            elif action == "rotate":
                random.choice(self.tiles).turn_piece(
                    random.choice([90, 180, 270])
                )
            elif action == "flip":
                random.choice(self.tiles).mirror_piece(
                    random.choice(["horizontal", "vertical"])
                )

    def give_the_player_a_clue(self):
        if self.hints_remaining <= 0 or self.game_over:
            return
        incorrect_tiles = [
            tile for tile in self.tiles if not tile.is_in_the_right_spot()
        ]
        if not incorrect_tiles:
            return

        self.active_hint_tile = random.choice(incorrect_tiles)
        self.hints_remaining -= 1
        self.hint_btn.config(text=f"Hint ({self.hints_remaining} left)")
        if self.hints_remaining == 0:
            self.hint_btn.config(state=tk.DISABLED)
        self.refresh_the_screen()

    def instantly_solve_everything(self):
        if not self.tiles or self.game_over:
            return
        for tile in self.tiles:
            tile.restore_original_state()
        self.moves, self.active_hint_tile, self.game_over = 0, None, True
        self.hint_btn.config(state=tk.DISABLED)
        self.solve_btn.config(state=tk.DISABLED)
        self.refresh_the_screen()
        messagebox.showinfo("Solved", "The puzzle has been fixed!")

    def add_grid_lines(self, grid_size):
        tw = th = self.canvas_size // grid_size
        for i in range(1, grid_size):
            self.puzzle_canvas.create_line(
                i * tw, 0, i * tw, self.canvas_size, fill="#a0a0a0", dash=(2, 2)
            )
            self.puzzle_canvas.create_line(
                0, i * th, self.canvas_size, i * th, fill="#a0a0a0", dash=(2, 2)
            )

    def mark_as_finished(self, x, y):
        self.puzzle_canvas.create_oval(
            x + 5, y + 5, x + 23, y + 23, fill="green", outline="white"
        )
        self.puzzle_canvas.create_line(
            x + 9, y + 14, x + 13, y + 18, fill="white", width=2
        )
        self.puzzle_canvas.create_line(
            x + 13, y + 18, x + 19, y + 10, fill="white", width=2
        )

    def show_clue_marker(self, canvas, x, y, tw, th):
        cx, cy = x + tw // 2, y + th // 2
        radius = min(tw, th) // 4
        canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            outline="red",
            width=3,
        )

    def refresh_the_screen(self):
        self.ref_canvas.delete("all")
        if self.original_tk_img:
            self.ref_canvas.create_image(
                0, 0, image=self.original_tk_img, anchor=tk.NW
            )

        self.puzzle_canvas.delete("all")
        grid_size = self.grid_size_var.get()
        tw = th = self.canvas_size // grid_size

        incorrect_count = sum(
            1 for tile in self.tiles if not tile.is_in_the_right_spot()
        )
        self.move_label.config(text=f"Moves: {self.moves}")
        self.incorrect_label.config(
            text=f"Incorrect: {incorrect_count}",
            fg="green" if incorrect_count == 0 else "red",
        )

        for i, tile in enumerate(self.tiles):
            img_matrix = tile.prepare_image_for_display()
            tile.tk_image = ImageTk.PhotoImage(
                image=Image.fromarray(img_matrix)
            )
            r, c = tile.current_pos
            x, y = c * tw, r * th

            self.puzzle_canvas.create_image(
                x, y, image=tile.tk_image, anchor=tk.NW
            )

            if self.selected_index == i and not self.game_over:
                self.puzzle_canvas.create_rectangle(
                    x + 1,
                    y + 1,
                    x + tw - 1,
                    y + th - 1,
                    outline="blue",
                    width=4,
                )

            if tile.is_in_the_right_spot():
                self.mark_as_finished(x, y)

        if self.active_hint_tile and not self.game_over:
            curr_r, curr_c = self.active_hint_tile.current_pos
            self.show_clue_marker(
                self.puzzle_canvas, curr_c * tw, curr_r * th, tw, th
            )
            corr_r, corr_c = self.active_hint_tile.correct_pos
            self.show_clue_marker(
                self.ref_canvas, corr_c * tw, corr_r * th, tw, th
            )

        self.add_grid_lines(grid_size)
        if self.has_the_player_won() and not self.game_over:
            self.game_over = True
            messagebox.showinfo("Win!", f"Finished in {self.moves} moves!")

    def on_tile_clicked(self, event):
        if self.game_over or not self.tiles:
            return
        grid_size = self.grid_size_var.get()
        tw, th = self.canvas_size // grid_size, self.canvas_size // grid_size
        idx = next(
            (
                i
                for i, t in enumerate(self.tiles)
                if t.current_pos == (event.y // th, event.x // tw)
            ),
            None,
        )
        if idx is None:
            return

        if self.selected_index is None:
            self.selected_index = idx
        elif self.selected_index == idx:
            self.selected_index = None
        else:
            t1, t2 = self.tiles[self.selected_index], self.tiles[idx]
            t1.current_pos, t2.current_pos = t2.current_pos, t1.current_pos
            (
                self.selected_index,
                self.moves,
                self.active_hint_tile,
            ) = (
                None,
                self.moves + 1,
                None,
            )
        self.refresh_the_screen()

    def on_tile_flipped(self, event):
        if self.game_over or not self.tiles:
            return
        tw, th = (
            self.canvas_size // self.grid_size_var.get(),
            self.canvas_size // self.grid_size_var.get(),
        )
        idx = next(
            (
                i
                for i, t in enumerate(self.tiles)
                if t.current_pos == (event.y // th, event.x // tw)
            ),
            None,
        )
        if idx is not None:
            self.tiles[idx].mirror_piece()
            self.moves, self.active_hint_tile = self.moves + 1, None
            self.refresh_the_screen()

    def on_tile_rotated(self, event):
        if self.game_over or not self.tiles:
            return
        tw, th = (
            self.canvas_size // self.grid_size_var.get(),
            self.canvas_size // self.grid_size_var.get(),
        )
        idx = next(
            (
                i
                for i, t in enumerate(self.tiles)
                if t.current_pos == (event.y // th, event.x // tw)
            ),
            None,
        )
        if idx is not None:
            self.tiles[idx].turn_piece()
            self.moves, self.active_hint_tile = self.moves + 1, None
            self.refresh_the_screen()

    def has_the_player_won(self):
        return len(self.tiles) > 0 and all(
            tile.is_in_the_right_spot() for tile in self.tiles
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGame(root)
    root.mainloop()