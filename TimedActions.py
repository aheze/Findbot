
import FileContents
import Moderation

import asyncio
from datetime import datetime, timedelta

TIME_FORMATTING = "%m.%d.%Y.%H.%M.%S"

# remove
def remove_timed_actions(keywords):
    new_file_contents = []
    with open('ServerShared/TimedActions.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)
        
        for line in file_contents:
            components = line.strip().split(":") # 0 is time, 1 is action
            if not any(word in components[1] for word in keywords):
                new_file_contents.append(line)

    with open('ServerShared/TimedActions.txt', 'w') as file:
        combined = FileContents.combine_file_contents(new_file_contents)
        file.write(combined)

def save_timed_action(time, action):
    delay_time_string = convert_date_to_string(time)
    with open('ServerShared/TimedActions.txt', 'a') as file:
        string = f"{delay_time_string}:{action}\n"
        file.write(string)

def convert_string_to_date(date_string):
    date = datetime.strptime(date_string, TIME_FORMATTING)
    return date

def convert_date_to_string(date):
    string = date.strftime(TIME_FORMATTING)
    return string
    
async def check_timed_actions(bot):
    while True:
        new_file_contents = []
        with open('ServerShared/TimedActions.txt', 'r') as file:
            file_contents = FileContents.get_file_contents(file)
            
            for line in file_contents:
                components = line.strip().split(":") # 0 is time, 1 is action
                time = convert_string_to_date(components[0])
                if datetime.now() > time: # execute action, delete line
                    action_string = components[1]
                    action_split = action_string.split(".")
                    server_id = int(action_split[1].strip())
                    user_id = int(action_split[2].strip())

                    if "unmute." in action_string:
                        server = bot.get_guild(server_id)
                        member = server.get_member(user_id)
                        await Moderation.general_unmute(bot, server, None, bot.user, member, ["Unmuted by Findbot"])
                else:
                    new_file_contents.append(line)
        with open('ServerShared/TimedActions.txt', 'w') as file:
            combined = FileContents.combine_file_contents(new_file_contents)
            file.write(combined)

        await asyncio.sleep(5)