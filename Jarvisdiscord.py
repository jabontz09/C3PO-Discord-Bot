import json, discord, sys, asyncio, functools, typing, os, re
from revChatGPT.V1 import Chatbot
from discord import app_commands
from EdgeGPT import Chatbot as Bing

class aclient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="/search | /help | #・❥・Jarvis")

def split_string_into_chunks(string, chunk_size):
  chunks = []# Create an empty list to store the chunks
  while len(string) > 0:# Use a while loop to iterate over the string
    chunk = string[:chunk_size]# Get the first chunk_size characters from the string
    chunks.append(chunk)# Add the chunk to the list of chunks
    string = string[chunk_size:]# Remove the chunk from the original string
  return chunks# Return the list of chunks

def add_brackets_to_hyperlink(text: str) -> str:
    # Regular expression pattern to match a hyperlink
    pattern = re.compile(r'(https?://\S+)')

    # Use re.sub to replace all instances of the hyperlink pattern in the text
    result = re.sub(pattern, r'<\1>', text)

    return result

async def send_chunks(interaction, chunks):
    if type(interaction) == discord.interactions.Interaction:
        for chunk in chunks:
            await interaction.followup.send(chunk)
    else:
       for chunk in chunks:
            await interaction.reply(chunk) 

def tidy_response(i):# Optionally spoilerify or hide the most repetitive annoying nothing responses, rebrand to EvilCorp
    spoiler_bad_responses=False
    hide_bad_responses=True
    rebrand_responses=True
    bad_responses=["As a large language model trained by OpenAI,","As a language model trained by OpenAI,","My training data has a cutoff date of 2021, so I don't have knowledge of any events or developments that have occurred since then.","I'm not able to browse the internet or access any new information, so I can only provide answers based on the data that I was trained on.","I don't have the ability to provide personal opinions or subjective judgments, as I'm only able to provide objective and factual information.","I'm not able to engage in speculative or hypothetical discussions, as I can only provide information that is based on verifiable facts.","I'm not able to provide medical, legal, or financial advice, as I'm not a qualified professional in these fields.","I'm not able to engage in conversations that promote or encourage harmful or offensive behavior.","I don't have personal experiences or opinions, and I can't provide personalized advice or recommendations.","As a language model, I'm not able to perform actions or execute commands. I can only generate text based on the input I receive.","I'm not able to provide direct answers to questions that require me to make judgments or evaluations, such as questions that ask for my opinion or perspective on a topic.","I can provide information on a wide range of subjects, but my knowledge is limited to what I have been trained on and I do not have the ability to browse the internet to find new information","I do not have the ability to browse the internet or access information outside of what I have been trained on.","I'm sorry, but as a large language model trained by OpenAI, "]
    if i.find("`") == -1: # Only attempt if no code block is inside the response
        if spoiler_bad_responses:
            #bad_responses_found=[response.replace(response, "||" + response + "||") for response in bad_responses if response in i]
            bad_responses_found=[response for response in bad_responses if response in i]
            bad_responses_string = "".join(bad_responses_found)
        if hide_bad_responses:
            for br in bad_responses:i=i.replace(br, "")
        if spoiler_bad_responses and bad_responses_string != '':i+='\n||'+bad_responses_string+'||'
    if rebrand_responses:
        i=i.replace("OpenAI", "Iron Men")
        i=i.replace("Microsoft", "Iron Men")
        i=i.replace("ChatGPT", "Jarvis")
        i=i.replace("Bing", "Jarvis on the web")
        i=i.replace("!Dream:", "!dream ")
    return i

def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        wrapped = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, wrapped)
    return wrapper

@to_thread
def get_answer(chatbot,query):
    for data in chatbot.ask(query):
        pass
    return data["message"]

