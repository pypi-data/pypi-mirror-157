import builtins
from keyword import iskeyword

from RhcsQeSdk.core.cli.cli import CLI
from RhcsQeSdk.core.runner.runner import Runner
from RhcsQeSdk.core.utilities.execute_command import ExecuteCommandMixin
from RhcsQeSdk.core.utilities.parallel_executor import ParallelExecutor
from RhcsQeSdk.core.utilities.redefine_args import RedefineArgs
from RhcsQeSdk.core.utilities.workflow import get_module

execute_command_mixin = ExecuteCommandMixin()
METHOD_MAP = dict(
    {
        "must_pass": execute_command_mixin.must_pass,
        "must_fail": execute_command_mixin.must_fail,
    }
)


class ConfigRun:
    def __init__(
        self,
        cluster_name,
        ceph_cluster_dict,
        is_redefine_args=True,
        is_root=False,
    ):
        self.cli_obj = CLI()
        self.cluster_name = cluster_name
        self.ceph_cluster_dict = ceph_cluster_dict
        self.parallel_executor = ParallelExecutor()
        self.fail = False
        self.is_redefine_args = is_redefine_args
        self.is_root = is_root

    def redefine_service(self, method):
        """
        This method is used to rename the inbuilt method by concatenating underscore.
        Args:
          method(str): Takes inbuilt method name as input.

        Returns:
          method(str): Modified method name.

        Example: changes the inbuilt keyword 'import' to 'import_'.
        """
        if "-" in str(method):
            method = str(method).replace("-", "_")
        if self.check_for_builtins(method):
            method = method + "_"
        return method

    def check_for_builtins(self, service):
        """
        This method is used to check whether the service is a inbuilt function.
        If it is an inbuilt function it is modified.
        Args:
          service(str): name of the method

        Returns:
          None
        """
        if iskeyword(service) or service in dir(builtins):
            return True
        else:
            for key in builtins.__dict__.keys():
                if service in dir(builtins.__dict__[key]):
                    return True
            return False

    def get_must_key(self, test_config):
        """
        This method is used to check whether test has to pass or fail or raise an exception mandatorily.
        Args:
          test_config(Dict): dictionary consists of test configuration in key-value pair.
        Returns:
          must_present_key(key): a key [must_pass | must_fail ]
        """
        for must_present_key in METHOD_MAP.keys():
            if test_config.get(must_present_key):
                must_present_key = must_present_key
            else:
                must_present_key = "must_pass"
            return must_present_key

    def run_config(self, config):
        for step in config:
            if step.get("parallel"):
                tasks = []
                for config_pll in step.get("parallel"):
                    tasks.append((self.run_step, config_pll))
                self.parallel_executor.run(tasks)
            if not self.run_step(step):
                break
        if self.fail:
            return False
        else:
            return True

    def run_step(self, step, env_config=None):
        runner = self.build_runner(step, env_config)
        runner.run()
        if runner.step_output.get("status") == "fail":
            self.fail = True
            return False
        return True

    def build_runner(self, step, env_config=None):
        cls = step.get("class")
        method = step.get("method")
        component = step.get("component")
        method = self.redefine_service(method)
        kw = {
            "cluster_name": self.cluster_name,
            "ceph_cluster_dict": self.ceph_cluster_dict,
            "step": step,
        }
        if self.is_redefine_args:
            args = RedefineArgs().get_args(kw=kw)
        else:
            args = step.get("args")
        method = self.redefine_service(method)
        role = step.get("role")
        must_present_key = self.get_must_key(step)
        module_method = get_module(
            obj=self.cli_obj, component=component, module=cls, service=method
        )
        must_method = METHOD_MAP.get(must_present_key)
        step_output = {"status": None, "result": None}
        runner = Runner(
            cluster_name=self.cluster_name,
            roles=role,
            method=module_method,
            must_method=must_method,
            kwargs=args,
            ceph_cluster_dict=self.ceph_cluster_dict,
            parallel=True,
            step_output=step_output,
            is_root=self.is_root,
            env_config=env_config,
        )
        return runner
