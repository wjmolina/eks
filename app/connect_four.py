from itertools import cycle

import requests


def make_move(pos: str, move: str) -> str:
    if pos.count(move) == 6 or not 1 <= int(move) <= 7:
        return pos

    new_pos = pos + move

    if is_game_over(pos_to_board(new_pos)):
        return new_pos

    score = requests.get(
        "https://connect4.gamesolver.org/solve?pos=" + new_pos,
        headers={
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        },
    ).json()["score"]
    new_move = str(max([i for i in range(7) if score[i] != 100], key=lambda i: score[i]) + 1)

    return new_pos + new_move


def visualize_board(board: str) -> str:
    moves = [":red_circle:", ":yellow_circle:"]
    result = ""
    count = 0

    for i in range(6):
        for j in range(7):
            if board[i][j] == 0:
                result += ":white_circle:"
            elif board[i][j] == 1:
                result += moves[0]
                count += 1
            else:
                result += moves[1]
                count += 1

        result += "\n"

    if is_game_over(board):
        message = " **winner** " + moves[(count + 1) % 2]
    else:
        message = " **your turn** " + moves[count % 2]

    return result[:-1] + message


def pos_to_board(pos: str) -> list[list[int]]:
    move_state = [5] * 7
    board = [[0] * 7 for _ in range(6)]
    moves = [1, -1]
    color = cycle(moves)

    for move in pos:
        move = int(move) - 1
        board[move_state[move]][move] = next(color)
        move_state[move] -= 1

    return board


def is_game_over(board: list[list[int]]) -> bool:
    for i in range(6):
        for j in range(4):
            section = {board[i][j + k] for k in range(4)}

            if section == {1} or section == {-1}:
                return True
    for i in range(3):
        for j in range(7):
            section = {board[i + k][j] for k in range(4)}

            if section == {1} or section == {-1}:
                return True
    for i in range(3):
        for j in range(4):
            section = {board[i + k][j + k] for k in range(4)}

            if section == {1} or section == {-1}:
                return True
    for i in range(3, 6):
        for j in range(4):
            section = {board[i - k][j + k] for k in range(4)}

            if section == {1} or section == {-1}:
                return True

    for j in range(7):
        if board[0][j] == 0:
            return False

    return True
