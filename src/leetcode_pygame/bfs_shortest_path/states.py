import random
from abc import ABC, abstractmethod
from collections import deque
from typing import List

import pygame

from leetcode_pygame.bfs_shortest_path.algorithm import (
    WALL,
    create_bad_grid,
    create_good_grid,
    visit_neighbors,
)
from leetcode_pygame.bfs_shortest_path.constants import (
    BLACK,
    CELL_SIZE,
    END_POS,
    GREEN,
    GRID_SIZE,
    RED,
    SCREEN_SIZE_X,
    SCREEN_SIZE_Y,
    START_POS,
    THICK_LINE_WIDTH,
    THIN_LINE_WIDTH,
    UPDATES_PER_SECOND,
    WHITE,
)
from leetcode_pygame.bfs_shortest_path.sprites import (
    CellSprite,
    CellType,
    LineSprite,
    OverlaySprite,
    TextSprite,
)
from leetcode_pygame.bfs_shortest_path.game import Game


class GameState(ABC):
    """
    Abstract base class representing the general state of the game.

    This class defines the essential methods that each game state must implement:
    - handle_events: Handles any input events (like keyboard or mouse actions).
    - update: Updates the state of the game, usually for animation or logic progression.
    - render: Renders the current state of the game on the screen.

    Inherits from ABC (Abstract Base Class) to ensure that any subclass must implement the abstract methods.
    However there are no abstract methods as of now.
    """

    def handle_events(self, events: List[pygame.event.Event]):
        """
        Handles input events for the current game state.

        Args:
            events (List[pygame.event.Event]): A list of events to process.
        """
        pass

    def update(self, delta_time: float):
        """
        Updates the game state, usually for animation or logic progression.

        Args:
            delta_time (float): The time elapsed since the last frame (in seconds).
        """
        pass

    def render(self):
        """
        Renders the current state of the game to the screen.
        """
        pass


class TimelyUpdateGameState(GameState, ABC):
    """
    A subclass of GameState that handles time-based updates.

    This class adds functionality to ensure that updates to the game state
    occur at a consistent rate, based on the specified updates per second
    (FPS). It ensures that updates are triggered only after the specified
    amount of time has passed.

    Args:
        game (Game): The game instance to which the state belongs.
        updates_per_second (float | int): The number of updates to be performed per second.
    """

    def __init__(self, game: Game, updates_per_second: float | int):
        """
        Initializes the state with the game instance and updates per second.

        Args:
            game (Game): The game instance to which the state belongs.
            updates_per_second (float | int): The number of updates per second for the game state.
        """
        self.game = game
        self.time_lapsed_since_last_update = 0
        self.updates_per_second = updates_per_second
        self.update_interval = 1 / updates_per_second

    def update(self, delta_time: float):
        """
        Updates the game state based on the elapsed time, ensuring that updates
        occur at the specified rate.

        Args:
            delta_time (float): The time elapsed since the last frame (in seconds).
        """
        self.time_lapsed_since_last_update += delta_time
        if self.time_lapsed_since_last_update < self.update_interval:
            return
        self.time_lapsed_since_last_update -= self.update_interval
        self.perform_update()

    @abstractmethod
    def perform_update(self):
        """
        Performs the actual update logic for the game state. This method must
        be implemented by any subclass.

        This method is called when the time threshold is reached for an update.
        """
        pass


