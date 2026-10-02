import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import random
from PIL import Image, ImageTk

# Hi sunil I encoured 8 problems when I was trying to run the code on vs code. 
# Fatal Indentation Error in scramble(): The for tile_index in selected[4:]: 
# loop is not properly indented, causing a syntax error. It should be indented to be part of the scramble() method.
# transformations_done += 1 used 2 spaces instead of matching the 4-space indent block.
# your original has over 1600 lines making it hard to read and maintain. I have simplified the original code by removing unnecessary comments 
# and whitespace, and by organizing the methods and classes more clearly.
# I did Appreciate the  print() statements because it helped me verify the logic works in your program. 
# But I would68 removed the print() statements to reduce clutter in the output. You can add them back if you want  detailed debugging information.

class Tile:

    def __init__(self, image, original_position):
        self.original_image = image.copy()
        self.image = image.copy()
        self.original_position = original_position

        self.rotation = 0
        self.horizontal_flip = False
        self.vertical_flip = False

    def get_image(self):
        return self.image

    def rotate_clockwise(self, angle=90):

        turns = (angle // 90) % 4

        for _ in range(turns):
            self.image = cv2.rotate(
                self.image,
                cv2.ROTATE_90_CLOCKWISE
            )

        self.rotation = (
            self.rotation + angle
        ) % 360

    def flip_horizontal(self):

        self.image = cv2.flip(
            self.image,
            1
        )

        self.horizontal_flip = (
            not self.horizontal_flip
        )

    def flip_vertical(self):

        self.image = cv2.flip(
            self.image,
            0
        )

        self.vertical_flip = (
            not self.vertical_flip
        )

    def reset(self):

        self.image = (
            self.original_image.copy()
        )

        self.rotation = 0
        self.horizontal_flip = False
        self.vertical_flip = False

    def orientation_correct(self):

        return np.array_equal(
            self.image,
            self.original_image
        )


class Transformation:

    def apply(self, tiles, indices):
        raise NotImplementedError


class SwapTransformation(Transformation):

    def apply(self, tiles, indices):

        first = indices[0]
        second = indices[1]

        tiles[first], tiles[second] = (
            tiles[second],
            tiles[first]
        )

        print(
            "Swapped tile",
            first,
            "with tile",
            second
        )


class RotateTransformation(Transformation):

    def apply(self, tiles, indices):

        tile_index = indices[0]

        angle = random.choice(
            [90, 180, 270]
        )

        tiles[tile_index].rotate_clockwise(
            angle
        )

        print(
            "Rotated tile",
            tile_index,
            "by",
            angle,
            "degrees"
        )



class FlipTransformation(Transformation):

    def apply(self, tiles, indices):

        tile_index = indices[0]

        direction = random.choice(
            [
                "horizontal",
                "vertical"
            ]
        )

        if direction == "horizontal":

            tiles[
                tile_index
            ].flip_horizontal()

        else:

            tiles[
                tile_index
            ].flip_vertical()

        print(
            "Flipped tile",
            tile_index,
            direction
        )

class Puzzle:

    def __init__(self):

        self.original_image = None
        self.tiles = []
        self.grid_size = 3


    def resize_image(
        self,
        image,
        max_size=420
    ):

        height, width = image.shape[:2]

        scale = min(
            max_size / width,
            max_size / height,
            1.0
        )

        new_width = max(
            1,
            int(width * scale)
        )

        new_height = max(
            1,
            int(height * scale)
        )

        return cv2.resize(
            image,
            (
                new_width,
                new_height
            )
        )



    def pad_to_square(
        self,
        image,
        size
    ):

        height, width = image.shape[:2]

        square_side = max(
            height,
            width
        )
        
        remainder = (
            square_side % size
        )

        if remainder != 0:
            square_side += (
                size - remainder
            )

        pad_left = (
            square_side - width
        ) // 2

        pad_right = (
            square_side - width - pad_left
        )

        pad_top = (
            square_side - height
        ) // 2

        pad_bottom = (
            square_side - height - pad_top
        )

        return cv2.copyMakeBorder(
            image,
            pad_top,
            pad_bottom,
            pad_left,
            pad_right,
            cv2.BORDER_CONSTANT,
            value=(240, 240, 240)
        )


    def create_tiles(self):

        self.tiles = []

        height, width = (
            self.original_image.shape[:2]
        )

        tile_height = (
            height // self.grid_size
        )

        tile_width = (
            width // self.grid_size
        )

        position = 0

        for row in range(
            self.grid_size
        ):

            for column in range(
                self.grid_size
            ):

                y1 = row * tile_height
                y2 = y1 + tile_height

                x1 = column * tile_width
                x2 = x1 + tile_width

                tile_image = (
                    self.original_image[
                        y1:y2,
                        x1:x2
                    ].copy()
                )

                self.tiles.append(
                    Tile(
                        tile_image,
                        position
                    )
                )

                position += 1


    def scramble(self):

        transformation_counts = {
            3: 6,
            4: 12,
            5: 20
        }

        transformation_count = transformation_counts[
            self.grid_size
        ]
        
        selected = random.sample(
            range(len(self.tiles)),
            transformation_count + 1
        )

        used = set()
        transformations_done = 0

        first = selected[0]
        second = selected[1]

        SwapTransformation().apply(
            self.tiles,
            [first, second]
        )

        used.add(first)
        used.add(second)
        transformations_done += 1
        rotate_index = selected[2]

        RotateTransformation().apply(
            self.tiles,
            [rotate_index]
        )

        used.add(rotate_index)
        transformations_done += 1

        # Guarantee one Flip transformation
        flip_index = selected[3]

        FlipTransformation().apply(
            self.tiles,
            [flip_index]
        )

        used.add(flip_index)
        transformations_done += 1

        for tile_index in selected[4:]:
            transformation = random.choice(
                [
                    RotateTransformation(),
                    FlipTransformation()
                ]
            )

            transformation.apply(
                self.tiles,
                [tile_index]
            )

            used.add(tile_index)
            transformations_done += 1

        print(
            "Total transformations:",
            transformations_done
        )

        print(
            "Total targeted tiles:",
            len(used)
        )

    def swap_tiles(
        self,
        first,
        second
    ):

        self.tiles[first], self.tiles[second] = (
            self.tiles[second],
            self.tiles[first]
        )

        print(
            "PLAYER SWAP:",
            first,
            "<->",
            second
        )


    def rotate_tile_clockwise(
        self,
        index
    ):

        self.tiles[
            index
        ].rotate_clockwise(90)

        print(
            "PLAYER ROTATE:",
            index,
            "90 degrees clockwise"
        )


    def flip_tile_horizontal(
        self,
        index
    ):

        self.tiles[
            index
        ].flip_horizontal()

        print(
            "PLAYER FLIP:",
            index,
            "horizontal"
        )


    def tile_is_correct(
        self,
        current_position
    ):

        tile = self.tiles[
            current_position
        ]

        correct_position = (
            tile.original_position
            == current_position
        )

        correct_orientation = (
            tile.orientation_correct()
        )

        return (
            correct_position
            and correct_orientation
        )


    def count_incorrect_tiles(self):

        incorrect = 0

        for position in range(
            len(self.tiles)
        ):

            if not self.tile_is_correct(
                position
            ):
                incorrect += 1

        return incorrect


    def is_complete(self):

        return (
            self.count_incorrect_tiles()
            == 0
        )


    def get_hint(self):

        incorrect_positions = []
        misplaced_positions = []

        for position in range(
            len(self.tiles)
        ):

            if not self.tile_is_correct(
                position
            ):

                incorrect_positions.append(
                    position
                )

                tile = self.tiles[
                    position
                ]

                if (
                    tile.original_position
                    != position
                ):

                    misplaced_positions.append(
                        position
                    )

        if not incorrect_positions:
            return None

        if misplaced_positions:

            current_position = random.choice(
                misplaced_positions
            )

        else:

            current_position = random.choice(
                incorrect_positions
            )

        tile = self.tiles[
            current_position
        ]

        home_position = (
            tile.original_position
        )

        return (
            current_position,
            home_position
        )

    def solve(self):

        self.tiles.sort(
            key=lambda tile: tile.original_position
        )

        for tile in self.tiles:
            tile.reset()

        print(
            "PUZZLE SOLVED AUTOMATICALLY"
        )


    def reassemble(self):

        rows = []

        for row in range(
            self.grid_size
        ):

            start = (
                row
                * self.grid_size
            )

            end = (
                start
                + self.grid_size
            )

            row_images = []

            for tile in self.tiles[
                start:end
            ]:

                row_images.append(
                    tile.get_image()
                )

            rows.append(
                np.hstack(
                    row_images
                )
            )

        return np.vstack(
            rows
        )


    def draw_grid(
        self,
        image,
        selected_index=None,
        hint_positions=None
    ):

        display = image.copy()

        height, width = (
            display.shape[:2]
        )

        tile_height = (
            height // self.grid_size
        )

        tile_width = (
            width // self.grid_size
        )

        for column in range(
            1,
            self.grid_size
        ):

            x = (
                column * tile_width
            )

            cv2.line(
                display,
                (x, 0),
                (x, height),
                (100, 100, 100),
                1
            )

        for row in range(
            1,
            self.grid_size
        ):

            y = (
                row * tile_height
            )

            cv2.line(
                display,
                (0, y),
                (width, y),
                (100, 100, 100),
                1
            )

        for index in range(
            len(self.tiles)
        ):

            if self.tile_is_correct(
                index
            ):

                row = (
                    index
                    // self.grid_size
                )

                column = (
                    index
                    % self.grid_size
                )

                x = (
                    column
                    * tile_width
                    + 12
                )

                y = (
                    row
                    * tile_height
                    + 25
                )

                cv2.putText(
                    display,
                    "✓",
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 180, 0),
                    2,
                    cv2.LINE_AA
                )

        if selected_index is not None:

            row = (
                selected_index
                // self.grid_size
            )

            column = (
                selected_index
                % self.grid_size
            )

            x1 = (
                column * tile_width
            )

            y1 = (
                row * tile_height
            )

            x2 = (
                x1
                + tile_width
                - 1
            )

            y2 = (
                y1
                + tile_height
                - 1
            )

            cv2.rectangle(
                display,
                (x1, y1),
                (x2, y2),
                (0, 0, 255),
                4
            )


        if hint_positions is not None:

            current_position = (
                hint_positions[0]
            )

            home_position = (
                hint_positions[1]
            )

            # Current tile position
            current_row = (
                current_position
                // self.grid_size
            )

            current_column = (
                current_position
                % self.grid_size
            )

            current_x = (
                current_column
                * tile_width
                + tile_width // 2
            )

            current_y = (
                current_row
                * tile_height
                + tile_height // 2
            )

            
            home_row = (
                home_position
                // self.grid_size
            )

            home_column = (
                home_position
                % self.grid_size
            )

            home_x = (
                home_column
                * tile_width
                + tile_width // 2
            )

            home_y = (
                home_row
                * tile_height
                + tile_height // 2
            )

            radius = max(
                15,
                min(
                    tile_width,
                    tile_height
                ) // 5
            )

            if current_position == home_position:

                cv2.circle(
                    display,
                    (
                        current_x,
                        current_y
                    ),
                    radius,
                    (0, 0, 255),
                    4
                )

                cv2.putText(
                    display,
                    "R/F",
                    (
                        current_x - 22,
                        current_y + 8
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA
                )

            else:

                cv2.circle(
                    display,
                    (
                        current_x,
                        current_y
                    ),
                    radius,
                    (0, 0, 255),
                    4
                )

                cv2.putText(
                    display,
                    "C",
                    (
                        current_x - 9,
                        current_y + 8
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA
                )

                cv2.circle(
                    display,
                    (
                        home_x,
                        home_y
                    ),
                    radius,
                    (0, 0, 255),
                    4
                )

                cv2.putText(
                    display,
                    "H",
                    (
                        home_x - 9,
                        home_y + 8
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA
                )

        return display


    def load_image(
        self,
        file_path,
        grid_size
    ):

        image_data = np.fromfile(
            file_path,
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_data,
            cv2.IMREAD_COLOR
        )

        if image is None:
            return False

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        self.grid_size = (
            grid_size
        )

        image = self.resize_image(
            image
        )

        image = self.pad_to_square(
            image,
            grid_size
        )

        if image is None:
            return False

        self.original_image = (
            image
        )

        self.create_tiles()

        return True

class PuzzleApp:

    def __init__(
        self,
        root
    ):

        self.root = root

        self.root.title(
            "HIT137 Image Puzzle Game"
        )

        self.root.geometry(
            "1100x800"
        )

        self.puzzle = Puzzle()

        self.grid_size = (
            tk.StringVar(
                value="3"
            )
        )

        self.selected_tile = None
        self.image_loaded = False

        self.moves = 0
        self.game_complete = False

        self.hints_left = 3
        self.active_hint = None

        self.create_widgets()


    def create_widgets(self):

        tk.Label(
            self.root,
            text="Choose Grid Size:"
        ).pack(
            pady=(15, 5)
        )

        grid_frame = tk.Frame(
            self.root
        )

        grid_frame.pack()

        for size in [
            3,
            4,
            5
        ]:

            tk.Radiobutton(
                grid_frame,
                text=f"{size} x {size}",
                variable=self.grid_size,
                value=str(size)
            ).pack(
                side=tk.LEFT,
                padx=10
            )


        button_frame = tk.Frame(
            self.root
        )

        button_frame.pack(
            pady=10
        )

        tk.Button(
            button_frame,
            text="Load Image",
            command=self.load_image
        ).pack(
            side=tk.LEFT,
            padx=10
        )

        self.hint_button = tk.Button(
            button_frame,
            text="Hint",
            command=self.show_hint,
            state=tk.DISABLED
        )

        self.hint_button.pack(
            side=tk.LEFT,
            padx=10
        )

        self.solve_button = tk.Button(
            button_frame,
            text="Solve",
            command=self.solve_puzzle,
            state=tk.DISABLED
        )

        self.solve_button.pack(
            side=tk.LEFT,
            padx=10
        )


        status_frame = tk.Frame(
            self.root
        )

        status_frame.pack(
            pady=5
        )

        self.moves_label = tk.Label(
            status_frame,
            text="Moves: 0",
            font=(
                "Arial",
                12,
                "bold"
            )
        )

        self.moves_label.pack(
            side=tk.LEFT,
            padx=20
        )

        self.tiles_left_label = tk.Label(
            status_frame,
            text="Tiles Left: 0",
            font=(
                "Arial",
                12,
                "bold"
            )
        )

        self.tiles_left_label.pack(
            side=tk.LEFT,
            padx=20
        )

        self.hints_label = tk.Label(
            status_frame,
            text="Hints Left: 3",
            font=(
                "Arial",
                12,
                "bold"
            )
        )

        self.hints_label.pack(
            side=tk.LEFT,
            padx=20
        )


        image_frame = tk.Frame(
            self.root
        )

        image_frame.pack(
            pady=15
        )

        original_frame = tk.Frame(
            image_frame
        )

        original_frame.pack(
            side=tk.LEFT,
            padx=20
        )

        tk.Label(
            original_frame,
            text="Original Image"
        ).pack()

        self.original_label = tk.Label(
            original_frame
        )

        self.original_label.pack()

        puzzle_frame = tk.Frame(
            image_frame
        )

        puzzle_frame.pack(
            side=tk.LEFT,
            padx=20
        )

        tk.Label(
            puzzle_frame,
            text="Puzzle Image"
        ).pack()

        self.puzzle_label = tk.Label(
            puzzle_frame
        )

        self.puzzle_label.pack()

        self.puzzle_label.bind(
            "<Button-1>",
            self.on_left_click
        )

        
        self.puzzle_label.bind(
            "<Button-3>",
            self.on_right_click
        )

    def display_image(
        self,
        image,
        label
    ):

        pil_image = Image.fromarray(
            image
        )

        photo = ImageTk.PhotoImage(
            pil_image
        )

        label.config(
            image=photo
        )

        label.image = photo


    def get_clicked_tile(
        self,
        event
    ):

        if not self.image_loaded:
            return None

        height, width = (
            self.puzzle.original_image.shape[:2]
        )

        if (
            event.x < 0
            or event.y < 0
            or event.x >= width
            or event.y >= height
        ):
            return None

        tile_width = (
            width
            // self.puzzle.grid_size
        )

        tile_height = (
            height
            // self.puzzle.grid_size
        )

        column = (
            event.x
            // tile_width
        )

        row = (
            event.y
            // tile_height
        )

        return (
            row
            * self.puzzle.grid_size
            + column
        )



    def on_left_click(
        self,
        event
    ):

        if self.game_complete:
            return

        tile_index = (
            self.get_clicked_tile(
                event
            )
        )

        if tile_index is None:
            return
        shift_pressed = bool(
            event.state & 0x0001
        )

        if shift_pressed:

            self.puzzle.flip_tile_horizontal(
                tile_index
            )

            self.moves += 1

            self.selected_tile = None

            self.active_hint = None

            self.after_move()

            return "break"


        if self.selected_tile is None:

            self.selected_tile = (
                tile_index
            )

            print(
                "Selected tile:",
                tile_index
            )

        elif (
            self.selected_tile
            == tile_index
        ):

            print(
                "Deselected tile:",
                tile_index
            )

            self.selected_tile = None

        else:

            first = (
                self.selected_tile
            )

            self.puzzle.swap_tiles(
                first,
                tile_index
            )

            self.selected_tile = None

            self.moves += 1

            self.active_hint = None

            self.after_move()

            return

        self.refresh_puzzle()


    def on_right_click(
        self,
        event
    ):

        if self.game_complete:
            return

        tile_index = (
            self.get_clicked_tile(
                event
            )
        )

        if tile_index is None:
            return

        self.puzzle.rotate_tile_clockwise(
            tile_index
        )

        self.selected_tile = None

        self.moves += 1

        # Hint disappears after move
        self.active_hint = None

        self.after_move()

    def show_hint(self):

        if not self.image_loaded:
            return

        if self.game_complete:
            return

        if self.hints_left <= 0:

            messagebox.showinfo(
                "Hints",
                "You have used all 3 hints."
            )

            return

        hint = (
            self.puzzle.get_hint()
        )

        if hint is None:
            return

        self.active_hint = hint

        self.hints_left -= 1

        current_position = (
            hint[0]
        )

        home_position = (
            hint[1]
        )

        if current_position == home_position:

            print(
                "HINT:",
                "tile at position",
                current_position,
                "is in the correct position but needs rotation/flip"
            )

        else:

            print(
                "HINT:",
                "tile at position",
                current_position,
                "belongs at position",
                home_position
            )

        self.update_status()
        self.refresh_puzzle()

        if self.hints_left == 0:

            self.hint_button.config(
                state=tk.DISABLED
            )


    def solve_puzzle(self):

        if not self.image_loaded:
            return

        if self.game_complete:
            return

        self.puzzle.solve()

        self.moves = 0

        self.selected_tile = None

        self.active_hint = None

        self.game_complete = True

        self.hint_button.config(
            state=tk.DISABLED
        )

        self.solve_button.config(
            state=tk.DISABLED
        )

        self.update_status()
        self.refresh_puzzle()

        print(
            "Solve button used"
        )

    def after_move(self):

        self.update_status()
        self.refresh_puzzle()

        if self.puzzle.is_complete():

            self.game_complete = True

            self.hint_button.config(
                state=tk.DISABLED
            )

            self.solve_button.config(
                state=tk.DISABLED
            )

            print(
                "PUZZLE COMPLETED!"
            )

            messagebox.showinfo(
                "Puzzle Complete",
                f"Congratulations!\n\n"
                f"You solved the puzzle in "
                f"{self.moves} moves."
            )


    def update_status(self):

        incorrect = (
            self.puzzle.count_incorrect_tiles()
        )

        self.moves_label.config(
            text=f"Moves: {self.moves}"
        )

        self.tiles_left_label.config(
            text=f"Tiles Left: {incorrect}"
        )

        self.hints_label.config(
            text=f"Hints Left: {self.hints_left}"
        )


    def refresh_original(self):

        original_display = self.puzzle.original_image.copy()

        if self.active_hint is not None:
            home_position = self.active_hint[1]
            height, width = original_display.shape[:2]
            tile_height = height // self.puzzle.grid_size
            tile_width = width // self.puzzle.grid_size
            row = home_position // self.puzzle.grid_size
            column = home_position % self.puzzle.grid_size
            center_x = column * tile_width + tile_width // 2
            center_y = row * tile_height + tile_height // 2
            radius = max(15, min(tile_width, tile_height) // 5)

            cv2.circle(
                original_display,
                (center_x, center_y),
                radius,
                (0, 0, 255),
                4
            )

            cv2.putText(
                original_display,
                "H",
                (center_x - 9, center_y + 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
                cv2.LINE_AA
            )

        self.display_image(
            original_display,
            self.original_label
        )

    def refresh_puzzle(self):

        self.refresh_original()

        puzzle_image = (
            self.puzzle.reassemble()
        )

        puzzle_image = (
            self.puzzle.draw_grid(
                puzzle_image,
                self.selected_tile,
                self.active_hint
            )
        )

        self.display_image(
            puzzle_image,
            self.puzzle_label
        )

    def load_image(self):

        file_path = (
            filedialog.askopenfilename(
                filetypes=[
                    (
                        "Image Files",
                        "*.jpg *.jpeg *.png *.bmp"
                    )
                ]
            )
        )

        if not file_path:
            return

        size = int(
            self.grid_size.get()
        )

        success = (
            self.puzzle.load_image(
                file_path,
                size
            )
        )

        if not success:

            messagebox.showerror(
                "Image Error",
                "The selected image could not be loaded."
            )

            return

        self.moves = 0

        self.selected_tile = None

        self.game_complete = False

        self.image_loaded = True


        self.hints_left = 3

        self.active_hint = None


        self.hint_button.config(
            state=tk.NORMAL
        )

        self.solve_button.config(
            state=tk.NORMAL
        )

        print()
        print("--------------------")
        print("SCRAMBLING PUZZLE")
        print("--------------------")

        self.puzzle.scramble()


        self.refresh_original()

        
        self.update_status()
        self.refresh_puzzle()

        print(
            "Image loaded successfully"
        )

        print(
            "Grid:",
            size,
            "x",
            size
        )

        print(
            "Total tiles:",
            len(
                self.puzzle.tiles
            )
        )

        print(
            "Tiles left:",
            self.puzzle.count_incorrect_tiles()
        )

if __name__ == "__main__":

    root = tk.Tk()

    app = PuzzleApp(
        root
    )

    root.mainloop()