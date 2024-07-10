import asyncio

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.memory_util import generate_memories
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel

from zhiwo.app.biz.gStore.query import get_answer_from_gStore, validate_relations


default_round = 2

default_eval_threshold = 60

default_retry_count = 2

class Ccks2024PeoplePlanner(Planner):
    """Discussion planner class."""

    def invoke(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """
        planner_config = agent_model.plan.get('planner')
        sub_agents = self.generate_sub_agents(planner_config)
        return self.agents_run(sub_agents, planner_config, planner_input, input_object)

    @staticmethod
    def generate_sub_agents(planner_config: dict) -> dict:
        """Generate sub agents.

        Args:
            planner_config (dict): Planner config object.
        Returns:
            dict: Planner agents.
        """
        agents = dict()
        participant = planner_config.get('participant', {})
        participant_names = participant.get('name', [])
        if len(participant_names) == 0:
            raise NotImplementedError
        agents = list()
        for participant_name in participant_names:
            agents.append((participant_name, AgentManager().get_instance_obj(participant_name)))
        return agents

    def agents_run(self, agents: list, planner_config: dict, agent_input: dict, input_object: InputObject) -> dict:
        """Planner agents run.

        Args:
            agents (dict): Planner agents.
            planner_config (dict): Planner config object.
            agent_input (dict): Planner input object.
            input_object (InputObject): Agent input object.
        Returns:
            dict: The planner result.
        """
        result: dict = dict()

        retry_count = planner_config.get('retry_count', default_retry_count)

        LOGGER.info(f"The question is {agent_input.get(self.input_key)}")
        LOGGER.info(f"The participant agents are {'|'.join([i[0] for i in agents])}")
        for count in range(retry_count):
            LOGGER.info(f"Starting peer agents, retry_count is {count}.")
            agent_input['retry_count'] = count
            if 'error' in agent_input:
                del agent_input['error']
            for agent_name, agent in agents:
                LOGGER.info("------------------------------------------------------------------")
                LOGGER.info(f"Start: agent is {agent_name}.")
                LOGGER.info(f"agent_input is: {agent_input}")
                # invoke participant agent
                agent_output: OutputObject = agent.run(**agent_input)
                agent_input = agent_output.to_dict()
                LOGGER.info(f"the agent {agent_name} result is:\n {agent_input}")
                if agent_name == "1_get_sparql_agent":
                    sparql = agent_input.get('sparql', '')
                    entities = agent_input.get('entities', [])
                    relations = agent_input.get('relations', [])
                    if validate_relations(relations):
                        LOGGER.info(f"The sparql is {sparql}")
                        answer,ok = get_answer_from_gStore(sparql)

                        if ok:
                            LOGGER.info(f"The answer is {answer}")
                            agent_input['result'] = answer
                            question_type = agent_input.get('question_type', '')
                            need_further_inference = agent_input.get('need_further_inference', True)
                            # 不再需要进一步3_get_answer_agent推理
                            if question_type == '数据查询' and not need_further_inference:
                                agent_input['answer'] = answer
                                LOGGER.info(f"The answer is {answer}")
                                return agent_input
                        else:
                            LOGGER.info(f"The sparql is error query")
                            agent_input['error'] = 'The sparql is error query'
                            log_ = agent_input.get('log', [])
                            log_.append(f'the sparql is error query：{sparql}')
                            agent_input['log'] = log_
                    else:
                        LOGGER.info(f"The relations is error")
                        agent_input['error'] = 'The relations is error'
                        log_ = agent_input.get('log', [])
                        log_.append(f'the relations is error：{relations}')
                        agent_input['log'] = log_
                error = agent_input.get('error', '')
                if error:
                    LOGGER.info(f"The agent {agent_name} error is {error}")
                    break
            if agent_input.get('answer', ''):
                return agent_input
        # finally invoke host agent
        return agent_input
