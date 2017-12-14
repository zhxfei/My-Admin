#!/usr/bin/env python

# import json, logging
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase


#   logging = logging.getLevelName()


class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    or writing your own custom callback plugin

    """

    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.job_id = 0
        self._result_host_all = {}
        self._result_host_ok = {}
        self._result_host_failed = {}
        self._result_host_unreachable = {}
        self._result_host_stdout_lines = {}
        self._result_host_stderr_lines = {}
        self._result_has_stderr_lines = False
        self._result_has_stdout_lines = False

    def v2_runner_on_ok(self, result, **kwargs):
        self.job_id += 1
        host = result._host.get_name() + ' job_' + str(self.job_id)
        self._result_host_all[host] = result._result
        self._result_host_ok[host] = result._result
        if result._result.get('stdout_lines'):
            self._result_has_stdout_lines = True
            self._result_host_stdout_lines[host] = result._result.get('stdout_lines')

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.job_id += 1
        host = result._host.get_name() + ' job_' + str(self.job_id)
        self._result_host_all[host] = result._result
        self._result_host_failed[host] = result._result
        if result._result.get('stderr_lines'):
            self._result_has_stderr_lines = True
            self._result_host_stderr_lines[host] = result._result.get('stderr_lines')

    def v2_runner_on_unreachable(self, result):
        self.job_id += 1
        host = result._host.get_name() + ' job_' + str(self.job_id)
        self._result_host_all[host] = result._result
        self._result_host_unreachable[host] = result._result


def _parse_task(task_lst):
    tasks = []
    if task_lst:
        for task in task_lst:
            module = task.get('module')
            args = task.get('args')
            tasks.append(dict(action=dict(module=module, args=args)))
    return tasks


class AnsibleRun(object):
    Options = namedtuple('Options',
                         ['connection',
                          'module_path',
                          'forks',
                          'become',
                          'become_method',
                          'become_user',
                          'check',
                          'diff',
                          'sudo',
                          'timeout'])

    def __init__(self, hosts, result_callback=None):
        self.loader = DataLoader()
        self.options = AnsibleRun.Options(connection='ssh',
                                          module_path='../../env/lib/python3.5/site-packages/ansible/modules/',
                                          forks=100,
                                          sudo='yes',
                                          become=None,
                                          become_method=None,
                                          become_user='root',
                                          check=False,
                                          diff=False,
                                          timeout=3)
        self.passwords = dict(vault_pass='secret')
        self.hosts = hosts
        self.inventory = InventoryManager(loader=self.loader, sources=['/etc/ansible/hosts'])
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        self.result_callback = result_callback if result_callback is not None else ResultCallback()

    def module_run(self, task_lst):
        """
        task_lst is a list for dict, Just like :
        [
            {
                'module': 'your_self_module',
                'args': 'args=sssss'
            },
            {
                'module': 'shell',
                'args': 'ifconfig'
            }
        ]
        :param task_lst:
        :return None:
        """
        tasks = _parse_task(task_lst)
        play_source = dict(
            name="Ansible Play",
            hosts=self.hosts,
            gather_facts='no',
            tasks=tasks
        )

        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        # actually run it
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
                stdout_callback=self.result_callback,
                # Use our custom callback instead of the ``default`` callback plugin
            )
            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

    def play_book_run(self):
        pass

    def get_result(self, result_type='all'):
        params_allow_lst = ['result_all',
                            'result_ok',
                            'result_stdout_lines',
                            'result_stderr_lines',
                            'result_failed',
                            'result_unreachable']
        assert result_type in params_allow_lst, 'result_type must in {params_allow_lst}'.format(
                                                                        params_allow_lst=params_allow_lst)
        if result_type == 'result_all':
            return self.result_callback._result_host_all
        if result_type == 'result_ok':
            return self.result_callback._result_host_ok
        if result_type == 'result_failed':
            return self.result_callback._result_host_failed
        if result_type == 'result_unreachable':
            return self.result_callback._result_host_unreachable
        if result_type == 'result_stdout_lines':
            if self.result_callback._result_has_stdout_lines:
                return self.result_callback._result_host_stdout_lines
        if result_type == 'result_stderr_lines':
            if self.result_callback._result_has_stderr_lines:
                return self.result_callback._result_host_stderr_lines


def test():
    ansible_client = AnsibleRun('all')
    ansible_client.module_run([
        # {
        #     'module': 'echo',
        #     'args': 'args=sssss'
        # },
        {
            'module': 'shell',
            'args': 'ipconfig'
        }
    ])
    out = ansible_client.get_result('result_all')
    print(out)
    out = ansible_client.get_result('result_ok')
    print(out)
    out = ansible_client.get_result('result_stdout_lines')
    print(out)
    out = ansible_client.get_result('result_failed')
    print(out)
    out = ansible_client.get_result('result_stderr_lines')
    print(out)
    out = ansible_client.get_result('result_unreachable')
    print(out)
