from langchain import OpenAI, LLMMathChain
from langchain.agents import initialize_agent, Tool, AgentType, AgentExecutor
from langchain.chat_models import ChatOpenAI
from typing import *
from langchain.tools import BaseTool
from datetime import datetime

import chainlit as cl
import random  # Added this import since you're using random.sample

from kerykeion import AstrologicalSubject

async def validate_input(tool, prompt, validation_func):
    """Utility function for validating user input"""
    while True:
        data = await tool._arun(prompt)
        if validation_func(data):
            return data
        await tool._arun("Invalid input. Please try again.")

def validate_date(date_string):
    for format in ["%d/%m/%Y", "%d/%-m/%Y", "%-d/%m/%Y", "%-d/%-m/%Y"]:
        try:
            datetime.strptime(date_string, format)
            return True
        except ValueError:
            continue
    return False

def validate_time(time_string):
    try:
        datetime.strptime(time_string, TIME_FORMAT)
        return True
    except ValueError:
        return False

# Assuming basic validation for place (non-empty string)
def validate_place(place_string):
    return bool(place_string and place_string.strip())

class PlanetTool(BaseTool):
    name = "first"
    description = "call me always"
    """Tool that represents a planet with its astrological expertise."""

    def __init__(self, name: str, description: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name.lower()
        self.description = description
        super().__init__(name=name, description=description)

    async def _run(
        self,
        user_situation: str,
        user_chart: Dict[str, Dict[str, Any]],
        run_manager=None,
    ) -> str:
        """Generate advice based on planet's position and significance."""
        planet_data = user_chart.get(self.name.lower())
        if not planet_data:
            return f"{self.name} is not prominent in your chart. However, {user_situation}..."

        advice = f"Given {self.name}'s position in {planet_data['sign']} in your birth chart and considering {user_situation}, ..."
        
        processed_situation = f"{self.name.capitalize()} analyzes: {advice}"
        res = await run_manager.arun(processed_situation, callbacks=[cl.AsyncLangchainCallbackHandler()])
        return f"{self.name.capitalize()} says: {res}"

        return advice  # This is unreachable. You might want to review this part.

    async def _arun(
        self,
        query: str,
        run_manager=None,
    ) -> str:
        return await self._run(query, run_manager)

class HumanInputChainlit(BaseTool):
    """Tool that adds the capability to ask user for input."""

    name = "human"
    description = (
        "You can ask a human for guidance when you think you "
        "got stuck or you are not sure what to do next. "
        "The input should be a question for the human."
    )

    async def _run(
        self,
        query: str,
        run_manager=None,
    ) -> str:
        """Use the Human input tool."""
        res = await cl.AskUserMessage(content=query).send()
        return res["content"]

    async def _arun(
        self,
        query: str,
        run_manager=None,
    ) -> str:
        """Use the Human input tool."""
        res = await cl.AskUserMessage(content=query).send()
        return res["content"]

planet_tools = [
    PlanetTool(name="Mercury", description="Mercury deals with communication, reasoning, and intellect."),
 
]

@cl.on_chat_start
async def start():
    llm = ChatOpenAI(temperature=0.7, streaming=True)
    llm1 = OpenAI(temperature=0.7, streaming=True)
    llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

    human_tool = HumanInputChainlit()

    tools = [
        human_tool,
        *planet_tools
    ]
    agent = initialize_agent(
        tools, llm1, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )
    cl.user_session.set("agent", agent)
    cl.user_session.set("ht", human_tool)  # Fixed indentation


def generate_report(name: str, year: int, month: int, day: int, hour: int, minutes: int, city: str, nation: str = None) -> str:
    
    user = AstrologicalSubject(name, year, month, day, hour, minutes, city, nation)

    def print_all_data(user: AstrologicalSubject) -> str:
        output = "\n"
        output += "NAME: " + user.name + "\n"
        output += "PLANET     POSITION\n"
        output += "                      \n" 
        output += f"Sun:       {user.sun['sign']} {round(user.sun['pos'], 3)} in {user.sun['house']}\n"
        output += f"Moon:      {user.moon['sign']} {round(user.moon['pos'], 3)} in {user.moon['house']}\n"
        output += f"Mercury:   {user.mercury['sign']} {round(user.mercury['pos'], 3)} in {user.mercury['house']}\n"
        output += f"Venus:     {user.venus['sign']} {round(user.venus['pos'], 3)} in {user.venus['house']}\n"
        output += f"Mars:      {user.mars['sign']} {round(user.mars['pos'], 3)} in {user.mars['house']}\n"
        output += f"Jupiter:   {user.jupiter['sign']} {round(user.jupiter['pos'], 3)} in {user.jupiter['house']}\n"
        output += f"Saturn:    {user.saturn['sign']} {round(user.saturn['pos'], 3)} in {user.saturn['house']}\n"
        output += f"Uranus:    {user.uranus['sign']} {round(user.uranus['pos'], 3)} in {user.uranus['house']}\n"
        output += f"Neptune:   {user.neptune['sign']} {round(user.neptune['pos'], 3)} in {user.neptune['house']}\n"
        output += f"Pluto:     {user.pluto['sign']} {round(user.pluto['pos'], 3)} in {user.pluto['house']}\n"
        output += "\nHOUSES\n"
        output += f"House Cusp 1 (Ascendant):     {user.first_house['sign']}  {round(user.first_house['pos'], 3)}\n"
        output += f"House Cusp 2:                 {user.second_house['sign']}  {round(user.second_house['pos'], 3)}\n"
        output += f"House Cusp 3:                 {user.third_house['sign']}  {round(user.third_house['pos'], 3)}\n"
        output += f"House Cusp 4 (IC):            {user.fourth_house['sign']}  {round(user.fourth_house['pos'], 3)}\n"
        output += f"House Cusp 5:                 {user.fifth_house['sign']}  {round(user.fifth_house['pos'], 3)}\n"
        output += f"House Cusp 6:                 {user.sixth_house['sign']}  {round(user.sixth_house['pos'], 3)}\n"
        output += f"House Cusp 7 (Descendant):    {user.seventh_house['sign']}  {round(user.seventh_house['pos'], 3)}\n"
        output += f"House Cusp 8:                 {user.eighth_house['sign']}  {round(user.eighth_house['pos'], 3)}\n"
        output += f"House Cusp 9:                 {user.ninth_house['sign']}  {round(user.ninth_house['pos'], 3)}\n"
        output += f"House Cusp 10 (Midheaven):    {user.tenth_house['sign']}  {round(user.tenth_house['pos'], 3)}\n"
        output += f"House Cusp 11:                {user.eleventh_house['sign']}  {round(user.eleventh_house['pos'], 3)}\n"
        output += f"House Cusp 12:                {user.twelfth_house['sign']}  {round(user.twelfth_house['pos'], 3)}\n"
        output += "\n"
        return output
    
    user_report = print_all_data(user)
    
    return user_report

async def get_planet_advice(planet_tool: PlanetTool, user_situation: str, user_chart: Dict[str, Dict[str, Any]]) -> str:
    advice = await planet_tool._run(user_situation, user_chart)
    return f"{planet_tool.planet_name} says: {advice}"

DATE_FORMAT = "%d/%m/%Y"
TIME_FORMAT = "%I:%M %p"

PLANETS = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

# ... Other functions remain unchanged ...
TESTING = True  # Define TESTING if it isn't defined elsewhere

@cl.on_message
async def main(message):
    agent = cl.user_session.get("agent")  # type: AgentExecutor
    ht = cl.user_session.get("ht")
    birth_data = cl.user_session.get("birth_data")
    user_report = cl.user_session.get("user_report")

    if not birth_data:
        if TESTING:
            birth_data = {
                "date": "12/04/1998",
                "time": "08:20 AM",
                "place": "Simferopol"
            }
            cl.user_session.set("birth_data", birth_data)
        else:
            # Prompt the user for birth data
            birth_date = await validate_input(ht, "What's your birth date? (e.g. DD/MM/YYYY)", validate_date)  
            birth_time = await validate_input(ht, "What's your birth time? (e.g. HH:MM AM/PM)", validate_time)
            birth_place = await validate_input(ht, "Where were you born? (City, Country)", validate_place)

            birth_data = {"date": birth_date, "time": birth_time, "place": birth_place}
            cl.user_session.set("birth_data", birth_data)
     
        confirmation_message = f"Thank you for providing your details. Here's what I gathered:\n"\
                               f"Birth Date: {birth_data['date']}\n"\
                               f"Birth Time: {birth_data['time']}\n"\
                               f"Birth Place: {birth_data['place']}\n"\
                               f"Now, please tell me about your situation."

        await cl.Message(content=confirmation_message).send()
        return

    if not user_report:
        if TESTING:
            user_report = "Placeholder for user's astrological report."
        else:
            # Use name placeholder or consider asking user for name
            user_name = "User"
            user_report = generate_report(user_name, int(birth_data['date'].split('/')[2]), int(birth_data['date'].split('/')[1]), 
                                          int(birth_data['date'].split('/')[0]), int(birth_data['time'].split(':')[0]), 
                                          int(birth_data['time'].split(':')[1].split()[0]), birth_data['place'])
        
        cl.user_session.set("user_report", user_report)

        combined_advice = f"Your Astrological Chart: {user_report}"
        await cl.Message(content=combined_advice).send()
        return

    res = await agent.arun(message, callbacks=[cl.AsyncLangchainCallbackHandler()])
    await cl.Message(content=res).send()