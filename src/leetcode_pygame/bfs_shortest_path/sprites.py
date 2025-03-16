from functools import cache
from typing import Final, Literal

import pygame

from leetcode_pygame.bfs_shortest_path.constants import (
    BLACK,
    BLUE,
    CELL_SIZE,
    DARK_RED,
    GRAY,
    GREEN,
    RED,
    THIN_LINE_WIDTH,
)

# Defines possible types of grid cells, each corresponding to a visual state.
CellType = Literal["wall", "unvisited", "visited", "final_path"]


def create_wall(cell_size: int = CELL_SIZE, padding: int = 2) -> pygame.Surface:
    """Creates a surface representing a wall cell.

    Args:
        cell_size (int): The size of the cell in pixels.
        padding (int): The padding inside the cell to adjust the wall appearance.

    Returns:
        pygame.Surface: A surface with a dark red rectangle representing a wall.
    """
    # Create a transparent surface of the given cell size
    surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA).convert_alpha()

    # Draw a dark red rectangle with padding to make the wall visually distinct
    pygame.draw.rect(
        surface,
        DARK_RED,  # Fill color
        (
            padding,  # X position of the rectangle within the `surface`
            padding,  # Y position of the rectangle within the `surface`
            cell_size - 2 * padding,  # Width of the rectangle
            cell_size - 2 * padding,  # Height of the rectangle
        ),
    )
    return surface


def create_circle(
    fill_color: tuple[int, int, int],
    border_color: tuple[int, int, int] = BLACK,
    cell_size: int = CELL_SIZE,
    padding: int = 1,
    border_width: int = 1,
) -> None:
    """Creates a circular surface with a border.

    Args:
        fill_color (tuple[int, int, int]): RGB color of the inner circle.
        border_color (tuple[int, int, int]): RGB color of the outer border.
        cell_size (int): The size of the cell in pixels.
        padding (int): Space between the circle and the edge of the surface.
        border_width (int): Thickness of the border.

    Returns:
        pygame.Surface: A surface containing a circle with the given properties.
    """
    # Create a transparent surface of the given cell size
    surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA).convert_alpha()

    # Calculate center coordinates
    center_x = cell_size // 2
    center_y = cell_size // 2

    # Calculate the outer and inner radii
    outer_radius = cell_size // 2 - 2 * padding
    inner_radius = outer_radius - 2 * border_width

    # Draw the outer circle (border)
    pygame.draw.circle(surface, border_color, (center_x, center_y), outer_radius)

    # Draw the inner circle (fill)
    pygame.draw.circle(surface, fill_color, (center_x, center_y), inner_radius)
    return surface


@cache
def get_cell_surfaces() -> dict[CellType, pygame.Surface]:
    """Pre-renders and caches surfaces for different cell types.

    Returns:
        dict[CellType, pygame.Surface]: A dictionary mapping cell types to
        their corresponding pre-rendered surfaces.
    """
    surfaces = {
        "wall": create_wall(),  # Surface for wall cells
        "unvisited": create_circle(GRAY),  # Surface for unvisited cells
        "visited": create_circle(BLUE),  # Surface for visited cells
        "final_path": create_circle(GREEN),  # Surface for the shortest path
    }
    return surfaces


class CellSprite(pygame.sprite.Sprite):
    """Represents a grid cell in the simulation as a Pygame sprite.

    Attributes:
        x (int): The x-coordinate of the cell in the grid.
        y (int): The y-coordinate of the cell in the grid.
        cell_type (CellType): The type of the cell (e.g., wall, visited, etc.).
        image (pygame.Surface): The visual representation of the cell.
        rect (pygame.Rect): The rectangle defining the cell's position.
    """

    def __init__(
        self,
        x: int,
        y: int,
        cell_type: CellType,
    ):
        """Initializes a CellSprite with position and type.

        Args:
            x (int): The x-coordinate of the cell in the grid.
            y (int): The y-coordinate of the cell in the grid.
            cell_type (CellType): The type of the cell (determines appearance).
        """
        super().__init__()
        self.x = x
        self.y = y
        self.cell_type = cell_type
        self.image = get_cell_surfaces()[
            self.cell_type
        ]  # Assign the corresponding surface
        self.rect = self.image.get_rect(
            topleft=(x * CELL_SIZE, y * CELL_SIZE)
        )  # Position in grid

    def update_type(self, cell_type: CellType):
        """Updates the cell's type and refreshes its appearance.

        Args:
            cell_type (CellType): The new type of the cell.
        """
        self.cell_type = cell_type
        self.image = get_cell_surfaces()[
            self.cell_type
        ]  # Update surface based on new type


