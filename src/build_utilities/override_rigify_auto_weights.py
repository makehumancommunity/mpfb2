#!/usr/bin/python3

import os, json

rigify_original_weights_file = "../mpfb/data/rigs/rigify/weights.human.json"
default_weights_file = "../mpfb/data/rigs/standard/weights.default.json"
game_engine_weights_file = "../mpfb/data/rigs/standard/weights.game_engine.json"
rigify_destination_file = "./rigify.json"

game_engine_table_file = "./translate_game_engine_to_rigify.csv"
default_table_file = "./translate_default_to_rigify.csv"

rigify_weights = dict()
game_engine_weights = dict()
default_weights = dict()

game_engine_table = []
default_table = []

with open(rigify_original_weights_file, "r") as json_file:
    rigify_weights = json.load(json_file)

with open(default_weights_file, "r") as json_file:
    default_weights = json.load(json_file)

with open(game_engine_weights_file, "r") as json_file:
    game_engine_weights = json.load(json_file)

with open(game_engine_table_file, "r") as table_file:
    game_engine_table = table_file.readlines()

with open(default_table_file, "r") as table_file:
    default_table = table_file.readlines()

from_weights = game_engine_weights["weights"]
to_weights = rigify_weights["weights"]

for line in game_engine_table:
    (from_name, to_name) = str(line).strip().split(";", 2)
    if from_name in from_weights and to_name in to_weights:
        to_weights[to_name] = from_weights[from_name]

from_weights = default_weights["weights"]

for line in game_engine_table:
    (from_name, to_name) = str(line).strip().split(";", 2)
    if from_name in from_weights and to_name in to_weights:
        to_weights[to_name] = from_weights[from_name]

with open(rigify_destination_file, "w") as json_file:
    json.dump(rigify_weights, json_file, indent=4, sort_keys=True)

