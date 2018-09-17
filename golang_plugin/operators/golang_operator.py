import os
import signal
from subprocess import Popen, STDOUT, PIPE
from tempfile import gettempdir, NamedTemporaryFile

from builtins import bytes

from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.file import TemporaryDirectory
from airflow.utils.operator_helpers import context_to_airflow_vars


class GolangOperator(BaseOperator):

    @apply_defaults
    def __init__(
            self,
            filename,
            xcom_push=False,
            env=None,
            output_encoding='utf-8',
            *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.env = env
        self.xcom_push_flag = xcom_push
        self.output_encoding = output_encoding

    def execute(self, context):
        if self.env is None:
            self.env = os.environ.copy()

        airflow_context_vars = context_to_airflow_vars(
            context, in_env_var_format=True)

        self.env.update(airflow_context_vars)

        self.lineage_data = self.filename

        with TemporaryDirectory(prefix='airflowtmp') as tmp_dir:
            def pre_exec():
                for sig in ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ'):
                    if hasattr(signal, sig):
                        signal.signal(getattr(signal, sig), signal.SIG_DFL)
                os.setsid()

            self.log.info("Running Golang program: %s", self.filename)
            sp = Popen(
                ['go', 'run', self.filename],
                stdout=PIPE, stderr=STDOUT,
                cwd=tmp_dir, env=self.env,
                preexec_fn=pre_exec)

            self.sp = sp

            self.log.info("Output:")
            line = ''
            for line in iter(sp.stdout.readline, b''):
                line = line.decode(self.output_encoding).rstrip()
                self.log.info(line)
            sp.wait()
            self.log.info(
                "Command exited with return code %s",
                sp.returncode
            )

            if sp.returncode:
                raise AirflowException("Golang program failed")

        if self.xcom_push_flag:
            return line

    def on_kill(self):
        self.log.info('Sending SIGTERM signal to Golang runtime process group')
        os.killpg(os.getpgid(self.sp.pid), signal.SIGTERM)