class InitState(GameState):
    """
    Represents the initial state of the game, where the user can choose to start
    a random, successful, or failure path.

    In this state, the user is presented with instructions on how to proceed,
    and their input determines the grid that will be generated for the next state.
    """

    def __init__(self, game: Game):
        """
        Initializes the InitState, which displays the initial instructions to the user.

        Args:
            game (Game): The game instance to which this state belongs.
        """
        self.game = game

        # Create text sprites to display on the screen with different instructions
        text_1 = TextSprite("Press SPACE to start randomly", 36, BLACK)
        text_2 = TextSprite("Press ENTER to start a successful path", 36, GREEN)
        text_3 = TextSprite("Press ESC to start a failure path", 36, RED)

        # Position the text sprites on the screen
        text_2.rect.center = (SCREEN_SIZE_X // 2, SCREEN_SIZE_Y // 2)
        text_1.rect.bottomleft = text_2.rect.topleft
        text_3.rect.topleft = text_2.rect.bottomleft

        # Add text sprites to the sprite group for rendering
        self.objects = pygame.sprite.Group()
        self.objects.add(text_1, text_2, text_3)

    def handle_events(self, events: List[pygame.event.Event]):
        """
        Handles input events for the InitState, where the user chooses how to proceed.

        Args:
            events (List[pygame.event.Event]): A list of events to process.
        """
        for event in events:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    # Start with a randomly generated grid
                    self._create_grid_and_navigate(GRID_SIZE, is_good=None)
                if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                    # Start with a successful path grid
                    self._create_grid_and_navigate(GRID_SIZE, is_good=True)
                if event.key == pygame.K_ESCAPE:
                    # Start with a failure path grid
                    self._create_grid_and_navigate(GRID_SIZE, is_good=False)

    def _create_grid_and_navigate(
        self, size: int, is_good: bool | None = None
    ) -> List[List[int]]:
        """
        Creates a grid based on the chosen type (good or bad) and transitions to
        the simulation state.

        Args:
            size (int): The size of the grid.
            is_good (bool | None): Whether to create a good or bad grid. If None,
                                   a random choice is made.

        Returns:
            List[List[int]]: The generated grid.
        """
        if is_good is None:
            is_good = random.choice([True, False])

        if is_good:
            # Generate a good grid
            grid = create_good_grid(size)
        else:
            # Generate a bad grid
            grid = create_bad_grid(size)

        # Transition to the simulation state with the generated grid
        self.game.next_state = SimulationState(
            self.game, grid=grid, start_pos=START_POS, end_pos=END_POS
        )

    def render(self):
        """
        Renders the initial state to the screen, displaying the instructions.

        This method fills the screen with a white background and draws the text
        sprites for user instructions.
        """
        screen = self.game.screen
        screen.fill(WHITE)
        self.objects.draw(screen)


class SimulationState(TimelyUpdateGameState):
    """
    A game state representing the simulation of BFS pathfinding on a grid.
    """

    def __init__(
        self,
        game: Game,
        grid: List[List[int]],
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
    ):
        """
        Initializes the simulation state with the given parameters.

        Args:
            game (Game): The current game instance.
            grid (List[List[int]]): A 2D grid representing the game environment.
            start_pos (tuple[int, int]): The starting position for the pathfinding.
            end_pos (tuple[int, int]): The destination position for the pathfinding.
        """
        super().__init__(game, UPDATES_PER_SECOND)

        self.grid = grid
        self.grid_size = len(grid)  # Only works for square grids
        self.visited = [
            [False] * self.grid_size for _ in range(self.grid_size)
        ]  # Track visited cells
        self.queue = deque([start_pos])  # Queue for BFS
        self.parents = {
            start_pos: None
        }  # Store parent of each cell for path reconstruction
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.visited[start_pos[0]][
            start_pos[1]
        ] = True  # Mark start position as visited
        self.cell_sprites = pygame.sprite.Group()  # Group for cell sprites
        self.line_sprites = (
            pygame.sprite.Group()
        )  # Group for lines representing the BFS path
        self.text_sprites = (
            pygame.sprite.GroupSingle()
        )  # Single group for text (level display)
        self.level = 0  # BFS level counter

        # Initialize cell sprites for the grid based on the type of each cell
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                cell_type = "wall" if self.grid[x][y] == WALL else "unvisited"
                cell_sprite = CellSprite(x, y, cell_type)
                self.cell_sprites.add(cell_sprite)

        self.update_cell_type(start_pos[0], start_pos[1], "visited")

    def perform_update(self):
        """
        Perform one update step for the BFS pathfinding algorithm.
        If the queue is empty, it transitions to the next state.
        """
        if len(self.queue) == 0:
            # If the queue is empty, no path is found; transition to NoPathState
            entities = self.get_all_sprites_as_group()
            self.game.next_state = NoPathState(self.game, entities, self.level)
            return

        elements_at_level = len(self.queue)
        self.level += 1  # Increase the level (depth) of BFS

        # Process each element at the current BFS level
        for _ in range(0, elements_at_level):
            x, y = self.queue.popleft()
            if (x, y) == self.end_pos:
                # If the end position is reached, build the final path
                self.build_final_path()
                entities = self.get_all_sprites_as_group()
                # Navigate to CompletionState to display the result
                self.game.next_state = CompletionState(self.game, entities, self.level)
                return

            # Visit neighboring cells of the current position
            self.visit_neighbors(x, y)

    def visit_neighbors(self, x: int, y: int) -> None:
        """
        Visit all valid neighboring cells and update their state.

        Args:
            x (int): The x-coordinate of the current cell.
            y (int): The y-coordinate of the current cell.
        """
        # This function alters visited and queue
        neighbors = visit_neighbors(
            x, y, self.grid, self.grid_size, self.visited, self.queue
        )
        for neighbor in neighbors:
            self.parents[neighbor] = (x, y)  # Set parent for path reconstruction
            self.update_cell_type(neighbor[0], neighbor[1], "visited")
            self.add_line((x, y), neighbor)

    def handle_events(self, events: List[pygame.event.Event]):
        """
        Handle user input events, such as pressing the escape key to return to the initial state.

        Args:
            events (List[pygame.event.Event]): List of pygame events to handle.
        """
        for event in events:
            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                # Escape key pressed, go back to initial state
                self.game.next_state = InitState(self.game)
                return

    @property
    def level(self) -> int:
        """
        The current BFS level (depth).

        Returns:
            int: The current level.
        """
        return self._level

    @level.setter
    def level(self, value: int):
        """
        Set the level and update the displayed level text sprite.

        Args:
            value (int): The new level value.
        """
        self._level = value
        sprite = TextSprite(f"Current Level: {value}", 36, BLACK)
        sprite.rect.topleft = (THIN_LINE_WIDTH, self.grid_size * CELL_SIZE)
        self.text_sprites.add(sprite)

    def update_cell_type(self, x: int, y: int, cell_type: CellType) -> None:
        """
        Update the cell sprite type for the given position.

        Args:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
            cell_type (CellType): The new cell type.
        """
        for sprite in self.cell_sprites:
            if sprite.x == x and sprite.y == y:
                sprite.update_type(cell_type)
                break

    def get_all_sprites_as_group(self) -> pygame.sprite.Group:
        """
        Get all sprites (cells, lines, text) as a pygame sprite group.

        Returns:
            pygame.sprite.Group: The group containing all sprites for rendering.
        """
        entities = pygame.sprite.Group()
        entities.add(self.cell_sprites)
        entities.add(self.line_sprites)
        return entities

    def add_line(
        self,
        from_point: tuple[int, int],
        to_point: tuple[int, int],
        line_width: int = THIN_LINE_WIDTH,
    ) -> None:
        """
        Add a line sprite between two points to represent the BFS path.

        Args:
            from_point (tuple[int, int]): The starting point of the line.
            to_point (tuple[int, int]): The ending point of the line.
            line_width (int, optional): The width of the line. Defaults to THIN_LINE_WIDTH.
        """
        line_sprite = LineSprite(from_point, to_point, line_width, RED)
        self.line_sprites.add(line_sprite)

    def build_final_path(self) -> None:
        """
        Reconstruct and display the final path from the end position to the start position.
        """
        current = self.end_pos
        self.update_cell_type(current[0], current[1], "final_path")

        # Reconstruct the path by tracing the parents
        while current != self.start_pos:
            previous = current
            current = self.parents[current]
            self.update_cell_type(current[0], current[1], "final_path")
            self.add_line(current, previous, line_width=THICK_LINE_WIDTH)

    def render(self):
        """
        Render all sprites (cells, lines, and text) to the screen.
        """
        screen = self.game.screen
        screen.fill(WHITE)

        self.cell_sprites.draw(screen)
        self.line_sprites.draw(screen)
        self.text_sprites.draw(screen)


class CompletionState(GameState):
    """
    A game state that represents the completion of the BFS pathfinding simulation.

    This state is shown when the algorithm successfully finds a path to the destination.
    It displays the shortest path length and offers the player an option to restart the simulation.

    Attributes:
        game (Game): The game instance, used to transition between states.
        entities (pygame.sprite.Group): A group containing the text and sprite entities to be rendered.
        shortest_path (int): The length of the shortest path found during the simulation.
    """

    def __init__(self, game: Game, entities: pygame.sprite.Group, shortest_path: int):
        """
        Initializes the completion state with the game, entities, and shortest path length.

        Args:
            game (Game): The game instance, which handles the state transitions.
            entities (pygame.sprite.Group): The group of entities (sprites, text) to be displayed.
            shortest_path (int): The length of the shortest path found in the simulation.
        """
        self.game = game
        self.entities = pygame.sprite.Group()
        self.entities.add(entities)
        self.shortest_path = shortest_path

        text_1 = TextSprite(
            f"Shortest path found at level {self.shortest_path}", 32, GREEN
        )
        text_2 = TextSprite("Press space to go to the beginning", 32, BLACK)
        text_1.rect.topleft = (THIN_LINE_WIDTH, GRID_SIZE * CELL_SIZE)
        text_2.rect.topleft = text_1.rect.bottomleft
        self.entities.add(text_1, text_2)

    def handle_events(self, events: List[pygame.event.Event]):
        """
        Handles the user input events during the completion state.

        Specifically, listens for the spacebar key press to transition to the initial state.

        Args:
            events (List[pygame.event.Event]): A list of events that are checked for input.
        """
        for event in events:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.game.next_state = InitState(self.game)
                    return

    def render(self):
        """
        Renders the completion state to the screen, displaying the entities.

        Clears the screen and draws all entities (text and sprites) to indicate the completion
        of the pathfinding simulation.
        """
        screen = self.game.screen
        screen.fill(WHITE)
        self.entities.draw(screen)


class NoPathState(GameState):
    """
    A game state that represents the scenario where no path was found in the BFS pathfinding simulation.

    This state is shown when the algorithm fails to find a path after visiting a certain number of levels.
    It informs the user that no path was found and provides an option to restart the simulation.

    Attributes:
        game (Game): The game instance, used to transition between states.
        entities (pygame.sprite.OrderedUpdates): A group containing the text and sprite entities to be rendered.
        final_level (int): The number of levels visited before determining that no path was found.
    """

    def __init__(self, game: Game, entities: pygame.sprite.Group, final_level: int):
        """
        Initializes the no-path state with the game, entities, and the number of levels visited.

        Args:
            game (Game): The game instance, which handles the state transitions.
            entities (pygame.sprite.Group): The group of entities (sprites, text) to be displayed.
            final_level (int): The number of levels that were visited without finding a path.
        """
        self.game = game  # Store the game instance to facilitate state transitions
        self.entities = (
            pygame.sprite.OrderedUpdates()
        )  # Create an ordered sprite group for entities
        self.entities.add(
            entities
        )  # Add the provided entities (sprites, text) to the group

        # Create a text sprite to display the message about the path not being found
        text_1 = TextSprite(
            f"Shortest path not found after visiting {final_level} levels!", 32, RED
        )
        text_1.rect.topleft = (
            THIN_LINE_WIDTH,
            GRID_SIZE * CELL_SIZE,
        )  # Position the text at the top left of the screen

        # Create another text sprite to instruct the player to press space to restart
        text_2 = TextSprite(f"Press space to go to the beginning", 32, BLACK)
        text_2.rect.topleft = (
            text_1.rect.bottomleft
        )  # Position this text below the first one

        # Create an overlay sprite that covers the grid area (used for background or effects)
        overlay = OverlaySprite(GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
        # Add the text and overlay sprites to the group of entities
        self.entities.add(text_1, text_2, overlay)

    def handle_events(self, events: List[pygame.event.Event]):
        """
        Handles the user input events during the no-path state.

        Specifically, listens for the spacebar key press to transition to the initial state.

        Args:
            events (List[pygame.event.Event]): A list of events that are checked for input.
        """
        for event in events:  # Loop through all the events to check for key presses
            if event.type == pygame.KEYUP:  # Check if a key has been released
                if event.key == pygame.K_SPACE:  # Check if the space key was pressed
                    self.game.next_state = InitState(
                        self.game
                    )  # Transition to the initial state

    def render(self):
        """
        Renders the no-path state to the screen, displaying the entities.

        Clears the screen and draws all entities (text and sprites) to indicate that no path was found
        in the pathfinding simulation.
        """
        screen = self.game.screen  # Get the game screen to render the state
        screen.fill(WHITE)  # Fill the screen with a white background

        self.entities.draw(
            screen
        )  # Draw all the entities (text, overlay, etc.) to the screen
