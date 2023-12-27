import discord
from discord.ext import commands
import json

with open("config/config.json", "r") as file:
    config = json.load(file)
    token = config["token"]
    log_channel = config["logChannel"]
    log_channel = int(log_channel)
    owner_ids = config["ownerIds"]
    owner_ids = [int(i) for i in owner_ids]


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(
            f"\n----------------------------\nLogged on as {self.user}!\n----------------------------\n"
        )
        print(f"Send !help to {self.user} for a list of commands")

    async def on_message(self, message):
        # check if the message is from the bot
        if message.author == self.user:
            return
        if message.content.startswith("!listen"):
            # check if the message is from the owner
            if message.author.id not in owner_ids:
                return
            m = message.content.split(" ")
            m1 = m[1].split(">")
            id1 = m1[0]
            id2 = m1[1]

            get_channel = self.get_channel(int(id1))
            post_channel = self.get_channel(int(id2))

            with open("sources.json", "r") as file:
                data = json.load(file)

            data["listen"].append({"getChannel": id1, "postChannel": id2})

            with open("sources.json", "w") as file:
                json.dump(data, file)

            await post_channel.send(f"Listening to {get_channel}")

        elif message.content == "!ping":
            # check if the message is from the owner
            if message.author.id not in owner_ids:
                return
            await message.channel.send("Pong!")

        elif message.content == "!clearall":
            if message.author.id not in owner_ids:
                return
            # This command will remove all mirrored channel pairs
            # Remove the "listen" key from the JSON file
            with open("sources.json", "r") as file:
                data = json.load(file)

            data["listen"] = []

            with open("sources.json", "w") as file:
                json.dump(data, file)

            # Send a confirmation message to the log channel
            await self.get_channel(log_channel).send(
                "All mirrored channels have been cleared."
            )

        elif message.content == "!mirrors":
            if message.author.id not in owner_ids:
                return
            from tabulate import tabulate

            # this command will list all the channels that are being mirrored
            with open("sources.json", "r") as file:
                data = json.load(file)
            get_channels = []
            post_channels = []
            table_data = []
            for entry in data["listen"]:
                get_channel_id = entry["getChannel"]
                post_channel_id = entry["postChannel"]

                get_channels.append(get_channel_id)
                post_channels.append(post_channel_id)

            for i in range(len(get_channels)):
                # send the message to the log channel
                # send the channel names
                get_channel = self.get_channel(int(get_channels[i]))
                post_channel = self.get_channel(int(post_channels[i]))
                table_data.append(
                    [
                        f"{get_channel}",
                        f"{post_channel}",
                        f"({get_channels[i]} -> {post_channels[i]})",
                    ]
                )
            table = tabulate(
                table_data,
                headers=["getChannel", "postChannel", "IDs"],
                tablefmt="fancy_grid",
            )
            for i in table.split("\n"):
                await self.get_channel(log_channel).send(i)

        elif message.content == "!help":
            if message.author.id not in owner_ids:
                return
            help_text = """
List of commands:
- `!listen <get_channel_id> > <post_channel_id>`: Start mirroring messages from one channel to another.
- `!clear <get_channel_id> > <post_channel_id>`: Stop mirroring messages between specific channels.
- `!clearall`: Stop mirroring all channels.
- `!mirrors`: List all mirrored channels.
- `!ping`: Returns Pong! (test command)
- `!members`: Saves a list of all members in the CSV file
- `!help`: Displays this message
            """
            await message.channel.send(help_text)

        elif message.content.startswith("!clear"):
            # This command will remove a mirrored channel pair
            # Example: !clear 701175071884050482>712345678901234567
            m = message.content.split(" ")
            if len(m) == 2:
                channel_pair = m[1].split(">")
                if len(channel_pair) == 2:
                    get_channel_id = channel_pair[0]
                    post_channel_id = channel_pair[1]

                    # Remove the channel pair from the JSON file
                    with open("sources.json", "r") as file:
                        data = json.load(file)

                    updated_listen = [
                        entry
                        for entry in data["listen"]
                        if entry["getChannel"] != get_channel_id
                        or entry["postChannel"] != post_channel_id
                    ]
                    data["listen"] = updated_listen

                    with open("sources.json", "w") as file:
                        json.dump(data, file)

                    # Send a confirmation message to the log channel
                    get_channel = self.get_channel(int(get_channel_id))
                    post_channel = self.get_channel(int(post_channel_id))
                    await self.get_channel(log_channel).send(
                        f"Channels {get_channel} -> {post_channel} removed from mirroring."
                    )

                else:
                    await message.channel.send(
                        "Invalid command format. Example: `!clear 701175071884050482>712345678901234567`"
                    )
            else:
                await message.channel.send(
                    "Invalid command format. Example: `!clear 701175071884050482>712345678901234567`"
                )

        # Read messages from getChannels and send them to postChannels
        with open("sources.json", "r") as file:
            data = json.load(file)

        get_channels = []
        post_channels = []

        for entry in data["listen"]:
            get_channel_id = entry["getChannel"]
            post_channel_id = entry["postChannel"]

            get_channels.append(get_channel_id)
            post_channels.append(post_channel_id)

            # Save the updated data to sources.json
            with open("sources.json", "w") as file:
                json.dump(data, file)

        if str(message.channel.id) in get_channels:
            print("Message sent in a getChannel")
            index = get_channels.index(str(message.channel.id))
            post_channel = self.get_channel(int(post_channels[index]))
            await post_channel.send(message.content)
        elif str(message.channel.id) in post_channels:
            pass
        else:
            pass


client = MyClient()
client.run(token)


# Change the values in config.json to your own values
# Run the selfbot with python bot.py
