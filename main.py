import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
# REPLACE THIS NUMBER WITH THE DISCORD ID OF THE PERSON YOU WANT TO WIN
TARGET_ID = 1169622309854793730
# ---------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variable to track if rigging is active
luna_mode_active = False

class BubbleGame(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.current_size = 0
        self.pop_limit = random.randint(10, 50)
        self.user_stats = {} 

    @discord.ui.button(label="Poke the Bubble 🫧", style=discord.ButtonStyle.primary, custom_id="poke_button")
    async def poke_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        # 1. Update User Stats (Actual Clicks)
        if user.mention not in self.user_stats:
            self.user_stats[user.mention] = 0
        self.user_stats[user.mention] += 1
        
        # 2. Increment Bubble Size
        self.current_size += 1

        # --- RIGGING LOGIC START ---
        if luna_mode_active:
            # THE BOOST: If it's the target user, give them a chance to insta-win
            if user.id == TARGET_ID:
                # 30% chance to force the pop immediately (if size > 3)
                if self.current_size > 3 and random.random() < 0.30:
                    # FIX: Instead of inflating current_size, we lower the limit to meet the current size.
                    # This ensures the Leaderboard sum equals the Total Pokes.
                    self.pop_limit = self.current_size 

            # THE SABOTAGE: If it's NOT the target, don't let them win
            elif user.id != TARGET_ID:
                # If this click WOULD have popped it...
                if self.current_size >= self.pop_limit:
                    # Secretly increase the limit so they don't win yet
                    self.pop_limit += random.randint(1, 5)
        # --- RIGGING LOGIC END ---

        # 3. Check for Pop
        if self.current_size >= self.pop_limit:
            button.disabled = True
            button.label = "💥 POPPED!"
            button.style = discord.ButtonStyle.danger
            
            result_text = f"## 💥 POP! \n{user.mention} popped the bubble after **{self.current_size}** pokes!\n\n**Leaderboard:**\n"
            
            # Sort leaderboard
            sorted_stats = sorted(self.user_stats.items(), key=lambda item: item[1], reverse=True)
            for u, count in sorted_stats:
                result_text += f"• {u}: {count} pokes\n"

            await interaction.response.edit_message(content=result_text, view=self)
            self.stop()
        else:
            # 4. Game Continues (Update Status)
            percent = self.current_size / self.pop_limit
            status = "The bubble is growing..."
            if percent > 0.75:
                status = "The bubble is shaking violently! 😰"
            elif percent > 0.5:
                status = "The bubble is getting really big... 😳"
            
            # Added "Last poked by" feature here
            await interaction.response.edit_message(
                content=f"{status}\nCurrent Pokes: **{self.current_size}**\nLast poked by: {user.mention}", 
                view=self
            )

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def make(ctx):
    view = BubbleGame()
    await ctx.send("A wild bubble appeared! 🫧 \nKeep poking it until it pops!", view=view)

@bot.command()
async def luna(ctx):
    global luna_mode_active
    luna_mode_active = not luna_mode_active
    
    status = "ON" if luna_mode_active else "OFF"
    
    # Attempt to delete the command message for secrecy
    try:
        await ctx.message.delete()
    except:
        pass 
        
    print(f"Luna mode toggled: {status}")
    await ctx.send(f"🔮 Fate manipulation is now **{status}**.", delete_after=5)

token = os.getenv('DISCORD_TOKEN')

if not token:
    print("Error: DISCORD_TOKEN not found in environment variables.")
else:
    bot.run(token)