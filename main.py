import asyncio
import discord
import os
import discord.ext
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions,  CheckFailure, check
import requests
import shutil
import string
import random
import threading
import json
import glob
from flask import Flask, request, render_template
#from flask_ngrok import run_with_ngrok
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
naaah = ["/","\\",".","*","%",",","'",'"',":",";","`","?","!","#","@"]
codesforscript = []
prefix = "!"

def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele+"\n"
    return str1

def listToStringClear(s):
    str1 = ""
    for ele in s:
        str1 += ele
    return str1

client = commands.Bot(command_prefix=prefix, description="", intents=intents)
client.remove_command('help')
@client.event
async def on_ready():
    print("bot online")
    
@client.command()
async def ping(ctx):
    await ctx.send(ctx.message.author.id)
    await ctx.message.add_reaction('✅')

@client.command()
async def help(ctx):
 embed=discord.Embed(title="Help command", color=0x00ffb3)
 embed.add_field(name=prefix+"upload", value="arg1(folder name)\narg2(script name)")
 embed.add_field(name=prefix+"create", value="arg1(folder name)")
 embed.add_field(name=prefix+"get", value="arg1(folder name or nothing)")
 embed.add_field(name=prefix+"removescript", value="arg1(folder name)\narg2(script name)")
 embed.add_field(name=prefix+"removefolder", value="arg1(folder name)")
 embed.add_field(name=prefix+"getscript", value="arg1(folder name)\narg2(script name)")
 embed.add_field(name=prefix+"setting", value="arg1(folder name)\narg2(parameter)\narg3(string)")
 embed.add_field(name=prefix+"share", value="arg1(folder name)\narg2(who)")
 await ctx.send(embed=embed)
 await ctx.message.add_reaction('✅')

@client.command()
async def upload(ctx,arg1,arg2):
 for letter in naaah:
    if letter in [*arg1]  or letter in [*arg2]:
        await ctx.send("Naaaah")
        return
 if arg2 == "settings":
    await ctx.send("File name not allowed") 
    return
 if not ctx.message.attachments:
  await ctx.send("Your message does not have an text for save") 
  return
 elif not str(ctx.message.attachments[0].url).endswith(".txt"):
  await ctx.send("Format not supported only .txt") 
  return
 userid = str(ctx.message.author.id)
 if not os.path.exists(userid):
   os.makedirs(userid)
 if not str(ctx.message.attachments[0].url).startswith("https://cdn.discordapp.com/attachments/"):
  await ctx.send("Website not allowed") 
  return
 
 try:
  r = requests.get(ctx.message.attachments[0].url, allow_redirects=True)
  with open(os.path.join(userid+"/"+arg1, arg2+'.txt'), 'wb') as temp_file:
    temp_file.write(r.content)
 except:
  await ctx.send("Invalid folder or file exists") 
  return
 await ctx.message.add_reaction('✅')

@client.command()
async def getscript(ctx,arg1,arg2):
 for letter in naaah:
    if letter in [*arg1] or letter in [*arg2]:
        await ctx.send("Naaaah")
        return
 userid = str(ctx.message.author.id)
 if not os.path.exists(userid):
   os.makedirs(userid)
 try:
  await ctx.send(file=discord.File(os.path.join(userid+"/"+arg1+"/"+arg2+".txt")), ephemeral=True)
 except: 
  await ctx.send("File not found") 
  return
 await ctx.message.add_reaction('✅')


@client.command()
async def create(ctx,arg1):
 for letter in naaah:
    if letter in [*arg1]:
        await ctx.send("Naaaah")
        return
    
 userid = str(ctx.message.author.id)
 if not os.path.exists(userid):
   os.makedirs(userid)
 if len(arg1) > 10:
    await ctx.send("Maximum string len limit reached")
    return
 if len(os.listdir(os.path.join(userid))) > 10:
    await ctx.send("Maximum folder limit reached")
    return

 if os.path.exists(os.path.join(userid+"/"+arg1)):
    await ctx.send("Folder exist")
    return
 os.mkdir(os.path.join(userid+"/"+arg1))
 rand = id_generator(12)
 with open(os.path.join(userid+"/"+arg1, 'settings.txt'), 'wb') as temp_file:
    temp_file.write(f"password:{rand}\ncanuse:true".encode())
 try:
     await ctx.message.author.send(f'Your password for folder {arg1} is {rand}')
 except: 
      await ctx.send(f"Open your dm for password and after use **{prefix}getscript {arg1} settings**")  

 await ctx.message.add_reaction('✅')

