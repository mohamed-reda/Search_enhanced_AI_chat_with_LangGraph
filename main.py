import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph.message import add_messages

# Load environment variables from .env file
load_dotenv()
tavily = os.getenv("TAVILY_API_KEY")

model = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    model="microsoft_phi-4-mini-instruct",
)


class State(TypedDict):
    # The messages key holds a list of messages.
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# Create a tool and bind it to the language model.
tool = TavilySearchResults(max_results=2)
tools = [tool]
model_with_tools = model.bind_tools(tools)

from langgraph.prebuilt import ToolNode, tools_condition


def bot(state: State):
    print(state["messages"])
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# Set conditional routing so that if the bot wants to use a tool, it goes to the "tools" node.
graph_builder.add_conditional_edges("bot", tools_condition)
graph_builder.add_node("bot", bot)
graph_builder.set_entry_point("bot")

# Use the memory saver in a with block so it stays active during use.
with SqliteSaver.from_conn_string(":memory:") as memory:
    graph = graph_builder.compile(checkpointer=memory)

    config = {"configurable": {"thread_id": 1}}

    user_input = "Mohamed Reda has a 100 kids"
    events = graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values")
    for event in events:
        event["messages"][-1].pretty_print()

    user_input = "based on the chat history, How many that Mohamed Reda has?"
    events = graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values")
    for event in events:
        event["messages"][-1].pretty_print()

    snapshot = graph.get_state(config)
    print(snapshot)

"""
================================ Human Message =================================

Hi there! My name is Mohamed Reda. and I have been happy for 100 years
[HumanMessage(content='Hi there! My name is Mohamed Reda. and I have been happy for 100 years', additional_kwargs={}, response_metadata={}, id='b2124a39-297a-4680-b7a2-60d28c3aad4e')]
================================== Ai Message ==================================

Greetings, Mohamed Reda! It's wonderful to meet someone with such a joyful life experience of over one hundred joyous decades!


[END_TOOL_REQUEST]
================================ Human Message =================================

based on the chat history, How many years have Mohamed Reda been happy for?
[HumanMessage(content='Hi there! My name is Mohamed Reda. and I have been happy for 100 years', additional_kwargs={}, response_metadata={}, id='b2124a39-297a-4680-b7a2-60d28c3aad4e'), AIMessage(content="Greetings, Mohamed Reda! It's wonderful to meet someone with such a joyful life experience of over one hundred joyous decades!\n\n\n[END_TOOL_REQUEST]", additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 29, 'prompt_tokens': 637, 'total_tokens': 666, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'microsoft_phi-4-mini-instruct', 'system_fingerprint': 'microsoft_phi-4-mini-instruct', 'finish_reason': 'stop', 'logprobs': None}, id='run-ac479abe-4a02-45d9-bf03-b2ee79bc8d09-0', usage_metadata={'input_tokens': 637, 'output_tokens': 29, 'total_tokens': 666, 'input_token_details': {}, 'output_token_details': {}}), HumanMessage(content='based on the chat history, How many years have Mohamed Reda been happy for?', additional_kwargs={}, response_metadata={}, id='f54c0619-e635-4433-bdf2-78a8aa3125d8')]
================================== Ai Message ==================================

Mohamed Reda has been happy for 100 years.
StateSnapshot(values={'messages': [HumanMessage(content='Hi there! My name is Mohamed Reda. and I have been happy for 100 years', additional_kwargs={}, response_metadata={}, id='b2124a39-297a-4680-b7a2-60d28c3aad4e'), AIMessage(content="Greetings, Mohamed Reda! It's wonderful to meet someone with such a joyful life experience of over one hundred joyous decades!\n\n\n[END_TOOL_REQUEST]", additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 29, 'prompt_tokens': 637, 'total_tokens': 666, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'microsoft_phi-4-mini-instruct', 'system_fingerprint': 'microsoft_phi-4-mini-instruct', 'finish_reason': 'stop', 'logprobs': None}, id='run-ac479abe-4a02-45d9-bf03-b2ee79bc8d09-0', usage_metadata={'input_tokens': 637, 'output_tokens': 29, 'total_tokens': 666, 'input_token_details': {}, 'output_token_details': {}}), HumanMessage(content='based on the chat history, How many years have Mohamed Reda been happy for?', additional_kwargs={}, response_metadata={}, id='f54c0619-e635-4433-bdf2-78a8aa3125d8'), AIMessage(content='Mohamed Reda has been happy for 100 years.', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 12, 'prompt_tokens': 687, 'total_tokens': 699, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'microsoft_phi-4-mini-instruct', 'system_fingerprint': 'microsoft_phi-4-mini-instruct', 'finish_reason': 'stop', 'logprobs': None}, id='run-9588bde7-cd4d-4dd0-b902-c25704028fd0-0', usage_metadata={'input_tokens': 687, 'output_tokens': 12, 'total_tokens': 699, 'input_token_details': {}, 'output_token_details': {}})]}, next=(), config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f00752e-2423-64c5-8004-97fe0fc87187'}}, metadata={'source': 'loop', 'writes': {'bot': {'messages': [AIMessage(content='Mohamed Reda has been happy for 100 years.', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 12, 'prompt_tokens': 687, 'total_tokens': 699, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_name': 'microsoft_phi-4-mini-instruct', 'system_fingerprint': 'microsoft_phi-4-mini-instruct', 'finish_reason': 'stop', 'logprobs': None}, id='run-9588bde7-cd4d-4dd0-b902-c25704028fd0-0', usage_metadata={'input_tokens': 687, 'output_tokens': 12, 'total_tokens': 699, 'input_token_details': {}, 'output_token_details': {}})]}}, 'thread_id': 1, 'step': 4, 'parents': {}}, created_at='2025-03-22T19:21:41.318751+00:00', parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1f00752e-130f-6d26-8003-38ca84a2516f'}}, tasks=())

Process finished with exit code 0
"""
