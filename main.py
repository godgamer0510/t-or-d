import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import os
from dotenv import load_dotenv

# Load environment variables (for local testing)
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class BubbleGame(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.current_size = 0
        self.pop_limit = random.randint(10, 50)
        self.user_stats = {} 

    @discord.ui.button(label="Poke the Bubble 🫧", style=discord.ButtonStyle.primary, custom_id="poke_button")
    async def poke_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        # 1. Update the user's click count
        if user.mention not in self.user_stats:
            self.user_stats[user.mention] = 0
        self.user_stats[user.mention] += 1
        
        # 2. Increase bubble size
        self.current_size += 1

        # 3. Check if the bubble pops
        if self.current_size >= self.pop_limit:
            # --- GAME OVER LOGIC ---
            button.disabled = True
            button.label = "💥 POPPED!"
            button.style = discord.ButtonStyle.danger
            
            result_text = f"## 💥 POP! \n{user.mention} popped the bubble after **{self.current_size}** pokes!\n\n**Leaderboard:**\n"
            
            sorted_stats = sorted(self.user_stats.items(), key=lambda item: item[1], reverse=True)
            for u, count in sorted_stats:
                result_text += f"• {u}: {count} pokes\n"

            await interaction.response.edit_message(content=result_text, view=self)
            self.stop()
            
        else:
            # --- GAME CONTINUE LOGIC ---
            
            # Calculate how dangerous the bubble looks
            percent = self.current_size / self.pop_limit
            status = "The bubble is growing..."
            if percent > 0.75:
                status = "The bubble is shaking violently! 😰"
            elif percent > 0.5:
                status = "The bubble is getting really big... 😳"

            # UPDATED MESSAGE: Now includes "Last Poke: {user.mention}"
            await interaction.response.edit_message(
                content=f"{status}\nLast Poke: {user.mention}\nCurrent Pokes: **{self.current_size}**", 
                view=self
            )

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def make(ctx):
    view = BubbleGame()
    await ctx.send("A wild bubble appeared! 🫧 \nKeep poking it until it pops!", view=view)

# Get the token from the environment variable
token = os.getenv('DISCORD_TOKEN')

if not token:
    print("Error: DISCORD_TOKEN not found in environment variables.")
else:
    bot.run(token)