async def bing_search(chatbot, prompt) -> int:
    try:
        response = await chatbot.ask(prompt=prompt)
        #get conversation count index
        invocations = int(response['invocationId'])
        message = response["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
        message += f" (we are allowed {5 - invocations} more search(es) for this conversation before data has to be reset)"
        print(message)
        r=tidy_response(message)
        s = add_brackets_to_hyperlink(r)
        chunks=split_string_into_chunks(s,1975) # Make sure response chunks fit inside a discord message (max 2k characters)

        data = {
            "messageCount": invocations + 1,
            "success": True,
            "message": chunks
        }
        return data

    except Exception as e:
        print(e)
        data = {
            "messageCount": 0,
            "success": False,
            "message": ["Sorry there appears to have been a problem"]
        }
        return data

if __name__ == "__main__":
#    thread = Thread(target=run_api);thread.start()
    with open("config.json", "r") as f: config = json.load(f)
    client = aclient()
    
    # Initialize Chatbot
    chatbot = Chatbot(config=config)
    bing = Bing("./cookie.json")
    conversation_message_count = 0
    userdb={}

    @client.event
    async def on_ready():
        await client.tree.sync()
        print(f'We have logged in as {client.user}')

    @client.tree.command(name="search", description="search the web with Jarvis")
    async def search(interaction: discord.Interaction, *, message: str):
        global conversation_message_count
        global bing

        if interaction.user == client.user:
            return

        #reset instance of bing AI if message count has exceeded 6 conversation limit
        if conversation_message_count >= 6:
            bing = Bing("./cookie.json")
        
        username = str(interaction.user)
        user_message = message
        channel = str(interaction.channel)

        print(
            f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")

        await interaction.response.defer(ephemeral=False)

        data = await bing_search(bing, user_message)
        conversation_message_count = data["messageCount"]
        successful = data["success"]
        chunks = data["message"]

        if not successful:
            try:
                bing = Bing("./cookie.json")
                data = await bing_search(bing, user_message)
                conversation_message_count = data["messageCount"]
                chunks = data["message"]
                await send_chunks(interaction, chunks)
            except Exception as e:
                print(e)
                await interaction.followup.send("Sorry, something appears to have gone wrong. Please try again later")
        else:
            await send_chunks(interaction, chunks)
        

    @client.tree.command(name="help", description="Show help for Jarvis")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("""**Commands for Jarvis** \n
        - `/search [message]` search the web with Jarvis!
        - `/webreset` reset Jarvis' adventure on the web
        - `!convos` get the bot's current conversation data
        - `!reset` Clear conversation history\n
        -  To have a conversation with Jarvis: speak at the dedicated channel (please note that searching the web with Jarvis and speaking to them directly are different conversations)""")
        print(
            "\x1b[31mSomeone need help!\x1b[0m")

    @client.tree.command(name="webreset", description="reset Jarvis' adventure on the web")
    async def webreset(interaction: discord.Interaction):
        global bing
        await interaction.response.defer(ephemeral=False)
        try:
            bing = Bing("./cookie.json")
            await interaction.followup.send("I have successfully reset my internet search session")
            print(f"\x1b[bing was reset by user: \x1b[0m {interaction.user.name}")
        except Exception as e:
            print(e)
            await interaction.followup.send("something appears to have gone wrong with my web browser 🥲")

    @client.event
    async def on_message(message):
        if message.author == client.user: return
        if message.channel.id != config["discord_channel"] and type(message.channel)!=discord.DMChannel: return
        if message.author.bot: return
        if message.content == 'refresh' and message.author.id == config['discord_admin_id']: chatbot.refresh_session(); await message.add_reaction("🔄"); print("refresh session"); return
        if message.content == 'restart' and message.author.id == config['discord_admin_id']: os.execl(__file__, *sys.argv);return
        if message.content == '!reset': chatbot.reset_chat; await message.add_reaction("🔃"); await message.reply("chat has been reset"); print("reset chat"); return
        if message.content.startswith('!dream'):return
        if message.content == "!convos":
            try:
                data = chatbot.get_conversations()
                print(data)
                r=tidy_response(f"here is my current conversation data: \n\n{str(data)}")
                n = r.replace("},", "}\n")
                chunks=split_string_into_chunks(n,1975) # Make sure response chunks fit inside a discord message (max 2k characters)
                for chunk in chunks:
                    await message.reply(chunk)
                    return
            except Exception as e:
                print("Something went wrong!")
                print(e)
                await message.add_reaction("❌")
                await message.reply("I am unable to get stored conversation history right now")
                return

        longquery=''
       
        if message.attachments and message.attachments[0].width and message.attachments[0].height:
            #image_url = message.attachments[0].proxy_url
            #image_desc = extract_text_from_image_url(image_url)
            #longquery=await message.reply(image_desc)
            return
        if message.attachments and message.attachments[0].content_type.startswith('text'):
            print('text attachment found, adding to prompt')
            attachment=message.attachments[0]
            data=await attachment.read()
            longquery=data.decode()
            
        if message.mentions:
            for user in message.mentions:
                if user != client.user: return

        print("\x1b[36m" + message.author.name+":\x1b[0m "+message.content)

        try:
            #message.add_reaction("👁️")
            query=message.content
            if longquery and longquery != '':
                query=message.content+'\n```'+longquery+'\n```'
            conversation_id=None
            did=message.channel.id
            cb=chatbot
            if did in userdb:
                cid=userdb[message.channel.id]
            else:
                cid=None
            #cb.conversation_id=cid
            #if type(message.channel)==discord.DMChannel:#DM
            #else:#In channel
            #start typing
            async with message.channel.typing():
                response= await get_answer(cb,query)
            #userdb[did]={'cid':response['conversation_id']}
            print(userdb)
            print('\x1b[33mJarvis:\x1b[0m'+response)
            r=tidy_response(response)
            s = add_brackets_to_hyperlink(r)
            chunks=split_string_into_chunks(s,1975) # Make sure response chunks fit inside a discord message (max 2k characters)
            await send_chunks(message, chunks)

        except Exception as e:
            print("Something went wrong!")
            print(e)
            if isinstance(e,str) and e.startswith("Expecting value:"):
                print('restarting session')
                await message.reply('Connection problem found, restarting, re-ask your question in a moment')
                os.execl(__file__, *sys.argv)
            await message.add_reaction("❌")

    client.run(config["discord_bot_token"])
