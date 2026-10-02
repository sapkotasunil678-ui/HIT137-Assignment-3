# Scrambled Image Puzzle Game 

As a group (DAN/EXT GROUP 28), we designed and built a Python desktop application that showcases core Object-Oriented Programming (OOP) concepts,
GUI design with Tkinter, and image manipulation via OpenCV. This program is an interactive image tile puzzle game where players can load custom images, 
scramble them into grid tiles, and solve the puzzle through swapping, rotating, and flipping tiles.

## Class Architecture Overview
```text
+-------------------------------------------------------+
|                      Tile Class                       |
|  - Encapsulates image array, state, and orientations  |
+-------------------------------------------------------+
                           ^
                           | (Inherits from)
+-------------------------------------------------------+
|                    GamePiece Class                    |
|  - Adds metadata & hints for puzzle pieces            |
+-------------------------------------------------------+
                           ^
                           | (Contains / Composition)
+-------------------------------------------------------+
|                   PuzzleGame Class                    |
|  - Manages Tkinter UI, event loop, state, & rendering |
+-------------------------------------------------------+
```

## Features

- **Custom Image Loading:** Load any local image (`.jpg`, `.png`, `.bmp`) to convert it into an interactive puzzle.
- **Dynamic Grid Sizes:** Choose between `3x3`, `4x4`, or `5x5` grid layouts.
- **Interactive Gameplay Controls:**
  - **Left Click:** Select or swap two tiles.
  - **Shift + Left Click:** Flip a tile horizontally.
  - **Right Click:** Rotate a tile clockwise by 90 degrees.
- **Visual Feedback:**
  - Blue outline highlight for selected tiles.
  - Green checkmark indicators for tiles placed in their correct spot and orientation.
- **Smart Hint System:** Highlights misplaced tiles and shows their target positions (limited to 3 hints per game).
- **Auto-Solve Feature:** Instantly restores the original image state.
- **Reference View:** Displays the original image alongside the active puzzle canvas.

---

## Getting Started

### Prerequisites

Ensure you have Python 3.8+ installed on your system.
The program can also be run through VS Code or Google Colab 

### Required Libraries/Packages

- **opencv-python** (`>=4.5.0`): Handles image loading, resizing, padding, cropping, rotating, and flipping operations.
- **numpy** (`>=1.20.0`): Handles matrix array manipulation for sliced image tiles.
- **Pillow** (`>=9.0.0`): Converts OpenCV image matrices (`PIL.Image`) into Tkinter-compatible images (`ImageTk.PhotoImage`).
- **tk** (`python3-tk`): Standard Python GUI toolkit for rendering windows, canvases, buttons, and dialogs. *(Pre-installed on Windows/macOS; required via package manager on Linux)*.
