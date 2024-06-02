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


def is_growing(snake):
    return snake["body"][-1] == snake["body"][-2]


def is_me(snake, me):
    return snake["id"] == me["id"]


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


def eliminate_snake_collision_moves(move_coordinates_dict, snake):
    # Find and remove any moves that would collide with a snake
    # Account for the fact that the tail space will be vacated if the snake isn't growing
    for direction in list(move_coordinates_dict.keys()):
        if move_coordinates_dict[direction]["coordinates"] in get_snake_body_next_turn(snake):
            del move_coordinates_dict[direction]
    return move_coordinates_dict


def get_snake_body_next_turn(snake):
    snake_body = snake["body"][:-1]
    if is_growing(snake):
        snake_body.append(snake["body"][-1])
    # print(snake_body)
    return snake_body


def evaluate_head_on_collisions(move_coordinates_dict, snake, me):
    snake_head = snake["head"]
    my_length = me["length"]
    possible_head_on_collision_coordinates = [
        {"x": snake_head["x"] + 1, "y": snake_head["y"]},
        {"x": snake_head["x"] - 1, "y": snake_head["y"]},
        {"x": snake_head["x"], "y": snake_head["y"] + 1},
        {"x": snake_head["x"], "y": snake_head["y"] - 1},
    ]
    # Mark any possible head-on collisions according to their type.
    # The type depends on the relative lengths of the snakes involved.
    for direction in move_coordinates_dict:
        if move_coordinates_dict[direction]["coordinates"] in possible_head_on_collision_coordinates:
            if snake["length"] < my_length:
                move_coordinates_dict[direction]["collision_type"] = "winning"
            elif snake["length"] == my_length:
                move_coordinates_dict[direction]["collision_type"] = "equal"
            else:
                move_coordinates_dict[direction]["collision_type"] = "losing"
    return move_coordinates_dict


def eliminate_collision_moves(move_coordinates_dict, snakes, me):
    # Find and remove any moves that would collide with snakes (including myself)
    for snake in snakes:
        move_coordinates_dict = eliminate_snake_collision_moves(move_coordinates_dict, snake)
    # Also evaluate moves that might be head on collisions
    for snake in [x for x in snakes if not is_me(x, me)]:
        move_coordinates_dict = evaluate_head_on_collisions(move_coordinates_dict, snake, me)
    return move_coordinates_dict


def create_map(width, height, snakes):
    # Create a map of the playing field. 0s represent empty space and 1s represent spaces containing snakes.
    board_row = [0] * width
    board_map = []
    for i in range(height):
        board_map.append(board_row[:])
    for snake in snakes:
        for coordinate in get_snake_body_next_turn(snake):
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


def pick_random_move(move_list):
    return random.choice(move_list)


def pick_only_move(move_coordinates_dict):
    # If there's only one move available, do it.
    if len(move_coordinates_dict) == 1:
        return list(move_coordinates_dict.keys())[0]
    else:
        return None


def eliminate_enclosed_space_moves(move_coordinates_dict, board_width, board_height, all_snakes):
    check_for_enclosed_spaces(move_coordinates_dict, board_width, board_height, all_snakes)
    max_space = max([x["space"] for x in move_coordinates_dict.values()])
    move_coordinates_dict = {k: v for k, v in move_coordinates_dict.items() if v["space"] == max_space}
    return move_coordinates_dict


def pick_winning_collision_move(move_coordinates_dict, board_width, board_height, all_snakes):
    # print(move_coordinates_dict)
    winning_collisions_dict = {k: v for k, v in move_coordinates_dict.items() if v["collision_type"] == "winning"}
    # print(winning_collisions_dict)
    if len(winning_collisions_dict) == 0:
        return None
    winning_collisions_dict = eliminate_enclosed_space_moves(winning_collisions_dict, board_width, board_height, all_snakes)
    return pick_random_move(list(winning_collisions_dict.keys()))


def choose_next_move(move_coordinates_dict, my_head, food_coordinates, board_width, board_height, all_snakes):
    # If there are no safe moves it doesn't matter which way we go so just move down.
    if len(move_coordinates_dict) == 0:
        print("No safe moves detected! Moving down")
        return "down"
    # If there's only one move available do that
    prospective_move = pick_only_move(move_coordinates_dict)
    if prospective_move:
        return prospective_move
    # Take winning head-on collision moves if there are any
    prospective_move = pick_winning_collision_move(move_coordinates_dict, board_width, board_height, all_snakes)
    if prospective_move:
        return prospective_move
    # Don't get trapped in a dead end
    move_coordinates_dict = eliminate_enclosed_space_moves(move_coordinates_dict, board_width, board_height,
                                                             all_snakes)
    # Of the remaining safe moves, first consider any that can't result in head-on collision
    non_collision_moves_list = [x for x in list(move_coordinates_dict.keys()) if
                                not (move_coordinates_dict[x]["collision_type"] == "losing" or move_coordinates_dict[x]["collision_type"] == "equal")]
    collision_moves_list = [x for x in list(move_coordinates_dict.keys()) if
                                move_coordinates_dict[x]["collision_type"]]
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
    print(game_state)
    my_body = game_state["you"]["body"]  # Coordinates of my whole snake
    my_head = game_state["you"]["head"]  # Coordinates of my snake's head
    move_coordinates_dict = {"left": {"coordinates": {"x": my_head["x"] - 1, "y": my_head["y"]},
                                      "space": 0, "collision_type": None},
                             "right": {"coordinates": {"x": my_head["x"] + 1, "y": my_head["y"]},
                                       "space": 0, "collision_type": None},
                             "up": {"coordinates": {"x": my_head["x"], "y": my_head["y"] + 1},
                                    "space": 0, "collision_type": None},
                             "down": {"coordinates": {"x": my_head["x"], "y": my_head["y"] - 1},
                                      "space": 0, "collision_type": None}
                             }
    all_snakes = game_state["board"]["snakes"]
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    # print(move_coordinates_dict)
    move_coordinates_dict = eliminate_backwards_move(move_coordinates_dict, my_body[1])
    # print(move_coordinates_dict)
    move_coordinates_dict = eliminate_out_of_bounds_moves(move_coordinates_dict, board_height, board_width)
    # print(move_coordinates_dict)
    move_coordinates_dict = eliminate_collision_moves(move_coordinates_dict, all_snakes, game_state["you"])
    # print(move_coordinates_dict)
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
