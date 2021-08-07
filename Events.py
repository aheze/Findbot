
import FileContents
import Utilities
import uuid
import discord

class EventInfo:
    def __init__(self, bot, name=None, description=None, who_can_vote=None, allowed_channels=None):
        self.id = str(uuid.uuid4())
        self.bot = bot
        self.name = name
        self.description = description
        self.who_can_vote = who_can_vote 
        # self.grouping_type = grouping_type 
        self.allowed_channels = allowed_channels 

    def generate_description(self):
        description = ""
        properties = [self.name, self.description, self.who_can_vote, self.allowed_channels]
        for index, property in enumerate(properties):
            if index == 0:
                string = "Name"
            elif index == 1:
                string = "Description"
            elif index == 2:
                string = "Who can vote"
            else:
                string = "Allowed channels"

            if property:
                emoji = Utilities.get_emoji(self.bot, f"{index + 1}Selected")
                line = f"{emoji} {string}\n"
            else:
                emoji = Utilities.get_emoji(self.bot, f"{index + 1}_")
                line = f"{emoji} {string}\n"
            description += line
        
        return description


    # async def save_name(keyvalue):
    #     print("save name!")
    #     print(keyvalue)
    #     keyvalue_split = keyvalue.split(":")
    #     key = keyvalue_split[0]
    #     value = keyvalue_split[1]




EVENT_NAME = "Funcing destroy the bot"
EVENT_DESCRIPTION = "Exploit <@784531493204262942>'s censoring loopholes: **get 1 point** for every should-be-censored word or false positive! Spam test words in <#864710025460187156>. Challenge ends July 15th, 11:59 PM PST."
EVENT_FOOTER = 'Be at the top to get the "Beta Tester" role!'

current_events = []
start_message = None

async def make_new_event(bot, ctx):
    global current_events
    global start_message

    new_event = EventInfo(bot)
    current_events.append(new_event)
    replied_message = await ctx.send("Join the thread to make an event!")

    description = new_event.generate_description()
    embed = discord.Embed(description=description, color=0x34c6eb)
    start_message = await ctx.send(embed=embed)
    new_thread = await ctx.channel.start_thread(name="Event Builder", message=start_message, type=discord.ChannelType.public_thread)

    Utilities.save_key_value_to_file('Output/EventsLog.txt', str(new_thread.id), f"{new_event.id},save_name")
    await new_thread.send("1. Send the event name")

async def check_reply(message):
    global current_event_infos
    if isinstance(message.channel, discord.Thread):
        thread_id = message.channel.id
        action = Utilities.read_value_from_file('Output/EventsLog.txt', str(thread_id))
        if action:
            action_split = action.split(",")
            event_id = action_split[0]
            action_name = action_split[1]

            matching_events = [event for event in current_events if event.id == event_id]
            continued_event = matching_events[0]

            if action_name == "save_name":
                continued_event.name = message.content
                await message.channel.send("2. Reply to this message with the description of the event.")
                Utilities.save_key_value_to_file('Output/EventsLog.txt', str(thread_id), f"{continued_event.id},save_desc")
            elif action_name == "save_desc":
                continued_event.description = message.content
                Utilities.save_key_value_to_file('Output/EventsLog.txt', str(thread_id), f"{continued_event.id},save_whocanvote")

                view = DropdownView(
                    guild=message.guild,
                    type="role",
                    event_id=continued_event.id
                )
                await message.channel.send('3. Who can vote?', view=view)

class NamedOption:
    def __init__(self, name=None):
        self.name = name
class RoleDropdown(discord.ui.Select):
    def __init__(self, guild, event_id):
        global current_events

        self.event_id = event_id
        roles = guild.roles
        roles.append(NamedOption("You"))
        roles.append(NamedOption("Server Owner"))

        options = []
        count = 0
        for index, role in enumerate(reversed(roles)):
            if index == 24:
                break
            count += 1

            option = discord.SelectOption(label=role.name)
            if role.name == "@everyone":
                option = discord.SelectOption(label=role.name, description='Everyone will be able to vote', emoji='🟨')
            elif role.name == "You":
                option = discord.SelectOption(label=role.name, description='You (the event creator) can vote', emoji='🟩')
            elif role.name == "Server Owner":
                option = discord.SelectOption(label=role.name, description='The server owner can vote', emoji='🟦')
            options.append(option)
        
        super().__init__(placeholder='Select roles', min_values=1, max_values=count, options=options)

    async def callback(self, interaction: discord.Interaction):
        global current_events
        matching_events = [event for event in current_events if event.id == self.event_id]
        continued_event = matching_events[0]
        continued_event.who_can_vote = ",".join(self.values)
        view = DropdownView(
            guild=interaction.guild,
            type="channel",
            event_id=continued_event.id
        )
        await interaction.response.send_message("4. Which channels?", view=view)



class ChannelDropdown(discord.ui.Select):
    def __init__(self, guild, event_id):
        self.event_id = event_id

        channels = guild.text_channels
        channels.insert(0, NamedOption("Serverwide"))

        options = []
        count = 0
        for index, channel in enumerate(channels):
            if index == 24:
                break
            count += 1

            option = discord.SelectOption(label=channel.name)
            if channel.name == "Serverwide":
                option = discord.SelectOption(label="Serverwide", description='Event is hosted in all channels', emoji='🟪')
            options.append(option)
        
        super().__init__(placeholder='Select roles', min_values=1, max_values=count, options=options)

    async def callback(self, interaction: discord.Interaction):
        global current_events
        matching_events = [event for event in current_events if event.id == self.event_id]
        continued_event = matching_events[0]
        continued_event.allowed_channels = ",".join(self.values)
        await interaction.response.send_message(f'Selected channels: {self.values}')

class DropdownView(discord.ui.View):
    def __init__(self, guild, type, event_id):
        super().__init__()
        if type == "role":
            self.add_item(RoleDropdown(guild, event_id))
        else:
            self.add_item(ChannelDropdown(guild, event_id))




async def send_leaderboard(bot, ctx, ping = None):
    with open("Output/Events.txt", 'r') as file:
        leaderboard = []
        file_contents = FileContents.get_file_contents(file)
        for line in file_contents:
            line_split = line.split(":")
            user_id = int(line_split[0])
            user = bot.get_user(user_id)
            number = int(line_split[1])

            tuple = (user, number)
            leaderboard.append(tuple)

        leaderboard.sort(key=lambda tup: tup[1], reverse=True)  # sorts in place

        leaderboard_description = ""
        for (index, tuple) in enumerate(leaderboard):
            user = tuple[0]
            points = tuple[1]

            starting_trophy = ""
            if index == 0:
                starting_trophy = Utilities.get_emoji(bot, "First")
            elif index == 1:
                starting_trophy = Utilities.get_emoji(bot, "Second")
            elif index == 2:
                starting_trophy = Utilities.get_emoji(bot, "Third")
            else:
                starting_trophy = Utilities.get_emoji(bot, "NotSelected")

            new_line = ""
            if points == 1:
                new_line += f"{starting_trophy} {points} point: "
            else:
                new_line += f"{starting_trophy} {points} points: "

            if ping:
                new_line += f"{user.mention}\n"
            else:
                new_line += f"**{user.name}**\n"

            leaderboard_description += new_line

        description_start = EVENT_DESCRIPTION
        description = f"{description_start}\n\n{leaderboard_description}"

        channel = ctx.channel
        embed = discord.Embed(title=f'Leaderboard for the "{EVENT_NAME}" event!', description=description, color=0xebc334)
        embed.set_footer(text=EVENT_FOOTER)

        await channel.send(embed=embed)
