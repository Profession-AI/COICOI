from monoai._agents import MultiAgent
from monoai.prompts.prompt_chain import PromptChain
from monoai.tools import WebSearch


multi_agent = MultiAgent(
    models=[
        {
            "provider": "openai",
            "model": "gpt-4o-mini"
        },
        {
            "provider": "openai",
            "model": "gpt-4o-mini"
        }
    ],
    tools=[WebSearch().get_tool()]
)

chain = PromptChain([
    "What is the capital of France?",
    "Given the city name, tell me its population."
])

result = multi_agent.run(chain)
print(result)
