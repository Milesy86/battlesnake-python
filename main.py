# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# Battlesnake Logic, based off the Python Starter snake template from battlesnake.com
# For more info see docs.battlesnake.com

import random
import typing


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "milesy86",
        "color": "#009900",
        "head": "tongue",  # TODO: Choose head
        "tail": "sharp",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


def eliminate_out_of_bounds_moves(move_coordinates_dict, board_width, board_height):
    # Find and eliminate any moves that would send the snake out of bounds
    for direction in list(move_coordinates_dict.keys()):
        if (move_coordinates_dict[direction]["coordinates"]["x"] < 0
                or move_coordinates_dict[direction]["coordinates"]["x"] == board_width
                or move_coordinates_dict[direction]["coordinates"]["y"] < 0
                or move_coordinates_dict[direction]["coordinates"]["y"] == board_height):
            del move_coordinates_dict[direction]
    return move_coordinates_dict


def eliminate_backwards_move(move_coordinates_dict, my_neck):
    # Find and remove the move that would be backwards
    for direction in list(move_coordinates_dict.keys()):
        if move_coordinates_dict[direction]["coordinates"] == my_neck:
            del move_coordinates_dict[direction]
            return move_coordinates_dict
    return move_coordinates_dict


def eliminate_self_collision_moves(move_coordinates_dict, my_body):
    # Find and remove any moves that would collide with self
    for direction in list(move_coordinates_dict.keys()):
        if move_coordinates_dict[direction]["coordinates"] in my_body:
            del move_coordinates_dict[direction]
    return move_coordinates_dict


def eliminate_enemy_collision_moves(move_coordinates_dict, my_length, enemy_snakes):
    # Find and remove any moves that would collide with enemy snakes
    for direction in list(move_coordinates_dict.keys()):
        for enemy_snake in enemy_snakes:
            # First check if you're going to hit the enemy snake as it exists now
            if move_coordinates_dict[direction]["coordinates"] in enemy_snake["body"]:
                del move_coordinates_dict[direction]
                break
            enemy_snake_head = enemy_snake["head"]
            possible_head_on_collision_coordinates = [
                {"x": enemy_snake_head["x"] + 1, "y": enemy_snake_head["y"]},
                {"x": enemy_snake_head["x"] - 1, "y": enemy_snake_head["y"]},
                {"x": enemy_snake_head["x"], "y": enemy_snake_head["y"] + 1},
                {"x": enemy_snake_head["x"], "y": enemy_snake_head["y"] - 1},
            ]
            # Check for head-on collisions (both snakes move into the same space)
            # A head-on collision can be won if you're longer than the other snake, so play chicken in that case.
            if (move_coordinates_dict[direction]["coordinates"] in possible_head_on_collision_coordinates
                    and enemy_snake["length"] >= my_length):
                move_coordinates_dict[direction]["possible_head_on_collision"] = True
    return move_coordinates_dict


def create_map(width, height, snakes):
    # Create a map of the playing field. 0s represent empty space and 1s represent spaces containing snakes.
    board_row = [0] * width
    board_map = []
    for i in range(height):
        board_map.append(board_row[:])
    for snake in snakes:
        for coordinate in snake["body"]:
            board_map[coordinate["y"]][coordinate["x"]] = 1
    return board_map


def count_spaces(board_map, space_type):
    count = 0
    for row in board_map:
        count += row.count(space_type)
    return count


def check_space_in_move_direction(move_coordinate, board_map):
    result_board_map = [x[:] for x in board_map[:]]

    def flood_fill(x, y, old, new):
        if x < 0 or x >= len(result_board_map[0]) or y < 0 or y >= len(result_board_map):
            return
        if result_board_map[y][x] != old:
            return
        result_board_map[y][x] = new
        flood_fill(x + 1, y, old, new)
        flood_fill(x - 1, y, old, new)
        flood_fill(x, y + 1, old, new)
        flood_fill(x, y - 1, old, new)

    flood_fill(move_coordinate["x"], move_coordinate["y"], 0, 2)
    return count_spaces(result_board_map, 2)


def check_for_enclosed_spaces(move_coordinates_dict, width, height, snakes):
    board_map = create_map(width, height, snakes)
    for direction in list(move_coordinates_dict.keys()):
        spaces_in_direction = check_space_in_move_direction(move_coordinates_dict[direction]["coordinates"], board_map)
        if spaces_in_direction == count_spaces(board_map, 0):
            break
        else:
            move_coordinates_dict[direction]["space"] = spaces_in_direction