@client.command()
async def setting(ctx,arg1,arg2,arg3):
 userid = str(ctx.message.author.id)
 for letter in naaah:
    if letter in [*arg1]:
        await ctx.send("Naaaah")
        return
 try:
  lines = open(os.path.join(userid+"/"+arg1+'/settings.txt'))
 except: 
   await ctx.send("File not found")
   return
 settings = []
 for i in lines.readlines():
  line = str.split(i,":",1)
  
  if line[0].startswith(arg2):
      if str(arg3).lower() == "random" and str(arg2) == "password":
       rand = id_generator(12)
       line[1] = rand+"\n"
       try:
        await ctx.message.author.send(rand)
       except: 
        await ctx.send("File not found or member had their dm close") 
      else:
       line[1] = arg3+"\n"


  line[0] = line[0]+":"
  settings.append(listToStringClear(line))


 with open(os.path.join(userid+"/"+arg1+'/settings.txt'),"wb") as temp_file:
    temp_file.write(str(listToStringClear(settings)).encode())
 lines.close()
 await ctx.message.add_reaction('✅')
  
@setting.error
async def setting_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send('Inccorrect arguments entered')
    else:
      await ctx.send('Unknown error '+error)

@client.command()
async def whitelist(ctx,folder,username,discordid):
 for letter in naaah:
    if letter in [*folder]:
        await ctx.send("Naaaah")
        return
 userid = str(ctx.message.author.id)
 path = userid+"/"+folder+'/whitelist.txt'
 if os.path.isfile(path):
  open(path,"w+")

 with open(path, 'a') as file:
    file.write(username+":"+discordid)
 await ctx.message.add_reaction('✅')

@whitelist.error
async def whitelist_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send('Inccorrect arguments entered')
    else:
      await ctx.send('Unknown error '+error)


@client.command()
async def removefolder(ctx,arg1):
 for letter in naaah:
    if letter in [*arg1]:
        await ctx.send("Naaaah")
        return
 
 userid = str(ctx.message.author.id)
 if not os.path.exists(userid):
   os.makedirs(userid)
 try:
  shutil.rmtree(os.path.join(userid+"/"+arg1))
 except: 
  await ctx.send("File not found")
  return
 await ctx.message.add_reaction('✅')

@client.command()
async def rename(ctx,arg1,arg2,arg3):
 for letter in naaah:
    if letter in [*arg1] or letter in [*arg2]:
        await ctx.send("Naaaah")
        return
 
 userid = str(ctx.message.author.id)
 if not os.path.exists(userid):
   os.makedirs(userid)
 try:
  os.rename(os.path.join(userid+"/"+arg1+"/",arg2+".txt"),os.path.join(userid+"/"+arg1+"/",arg3+".txt"))
 except: 
  await ctx.send("File not found")
  return
 await ctx.message.add_reaction('✅')

@client.command()
async def removescript(ctx,arg1,arg2):
 for letter in naaah:
    if letter in [*arg1]  or letter in [*arg2]:
        await ctx.send("Naaaah")
        return


 userid = str(ctx.message.author.id)
 if not os.path.exists(userid):
   os.makedirs(userid)
 try:
  os.remove(os.path.join(userid+"/"+arg1+"/"+arg2+".txt"))
 except: 
   await ctx.send("File not found")
   return
 await ctx.message.add_reaction('✅')

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@client.command()
async def testvote(discouser,plr,folder):
  discouser = int(discouser)
  user = await client.fetch_user(discouser)
  msg = await user.send(f"Player **{plr}** wanna start your script from folder **{folder}**")  
  await msg.add_reaction('✅')
  await msg.add_reaction('❌')
  def check(reaction, user):
     if reaction.message.id == msg.id and user.id == discouser and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌'):
      return True
  try:
   wat = await  client.wait_for('reaction_add',check=check, timeout=30.0)
  except asyncio.TimeoutError as error:
       await msg.edit(content=f"Time is over for your script from folder **{folder}** user: {plr}")
       return False
  else:
    if str(wat[0]) == "✅":
     await msg.edit(content=f"Launch confirmed for **{plr}**")
     return True
    else:
     await msg.edit(content=f"Launch denied for **{plr}** (change your password of your script if you get spam)")
    return False
  

