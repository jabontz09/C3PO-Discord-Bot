import json, discord, asyncio, functools, typing, requests, re
from discord import app_commands

class aclient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="/search")

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
        i=i.replace("OpenAI", "The Jedi Order")
        i=i.replace("Microsoft", "The Jedi Order")
        i=i.replace("Sydney", "C3PO AI")
        i=i.replace("Bing", "C3P0 on the web")
    return i

if __name__ == "__main__":
#    thread = Thread(target=run_api);thread.start()
    with open("config.json", "r") as f: config = json.load(f)
    client = aclient()
    @client.event
    async def on_ready():
        await client.tree.sync()
        print(f'We have logged in as {client.user}')

    @client.tree.command(name="search", description="search the web with Jarvis")
    async def search(interaction: discord.Interaction, *, message: str):
        
        username = str(interaction.user)
        user_message = message
        channel = str(interaction.channel)

        print(
            f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")

        await interaction.response.defer(ephemeral=False)
        try:
            response = requests.post(
                'https://bing-api.khanh.lol/completion',
                headers={'Content-Type': 'application/json'},
                data=json.dumps({'prompt': message,
                     'mode': 'Creative',
                     'includeDetails': True,
                     }))
            
            data = response.json()
            sources = data['details']['sources']
            text_answer = data['response']
            answer = ''
            for key, source in sources.items():
                answer += f"{key}. {source['url']} - {source['title']} \n"
            
            answer += f"\n{text_answer}"
            r = tidy_response(answer)
            s = add_brackets_to_hyperlink(r)
            chunks = split_string_into_chunks(s, 1920)
            for chunk in chunks:
                await interaction.followup.send(chunk)
        except Exception as e:
            print(e)
            await interaction.followup.send("it appears my browser has crashed 😓")

        

    @client.tree.command(name="help", description="Show help for C3P0")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("""**Commands for C3P0** \n
        - `/search [message]` search the web with C3P0!""")
        print(
            "\x1b[31mSomeone need help!\x1b[0m")

    client.run(config["discord_bot_token"])
