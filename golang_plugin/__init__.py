from airflow.plugins_manager import AirflowPlugin

from golang_plugin.operators import GolangOperator

class GolangPlugin(AirflowPlugin):
    name = "golang_plugin"
    operators = [
        GolangOperator
    ]