@client.command()
async def get(ctx,arg1):
 for letter in naaah:
  if letter in [*arg1]:
        await ctx.send("Naaaah")
        return   
  
 userid = str(ctx.message.author.id)
 if not os.path.exists(userid):
   os.makedirs(userid)
 res = []
 for path in os.listdir(os.path.join(userid+"/"+arg1)):
    res.append(f"```{path}```")

 try:
     await ctx.send(listToString(res)) 
 except: 
   await ctx.send("Your folder with scripts is empty")
   return
 await ctx.message.add_reaction('✅')


@client.command()
async def share(ctx,arg1):
 for letter in naaah:
    if letter in [*arg1]:
        await ctx.send("Naaaah")
        return
    
 try:
  if ctx.message.mentions[0].id == 1:
    return
 except: 
   await ctx.send("Invalid user") 
   return
 userid = str(ctx.message.author.id)
 if not os.path.exists(userid):
   os.makedirs(userid)
 print(str(ctx.message.mentions[0].id))
 if not os.path.exists(str(ctx.message.mentions[0].id)):
   os.makedirs(str(ctx.message.mentions[0].id))
 shutil.copytree(os.path.join(userid+"/"+arg1), os.path.join(str(ctx.message.mentions[0].id)+"/"+arg1), copy_function = shutil.copy)
 await ctx.message.add_reaction('✅')
 print(client.get_user(ctx.message.mentions[0].id))
 await client.get_user(ctx.message.mentions[0].id).send("<@"+userid+"> shared the script with you")

@get.error
async def get_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      userid = str(ctx.message.author.id)
      if not os.path.exists(userid):
       os.makedirs(userid)
      res = []
      for path in os.listdir(os.path.join(userid)):
       res.append(f"```{path}```")
      try:
       await ctx.send(listToString(res)) 
      except: 
        await ctx.send("Your folder is empty")
        return
      await ctx.message.add_reaction('✅')
    else:
      print(error)
      await ctx.send('Unknown error')
   
@upload.error
async def upload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send('Inccorrect arguments entered')
    else:
      print(error)
      await ctx.send('Unknown error')



@create.error
async def create_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send('Inccorrect arguments entered')
    else:
      print(error)
      await ctx.send('Unknown error')

@client.event 
async def on_command_error(ctx, error): 
    if isinstance(error, commands.CommandNotFound): 
        em = discord.Embed(title=f"Error", description=f"Command not found.", color=ctx.author.color) 
        await ctx.send(embed=em)
    else: print(error)




app = Flask(__name__)



@app.route('/', methods=['POST'])
def result():
  print(request.json)
  if "get" in request.json:
    lines2 = None
    args = request.json['get'].split(":",4)
    user = args[0]
    if os.path.isfile(args[0]+"/"+args[1]+'/whitelist.txt'):
      lines2 = open(os.path.join(args[0]+"/"+args[1]+'/whitelist.txt'))
      for i in lines2.readlines():
        line = str.split(i,":",1)
        if line[0] == args[3]: #check for username and discordid like Emilsaaybye11:407242708143570967
          user = line[1]

    try:
      lines = open(os.path.join(args[0]+"/"+args[1]+'/settings.txt'))
    except: 
      print("fail")
      return False
    for i in lines.readlines():
      line = str.split(i,":",1)
      if line[0] == "password":
       if (line[1] == args[2] or line[1] == args[2]+"\n") and  asyncio.run_coroutine_threadsafe(testvote(user,args[3],args[1]), client.loop).result():   
          dir_con={}
          for f in glob.glob((args[0]+"/"+args[1])+"/*.txt"):
           with open(f, encoding="utf-8") as f:
              filename = os.path.splitext(os.path.basename(f.name))[0] 
              if filename != "settings" and filename != "whitelist":
               dir_con[filename]=f.readlines()
          return json.dumps(dir_con)
       else:
         return False
    

@client.event
async def on_command(ctx):
    user = ctx.author
    command = ctx.message.content
    print(f'{user} > {command}')

def apprun():
  #run_with_ngrok(app)
  app.run(host='0.0.0.0')

th = threading.Thread(target=apprun)
th.daemon = True
th.start()



client.run("token")
