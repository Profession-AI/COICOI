from pydantic_ai import Agent
from models._base_model import BaseModel
from models._keys_manager import load_key
from models._response_processor import ResponseProcessorMixin
from models._prompt_executor import PromptExecutorMixin
from typing import Sequence, Dict, Union
from tokens.token_counter import TokenCounter
from tokens.token_cost import TokenCost
from typing import override
from prompts.prompt_chain import PromptChain
from prompts.prompt import Prompt

class Model(BaseModel, ResponseProcessorMixin, PromptExecutorMixin):
    def __init__(
        self, 
        provider_name: str, 
        model_name: str, 
        system_prompt: str | Sequence[str] = (),
        count_tokens: bool = False, 
        count_cost: bool = False
    ):
        """
        Initialize Model with provider and model name.
        
        Args:
            provider_name: Name of the provider (e.g., 'openai', 'anthropic')
            model_name: Name of the model (e.g., 'gpt-4', 'claude-3')
            system_prompt: System prompt or sequence of prompts
            count_tokens: Whether to count tokens for each request
            count_cost: Whether to calculate costs for each request
        """
        super().__init__(count_tokens, count_cost)
        load_key(provider_name)

        self.provider_name = provider_name
        self.model_name = model_name
        self._agent = Agent(provider_name + ":" + model_name, system_prompt=system_prompt)

    @override
    async def ask_async(self, prompt: Union[str, Prompt, PromptChain]) -> Dict:
        """
        Ask the model asynchronously.
        
        Args:
            prompt: The prompt or prompt chain to process
            
        Returns:
            Dictionary containing the response and optional stats
        """
        response = await self._execute_async(prompt, self._agent)
        return self._process_response(
            prompt,
            response,
            self.provider_name,
            self.model_name,
            self._count_tokens,
            self._count_cost
        )

    @override
    def ask(self, prompt: Union[str, Prompt, PromptChain]) -> Dict:
        """
        Ask the model synchronously.
        
        Args:
            prompt: The prompt or prompt chain to process
            
        Returns:
            Dictionary containing the response and optional stats
        """
        response = self._execute(prompt, self._agent)
        return self._process_response(
            prompt,
            response,
            self.provider_name,
            self.model_name,
            self._count_tokens,
            self._count_cost
        )

    def _post_process_response(self, question: str, answer: str) -> Dict:
        """
        Process the response and add optional token and cost information.
        
        Args:
            question: The input question
            answer: The model's answer
            
        Returns:
            Dictionary containing the response and optional stats
        """
        response = {
            "input": question, 
            "output": answer, 
            "model": {
                "provider": self.provider_name, 
                "name": self.model_name
            }
        }
        
        if self._count_tokens or self._count_cost:
            tokens = None
            if self._count_tokens:
                tokens = TokenCounter().count(self.model_name, question, answer)
                response["tokens"] = tokens
                
            if self._count_cost and tokens:
                cost = TokenCost().compute(
                    self.provider_name, 
                    self.model_name, 
                    tokens["input_tokens"], 
                    tokens["output_tokens"]
                )
                response["cost"] = cost
                
        return response


if __name__ == "__main__":
    # Initialize with counting preferences
    model = Model(
        provider_name="openai",
        model_name="gpt-4o-mini",
        count_tokens=True,
        count_cost=True
    )
    
    # Example with simple prompt
    result = model.ask("What is the capital of France?")
    print("\nSimple prompt result:")
    print(result)
    
    # Example with prompt chain
    chain = PromptChain([
        "What is the capital of France?",
        "Based on the previous answer, what is its population?"
    ])
    result = model.ask(chain)
    print("\nPrompt chain result:")
    print(result)