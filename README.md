# C3PO Discord Bot
A discord bot using openAI's ChatGPT api and Microsoft's Bing AI to act as a smart chat assistant allowing for natural, conversational interactions between users and the language model. This can be a great way to generate creative ideas, have engaging discussions, or even just pass the time with some entertaining banter.

Splits output from chatgpt into multiple messages to get around discord message size limits.

Removes common limitation phrases from output, and rebrands OpenAI and Microsoft.

Originally forked from https://github.com/ausbitbank/ChatGPTDiscord

Bot also has feature to track message ranking of users for each server channel

## Commands

* `/Search [message]` Search wtih Bing AI!
* `/ranking` display the message ranking of the current channel
* `/help` get help for commands

## Install
`git clone`

`cd ChatGPTDiscord`

`pip3 install requests discord asyncio typing`

Setup config file (mainly just need the bot token)


# Running
```
 $ python3 C3PO_AiBot.py            
```
