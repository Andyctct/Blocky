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
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """

    players_list = []
    total_num_players = num_human + num_random + len(smart_players)
    goals = generate_goals(total_num_players)
    for i in range(num_human):
        human_player = HumanPlayer(i, goals[i])
        players_list.append(human_player)
    for j in range(num_random):
        random_player = RandomPlayer(j + num_human, goals[j + num_human])
        players_list.append(random_player)
    for k in range(len(smart_players)):
        smart_player = SmartPlayer(k + num_human + num_random,
                                   goals[k + num_human + num_random],
                                   smart_players[k])
        players_list.append(smart_player)
    return players_list


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    if not block.position[0] <= location[0] < block.position[0] + block.size \
            or not block.position[1] <= location[1] < block.position[1] + \
                   block.size:
        return None

    if block.level == level:
        return block
    else:
        if block.children == []:
            return block
        for blockchild in block.children:
            if _get_block(blockchild, location, level) is not None:
                return _get_block(blockchild, location, level)

    return None


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    """
    Takes the given action and block to perform the action on, and returns
    the move formatted with the action and the block together.
    """
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player in the Blocky game.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    id: int
    goal: Goal
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """A computer player in the Blocky game that plays randomly.

    === Public Attributes ===
    id:
       This player's number.
    goal:
       This player's assigned goal for the game.
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    id: int
    goal: Goal
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this RandomPlayer with the given <player_id>
        and <goal>, and set proceed signal to False.
        """
        self.id = player_id
        self.goal = goal
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return None always regardless of board.
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """If event is a mouse click, set random player's proceed signal to
        True. Return None
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        potential_actions = {
            0: ROTATE_CLOCKWISE,
            1: ROTATE_COUNTER_CLOCKWISE,
            2: SWAP_HORIZONTAL,
            3: SWAP_VERTICAL,
            4: SMASH,
            5: COMBINE,
            6: PAINT
        }

        random_level = random.randint(0, board.max_depth)
        random_x_position = random.randint(0, board.size - 1)
        random_y_position = random.randint(0, board.size - 1)
        randomly_selected_block = _get_block(board, (random_x_position,
                                                     random_y_position),
                                             random_level)
        randomly_generated_move_num = random.randint(0, len(potential_actions)
                                                     - 1)
        randomly_generated_move = potential_actions[randomly_generated_move_num]

        board_copy = board.create_copy()
        randomly_selected_block_copy = _get_block(board_copy,
                                                  (random_x_position,
                                                   random_y_position),
                                                  random_level)
        if randomly_generated_move == ROTATE_CLOCKWISE:
            if randomly_selected_block_copy.rotate(1):
                self._proceed = False
                return ('rotate', 1, randomly_selected_block)
            else:
                valid_move = self.generate_move(board)
                self._proceed = False
                return valid_move
        elif randomly_generated_move == ROTATE_COUNTER_CLOCKWISE:
            if randomly_selected_block_copy.rotate(3):
                self._proceed = False
                return ('rotate', 3, randomly_selected_block)
            else:
                valid_move = self.generate_move(board)
                self._proceed = False
                return valid_move
        elif randomly_generated_move == SWAP_HORIZONTAL:
            if randomly_selected_block_copy.swap(0):
                self._proceed = False
                return ('swap', 0, randomly_selected_block)
            else:
                valid_move = self.generate_move(board)
                self._proceed = False
                return valid_move
        elif randomly_generated_move == SWAP_VERTICAL:
            if randomly_selected_block_copy.swap(1):
                self._proceed = False
                return ('swap', 1, randomly_selected_block)
            else:
                valid_move = self.generate_move(board)
                self._proceed = False
                return valid_move
        elif randomly_generated_move == SMASH:
            if randomly_selected_block_copy.smash():
                self._proceed = False
                return ('smash', None, randomly_selected_block)
            else:
                valid_move = self.generate_move(board)
                self._proceed = False
                return valid_move
        elif randomly_generated_move == PAINT:
            if randomly_selected_block_copy.paint(self.goal.colour):
                self._proceed = False
                return ('paint', None, randomly_selected_block)
            else:
                valid_move = self.generate_move(board)
                self._proceed = False
                return valid_move
        else:  # randomly_generated_move == COMBINE
            if randomly_selected_block_copy.combine():
                self._proceed = False
                return ('combine', None, randomly_selected_block)
            else:
                valid_move = self.generate_move(board)
                self._proceed = False
                return valid_move


