import os
import torch
from atorch.common.log_utils import default_logger as logger
from atorch.common.util_func import find_free_port


class _DistributedContext:
    LOCAL_RANK = None
    RANK = None
    WORLD_SIZE = None
    BACKEND = None
    INITIALIZED = False
    USE_HOROVOD = False


def local_rank():
    return _DistributedContext.LOCAL_RANK


def rank():
    return _DistributedContext.RANK


def world_size():
    return _DistributedContext.WORLD_SIZE


def backend():
    return _DistributedContext.BACKEND


def _check_env():
    local_rank = os.getenv("LOCAL_RANK")
    if not local_rank:
        logger.warning("LOCAL_RANK env not set. Set as 0")
        os.environ["LOCAL_RANK"] = "0"

    rank = os.getenv("RANK")
    if not rank:
        logger.warning("RANK env not set. Set as 0")
        os.environ["RANK"] = "0"

    world_size = os.getenv("WORLD_SIZE")
    if not world_size:
        logger.warning("WORLD_SIZE env not set. Set as 1")
        os.environ["WORLD_SIZE"] = "1"

    master_addr = os.getenv("MASTER_ADDR")
    if not master_addr:
        logger.warning("MASTER_ADDR env not set. Set as 127.0.0.1")
        os.environ["MASTER_ADDR"] = "127.0.0.1"

    master_port = os.getenv("MASTER_PORT")
    if not master_port:
        port = find_free_port()
        logger.warning("MASTER_PORT env not set. Set as {}".format(port))
        os.environ["MASTER_PORT"] = str(port)


def init_distributed(
    backend="nccl",
    use_horovod=False,
    elastic=False,
    set_cuda_device_using_local_rank=False,
):
    """
    Initializes the distributed contexts. Support DDP and Horovod.

    Arguments:
        backend (str): The backend to use. Supports 'nccl', 'gloo', 'accl'.
        use_horovod (bool): If True, use horovod instead of DDP.
        elastic (bool): If True, supports elastic training.
        set_cuda_device_using_local_rank (bool):
           If True, set cuda device using local rank.
    Return:
        True if initialized successfully. False otherwise.
    """

    backend = backend.lower()
    if backend not in ["nccl", "gloo", "accl"]:
        logger.error("Invalid backend {}".format(backend))
        return False

    _DistributedContext.BACKEND = backend
    _DistributedContext.USE_HOROVOD = use_horovod
    _check_env()

    # init local_rank, rank, world_size from env
    _DistributedContext.LOCAL_RANK = int(os.getenv("LOCAL_RANK"))
    _DistributedContext.RANK = int(os.getenv("RANK"))
    _DistributedContext.WORLD_SIZE = int(os.getenv("WORLD_SIZE"))

    if use_horovod:
        from atorch.distributed.horovod import init_horovod

        status = init_horovod()
        if status is False:
            logger.warning("Failed to init_horovod")
            return False
    else:
        if backend == "accl":
            try:
                # noqa: F401
                import torch_accl
            except ImportError:
                logger.error("import torch_accl failed")
                return False
        # init with init_process_group using env
        torch.distributed.init_process_group(backend, init_method="env://")
        if not torch.distributed.is_initialized():
            logger.error("Failed to init_process_group")
            return False
        torch.distributed.barrier()

    if elastic:
        logger.warning("elastic not supported yet!")

    if set_cuda_device_using_local_rank:
        gpu_num = torch.cuda.device_count()
        if gpu_num == 0:
            logger.warning(
                "No gpu found, set_cuda_device_using_local_rank ignored!"
            )
        else:
            torch.cuda.set_device(local_rank() % gpu_num)
            logger.info("Set cuda device as {}".format(local_rank() % gpu_num))

    logger.info(
        "Distributed contex initialized: "
        "rank={}, local_rank={}, world_size={}".format(
            rank(), local_rank(), world_size()
        )
    )

    _DistributedContext.INITIALIZED = True
    return True


def reset_distributed():
    """
    Reset the distributed context.
    If backend is nccl or gloo, delete the process group.
    """
    if not _DistributedContext.INITIALIZED:
        return
    if _DistributedContext.USE_HOROVOD:
        from atorch.distributed.horovod import reset_horovod

        reset_horovod()
    else:
        torch.distributed.destroy_process_group()

    _DistributedContext.INITIALIZED = False
    _DistributedContext.BACKEND = None
    _DistributedContext.RANK = None
    _DistributedContext.LOCAL_RANK = None
    _DistributedContext.WORLD_SIZE = None
    _DistributedContext.USE_HOROVOD = False
