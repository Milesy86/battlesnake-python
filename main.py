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
        if (move_coordinates_dict[direction]["x"] < 0
                or move_coordinates_dict[direction]["x"] == board_width
                or move_coordinates_dict[direction]["y"] < 0
                or move_coordinates_dict[direction]["y"] == board_height):
            del move_coordinates_dict[direction]


def eliminate_backwards_move(move_coordinates_dict, my_neck):
    # Find and remove the move that would be backwards
    for direction in list(move_coordinates_dict.keys()):
        if move_coordinates_dict[direction] == my_neck:
            del move_coordinates_dict[direction]
            break


def eliminate_self_collision_moves(move_coordinates_dict, my_body):
    # Find and remove any moves that would collide with self
    for direction in list(move_coordinates_dict.keys()):
        if move_coordinates_dict[direction] in my_body:
            del move_coordinates_dict[direction]


def eliminate_enemy_collision_moves(move_coordinates_dict, my_length, enemy_snakes):
    # Find and remove any moves that would collide with enemy snakes
    for direction in list(move_coordinates_dict.keys()):
        for enemy_snake in enemy_snakes:
            # First check if you're going to hit the enemy snake as it exists now
            if move_coordinates_dict[direction] in enemy_snake["body"]:
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
            if (move_coordinates_dict[direction] in possible_head_on_collision_coordinates
                    and enemy_snake["length"] >= my_length):
                del move_coordinates_dict[direction]
                break


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


def choose_next_move(move_coordinates_dict, my_head, food_coordinates):
    # If there's only one safe move, do it.
    if len(move_coordinates_dict) == 1:
        return list(move_coordinates_dict.keys())[0]
    # If there are no safe moves it doesn't matter which way we go so just move down.
    if len(move_coordinates_dict) == 0:
        print("No safe moves detected! Moving down")
        return "down"
    # If there are multiple safe moves, take one that moves us closer to the closest food
    food_distance_list = identify_closest_food(my_head, food_coordinates)
    for food in food_distance_list:
        for direction in list(move_coordinates_dict.keys()):
            if calculate_distance_between(food["location"], move_coordinates_dict[direction]) < food["distance"]:
                return direction
    # If we're not going to get closer to that food, just move in a random direction.
    return random.choice(list(move_coordinates_dict.keys()))


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    my_body = game_state["you"]["body"]  # Coordinates of my whole snake
    my_head = game_state["you"]["head"]  # Coordinates of my snake's head
    move_coordinates_dict = {"left": {"x": my_head["x"] - 1, "y": my_head["y"]},
                             "right": {"x": my_head["x"] + 1, "y": my_head["y"]},
                             "up": {"x": my_head["x"], "y": my_head["y"] + 1},
                             "down": {"x": my_head["x"], "y": my_head["y"] - 1}
                             }
    enemy_snakes = [x for x in game_state["board"]["snakes"] if x["id"] != game_state["you"]["id"]]
    my_length = game_state["you"]["length"]
    eliminate_backwards_move(move_coordinates_dict, my_body[1])
    eliminate_out_of_bounds_moves(move_coordinates_dict, game_state['board']['height'], game_state['board']['width'])
    eliminate_self_collision_moves(move_coordinates_dict, my_body)
    eliminate_enemy_collision_moves(move_coordinates_dict, my_length, enemy_snakes)
    next_move = choose_next_move(move_coordinates_dict, my_head, game_state["board"]["food"])

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
