from typing import List


COMPLETE_CONDITION = 'complete'
ACTION_STATUSES = ['failure', 'success']
ALL_COMPLETE_CONDITIONS = [COMPLETE_CONDITION] + ACTION_STATUSES


class Action:
    def __init__(self, use, config=None, params=None, condition=None, template=None):
        self.use = use
        self.params = params or {}
        self.condition = condition.lower() if condition else condition
        self.template = template
        self.config = config

    def is_first_run_action(self):
        return self.condition not in ALL_COMPLETE_CONDITIONS

    def evaluate_condition(self, value):
        return self.condition == value or (value in ACTION_STATUSES and self.condition == COMPLETE_CONDITION)

    def send(self, **params):
        new_params = self.params.copy()
        new_params.update(params)
        self.config.templates.use(self.use).render(**new_params).send()


class Actions:
    def __init__(self, actions, config):
        self._actions: List[Action] = [Action(config=config, **action) for action in actions]
        self.config = config

    def get_first_run_actions(self):
        return filter(lambda x: x.is_first_run_action(), self._actions)

    def get_complete_actions(self):
        return filter(lambda x: not x.is_first_run_action(), self._actions)
