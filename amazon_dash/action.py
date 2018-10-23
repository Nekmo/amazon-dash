from typing import List


COMPLETE_CONDITION = 'complete'
ACTION_STATUSES = ['failure', 'success']
ALL_COMPLETE_CONDITIONS = [COMPLETE_CONDITION] + ACTION_STATUSES


class Action:
    def __init__(self, use, params=None, condition=None, template=None):
        self.use = use
        self.params = params
        self.condition = condition.lower() if condition else condition
        self.template = template

    def is_first_run_action(self):
        return self.condition not in ALL_COMPLETE_CONDITIONS

    def evaluate_condition(self, value):
        return self.condition == value or (value in ACTION_STATUSES and self.condition == COMPLETE_CONDITION)


class Actions:
    def __init__(self, actions):
        self._actions: List[Action] = [Action(**action) for action in actions]

    def get_first_run_actions(self):
        return filter(lambda x: x.is_first_run_action(), self._actions)

    def get_complete_actions(self):
        return filter(lambda x: not x.is_first_run_action(), self._actions)
