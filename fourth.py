import openai
import os
import chainlit as cl
import asyncio

openai.api_key = os.environ.get("OPENAI_API_KEY")

model_name = "gpt-3.5-turbo"
settings = {
    "temperature": 0.3,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

PLANETS = [
    {"name": "Sun", "image": "https://upload.wikimedia.org/wikipedia/commons/e/e1/Sun_poster.svg"},
    {"name": "Moon", "image": "https://upload.wikimedia.org/wikipedia/commons/6/68/FullMoon2010.jpg"},
    {"name": "Mercury", "image": "https://upload.wikimedia.org/wikipedia/commons/d/d9/Mercury_in_color_-_Prockter07_centered.jpg"},
    {"name": "Venus", "image": "https://upload.wikimedia.org/wikipedia/commons/e/ef/Venus-real_color.jpg"},
    {"name": "Mars", "image": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Mars_Valles_Marineris.jpeg"},
    {"name": "Jupiter", "image": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Jupiter_and_its_shrunken_Great_Red_Spot.jpg"},
    {"name": "Saturn", "image": "https://upload.wikimedia.org/wikipedia/commons/c/c7/Saturn_during_Equinox.jpg"},
    {"name": "Uranus", "image": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Uranus2.jpg"},
    {"name": "Neptune", "image": "https://upload.wikimedia.org/wikipedia/commons/5/56/Neptune_Full.jpg"},
    {"name": "Pluto", "image": "https://upload.wikimedia.org/wikipedia/commons/e/ef/Pluto_by_LORRI_and_Ralph%2C_13_July_2015.jpg"}
]

@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "message_history",
        [
            {
                "role": "system",
                "content": "You're entering a conversation with the celestial bodies of our solar system. Please ask them any question or advice you seek.",
            }
        ],
    )
    for planet in PLANETS:
        await cl.Avatar(name=planet["name"], url=planet["image"]).send()

async def answer_as(name):
    message_history = cl.user_session.get("message_history")
    msg = cl.Message(author=name, content="")

    async for stream_resp in await openai.ChatCompletion.acreate(
        model=model_name,
        messages=message_history + [{"role": "user", "content": f"speak as {name}"}],
        stream=True,
        **settings,
    ):
        token = stream_resp.choices[0]["delta"].get("content", "")
        await msg.stream_token(token)

    message_history.append({"role": "assistant", "content": msg.content})
    await msg.send()

@cl.on_message
async def main(message: str):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message})

    # For the sake of brevity, let's only get responses from Sun and Moon in this example. 
    # You can extend this to include other planets as per your requirements.
    await asyncio.gather(answer_as("Sun"), answer_as("Moon"))
