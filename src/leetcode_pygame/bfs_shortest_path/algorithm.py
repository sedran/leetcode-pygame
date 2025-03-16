from collections import deque
import random
from typing import Callable, List, Optional
from functools import partial

WALL = 1
NON_WALL = 0

DIRECTIONS = [
    (1, 0),  # Right
    (1, 1),  # Bottom-Right
    (0, 1),  # Bottom
    (-1, 1),  # Bottom-Left
    (-1, 0),  # Left
    (-1, -1),  # Top-Left
    (0, -1),  # Top
    (1, -1),  # Top-Right
]


def is_valid(
    x: int,
    y: int,
    grid: List[List[int]],
    size: int,
    visited: List[List[bool]],
) -> bool:
    """
    Given a position (x, y), verifies if it is within the grid's boundaries,
    if it is not a wall (grid[x][y] == 1), if it is not visited before.
    Use this function to test if a candidate neighbor can be queued for a visit.
    """
    if not (x >= 0 and x < size and y >= 0 and y < size):
        return False
    if grid[x][y] == WALL:
        return False
    if visited[x][y]:
        return False
    return True


def visit_neighbors(
    x: int,
    y: int,
    grid: List[List[int]],
    size: int,
    visited: List[List[bool]],
    queue: deque,
) -> None:
    """
    Given a position (x, y), visit its neighbors and queue them for a visit.
    Returns the list of neighbors for further processing in the simulation.
    """
    is_valid_partial = partial(is_valid, grid=grid, size=size, visited=visited)
    neighbors = []

    for dx, dy in DIRECTIONS:
        new_x, new_y = x + dx, y + dy
        if is_valid_partial(new_x, new_y):
            visited[new_x][new_y] = True
            neighbors.append((new_x, new_y))

    queue.extend(neighbors)
    return neighbors


def shortest_path(
    grid: List[List[int]],
    start: tuple[int, int] = (0, 0),
    end: tuple[int, int] = None,
) -> int:
    """
    Given a square grid, find the shortest path from the start to the end.
    Returns the number of steps required to reach the end from the start.
    If no path is found, returns -1.
    """

    # Size of the grid; assuming it is a square grid
    size = len(grid)

    # Initialize the level of the BFS traversal
    level = 0

    # If end is not provided, set it to the bottom-right corner of the grid
    if end is None:
        end = (size - 1, size - 1)

    # If start or end is a wall, return -1
    start_x, start_y = start
    end_x, end_y = end
    if grid[start_x][start_y] == WALL or grid[end_x][end_y] == WALL:
        return -1

    # Initialize the visited matrix and the queue for BFS traversal
    # Both data structures are initialized with the start position
    visited = [[False] * size for _ in range(size)]
    visited[start_x][start_y] = True
    queue = deque([start])

    # Perform BFS traversal. Loop until the queue is empty.
    while len(queue) > 0:
        # At each iteration, we exhaust all elements at the current level.
        level += 1

        # Loop through only the number of elements at the current level because the queue
        # will be modified during the iteration.
        elements_at_level = len(queue)
        for _ in range(0, elements_at_level):
            # Pop the element from the queue
            x, y = queue.popleft()
            # If the end is reached, return the level
            if x == end_x and y == end_y:
                return level
            # Visit the neighbors of the current element. They will be processed in the next level.
            visit_neighbors(x, y, grid, size, visited, queue)

    # There are no more elements to visit and the end was not reached
    return -1


def create_good_grid(
    size: int = 10,
    start_position: tuple[int, int] = (0, 0),
    end_position: Optional[tuple[int, int]] = None,
) -> List[List[int]]:
    """
    Creates a grid where a valid path exists from the start to the end position.

    Args:
        size (int): The size of the grid (default is 10).
        start_position (tuple[int, int]): The starting position in the grid (default is (0, 0)).
        end_position (Optional[tuple[int, int]]): The end position in the grid. If None, defaults to (size-1, size-1).

    Returns:
        List[List[int]]: A grid where the shortest path length is greater than 0 (i.e., a valid path exists).
    """
    return create_grid(
        size=size,
        start_position=start_position,
        end_position=end_position,
        predicate=lambda x: x > 0,  # Ensures a valid path exists
    )


def create_bad_grid(
    size: int = 10,
    start_position: tuple[int, int] = (0, 0),
    end_position: Optional[tuple[int, int]] = None,
) -> List[List[int]]:
    """
    Creates a grid where no valid path exists from the start to the end position.

    Args:
        size (int): The size of the grid (default is 10).
        start_position (tuple[int, int]): The starting position in the grid (default is (0, 0)).
        end_position (Optional[tuple[int, int]]): The end position in the grid. If None, defaults to (size-1, size-1).

    Returns:
        List[List[int]]: A grid where the shortest path length is -1 (i.e., no valid path exists).
    """
    return create_grid(
        size=size,
        start_position=start_position,
        end_position=end_position,
        predicate=lambda x: x == -1,  # Ensures no valid path exists
    )


def create_grid(
    size: int = 10,
    start_position: tuple[int, int] = (0, 0),
    end_position: Optional[tuple[int, int]] = None,
    predicate: Callable[[int], bool] = None,
) -> List[List[int]]:
    """
    Generates a grid based on the given size, start/end positions, and a predicate function.

    Args:
        size (int): The size of the grid (default is 10).
        start_position (tuple[int, int]): The starting position in the grid (default is (0, 0)).
        end_position (Optional[tuple[int, int]]): The end position in the grid. If None, defaults to (size-1, size-1).
        predicate (Callable[[int], bool]): A function that determines if the generated grid meets the desired condition.

    Returns:
        List[List[int]]: A grid that satisfies the predicate condition.

    Raises:
        ValueError: If the grid size is less than 3.
    """
    # Ensure the grid size is at least 3 to allow for meaningful simulation
    if size < 3:
        raise ValueError("Size must be at least 3")

    # Default end position to the bottom-right corner if not provided
    if end_position is None:
        end_position = (size - 1, size - 1)

    # Continuously generate grids until one satisfies the predicate condition
    while True:
        # Create a random grid with walls (1) and open cells (0)
        grid = [
            [random.choice([NON_WALL, WALL]) for _ in range(size)] for _ in range(size)
        ]

        # Ensure the start and end positions are open cells
        grid[start_position[0]][start_position[1]] = NON_WALL
        grid[end_position[0]][end_position[1]] = NON_WALL

        # Calculate the shortest path length using the BFS algorithm
        shortest_path_length = shortest_path(grid, start_position, end_position)

        # Return the grid if it satisfies the predicate condition
        if predicate(shortest_path_length):
            return grid
