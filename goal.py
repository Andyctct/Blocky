"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    colour_list_copy = COLOUR_LIST[:]
    random_assurance_list = [0, 1]
    rando = random.choice(random_assurance_list)
    goal_list = []
    if rando == 0:
        i = 0
        while i < num_goals:
            rando_colour = random.choice(colour_list_copy)
            goal_list.append(BlobGoal(rando_colour))
            colour_list_copy.remove(rando_colour)
            i += 1

    elif rando == 1:
        i = 0
        while i < num_goals:
            rando_colour = random.choice(colour_list_copy)
            goal_list.append(PerimeterGoal(rando_colour))
            colour_list_copy.remove(rando_colour)
            i += 1
    return goal_list


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    flattened_board = []
    num_col_row = 2 ** (block.max_depth - block.level)
    for i in range(num_col_row):
        flattened_board.append([])
    if block.children == []:
        for i in range(num_col_row):
            j = 0
            while j < num_col_row:
                flattened_board[i].append(block.colour)
                j += 1
    else:
        for i in range(num_col_row // 2):
            flattened_board[i].extend(_flatten(block.children[1])[i])
            flattened_board[num_col_row // 2 + i] \
                .extend(_flatten(block.children[0])[i])
            flattened_board[i].extend(_flatten(block.children[2])[i])
            flattened_board[num_col_row // 2 + i] \
                .extend(_flatten(block.children[3])[i])

    return flattened_board


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A goal in the game of Blocky. The perimeter goal is to amass the greatest
    number of target colour blocks on the perimeter of the board.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.
           The score for perimeter goal is calculated by counting the
           total number of blocks located on the perimeter of board
           that are of the target colour of this goal. Blocks on the corner of
           board count twice towards the score.
           The score is always greater than or equal to 0.
        """
        flattened_board = _flatten(board)
        points = 0
        if len(flattened_board) == 1:
            if flattened_board[0][0] == self.colour:
                points += 4
                return points

        for i in range(len(flattened_board) - 2):
            if flattened_board[i + 1][0] == self.colour:
                points += 1
            if flattened_board[i + 1][-1] == self.colour:
                points += 1

        for i in range(len(flattened_board[0])):
            if flattened_board[0][i] == self.colour:
                if i in (0, len(flattened_board[0]) - 1):
                    points += 2
                else:
                    points += 1

        for i in range(len(flattened_board[-1])):
            if flattened_board[-1][i] == self.colour:
                if i in (0, len(flattened_board[-1]) - 1):
                    points += 2
                else:
                    points += 1

        if points < 0:
            points = 0

        return points

    def description(self) -> str:
        """Return a description of this goal.
        """
        return 'Aim for the greatest number of ' + colour_name(self.colour) \
               + ' blocks on the perimeter of the board. \
               Corner blocks count for twice as much.'


class BlobGoal(Goal):
    """A goal in the game of Blocky. The blob goal is to amass the greatest
    number of target colour blocks in a blob on the board.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.
           The score for blob goal is calculated by counting the
           total number of blocks in the biggest blob of blocks of the target
           colour. Only blocks that share a side are considered to be part of
           the same blob. The score is always greater than or equal to 0.
        """
        flattened_board = _flatten(board)
        visited_board = []
        for i in range(len(flattened_board)):
            visited_board.append([])
        for i in range(len(flattened_board)):
            for j in range(len(flattened_board)):
                visited_board[i].append(-1)

        all_blob_scores = []

        for i in range(len(flattened_board)):
            for j in range(len(flattened_board)):
                all_blob_scores.append \
                    (self._undiscovered_blob_size((i, j), flattened_board,
                                                  visited_board))

        if max(all_blob_scores) < 0:
            return 0

        return max(all_blob_scores)

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        blob_size = 1

        if pos[0] >= len(board) or pos[1] >= len(board) or pos[0] < 0 \
                or pos[1] < 0:
            return 0

        if visited[pos[0]][pos[1]] != -1:
            return 0

        if board[pos[0]][pos[1]] != self.colour:
            visited[pos[0]][pos[1]] = 0
            return 0

        else:
            visited[pos[0]][pos[1]] = 1

            blob_size += self._undiscovered_blob_size((pos[0], pos[1] + 1),
                                                      board, visited)
            blob_size += self._undiscovered_blob_size((pos[0], pos[1] - 1),
                                                      board, visited)
            blob_size += self._undiscovered_blob_size((pos[0] + 1, pos[1]),
                                                      board, visited)
            blob_size += self._undiscovered_blob_size((pos[0] - 1, pos[1]),
                                                      board, visited)

        return blob_size

    def description(self) -> str:
        """Return a description of this goal.
        """
        return 'Aim for the largest group of connected ' + \
               colour_name(self.colour) + ' blocks.'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
