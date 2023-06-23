
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

from langchain.tools import BaseTool

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
)
from langchain.output_parsers import RegexParser

class AgentTL():
    @classmethod
    def __init__(self, model):
        self.model = model
        self.instructions = """
        This is to paraphrase the input message with intergections words in Japanese to express emotions.
        For example, use lots of intergection words like うふふ , あぁ for smiling
        Use うう for angry. Use あーら , パチッ for excitement.

        Output the short sentence Japanese ONLY to express emotions.

        """
        self.message_history = []
        self.ret = 0

    def reset(self):
        self.message_history = [
            SystemMessage(content=self.instructions),
        ]
    
    def run(self, words):
        obs_message = f"""
        {words}
        """
        self.message_history.append(HumanMessage(content=obs_message))
        act_message = self.model(self.message_history)
        self.message_history.append(act_message)
        self.message_history = [];
        return act_message.content

agent_chain = AgentTL(model=ChatOpenAI(temperature=1, model_name = 'gpt-3.5-turbo'))
agent_chain.reset()
