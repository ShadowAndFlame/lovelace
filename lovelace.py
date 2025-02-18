import discord
import random
import json
import re
import datetime as dt

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True 

ada = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(ada)

with open('token.txt', 'r') as f:
    token = f.read()
with open('pjjam_id.txt', 'r') as f:
    pjjam = discord.Object(id=int(f.read()))
  
vote_triggers = ['poll', 'vote', 'react']

def get_reply(mode, rarity_override = None):
    seed = random.random()
    rarities = ['common', 'rare', 'epic', 'legendary']
    rarity_indicators = ['⬜', '🟦', '🟪', '🟨']
    if seed >= 0.99:
        rarity = 3
    elif seed >= 0.95:
        rarity = 2
    elif seed >= 0.75:
        rarity = 1
    else:
        rarity = 0
    if rarity_override is not None:
        rarity = rarity_override
    with open('replies.json', 'r') as f:
        if rarity < 0:
            return "I have nothing to say."
        try:
            return random.choice(json.load(f)[mode][rarities[rarity]]), rarity_indicators[rarity]
        except (KeyError, IndexError):
            return get_reply(mode, rarity-1)
    
@ada.event
async def on_ready():
    print(f'We have logged in as {ada.user}')

@ada.event
async def on_message(message):
    if message.author == ada.user:
        return
    content = str(message.content).lower()
    reply_mode = None
    if re.search(r'\bping\b', content):
        reply_mode = 'ping'
    if re.search(r'\bada\b', content):
        if 'thank' in content:
            reply_mode = 'thanks'
        elif any(word in content for word in ['hi', 'hello', 'hey']):
            reply_mode = 'greeting'
        elif any(word in content for word in ['dead', 'ded', 'die', 'died', 'back', 'alive']):
            reply_mode = 'dead'
        else: 
            reply_mode = 'mention'
    if re.search(r'\bbees?\b', content):
        reply_mode = 'bee'
    if reply_mode:
        reply, rarity = get_reply(reply_mode)
        m = await message.channel.send(reply)
        await m.add_reaction(rarity)
    if content == '!list_replies':
        with open('replies.json', 'r') as f:
            reply_tree = json.load(f)
        for mode in reply_tree:
            for rarity in reply_tree[mode]:
                for reply in reply_tree[mode][rarity]:
                    await message.channel.send(reply)
    # if any(trigger in content for trigger in vote_triggers):
    #     for c in emoji.emojize(content):
    #         if emoji.is_emoji(c):
    #             await message.add_reaction(c)
    if 'connections\npuzzle #' in content:
        guesses = [line for line in content.split('\n') if any(square in line for square in ['🟨','🟩','🟦','🟪'])]
        correct_guesses = [guess for guess in guesses if len(set(guess))==1]
        incorrect_guesses = [guess for guess in guesses if len(set(guess))>1]
        medals = ['🏆', '🥇', '🥈', '🥉', '😵']
        await message.add_reaction(medals[len(incorrect_guesses)])
        if len(correct_guesses) == 0:
            await message.add_reaction('💀')
        else:
            occupations = {'🟪': '🧑‍🚀', '🟦': '🧑‍🔬', '🟩': '🧑‍🏫', '🟨': '🧑‍🌾'}   
            await message.add_reaction(occupations[correct_guesses[0][0]])
        if len(correct_guesses) < 4:
            await message.add_reaction('💔')
        else:            
            hearts = {'🟨': '❤️‍🔥', '🟩': '💘', '🟦': '💕', '🟪': '❤️'}
            await message.add_reaction(hearts[correct_guesses[-1][0]])
    if ('wordle' in content) and ('/6' in content) and ('bandle' not in content):
        if ('🟩'*5 in content) and (content.count('🟩') == 5) and (content.count('🟨') > 0):
            await message.add_reaction('🍋')
        if (content.count('🟩') == 0) and (content.count('🟨') > 0):
            await message.add_reaction('🍋')
        if (content.count('🟨') == 0) and (content.count('🟩') > 0):
            await message.add_reaction('🍏')
    today = lambda m_: m_.created_at >= dt.datetime.now().astimezone().replace(hour=0,minute=0,second=0,microsecond=0)
    today_messages = [m for m in ada.cached_messages if today(m) and (m.channel == message.channel)]
    for m in today_messages:
        if m == message:
            continue
        if m.content == '':
            continue
        if m.author == message.author:
            continue
        if m.content == message.content:
            await m.add_reaction('👯')
            await message.add_reaction('👯')
    if 'discord.com' in content:
        await message.add_reaction('🌊')
    link_sub = {
        'x.com': 'vxtwitter.com',
        'twitter.com': 'vxtwitter.com',
        # 'tiktok.com': 'vxtiktok.com',
        'instagram.com': 'ddinstagram.com'
    }
    # link_re = r'(?:.*? )?(?:(?:https:\/\/)?(?:www.)?((?:\bx\.com\b)|(?:\btwitter\.com\b)|(?:\binstagram\.com\b)|(?:\btiktok\.com\b))[^ ]*)(?: .*)?'
    link_re = r'(?:\bx\.com\b)|(?:\btwitter\.com\b)|(?:\binstagram\.com\b)|(?:\btiktok\.com\b)'
    link_match = re.search(link_re, str(message.content))
    if link_match and not message.attachments:
        domain = link_match.group(0)
        fixed_content = str(message.content).replace(domain, link_sub[domain])
        reply = f'{message.author.mention} posted a link but it didn\'t embed correctly, so I fixed it.\n>>> {fixed_content}'
        await message.channel.send(reply)
        await message.delete()

@ada.event
async def on_reaction_add(reaction, user):
    if user == ada.user:
        return
    # content = str(reaction.message.content).lower()
    # if any(trigger in content for trigger in vote_triggers):
    #     await reaction.message.add_reaction(reaction.emoji)
    if reaction.emoji == '📌':
        await reaction.message.pin()
    if reaction.emoji == '🐝':
        await reaction.message.add_reaction('🐝')
    if reaction.emoji == '🍅':
        if reaction.message.author == ada.user:
            reply, rarity = get_reply('ada-heckle')
            heckle = await reaction.message.reply(f'{user.mention} {reply}', mention_author = False)
            await heckle.add_reaction(rarity)
        elif reaction.message.author == user:
            reply, rarity = get_reply('self-heckle')
            heckle = await reaction.message.reply(reply)
            await heckle.add_reaction(rarity)
        else:
            reply, rarity = get_reply('heckle')
            heckle = await reaction.message.reply(reply)
            await heckle.add_reaction(rarity)
    if random.random() < 0.05:
        await reaction.message.add_reaction(reaction.emoji)

@ada.event
async def on_reaction_remove(reaction, user): 
    if reaction.emoji == '📌' and reaction.count == 0:
        await reaction.message.unpin()

ada.run(token)