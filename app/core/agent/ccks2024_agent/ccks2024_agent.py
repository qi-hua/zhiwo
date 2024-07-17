import json
import re
from datetime import datetime
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.util.logging.logging_util import LOGGER

from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager

from langchain_core.output_parsers.json import parse_and_check_json_markdown


class GetBackgroundAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']
    
    def output_keys(self) -> list[str]:
        return ['background']
    
    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        return agent_input
    
    def parse_result(self, planner_result: dict) -> dict:
        return planner_result
    
    def run(self, **kwargs) -> OutputObject:
        """Agent instance running entry.

        Returns:
            OutputObject: Agent execution result
        """
        self.input_check(kwargs)
        agent_input = dict()
        agent_input.update(kwargs)
        knowledge = KnowledgeManager().get_instance_obj(self.agent_model.action.get('knowledge',['sparql_train_knowledge'])[0])
        query_input = {
            'query_str': kwargs.get(self.input_keys()[0]),
            'similarity_top_k': self.agent_model.action.get('knowledge_similarity_top_k', 3)
        }
        agent_input['background'] = '\n'.join([doc.text for doc in knowledge.query_knowledge(**query_input)])

        output_object = OutputObject(agent_input)
        
        return output_object
    
class BaseAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']
    
    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        return agent_input
    
    def parse_result(self, planner_result: dict) -> dict:
        planner_result.pop('chat_history')
        planner_result['answered_by'] = self.get_instance_code()
        res = planner_result.pop('output')
        try:
            try:
                result = parse_and_check_json_markdown(res, self.output_keys())
            except:
                # 使用正则表达式进行替换 
                # 将^^<http://www.w3.org/2001/XMLSchema#float> 进行删除
                res = re.sub(r"\^\^\s*<[^>]+>", r'\\"\1\\"', res)
                # 匹配双引号后有'.'的情况（sparql语句中）
                res = re.sub(r"\"([^\"]+)\"(?=\s*\.)", r'\\"\1\\"', res)
                result = parse_and_check_json_markdown(res, self.output_keys())
            planner_result.update(result)
            return planner_result
        except:
            if planner_result.get('retry_count', 0) >= self.agent_model.profile.get('max_retry_count', 2):
                planner_result['error'] = f'maximum retries: {self.get_instance_code()}'
                return planner_result
            else:
                planner_result['retry_count'] = planner_result.get('retry_count', 0) + 1
                log_ = planner_result.get('log', [])
                log_.append(f'{self.get_instance_code()} parse error, output: {res}')
                planner_result['log'] = log_

                # LOGGER.info(f"The parse_result  {planner_result}")
                return self.run(**planner_result).to_dict()

    def run(self, **kwargs) -> OutputObject:
        """Agent instance running entry.

        Returns:
            OutputObject: Agent execution result
        """
        self.input_check(kwargs)
        agent_input = dict()
        agent_input['chat_history'] = kwargs.get('chat_history') or ''
        agent_input['background'] = kwargs.get('background') or ''
        # agent_input['date'] = datetime.now().strftime('%Y-%m-%d')
        agent_input.update(kwargs)
        input_object = InputObject(agent_input)

        planner_result = self.execute(input_object, agent_input)

        agent_result = self.parse_result(planner_result)

        output_object = OutputObject(agent_result)
        return output_object
    
class GetNameAgent(BaseAgent):
    def input_keys(self) -> list[str]:
        return ['input', 'sparql']
    
    def output_keys(self) -> list[str]:
        return ['difficulty_level', 'subjects', 'properties', 'objects', 'sparql']
    
class GetTrainNameAgent(BaseAgent):
    def input_keys(self) -> list[str]:
        return ['input', 'sparql']
    
    def output_keys(self) -> list[str]:
        return ['difficulty_level', 'subjects', 'properties', 'objects', 'entities']


class GetNameAndSparqlAgent(BaseAgent):
    def input_keys(self) -> list[str]:
        return ['input']
    
    def output_keys(self) -> list[str]:
        return ['difficulty_level', 'subjects', 'properties', 'objects', 'sparql']


class ReplaceNameAgent(BaseAgent):
    def input_keys(self) -> list[str]:
        return ['input', 'sparql', 'background', 'difficulty_level', 'subjects', 'properties', 'objects', 'subjects_choices', 'properties_choices', 'objects_choices']
    
    def output_keys(self) -> list[str]:
        return ['best_subjects', 'best_properties', 'best_objects', 'changed_sparql', 'entities']

class ReplaceNameAgainAgent(BaseAgent):
    # ccks2024_replace_name_again_agent
    def input_keys(self) -> list[str]:
        return ['input', 'sparql', 'background', 'difficulty_level', 'subjects', 'properties', 'objects', 'subjects_choices', 'properties_choices', 'objects_choices', 'error_names']
    
    def output_keys(self) -> list[str]:
        return ['best_subjects', 'best_properties', 'best_objects', 'changed_sparql', 'entities']

class GetAnswerAgent(BaseAgent):
    def input_keys(self) -> list[str]:
        return ['input', 'sparql', 'all_triples']
    
    def output_keys(self) -> list[str]:
        return ['analysis', 'need_further_inference', 'next_subjects', 'summarize', 'answers',]
    

class GetAnswerRepeaterAgent(BaseAgent):
    def input_keys(self) -> list[str]:
        return ['input', 'sparql', 'analysis', 'summarize', 'all_triples']
    
    def output_keys(self) -> list[str]:
        return ['analysis', 'need_further_inference', 'next_subjects', 'summarize', 'answers',]