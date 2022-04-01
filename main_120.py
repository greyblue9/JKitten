inputs = {}; responses = {}; bot_message = ""; DialoGPT=""; uid="0"; channel_name=""; mention=""; has_proper_noun=False
import traceback
from bs4 import BeautifulSoup as BS

        
    
            
if (
        "i am dad" in response.lower()
        or "i'm dad" in response.lower()
        or "hi jon" in response.lower()
        or ", jon" in response.lower()
        or "hi kyle" in response.lower()
        or ", kyle" in response.lower()
        or "hi paul" in response.lower()
        or ", paul" in response.lower()
        or "hi mat" in response.lower()
        or ", mat" in response.lower()
      ):
        response = random.choice(
          [
            f"Hey there! How are you, {message.author.mention}?",
            "Hello",
            "Hi what'a up?",
            f"Hey, good to see you again, {message.author.mention}.",
            f"Welcome back, {message.author.mention}!",
            f"Yo what's up, {message.author.mention}",
            "Hi, it's good to see you again.",
            "Hello there." "Well, hello!",
            "Hiya bro",
            f"Yay {message.author.mention}! You're exactly who I was hoping to see.",
            "Sup, dude?",
          ]
        )
            
   
          
   
          
   
        
   
   
       
   
   
        if "SRAIXFAILED" in response:
          response = ""
          "how much " in bot_message
          from bs4 import BeautifulSoup as BSimport
          import sys
          import urllib.parse, urllib.request
          inpt = bot_message
          try:
            resp = urllib.request.urlopen(
              urllib.request.Request(
                f"http://api.wolframalpha.com/v2/query?appid=2U987T-JJR9G73T6P&input={urllib.parse.quote(inpt)}"
              )
            )
            doc = BS(resp.read().decode(), features="lxml")
            response = str(
              sorted(
                filter(
                  lambda i: i.text,
                  doc.select(
                    'pod[error=false] > subpod[title=""] > plaintext'
                  ),
                ),
                key=lambda i: len(i.text),
              )[0].text
            )
            if response:
              inputs.append(bot_message)
              responses.append(response)
          except:
            pass
    
    
    
    
        