class LineSprite(pygame.sprite.Sprite):
    """Represents a line connecting two points in the grid.

    This sprite is used to visually represent paths or connections between cells
    in the grid-based simulation. It supports drawing both straight and diagonal
    lines with configurable width and color.

    Attributes:
        image (pygame.Surface): The surface containing the drawn line.
        rect (pygame.Rect): The rectangular area occupied by the line.
    """

    def __init__(
        self,
        from_point: tuple[int, int],
        to_point: tuple[int, int],
        line_width: int = THIN_LINE_WIDTH,
        color: tuple[int, int, int] = RED,
    ):
        """Initializes a LineSprite connecting two grid points.

        Args:
            from_point (tuple[int, int]): The starting point (grid coordinates).
            to_point (tuple[int, int]): The ending point (grid coordinates).
            line_width (int, optional): The width of the line. Defaults to THIN_LINE_WIDTH.
            color (tuple[int, int, int], optional): The color of the line. Defaults to RED.
        """
        super().__init__()

        # Convert grid coordinates to pixel coordinates.
        x1, y1, x2, y2 = (p * CELL_SIZE for p in (*from_point, *to_point))

        # Calculate the required surface dimensions to fit the line.
        width, height = abs(x1 - x2) + CELL_SIZE, abs(y1 - y2) + CELL_SIZE

        # Create a transparent surface to draw the line on.
        self.image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect(topleft=(min(x1, x2), min(y1, y2)))

        # Adjust line width for diagonal lines to make them more visible.
        if x1 != x2 and y1 != y2:
            line_width = int(line_width * 1.5)

        # Center the line within the grid cell.
        shift_by_x = CELL_SIZE // 2 - self.rect.left
        shift_by_y = CELL_SIZE // 2 - self.rect.top

        # Draw the line from the starting point to the ending point.
        pygame.draw.line(
            self.image,
            color,
            (x1 + shift_by_x, y1 + shift_by_y),
            (x2 + shift_by_x, y2 + shift_by_y),
            line_width,
        )


class TextSprite(pygame.sprite.Sprite):
    """
    A sprite class for rendering and displaying text in a Pygame game.

    This class is used to create a text element that can be added to the
    Pygame sprite system for rendering.

    Attributes:
        image (pygame.Surface): The surface containing the rendered text.
        rect (pygame.Rect): The rectangle that defines the boundaries of the text.
    """

    def __init__(self, text: str, font_size: int, color: tuple[int, int, int]):
        """
        Initialize the TextSprite object.

        Args:
            text (str): The text string to display in the sprite.
            font_size (int): The font size for rendering the text.
            color (tuple[int, int, int]): The color of the text in RGB format.
        """
        super().__init__()

        # Create a font object with the specified font size.
        font = pygame.font.Font(None, font_size)

        # Render the text with the specified color and store it in the 'image' attribute.
        self.image = font.render(text, True, color)

        # Get the rectangle for the rendered text to define its position and size.
        self.rect = self.image.get_rect()


class OverlaySprite(pygame.sprite.Sprite):
    """
    A sprite that creates a semi-transparent overlay for the game screen.

    This class creates an overlay that can be used for effects such as modal dialogs,
    backgrounds for text, or to create visual focus. The overlay is customizable in terms of size,
    color, and transparency (alpha value).

    Attributes:
        image (pygame.Surface): The surface representing the overlay sprite.
        rect (pygame.Rect): The rectangle used for positioning the overlay sprite.
    """

    def __init__(self, width: int, height: int, color=(128, 128, 128), alpha=200):
        """
        Initialize the OverlaySprite with the given width, height, color, and alpha.

        Args:
            width (int): The width of the overlay.
            height (int): The height of the overlay.
            color (tuple[int, int, int]): The RGB color of the overlay (default is gray).
            alpha (int): The transparency of the overlay (default is 200).
        """
        super().__init__()

        # Create a new surface with the given width and height and transparent background
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        # Fill the surface with the specified color and alpha (transparency)
        self.image.fill((*color, alpha))

        # Set the rect attribute for positioning the sprite
        self.rect = self.image.get_rect()
