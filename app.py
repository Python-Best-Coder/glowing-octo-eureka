import discord
from discord.ext import commands
import asyncio
import random
import re
import os
import sentence
# Load the bot token from an environment variable
TOKEN = 'no'

data = {}

hangman = False
the_chosen = ''  # This will store the ID of the chosen user

# Set up the bot
intents = discord.Intents.default()  # Initialize intents
intents.message_content = True       # Enable the intent to read message content

bot = commands.Bot(command_prefix='!', intents=intents)

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Connected to {len(bot.guilds)} servers.')

# Command to respond with "Hello!"
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('Hello!')


@bot.command(name='execute')
async def execute(ctx, *, user_input: str):
    variables = {}

    async def say(text):
        await ctx.send(text)
    modified_input = user_input.strip()
    
    # Remove code block delimiters
    if modified_input.startswith('```') and modified_input.endswith('```'):
        modified_input = modified_input[3:-3]
    
    # Split input into lines
    modified_input = modified_input.split('~')

    # Process each line
    for line in modified_input:
        # Search for print command
        printing = re.search(r'cmd\[say\] => \[(.+)\]', line)
        # Search for assignment command
        assign = re.search(r'cmd\[store\] => \{(.+),(.+)\}', line)
        # Search for operation command
        change = re.search(r'cmd\[operate\] @> \((\+=|-=)\)\{(.+)\}', line)

        sleep = re.search(r'cmd\[time\]^\(sleep\) => \{(.+)\}',line)
        # Search for debug command
        debug = re.search(r'cmd\[debuginfo\]--', line)

        helpzone = re.search(r'cmd\[\.\] => help', line)

        listmake = re.search(r'cmd\[list =>\]\{(.+)\} ',line)

        append = re.search(r'cmd\[append{(.+)=>{(.+)}}\]',line)

        if helpzone:
            await say('HELP:')
            await say('cmd[say] => [<text>] - prints a variable, or a piece of text.')
            await say('cmd[store] => {<variable_name>,<variable_value>} - assigns a variable.')
            await say('cmd[say] => [<text>] - prints a variable, or a piece of text.')
            await say('cmd[operate] @> (<+= or -=){<variable_name>} - adds or subtracts 1 from an assigned value.')
            await say('cmd[time]^(sleep) => {<int>} - sleeps for a number of seconds (i recommend using thing after operate before printing.)')
            await say('cmd[debuginfo]-- - gives you debug info like the variables so i dont have to keep on putting print(variables)')
            await say('cmd[list =>]{<variable_name>} - creates a new, empty list.')
            await say('cmd[append{<anything>}=>{<var_name}] - appends to a list.')

        if append:
            var_name = append.group(2)
            if isinstance(variables[var_name],list):
                variables[var_name].append(append.group(1))
            else:
                await say('Please use this command on a list!')
        if listmake:
            # Output the value of the variable if it exists
            var_name = listmake.group(1)
            variables[var_name] = []

        
        if printing:
            # Output the value of the variable if it exists
            var_name = printing.group(1)
            for variable in variables:
                var_name = var_name.replace(variable + ' ',variables[variable] + ' ')

            if var_name in variables:
                await ctx.send(variables[var_name])
            else:
                await ctx.send(var_name)
        
        if assign:
            # Store a new variable or update an existing one
            var_name, value = assign.group(1), assign.group(2)
            variables[var_name] = value
        
        if change:
            # Apply the specified operation to the variable
            operation, var_name = change.group(1), change.group(2)
            if var_name in variables:
                try:
                    # Convert value to integer for arithmetic operations
                    value = int(variables[var_name])
                    if operation == '-=':
                        variables[var_name] = str(value - 1)
                    elif operation == '+=':
                        variables[var_name] = str(value + 1)
                except ValueError:
                    await ctx.send(f"Error: Variable '{var_name}' is not an integer.")
        if sleep:
            var_name = int(sleep.group(1))

            if var_name in variables:
                var_name = int(variables[var_name])
            asyncio.sleep(var_name)
        if debug:
            # Output debug information
            await ctx.send('DEBUG')
            await ctx.send(f'VARIABLES: {variables}')



# Command for gambling game
@bot.command(name='gamble')
async def gamble(ctx):
    items = ['7', '7', '7']
    await ctx.send('Let’s go gambling!')

    def getit(itemsx):
        return f'{itemsx[0]}|{itemsx[1]}|{itemsx[2]}'

    message = await ctx.send(f'{getit(items)}')
    for _ in range(5):
        generates = [str(random.randint(1, 9)) for _ in range(3)]  # Extended range
        items = generates
        await message.edit(content=getit(items))
        await asyncio.sleep(0.5)  # Increased delay for better visibility
    
    # Determine the outcome of the game
    if items[0] == items[1] == items[2]:
        await ctx.send('Wow! You win!')
    else:
        await ctx.send('Oof! You lose...')

# Command to handle user input
@bot.command(name='make_bot')
async def make_bot(ctx, *, user_input: str):
    global the_chosen  # Use global to modify the global variable
    if user_input.startswith('@'):
        user_id = user_input[2:-1]  # Extract user ID from mention
        the_chosen = user_id
        await ctx.send(f'Success! {user_input} is now the chosen one.')

@bot.command(name='generate')
async def generate(ctx):
    
    await ctx.send(sentence.generatesentence(sentence.proceed,20))

@bot.command(name='hangman')
async def hangmangame(ctx):
    if hangman:
        await ctx.send('Someone is already playing hangman.')
        

# Event to handle incoming messages
@bot.event
async def on_message(message):
    # Don't let the bot reply to itself
    if message.author == bot.user:
        return
    
    await message.add_reaction('🍉')
    
    if the_chosen:
        if str(message.author.id) == the_chosen:
            await message.delete()
            await message.channel.send(message.content)
    
    if message.content == 'ping':
        await message.channel.send('pong')
    
    # Process commands if any
    await bot.process_commands(message)

# Run the bot with your token
bot.run(TOKEN)
