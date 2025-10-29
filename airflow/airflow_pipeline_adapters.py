from datetime import datetime
from pipelines.DataPipeline import StageResult, PipelineContext
from commons.parametrization.PythonParametrization import PythonParametrization
from commons.utils.LoggingUtils import instantiate_logging
# Airflow specific configuration
from airflow.operators.python import PythonOperator
from airflow.models import DAG


class AirflowPipelineContext(PipelineContext):

    @staticmethod
    def from_airflow_context(airflow_kwargs) -> PipelineContext:
        """
        Factory method to construct a PipelineContext from Airflow runtime context.
        """
        task_instance = airflow_kwargs.get("ti")  # Airflow TaskInstance
        dag_id = task_instance.dag_id if task_instance else "unknown_dag"
        task_id = task_instance.task_id if task_instance else "unknown_task"
        execution_date = airflow_kwargs.get("execution_date", datetime.utcnow())
        # Setup logger
        logger = instantiate_logging(log_id=f"{dag_id}.{task_id}")
        # Load config file
        config_file =  airflow_kwargs.get("configuration_file")
        params = PythonParametrization(config_ini_file=config_file)

        # Optionally inject Airflow context info
        params.airflow_context = {
            "dag_id": dag_id,
            "task_id": task_id,
            "execution_date": execution_date,
        }
        ctx = PipelineContext()
        ctx.params = params
        ctx.logger = logger
        return ctx



class AirflowStageMixin:
    """
    A mixin that adapts any BaseStage to be run as an Airflow PythonOperator task.

    Usage:
        class MyStage(AirflowStageMixin, BaseStage):
            ...

        task = MyStage.to_task(dag, ctx_factory=PipelineContext.from_airflow_context)
    """

    @classmethod
    def to_task(cls, dag: DAG, ctx_factory, **kwargs):
        """Convert this Stage class into a PythonOperator task."""
        def _wrapped(**airflow_kwargs):
            # Create the pipeline context from Airflow’s execution context
            ctx = ctx_factory(airflow_kwargs)

            # Instantiate and run the stage
            stage = cls(name=cls.__name__)
            result, message = stage.run(ctx)

            # Fail Airflow task if the stage failed
            if result not in (StageResult.SUCCESS, StageResult.SUCCESS_WITH_WARNINGS):
                raise Exception(f"Stage {cls.__name__} failed: {message}")
            return message

        return PythonOperator(
            task_id=cls.__name__,
            python_callable=_wrapped,
            provide_context=True,
            dag=dag,
            **kwargs,
        )