import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
# Enter the 3 User IDs you want to choose between.
# You can switch between them using !luna 1, !luna 2, etc.
VIP_LIST = {
    1: 1169622309854793730,  # Person 1 ID
    2: 916106297190019102,   # Person 2 ID
    3: 804009443088007189    # Person 3 ID
}
# ---------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables
luna_mode_active = False
current_target_id = VIP_LIST[1] # Default to the first person

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
        # We access the global 'current_target_id' here so you can switch targets mid-game
        if luna_mode_active:
            # THE BOOST: If it's the CHOSEN target, give them a chance to insta-win
            if user.id == current_target_id:
                # 30% chance to force the pop immediately (if size > 3)
                if self.current_size > 3 and random.random() < 0.30:
                    self.pop_limit = self.current_size 

            # THE SABOTAGE: If it's NOT the target, don't let them win
            elif user.id != current_target_id:
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
            
            sorted_stats = sorted(self.user_stats.items(), key=lambda item: item[1], reverse=True)
            for u, count in sorted_stats:
                result_text += f"• {u}: {count} pokes\n"

            await interaction.response.edit_message(content=result_text, view=self)
            self.stop()
        else:
            # 4. Game Continues
            percent = self.current_size / self.pop_limit
            status = "The bubble is growing..."
            if percent > 0.75:
                status = "The bubble is shaking violently! 😰"
            elif percent > 0.5:
                status = "The bubble is getting really big... 😳"
            
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
async def luna(ctx, choice: int = 0):
    global luna_mode_active, current_target_id
    
    # Attempt to delete the command message for secrecy
    try:
        await ctx.message.delete()
    except:
        pass 

    message = ""

    # If the user typed a number (1, 2, or 3)
    if choice in VIP_LIST:
        current_target_id = VIP_LIST[choice]
        luna_mode_active = True # Auto-enable when a target is picked
        message = f"🔮 Target locked on **Person #{choice}**. Fate manipulation **ON**."
    
    # If no number provided (or invalid number), just toggle ON/OFF
    else:
        luna_mode_active = not luna_mode_active
        status = "ON" if luna_mode_active else "OFF"
        message = f"🔮 Fate manipulation is now **{status}**."

    print(f"Luna Command: Active={luna_mode_active}, TargetID={current_target_id}")
    await ctx.send(message, delete_after=5)

token = os.getenv('DISCORD_TOKEN')

if not token:
    print("Error: DISCORD_TOKEN not found in environment variables.")
else:
    bot.run(token)