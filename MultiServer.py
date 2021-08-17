from discord import file
import FileContents

import discord

import os
import pathlib
import json


def setup_new_server(bot, guild):
    print("setting up")
    create_server_folder(bot, guild)

def create_server_folder(bot, guild):
    guild_folder_path = f"ServerSpecific/{guild.id}"
    path = pathlib.Path(guild_folder_path)
    path.mkdir(parents=True, exist_ok=True)


    config_path = path / "Config"
    logs_path = path / "Logs"
    storage_path = path / "Storage"

    config_path.mkdir(parents=True, exist_ok=True)
    logs_path.mkdir(parents=True, exist_ok=True)
    storage_path.mkdir(parents=True, exist_ok=True)

    # config
    bad_words_map = config_path / "BadWordsMap.txt"
    bad_words_regex = config_path / "BadWordsRegex.txt"
    help = config_path / "Help.txt"
    poll_emojis = config_path / "PollEmojis.txt"
    random_message = config_path / "RandomMessage.txt"
    stories = config_path / "Stories.txt"
    tutorials = config_path / "Tutorials.txt"

    with open(bad_words_map, 'w'): pass
    with open(bad_words_regex, 'w'): pass
    with open(help, 'w'): pass
    with open(poll_emojis, 'w'): pass
    with open(random_message, 'w'): pass
    with open(stories, 'w'): pass
    with open(tutorials, 'w'): pass

    # logs
    errors = logs_path / "Errors.txt"
    server_boosters = logs_path / "ServerBoosters.txt"
    server_members = logs_path / "ServerMembers.txt"

    with open(errors, 'w'): pass
    with open(server_boosters, 'w'): pass
    with open(server_members, 'w'): pass

    # storage
    permanent_reaction_actions = storage_path / "PermanentReactionActions.txt"
    polls_log = storage_path / "PollsLog.txt"
    saved_roles = storage_path / "SavedRoles.txt"
    server_config = storage_path / "ServerConfig.txt"
    timed_actions = storage_path / "TimedActions.txt"
    tutorials_log = storage_path / "TutorialsLog.txt"

    with open(permanent_reaction_actions, 'w'): pass
    with open(polls_log, 'w'): pass
    with open(saved_roles, 'w'): pass
    with open(server_config, 'w'): pass
    with open(timed_actions, 'w'): pass
    with open(tutorials_log, 'w'): pass


    populate_server_config(server_config)

def populate_server_config(config_path):
    server_config = {
        "modlog": None,
        "status": None,
        "swear_filter_enabled": False
    }

    output_json = json.dumps(server_config, indent=4)
    with open(config_path, 'w') as file:
        file.write(output_json)



