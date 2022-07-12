import discord, time, requests
from bs4 import BeautifulSoup
from discord.ext import commands, tasks

"""

Breach Bot v 2.0

Language: Python 3.10

Date: July 12, 2022

Dependencies: BeautifulSoup, Discord.py, time, requests, commands, tasks

Author: Alfred Simpson
------------------------------

This is meant to be used as a discord bot and currently exists on Discord, serving NJIT's Information & Cybersecurity Club (NICC). 

Licensing: This is free to use as you please so long as proper credit is given. 

Considerations:

As this is a public file, I will be using TOKEN as a placeholder for the BB1's actual API Token. Please note: this must be replaced with your bot's own token should you wish to copy this. Your token should appear within ' ' where you see TOKEN appearing. 

Planned improvements since V1.0:
----- V2.0 is about User Input. This is tricky to do within the confines of Discord and the Discord API. These are the features I plan to include, if possible:
- User input to control frequency of news postings
- User input to add sources
- User input to call news on demand, within reason (time limits)
- User input to purge all BreachBot Messages (within the limit)
- User input to purge all messages.
"""

client = discord.Client()
bot = commands.Bot(command_prefix='.')
xxx = 'TOKEN' #Replace with your own token\
channel = bot.get_channel(id) #Replace id with your channel id, found by enabling developer mode on Discord and right clicking on the correct channel.

#These two lists need to be initialized to work appropriately.
mostRecent = []
noNews = []

#This is used further on to highlight websites where there were no news updates
sourceDict = {
    0   :   "Wired",
    1   :   "ThreatPost",
    2   :   "The Hackers' News",
    3   :   "Krebs on Security",
    4   :   "Dark Reading",
    5   :   "CISA - Current Activity",
    6   :   "CISA - Vulnerability Bulletins"
    }

#These are the sources I chose to use for cybersecurity articles as they are trustworthy, exhibit parity online, and tend to not focus on a political bias.
#Choosing to alter these sources would require altering the above dictionary. Should any of these feeds change in how they show their XML to the public, their links would also need to change.

sources = [
        'https://www.wired.com/feed/category/security/latest/rss', 
        'https://threatpost.com/feed/',
        'http://feeds.feedburner.com/TheHackersNews?format=xml',
        'https://krebsonsecurity.com/feed/',
        'https://www.darkreading.com/rss.xml',
        'https://www.cisa.gov/uscert/ncas/current-activity.xml',
        'https://www.cisa.gov/uscert/ncas/bulletins.xml'
        ]

numSources = len(sources)

for i in range(numSources):
    mostRecent.append(i)
#mostRecent has now been initalized, allowing the bot to work appropriately.

#on_message listens for messages and responds appropriately
@bot.event
async def on_message(message):
    if message.content.startswith("$BB"):
        await message.channel.send("Hi! I'm Breach-Bot and I'm here to keep you up to date on the latest in cybersecurity!\n:smile:\t:eyes:")
        """ The below messages are currently commented out as they are not fully operational. They represent what changes I'd like to make in forthcoming versions of BB before BB2."""
    # if message.content.startswith('$Clear'):
    #     await message.channel.send("\n\nPurging the system.\n\n")
    #     await thePurge()
    # if message.content.startswith("!BB"):
    #     await message.channel.send("Hi, I'm Breach Bot.\nI'm going to check the news.\nIf you need extra help, simply type !Help and I'll point you in the right direction. \nUntil then, I'll report the news on a regular basis.\n")
    # if message.content.startswith("!Help"):
    #     await message.channel.send("\nI'm here to report the news.\nThe following commands will help you understand more.\n!Sources : \tReturns a list of our sources.\n!Pause : \tPause will tell me to take a break from the news for 24 hours.")


#on_ready is similar to the Start() function for C# users who build for Unity games. This essentially says once the bot is online and signed in, do the following.
@bot.event
async def on_ready():
    print('\nBreach Bot ready to go!\n') #This will only show in your terminal - not on Discord!
    getNews.start()



"""
This section repeats once per hour (3600 seconds). BB1 is limited to a predetermined frequency. BB2 will take user-input to not only determine frequency, but control if it runs non-stop or at will. This section also utilizes BeautifulSoup to interpret the XML files. Note, if a developer chooses to use a different organizational layout for the RSS feed you may have mismatched data. If any substantial updates happen to the language this may also affect it negatively.

"""

@tasks.loop(seconds=3600) 
async def getNews():
    channel = bot.get_channel(id) #Replace with channel id as noted above.
    print("\nGetting the news\n")
    count = 0
    for source in sources:
        url = requests.get(source)
        soup = BeautifulSoup(url.content, 'xml')
        articles = soup.find_all('item')
        if (count < 5):
            #Count is set to trigger at < 5 as the sources above that do not provide adequate snippets/descriptions. 
            title = articles[0].title.text
            snippet = articles[0].description.get_text()
            link = articles[0].link.text
            output = (f"Title: {title}\n\nSnippet: {snippet}\n\nLink: {link}\n\n--------\n\n")
        else:
            title = articles[0].title.text
            snippet = "Click for more information."
            link = articles[0].link.text
            output = (f"Title: {title}\n\nSnippet: {snippet}\n\nLink: {link}\n\n--------\n\n")

        #After compiling the sources and condensing them into blurbs, we run it against another function, checkPosted, to ensure we're not posting the same news over and over again.
        await checkPosted(output, count, articles[0])
        count += 1
    
    if len(noNews) > 0:
        noNews.clear()
    await channel.send("I'll be back soon with updates!")


"""
This function is what outputs the text to Discord but also monitors for any duplicate stories.
"""
@bot.listen()
async def checkPosted(output, sourceNum, article):
    channel = bot.get_channel(id) #Replace with channel id as noted above. Though this may be redundant. I'll double check this by V2.

    if output in mostRecent:
        noNews.append(sourceDict[sourceNum])
        output = 'Nothing new to report from: '+sourceDict[sourceNum]
        await channel.send(output)
    else:
        mostRecent[sourceNum] = output
        await channel.send(output)
        time.sleep(5)
        #Use time.sleep(5) for a delay in sending messages. Early testing saw spamming a channel rather than a trickle in, which was annoying. While it might get more attention that way, it'll also get turned off quicker that way. Better to not annoy and inform users. 5 = 5 seconds, so if you prefer to wait longer (or less), adjust it here. I'm still testing on the server to find a right fit.

"""
This function was created to delete all of the messages it created while testing in the test server. It does not currently work, but will before V2. If called, it will delete all messages and nuke a page. I ultimately want to include this on the final version of the bot as a failsafe measure for security or to create a signal-style chat room.
"""
@bot.listen()
async def thePurge(limit=100):
    await channel.purge()
    #Doesn't work right now - None type?   

#Finally, we just need to run the bot with the api-token. Anything below this ***will not run***. So bear that in mind. I hope you enjoy BreachBot version 1.0!

bot.run(xxx)