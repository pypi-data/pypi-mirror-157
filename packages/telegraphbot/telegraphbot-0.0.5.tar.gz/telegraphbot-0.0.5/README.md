[![License](https://img.shields.io/github/license/italia/bootstrap-italia.svg)](https://github.com/italia/bootstrap-italia/blob/master/LICENSE)

# What is Telegraphbot
Telegraphbot is a handy Python tool that allows newcomers to the world of Telegram bots to easily build one and in particular it allows to structure the conversation following a graph paradigm.


## Installation

There are two ways to install the library:

* Via pip:

```
$ pip install telegraphbot
```
* Via git:

```
$ git clone https://github.com/PythonUser-ux/Telegraphbot.git
$ cd Telegraphbot
$ python setup.py install
```
or:
```
$ pip install git+https://github.com/PythonUser-ux/Telegraphbot.git
```
# The graph paradigm

Using telegraphbot every conversation can be represented as an oriented graph in which nodes represent states and arcs represent the possible transitions. <br> Every state is given by: <br>
- an integer for the degree of depth (distance from the initial node)
- a (optional) string to introduce the user to the state (typically a question)
- an ordered list of answers accepted by the bot during that state
- an ordered list of functions to be called for the corresponding accepted answers
- a function to be called in case the user input is not among the accepted ones
- an (optional) ordered list of successive nodes

Therefore each input given by the user is associated with a function call which can do whatever you want!

The conversation always start at depth 0 by simply launching the bot using the command "/start" in the chat.
Only one node should have 0 depth in order to avoid undesired behaviour.

There can be arcs exiting from an edge which does not enter in any edge, this is because we may be only interested in the transition.

Let's see the actual code.

## Step 1: Obtaining an API token

First of all look for [@BotFather](https://core.telegram.org/bots#botfather) on Telegram, this is the father of all bots: it explains you how to get your bot registered on Telegram's servers and gives you the API required to control your bot.

## Step 2: Design your bot
> *Draw a graph of what your program will do*

![](Draft.png)

It can be useful to make a draft of your bot if it becomes too complex.

## Step 3: Instantiate the bot

```python
from telegraphbot import BOT

API_TOKEN = 'SECRET_TOKEN'

my_bot = BOT(name="Wall-e", token=API_TOKEN)
```

## Step 4: Make your "first steps"

A conversation node is created calling the *chat_step* method inside a function that only takes *message* as argument. This choice is for compatibility reasons.

```python

lz=my_bot.lazy
unrecognized=my_bot.unrecognized
chat_step=my_bot.chat_step

def step0(message):
    chat_step(0, message, "What are your orders?", ["Hit the console", "Give me an opinion"], [action1, lz], unrecognized, next_steps=[None,step1])
    
def action1(message):
    for i in range(10):
        print("SPAM")
    my_bot.reset()

```
In so doing we are creating a very first node for our conversation. <br> After sending the command "/start" our bot will be asking "What are your orders?" and the only accepted answers are those passed as next argument.<br> The first input will cause the call of *action1* and since the corresponding next step is *None* then the bot will not pass to a next node; the second proper answer will call the function *my_bot.lazy*, which does literallly nothing, but this time *step1* will be the next state. Of course, *step1* needs to be de defined as well. <br> *my_bot.unrecognized* is the default function called when the user inputs an unaccepted answer. <br> Note that for every function called by mean of a transition *message* should be the only argument. <br> Even tough this may seem limiting, other "arguments" can actually be passed using global variables, and it is not a big deal assuming the only reason why a function changes its behaviour is due to user inputs. This point will be adressed in details in the next uptades of this description.

```python
from anything import Anything

def step1(message):
    chat_step(1, message, "Okay, send me a selfie", [Anything], [make_a_compliment], unrecognized, next_steps=[])

def make_a_compliment(message):
    if message.content_type=="photo":
        my_bot._bot.send_message(message.chat.id,"You look cool!")
    else:
        my_bot._bot.send_message(message.chat.id,"Don't be shy!")
    my_bot.reset()
```

What this step does is simply to accept everything and to call the *make_a_compliment* function that sends a different message to the user depending on the type of the input. <br>

If the bot receives a file, the content is automatically stored by default in the same directory of the source code and named with a trivial name. To modify this behaviour you should specify a directory when instantiating the bot. Moreover, a file can be saved with a different name if it is sent with a caption, in this case the caption becomes the file name.

As you may have noted, each time a function is also meant to restart the bot, the *reset()* method is called; this will bring your bot before its activation. An alternative to *reset()* is *soft_reset()* that brings the bot at the state of depth 0 and you do not need to send "/start" again.

Note that *step1* has depth 1 as it is the son of a step of depth 0.

## Step 5: Add the steps

```python
my_bot.steps.append(step0)
my_bot.steps.append(step1)

# Or
# my_bot.steps=[step0,step1]
```

Important: the root node should be added as first.

## Step 6: Activate the bot

```python
my_bot.polling()
```

This function should not be called more than once.

# Commands

One of the main features of Telegram bots are commands. Those are special user message like /start, which begins with / and have priority over normal messages. To define a command using the class *Command* from *telegraphbot* just type:

```python
from telegraphbot import Command
command1=Command("help", console_description)

def console_description():
    print("This bot is designed to annoy you")
```

Now whenever your bot receives "/help" the *console_description* function is called.
All you have to know is that "/start" has the priority over all the other commands.

# Bot variables

The position of the user inside the conversation graph is fixed by two variables:

- The depth degree of the node

- The ordered list of answers accepted so far

Therefore it can be useful to modify those variable as part of your action effects.

You can access those variables as follows

```python
self._deep_degree
self._conversation
```

However you should pay attention to the coherence between the two.

# Work in progress

This tutorial contains the absolute minimum to get started, new uptades are coming from month to month.

# Licence
MIT Licence
# Author
Made by Andrea Virgillito.