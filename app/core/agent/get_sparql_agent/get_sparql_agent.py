import json
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject

from langchain_core.output_parsers.json import parse_and_check_json_markdown


class BaseAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']
    
    def output_keys(self) -> list[str]:
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result

class PipelineAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result
    
    
class AnalyzeAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        # agent_input['input'] = input_object.get_data('input')
        return agent_input
    
    def parse_result(self, planner_result: dict) -> dict:
        res = planner_result.pop('output')
        try:
            result = parse_and_check_json_markdown(res, ['question_type', 'need_further_inference','question_analysis'])
            planner_result.update(result)
            return planner_result
        except:
            if planner_result.get('retry_count', 0) >= self.agent_model.profile.get('max_retry_count'):
                planner_result['error'] = f'maximum retries: {self.get_instance_code()}'
                return planner_result
            else:
                planner_result['retry_count'] = planner_result.get('retry_count', 0) + 1
                log_ = planner_result.get('log', [])
                log_.append(f'{self.get_instance_code()} parse error, output: {res}')
                planner_result['log'] = log_
                return self.run(**planner_result).to_dict()
            
    def run(self, **kwargs) -> OutputObject:
        """Agent instance running entry.

        Returns:
            OutputObject: Agent execution result
        """
        self.input_check(kwargs)
        input_object: InputObject = None
        agent_input = kwargs

        planner_result = self.execute(input_object, agent_input)

        agent_result = self.parse_result(planner_result)

        output_object = OutputObject(agent_result)
        return output_object
    

class GetSparqlAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input','question_analysis']

    def output_keys(self) -> list[str]:
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        # agent_input['input'] = input_object.get_data('input')
        # agent_input['question_analysis'] = input_object.get_data('question_analysis')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        res = planner_result.pop('output')
        try:
            result = parse_and_check_json_markdown(res, ['sparql', 'entities','relations'])
            planner_result.update(result)
            return planner_result
        except:
            if planner_result.get('retry_count', 0) >= self.agent_model.profile.get('max_retry_count'):
                planner_result['error'] = f'maximum retries: {self.get_instance_code()}'
                return planner_result
            else:
                planner_result['retry_count'] = planner_result.get('retry_count', 0) + 1
                log_ = planner_result.get('log', [])
                log_.append(f'{self.get_instance_code()} parse error, output: {res}')
                planner_result['log'] = log_
                return self.run(**planner_result)

    def run(self, **kwargs) -> OutputObject:
        """Agent instance running entry.

        Returns:
            OutputObject: Agent execution result
        """
        self.input_check(kwargs)
        input_object: InputObject = None
        agent_input = kwargs

        planner_result = self.execute(input_object, agent_input)

        agent_result = self.parse_result(planner_result)

        output_object = OutputObject(agent_result)
        return output_object

class GetAnswerAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input','question_analysis','sparql']

    def output_keys(self) -> list[str]:
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        # agent_input['input'] = input_object.get_data('input')
        # agent_input['question_analysis'] = input_object.get_data('question_analysis')
        # agent_input['sparql'] = input_object.get_data('sparql')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        res = planner_result.pop('output')
        try:
            result = parse_and_check_json_markdown(res, ['answer'])
            planner_result.update(result)
            return planner_result
        except:
            if planner_result.get('retry_count', 0) >= self.agent_model.profile.get('max_retry_count'):
                planner_result['error'] = f'maximum retries: {self.get_instance_code()}'
                return planner_result
            else:
                planner_result['retry_count'] = planner_result.get('retry_count', 0) + 1
                log_ = planner_result.get('log', [])
                log_.append(f'{self.get_instance_code()} parse error, output: {res}')
                planner_result['log'] = log_
                return self.run(**planner_result)

    def run(self, **kwargs) -> OutputObject:
        """Agent instance running entry.

        Returns:
            OutputObject: Agent execution result
        """
        self.input_check(kwargs)
        input_object: InputObject = None
        agent_input = kwargs

        planner_result = self.execute(input_object, agent_input)

        agent_result = self.parse_result(planner_result)

        output_object = OutputObject(agent_result)
        return output_object