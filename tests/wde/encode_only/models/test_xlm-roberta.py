import pytest
import random
from typing import TypeVar
from transformers import BatchEncoding, BatchFeature
import torch
import torch.nn as nn
from tests.wde.utils import HfRunner, VllmRunner, compare_embeddings

_T = TypeVar("_T", nn.Module, torch.Tensor, BatchEncoding, BatchFeature)


@pytest.fixture(scope="session")
def hf_runner():
    return HfRunner


@pytest.fixture(scope="session")
def vllm_runner():
    return VllmRunner


@pytest.fixture(scope="session")
def example_prompts():
    prompts = [
        "Hello, my name is",
        "The president of the United States is",
        "The capital of France is",
        "The future of AI is",
    ] * 11
    random.shuffle(prompts)
    return prompts


MODELS = ['FacebookAI/xlm-roberta-base', 'FacebookAI/xlm-roberta-large']


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("dtype", ["half"])
@pytest.mark.parametrize("max_num_seqs", [2, 3, 5, 7])
@pytest.mark.parametrize("scheduling", ["sync", "async", "double_buffer"])
@torch.inference_mode
def test_models(hf_runner, vllm_runner, example_prompts, model: str,
                dtype: str, max_num_seqs: int, scheduling: str) -> None:
    with hf_runner(model, dtype=dtype) as hf_model:
        hf_outputs = hf_model.encode(example_prompts)

    with vllm_runner(model,
                     dtype=dtype,
                     max_num_seqs=max_num_seqs,
                     scheduling=scheduling) as vllm_model:
        vllm_outputs = vllm_model.encode(example_prompts)

    similarities = compare_embeddings(hf_outputs, vllm_outputs)
    all_similarities = torch.stack(similarities)
    tolerance = 1e-2
    assert torch.all((all_similarities <= 1.0 + tolerance)
                     & (all_similarities >= 1.0 - tolerance)
                     ), f"Not all values are within {tolerance} of 1.0"
