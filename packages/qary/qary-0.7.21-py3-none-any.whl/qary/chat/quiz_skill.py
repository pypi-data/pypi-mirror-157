# qary.chat.quiz_skill (v2 Jose QuizBot format)
""" Load *.v2.dialog.yml files and execute recognize_intent() function:

  Rule-based (intent recognition and templated responses) chatbot dialog engine for quizzes
  by Jose Robins


  Inputs:
    state name (str): e.g. 'language-selected-english'
    user utterance (str): 'Hello chatobt'
  Outputs:
    id (str): state name
    text: bot utterance
"""
import logging

from qary.chat.v2 import WELCOME_STATE_NAME
from qary.chat.v2 import INTERN_QUIZ_PATH
from qary.chat.v2 import load_dialog
from qary.chat.v2 import TurnsPreparation
from qary.chat.v2 import get_nxt_cndn_match_mthd_dict
from qary.chat.understanders import check_match

log = logging.getLogger(__name__)


class Skill:
    r"""Skill for Quiz"""

    def __init__(self, datafile=None, turns_list=None, use_nlp=False):
        """If datafile is not given, the turns list of dicts can directly be passed to seed the data
        This would be useful for testing purposes and such
        """
        self.datafile = datafile
        self.turns = {}
        self.use_nlp = use_nlp
        # if turns is passed, then you should not set the datafile

        self.turns_input = turns_list
        if not self.turns_input:
            self.turns_input = load_dialog(datafile or INTERN_QUIZ_PATH)
        log.warning(f'self.turns_input: {self.turns_input}')
        # Do more complex operations using the helper '_TurnsPreparation' class
        turns_preparation = TurnsPreparation(
            turns_list=self.turns_input, use_nlp=self.use_nlp)
        log.warning(f'self.turns_input: {self.turns_input}')
        self.turns = turns_preparation.prepare_turns()
        log.warning(f'self.turns: {self.turns}')
        self.state_name = None

    def find_next_state(self, statement, method, nxt_cndn_match_mthd_dict):
        for next_state_option in nxt_cndn_match_mthd_dict[method]:
            match_response = check_match(
                statement, next_state_option, method
            )

            match_found = match_response[0]
            self.state_name = match_response[1]

            if match_found:
                return match_found

    def reply(self, statement, context=None):
        r"""Except for the welcome state, all other states are mere recordings of the quiz responses

        Examples:
            #TODO
        """
        if statement in [None, 'none']:
            statement = None

        # if in initial state, before __WELCOME__ state
        if (self.state_name is None or not self.state_name
                or self.state_name in (WELCOME_STATE_NAME, '0', 'none', 'None')):
            self.state_name = WELCOME_STATE_NAME
            log.warning(f'self.turns: {self.turns}')
            self.current_turn = self.turns.get(self.state_name)
            if self.current_turn is None:
                response = ""
            else:
                log.warning(f'self.state_name: {self.state_name}')
                log.warning(f'self.turns: {self.turns}')
                log.warning(f'type(self.current_turn): {type(self.current_turn)}')
                response = '\n'.join(self.current_turn['bot'])
        else:
            nxt_cndn = self.current_turn['next_condition']
            nxt_cndn_match_mthd_dict = get_nxt_cndn_match_mthd_dict(nxt_cndn)
            # for match_method_keyword in ['EXACT', '']
            match_found = False

            for matcher in 'EXACT LOWER CASE_SENSITIVE_KEYWORD KEYWORD NORMALIZE'.split():
                match_found = self.find_next_state(statement, matcher, nxt_cndn_match_mthd_dict)
                if match_found:
                    break

            if not match_found:
                self.state_name = nxt_cndn_match_mthd_dict[None][0][1]
            self.current_turn = self.turns.get(self.state_name or '', None)
            if self.current_turn is not None:
                response = self.current_turn.get('bot') or ''
                if not isinstance(response, str):
                    response = '\n'.join(response)
            else:
                response = (
                    'Session is already over! Type "quit" to exit or press "Enter" for a '
                    'new session'
                )
        return [(1.0, response)]
