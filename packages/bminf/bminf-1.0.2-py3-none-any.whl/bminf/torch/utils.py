import torch
from ..core import Tensor, Memory, Device
import numpy as np
from cpm_kernels.library import cudart
import torch.nn.functional as F

def torch_to_dtype(dtype : torch.dtype) -> np.dtype:
    MAP = {
        torch.float32 : np.float32,
        torch.float64 : np.float64,
        torch.int32 : np.int32,
        torch.int64 : np.int64,
        torch.uint8 : np.uint8,
        torch.int8 : np.int8,
        torch.bool : np.bool8,
        torch.half : np.float16,
        torch.short : np.int16,
    }
    assert dtype in MAP, "unsupported dtype %s" % dtype
    return MAP[dtype]()

def torch_to_tensor(x : torch.Tensor) -> Tensor:
    assert x.is_cuda, "x must be on CUDA device"
    assert x.is_contiguous(), "x must be contiguous"

    return Tensor(
        Memory(x.data_ptr(), x.numel() * x.element_size(), Device(x.device.index)), 
        tuple(x.size()), 
        torch_to_dtype(x.dtype)
    )


def wait_stream(stream1, stream2):
    """
    stream2 wait stream1
    """
    evt = cudart.cudaEventCreate()
    cudart.cudaEventRecord(evt, stream1)
    cudart.cudaStreamWaitEvent(stream2, evt)
    cudart.cudaEventDestroy(evt)

def clone_tensor(x: torch.Tensor) -> torch.Tensor:
    if x.size(-1) % 4 != 0:
        return F.pad(x, (0, 4 - (x.size(-1) % 4)), "constant", 0).contiguous()
    else:
        return x.clone(memory_format=torch.contiguous_format)

def align_mask(last_dim, mask : np.ndarray):
    assert mask.ndim == 2
    assert last_dim >= mask.shape[-1]
    
    if mask.shape[1] != last_dim:
        nw_mask = np.zeros(mask.shape[:-1] + (last_dim,), dtype=np.int8)
        nw_mask[:, :mask.shape[-1]] = mask
        return nw_mask
    else:
        return mask

class ResultClass:
    def __init__(self, **kwargs):
        for kw, val in kwargs.items():
            setattr(self, kw, val)