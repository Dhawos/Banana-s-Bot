from discord.ext import commands
from client.constants import adminId
from client.constants import private_channel_id_with_admin
import random
import discord
import json
import http.client
import asyncio

polls = {}
class Poll:
    def __init__(self,misc,channel,question,choices,duration):
        self.misc=misc
        self.channel = channel
        self.question = question
        self.choices = choices
        self.answers = {key:0 for key in self.choices}
        self.running = False
        self.voters = []
        self.duration = duration

    async def start(self):
        self.running = True
        msg = "***Sondage lancé !***\n{0}".format(self.question)
        msg += "\n"
        i = 1
        for choice in self.choices:
            msg += str(i)
            msg += " - "
            msg += choice
            msg += "\n"
            i += 1
        msg.strip()
        await self.misc.bot.send_message(self.channel,msg)
        polls[self.channel.id] = self
        await asyncio.sleep(self.duration * 60)
        await self.stop()

    async def stop(self):
        if self.running:
            await self.misc.bot.send_message(self.channel,"***Fin du sondage***")
            result = "Résultats\n"
            i=1
            for key in sorted(self.answers,key=self.answers.get,reverse=True):
                result += "{0} : {1}\n".format(key,self.answers[key])
                i += 1
            await self.misc.bot.send_message(self.channel,result.strip())
            del polls[self.channel.id]
            self.running = False