def identify_closest_food(my_head, food_coordinates):
    # Identify how close all the food is to our snake's head. Returns a list sorted by distance, closest first
    food_distance_list = []
    for food_location in food_coordinates:
        distance_to_food = calculate_distance_between(food_location, my_head)
        food_distance_list.append({"distance": distance_to_food, "location": food_location})
    food_distance_list.sort(key=lambda row: row["distance"])
    return food_distance_list


def calculate_distance_between(first_coordinate, second_coordinate):
    return abs(first_coordinate["x"] - second_coordinate["x"]) + abs(first_coordinate["y"] - second_coordinate["y"])


def choose_next_move(move_coordinates_dict, my_head, food_coordinates, board_width, board_height, all_snakes):
    # If there are no safe moves it doesn't matter which way we go so just move down.
    if len(move_coordinates_dict) == 0:
        print("No safe moves detected! Moving down")
        return "down"
    # If there's only one safe move, do it.
    if len(move_coordinates_dict) == 1:
        return list(move_coordinates_dict.keys())[0]

    # If there are multiple safe moves, eliminate ones that might send us into an enclosed space
    check_for_enclosed_spaces(move_coordinates_dict, board_width, board_height, all_snakes)
    print(move_coordinates_dict)
    max_space = max([x["space"] for x in move_coordinates_dict.values()])
    move_coordinates_dict = {k: v for k, v in move_coordinates_dict.items() if v["space"] == max_space}
    print(move_coordinates_dict)

    # Of the remaining safe moves, first consider any that can't result in a head-on collision
    non_collision_moves_list = [x for x in list(move_coordinates_dict.keys()) if
                                not move_coordinates_dict[x]["possible_head_on_collision"]]
    collision_moves_list = [x for x in list(move_coordinates_dict.keys()) if
                                move_coordinates_dict[x]["possible_head_on_collision"]]
    food_distance_list = identify_closest_food(my_head, food_coordinates)
    # Move closer to food if possible, otherwise move randomly of the available choices
    for food in food_distance_list:
        for direction in non_collision_moves_list:
            if calculate_distance_between(food["location"], move_coordinates_dict[direction]["coordinates"]) < food["distance"]:
                return direction
        # If there are non-collision moves but none move closer to food, pick from them at random
        if len(non_collision_moves_list) != 0:
            return random.choice(non_collision_moves_list)
        # Now consider possible head-on collision moves, choosing to move closer to food if possible.
        for direction in collision_moves_list:
            if calculate_distance_between(food["location"], move_coordinates_dict[direction]["coordinates"]) < food["distance"]:
                return direction
            return random.choice(collision_moves_list)


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    my_body = game_state["you"]["body"]  # Coordinates of my whole snake
    my_head = game_state["you"]["head"]  # Coordinates of my snake's head
    move_coordinates_dict = {"left": {"coordinates": {"x": my_head["x"] - 1, "y": my_head["y"]},
                                      "space": 0, "possible_head_on_collision": False},
                             "right": {"coordinates": {"x": my_head["x"] + 1, "y": my_head["y"]},
                                       "space": 0, "possible_head_on_collision": False},
                             "up": {"coordinates": {"x": my_head["x"], "y": my_head["y"] + 1},
                                    "space": 0, "possible_head_on_collision": False},
                             "down": {"coordinates": {"x": my_head["x"], "y": my_head["y"] - 1},
                                      "space": 0, "possible_head_on_collision": False}
                             }
    all_snakes = game_state["board"]["snakes"]
    enemy_snakes = [x for x in all_snakes if x["id"] != game_state["you"]["id"]]
    my_length = game_state["you"]["length"]
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    print(move_coordinates_dict)
    move_coordinates_dict = eliminate_backwards_move(move_coordinates_dict, my_body[1])
    print(move_coordinates_dict)
    move_coordinates_dict = eliminate_out_of_bounds_moves(move_coordinates_dict, board_height, board_width)
    print(move_coordinates_dict)
    move_coordinates_dict = eliminate_self_collision_moves(move_coordinates_dict, my_body)
    print(move_coordinates_dict)
    move_coordinates_dict = eliminate_enemy_collision_moves(move_coordinates_dict, my_length, enemy_snakes)
    print(move_coordinates_dict)
    next_move = choose_next_move(move_coordinates_dict, my_head, game_state["board"]["food"], board_width, board_height, all_snakes)
    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({
        "info": info,
        "start": start,
        "move": move,
        "end": end
    })
