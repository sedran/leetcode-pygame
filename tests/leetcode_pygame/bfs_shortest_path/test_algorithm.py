from leetcode_pygame.bfs_shortest_path.algorithm import shortest_path


def test_shortest_path_2x2_solvable():
    # The first example on the LeetCode question
    grid = [
        [0, 1],
        [1, 0],
    ]
    assert 2 == shortest_path(grid)


def test_shortest_path_3x3_solvable():
    # The second example on the LeetCode question
    grid = [
        [0, 0, 0],
        [1, 1, 0],
        [1, 1, 0],
    ]
    assert 4 == shortest_path(grid)


def test_shortest_path_5x5_solvable():
    # Our randomly generated example we've seen in first post of this series
    grid = [
        [0, 0, 0, 1, 1],
        [1, 0, 1, 1, 1],
        [1, 0, 1, 0, 1],
        [0, 0, 1, 0, 0],
        [1, 0, 0, 0, 0],
    ]
    assert 7 == shortest_path(grid)


def test_shortest_path_5x5_unsolvable():
    # Just flipping (x=1, y=2) from 0 to 1, we have made our above example unsolvable
    grid = [
        [0, 0, 0, 1, 1],
        [1, 0, 1, 1, 1],
        [1, 1, 1, 0, 1],
        [0, 0, 1, 0, 0],
        [1, 0, 0, 0, 0],
    ]
    assert -1 == shortest_path(grid)
