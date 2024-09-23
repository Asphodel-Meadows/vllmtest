from vllm.wde.core.workflow import Workflow


class PrefillOnlyWorkflow(Workflow):

    InputProcessor: str = ("vllm.wde.prefill_only.processor."
                           "input_processor:PrefillOnlyModelInputProcessor")
    RequestProcessor: str = (
        "vllm.wde.prefill_only.processor."
        "input_processor:PrefillOnlyModelRequestProcessor")
    OutputProcessor: str = ("vllm.wde.prefill_only.processor."
                            "output_processor:PrefillOnlyModelOutputProcessor")
    ModelInputBuilder: str = (
        "vllm.wde.prefill_only.processor."
        "model_input_builder:PrefillOnlyModelInputBuilder")
    Worker: str = "vllm.wde.prefill_only.worker.gpu_worker:Worker"
    Executor: str = "vllm.wde.prefill_only.executor.gpu_executor"
    Scheduler: str = "vllm.wde.prefill_only.scheduler:PrefillOnlyScheduler"
    AttnBackend: str = ("vllm.wde.prefill_only.layers."
                        "attention.selector:AttnBackend")

    @classmethod
    def from_engine(cls, engine):
        workflow = cls()
        if engine.engine_config.scheduler_config.scheduling in ["sync"]:
            workflow.Executor += ":GPUExecutor"
        elif engine.engine_config.scheduler_config.scheduling in [
                "async", "double_buffer"
        ]:
            workflow.Executor += ":GPUAsyncExecutor"

        return workflow