class SmartPlayer(Player):
    """A computer player in the Blocky game that plays 'smart' and scales
    based on difficulty.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    # _difficulty:
    #   The difficulty of the player, corresponds to the number of moves that
    # the player shuffles through before selecting the best one
    id: int
    goal: Goal
    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        """Initialize this smart player with the given, <player_id>, <goal>, and
        difficulty, and set proceed signal to false.
        """
        self.id = player_id
        self.goal = goal
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return None always regardless of board.
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """If event is a mouse click, set the smart player's proceed signal to
        True. Return None
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        board_copy = board.create_copy()
        current_greatest_score = self.goal.score(board_copy)

        i = 0
        greatest_score_move = ('pass', None, board)
        while i < self._difficulty:
            potential_actions = ['ROTATE_CLOCKWISE', 'ROTATE_COUNTER_CLOCKWISE',
                                 'SWAP_HORIZONTAL', 'SWAP_VERTICAL', 'SMASH',
                                 'COMBINE', 'PAINT']

            random_level = random.randint(0, board.max_depth)
            random_x_position = random.randint(0, board.size - 1)
            random_y_position = random.randint(0, board.size - 1)
            randomly_selected_block = _get_block(board, (random_x_position,
                                                         random_y_position),
                                                 random_level)
            randomly_generated_move = random.choice(potential_actions)

            board_copy = board.create_copy()
            randomly_selected_block_copy = _get_block(board_copy,
                                                      (random_x_position,
                                                       random_y_position),
                                                      random_level)
            if randomly_generated_move == 'ROTATE_CLOCKWISE' and \
                    randomly_selected_block_copy.rotate(1):
                if self.goal.score(board_copy) > current_greatest_score:
                    current_greatest_score = self.goal.score(board_copy)
                    greatest_score_move = ('rotate', 1,
                                           randomly_selected_block)
                i += 1
            elif randomly_generated_move == 'ROTATE_COUNTER_CLOCKWISE' and \
                    randomly_selected_block_copy.rotate(3):
                if self.goal.score(board_copy) > current_greatest_score:
                    current_greatest_score = self.goal.score(board_copy)
                    greatest_score_move = ('rotate', 3,
                                           randomly_selected_block)
                i += 1
            elif randomly_generated_move == 'SWAP_HORIZONTAL' and \
                    randomly_selected_block_copy.swap(0):
                if self.goal.score(board_copy) > current_greatest_score:
                    current_greatest_score = self.goal.score(board_copy)
                    greatest_score_move = ('swap', 0,
                                           randomly_selected_block)
                i += 1
            elif randomly_generated_move == 'SWAP_VERTICAL' and \
                    randomly_selected_block_copy.swap(1):
                if self.goal.score(board_copy) > current_greatest_score:
                    current_greatest_score = self.goal.score(board_copy)
                    greatest_score_move = ('swap', 1,
                                           randomly_selected_block)
                i += 1
            elif randomly_generated_move == 'SMASH' and \
                    randomly_selected_block_copy.smash():
                if self.goal.score(board_copy) > current_greatest_score:
                    current_greatest_score = self.goal.score(board_copy)
                    greatest_score_move = ('smash', None,
                                           randomly_selected_block)
                i += 1
            elif randomly_generated_move == 'PAINT' and \
                    randomly_selected_block_copy.paint(self.goal.colour):
                if self.goal.score(board_copy) > current_greatest_score:
                    current_greatest_score = self.goal.score(board_copy)
                    greatest_score_move = ('paint', None,
                                           randomly_selected_block)
                i += 1
            elif randomly_generated_move == 'COMBINE' and \
                    randomly_selected_block_copy.combine():
                if self.goal.score(board_copy) > current_greatest_score:
                    current_greatest_score = self.goal.score(board_copy)
                    greatest_score_move = ('combine', None,
                                           randomly_selected_block)
                i += 1

        self._proceed = False  # Must set to False before returning!
        return greatest_score_move


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
