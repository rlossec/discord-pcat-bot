import discord


class DiscordBot:
    def __init__(self, token: str, guild_id: int, intents: discord.Intents.default(), **kwargs):
        self.token = token
        self.guild_id = guild_id
        self.config = kwargs
        self.intents = intents

    def initialize_client(self):
        self.client = discord.Client(intents=self.intents)

        # Attacher les événements
        @self.client.event
        async def on_ready():
            await self.on_ready()

        @self.client.event
        async def on_message(message):
            await self.on_message(message)

    def run(self):
        if self.client is None:
            raise RuntimeError("Client is not initialized.")
        self.client.run(self.token)

    async def on_ready(self):
        guild = self.client.get_guild(self.guild_id)
        if guild is None:
            raise ValueError(f"Guild with ID {self.guild_id} not found")
        print(f'Successfully connected to guild: {guild.name}')

    async def on_message(self, message):
        if message.author == self.client.user:
            return
        
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')





