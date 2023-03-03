# ChatGPTDiscord
A discord bot using openAI's ChatGPT api and Microsoft's Bing AI to act as a smart chat assistant allowing for natural, conversational interactions between users and the language model. This can be a great way to generate creative ideas, have engaging discussions, or even just pass the time with some entertaining banter.

ChatGPT is setup for a single channel, and a single conversational thread. Will allow user to DM as well, but conversational context is shared with the public channel.

Accepts discord file upload of text based files (analyse code or essays!)

Splits output from chatgpt into multiple messages to get around discord message size limits.

Removes common limitation phrases from output, and rebrands OpenAI and Microsoft.

You will need access to the new Bing in order for the search command to work. For instructions, see https://github.com/acheong08/EdgeGPT

Originally forked from https://github.com/acheong08/ChatGPT

## Commands

* `/Search [message]` Search wtih Bing AI!
* `!reset` Clear ChatGPT conversation history

## Install
`git clone`

`cd ChatGPTDiscord`

`pip3 install requests discord asyncio typing`

`pip3 install revChatGPT=2.2.2`

`pip3 install EdgeGPT --upgrade`

Setup config file with the steps in https://github.com/acheong08/ChatGPT/wiki/Setup
Be sure to add in your "discord_bot_token" (api key), "discord_channel" (channel id for where you want it to response) and "discord_admin_id": (numeric admin account id)

## Setup Bing cookies
in order to get Bing AI to work, you will need access to the new Bing

- Install the latest version of Microsoft Edge
- Open http://bing.com/chat
- If you see a chat feature, you are good to go

  <summary>

### Getting authentication (Required)

  </summary>

- Install the cookie editor extension for [Chrome](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) or [Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)
- Go to `bing.com`
- Open the extension
- Click "Export" on the bottom right (This saves your cookies to clipboard)
- Paste your cookies into a file `cookies.json`

</details>

# Running
```
 $ python3 Jarvisdiscord.py            
```