class Miscellaneous:
    """Miscellaneous commands"""
    def __init__(self, bot):
        self.bot = bot
        self.annoyToggle = False
        self.msg_counter = 0
        self.currency = {}

    def check_pm(ctx):
        return ctx.message.channel.user.id == adminId

    @commands.command(pass_context=True,no_pm=True)
    async def vote(self,ctx,choice:int):
        if ctx.message.channel.id in polls:
             currentPoll = polls[ctx.message.channel.id]
             if ctx.message.author.id in currentPoll.voters:
                 await self.bot.reply("Tu as déjà voté ptit malin !")
                 return
             else:
                 currentPoll.voters += [ctx.message.author.id]
                 currentPoll.answers[currentPoll.choices[choice-1]] += 1
                 await self.bot.reply(":ok:")
        else:
             self.bot.say("Pas de sondage en cours dans ce channel")

    @commands.command(pass_context=True,no_pm=True)
    async def poll(self,ctx,question : str, options:str,duration:int):
         if ctx.message.channel.id in polls:
             await self.bot.reply("Sondage deja en cours")
         else:
             if duration > 30 or duration < 1:
                 await self.bot.reply("Temps incorrect")
                 return
             newPoll = Poll(self,ctx.message.channel,question,options.split(','),duration)
             await newPoll.start()

    
    @commands.command(pass_context=True,no_pm=True)
    async def courageboard(self,ctx):
        i = 1
        str = '```\n'
        for w in sorted(self.currency,key=self.currency.get,reverse=True):
            member = ctx.message.server.get_member(w)
            str += '{0}-{1} : {2} \n'.format(i,member.name,self.currency[w])
            i += 1
        str.strip()
        str += '```'
        await self.bot.say(str)

    @commands.command(pass_context=True,no_pm=True)
    async def courage(self,ctx,user:discord.Member,value:int):
        """Gives a user some courage"""
        giver = ctx.message.author
        await self.bot.delete_message(ctx.message)
        if not(giver.id in self.currency):
            self.currency[giver.id] = random.randint(1,100)
        if not(user.id in self.currency):
            self.currency[user.id] = random.randint(1,100)
        if value <= 0 or value > self.currency[giver.id]:
            await self.bot.reply("Wesh prend moi pas pour un jambon")
            return
        self.currency[giver.id] -= value
        self.currency[user.id] += value
        await self.bot.say("{0} a donné {1} de courage a {2} !".format(giver.mention,value,user.mention))
    
    @commands.command(no_pm=True,pass_context=True)
    async def courageamount(self,ctx,target:discord.Member=None):
        """How much courage do you have"""
        if target is None:
            target=ctx.message.author
        if not(target.id in self.currency):
            self.currency[target.id] = random.randint(1,100)
        await self.bot.say("{0} a {1} de courage !".format(target.mention,self.currency[target.id]))

    @commands.command(hidden=True)
    @commands.check(check_pm)
    async def say(self,channelId:str,message:str):
        """Says something that has been given in private message"""
        print(channelId)
        print(message)
        await self.bot.send_message(self.bot.get_channel(channelId),message)

    @commands.command(hidden=True)
    async def horoscope(self, sign:str):
        """Retrieves today's horoscope"""
        conn = http.client.HTTPConnection("horoscope-api.herokuapp.com")
        headers = {}
        conn.request("GET","/horoscope/today/" + sign)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        parsedData = json.loads(data)
        await self.bot.reply("\n" + parsedData["horoscope"])

    @commands.command()
    async def roll(self,dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await self.bot.reply('Format has to be in NdN!')
            return
        if rolls > 200 or rolls < 1 or limit > 500 or limit < 2:
            await self.bot.reply('T\'as que ca a branler de faire des jets pourraves ?')
        else:
            result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
            await self.bot.reply(result)


    @commands.command(pass_context=True,hidden=True)
    async def annoy(self,ctx):
        """Send an annoying message every 5 messages received"""
        if ctx.message.author.id == adminId:
            self.annoyToggle = not self.annoyToggle
        else:
            await self.bot.reply('Toi t\'as pas le droit !')

    @commands.command(pass_context=True, hidden=True,no_pm=True)
    async def oracle(self, ctx, question:str):
        """Answers a very important question"""
        if ctx.message.author != self.bot.user:
            n = len(ctx.message.content) % 7
            if(n == 0):
                str = 'J\'ai besoin de temps pour me concentrer !'
            elif(n == 1):
                str = 'Oui'
            elif(n == 2):
                str = 'Non'
            elif(n == 3):
                str = 'Je ne peux pas répondre à cette question'
            elif(n == 4):
                str = 'Oui mais honnêtement je suis pas sur, au pire lance un dé'
            elif(n == 5):
                str = 'Concrètement c\'est mort'
            elif(n == 6):
                str = 'A mon avis non'
            elif(n == 7):
                str = 'Non, sinon attention au claquage'
            if 'travail' in question:
                if ctx.message.author.name == 'Garma':
                    str = 'Comme si ma réponse allait changer quelquechose'
                else:
                    str = 'Non c\'est pas une bonne idée'
            elif 'aujourd\'hui' in question:
                str = 'Non non pas aujourd\'hui'
            await self.bot.reply(str)

    @commands.command(pass_context=True,no_pm=True)
    async def highfive(self,ctx,user : discord.Member):
        """Gives someone a high five !"""
        await self.bot.say("Hey " + user.mention + " give me five ! o/")
        answer = await self.bot.wait_for_message(timeout=10.0, author=user, check=high_five_check)
        if answer is None :
            await self.bot.say("Hey " + user.mention + " ! FUCK YOU")
        else:
            await self.bot.say(user.mention + " Bien joué !")

    @commands.command(hidden=True)
    async def ping(self):
        """Pong."""
        await self.bot.say("Pong.")

    @commands.command(no_pm=True,pass_context=True)
    async def hug(self, ctx,target: str, intensity: int = 1, hidden: bool = False):
        """Hugs someone, because we're bunch of good ol' lads !

        Accepts three parameters:
        The user you want to hug as a string, not a mention
        The intensity of the hug as an integer defaults to 1
        Whether or not the message should be deleted as a boolean"""
        newTarget = discord.utils.get(ctx.message.server.members, name=target)
        if newTarget is None:
            newTarget = discord.utils.get(ctx.message.server.roles, name=target)
        if newTarget is None:
            await self.bot.say("Je ne peux pas caliner ce qui n\'existe pas")
            return
        name = " *" + newTarget.mention + "*"
        if intensity <= 0:
            msg = "(っ˘̩╭╮˘̩)っ" + name
        elif intensity <= 3:
            msg = "(っ´▽｀)っ" + name
        elif intensity <= 6:
            msg = "╰(*´︶`*)╯" + name
        elif intensity <= 9:
            msg = "(つ≧▽≦)つ" + name
        elif intensity >= 10:
            msg = "(づ￣ ³￣)づ" + name + " ⊂(´・ω・｀⊂)"
        await self.bot.say(msg)
        if hidden:
            await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, no_pm=True)
    async def userinfo(self, ctx, user: discord.Member = None):
        """Shows users's informations

        Shows user info, user can be given in arguments as a mention, otherwise
        it will be the author of the command."""
        author = ctx.message.author
        if not user:
            user = author
        roles = [x.name for x in user.roles if x.name != "@everyone"]
        if not roles: roles = ["None"]
        data = "```python\n"
        data += "Name: {}\n".format(user.name)
        data += "ID: {}\n".format(user.id)
        passed = (ctx.message.timestamp - user.created_at).days
        data += "Created: {} ({} days ago)\n".format(user.created_at, passed)
        passed = (ctx.message.timestamp - user.joined_at).days
        data += "Joined: {} ({} days ago)\n".format(user.joined_at, passed)
        data += "Roles: {}\n".format(", ".join(roles))
        data += "Avatar: {}\n".format(user.avatar_url)
        data += "```"
        await self.bot.say(data)



    async def on_message(self,message):
        if message.author == self.bot.user:
            return
        self.msg_counter += 1
        if self.annoyToggle and "dur" in message.content:
            await self.bot.send_message(message.channel, 'Hum')
            self.msg_counter = 0

    async def on_ready(self):
        print('Logged in as')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print('------')
        newgame = discord.Game(name="with your mom")
        await self.bot.change_status(game=newgame, idle=False)



def setup(bot):
    n = Miscellaneous(bot)
    bot.add_cog(n)

def high_five_check(message):
    if (message.content == '\o'):
        return True 
    else:
        return False
