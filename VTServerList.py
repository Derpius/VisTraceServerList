import os
from datetime import datetime
from dotenv import load_dotenv

import asyncio
import discord

from sourceserver.sourceserver import SourceServer
from sourceserver.exceptions import SourceError

load_dotenv()

TOKEN = os.getenv("VTSERVERLIST_TOKEN")
if TOKEN is None:
	print("VTSERVERLIST_TOKEN is not set")
	exit(-1)

CHANNEL = os.getenv("VTSERVERLIST_CHANNEL_ID")
if CHANNEL is None:
	print("VTSERVERLIST_CHANNEL_ID is not set")
	exit(-1)
try:
	CHANNEL = int(CHANNEL)
except ValueError:
	print("VTSERVERLIST_CHANNEL_ID is not a number")
	exit(-1)

RATE = os.getenv("VTSERVERLIST_UPDATE_RATE")
if RATE is None:
	print("VTSERVERLIST_UPDATE_RATE is not set")
	exit(-1)
try:
	RATE = float(RATE)
except ValueError:
	print("VTSERVERLIST_UPDATE_RATE is not a number")
	exit(-1)

SERVERS = []
with open(os.path.join(os.path.dirname(__file__), "servers.cfg"), "r") as f:
	SERVERS = [line for line in f if len(line) > 0]

intents = discord.Intents.default()

client = discord.Client(intents=intents)

async def updateServers():
	while True:
		try:
			channel = await client.fetch_channel(CHANNEL)
		except:
			print("Error getting channel")
			break
		else:
			toEdit = None
			async for message in channel.history(limit=20, oldest_first=False):
				if message.author == client.user:
					toEdit = message
					break
			else:
				toEdit = await channel.send(content="")

			embed = discord.Embed(
				colour=discord.Colour.from_rgb(255, 150, 0),
				title="Servers running VisTrace"
			)
			embed.set_footer(text=f"Last updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

			for server in SERVERS:
				try:
					serverCon = SourceServer(server)
					info = serverCon.info
					players = serverCon.getPlayers()
					rules = serverCon.rules
				except SourceError as e:
					embed.add_field(name=f"Failed to connect to {server}", value=e.message, inline=False)
				else:
					locale = None
					for keyword in info["keywords"].split(" "):
						kv = keyword.split(":")
						if kv[0] == "loc":
							locale = kv[1]
							break
					flag = ":no_entry_sign:" if locale is None else f":flag_{locale}:"

					version = "older than v0.12"
					if "vistrace_version" in rules:
						version = f"v{rules['vistrace_version']}"

					embed.add_field(
						name=f"{flag} {info['name']}",
						value=f"{players[0]}/{info['max_players']} Playing {info['game']} on {info['map']} | VisTrace {version}",
						inline=False
					)

			await toEdit.edit(content="", embed=embed)

		await asyncio.sleep(RATE * 60)

async def setup():
	client.loop.create_task(updateServers())
client.setup_hook = setup

client.run(TOKEN)
