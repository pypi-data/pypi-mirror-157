import time
import socket
import os
from atorch.common.log_utils import default_logger as logger
from atorch.common.constants import HorovodEnv

try:
    import horovod.torch as hvd
    from horovod.runner.common.util.hosts import (
        get_host_assignments,
        parse_hosts,
    )
    from horovod.runner.util.threads import in_thread
    from horovod.runner.http.http_server import (
        RendezvousServer,
        RendezvousHandler,
        RendezvousHTTPServer,
    )

    _HOROVOD_INSTALLED = True
except ImportError:
    _HOROVOD_INSTALLED = False

_HOST_SEP = ","


class _HorovodContext:
    RENDEZVOUS_SERVER = None


def set_horovod_env(env, host_alloc_plan):
    logger.info("start set_horovod_env")
    os.environ[HorovodEnv.RANK] = str(env["RANK"])
    os.environ[HorovodEnv.SIZE] = str(env["WORLD_SIZE"])
    os.environ[HorovodEnv.RENDEZVOUS_ADDR] = str(env["MASTER_ADDR"])
    os.environ[HorovodEnv.RENDEZVOUS_PORT] = str(env["MASTER_PORT"])
    os.environ[HorovodEnv.GLOO_TIMEOUT_SECONDS] = "3600"

    rank = int(env["RANK"])
    os.environ[HorovodEnv.HOSTNAME] = str(host_alloc_plan[rank].hostname)
    os.environ[HorovodEnv.HOROVOD_LOCAL_RANK] = str(
        host_alloc_plan[rank].local_rank
    )
    os.environ[HorovodEnv.HOROVOD_LOCAL_SIZE] = str(
        host_alloc_plan[rank].local_size
    )
    os.environ[HorovodEnv.HOROVOD_CROSS_RANK] = str(
        host_alloc_plan[rank].cross_rank
    )
    os.environ[HorovodEnv.HOROVOD_CROSS_SIZE] = str(
        host_alloc_plan[rank].cross_size
    )
    if rank == 0:
        os.environ[HorovodEnv.CONTROLLER] = "gloo"
        os.environ[HorovodEnv.CPU_OPERATIONS] = "gloo"


def init_horovod():
    logger.info("start init_horovod")
    env = os.environ.copy()

    hosts_slots = get_all_hosts_slots(env)
    if not hosts_slots:
        return False
    host_alloc_plan = get_host_plan(hosts_slots, int(env["NPROC_PER_NODE"]))
    set_horovod_env(env, host_alloc_plan)

    if int(env["RANK"]) == 0:
        status = start_rendezvous_server(env, host_alloc_plan)
    else:
        status = wait_rendezvous_server(env)

    if status is False:
        if int(env["RANK"]) == 0:
            logger.warning("start rendezvous server failed")
        else:
            logger.warning("wait rendezvous server failed")
        return False

    try:
        logger.info("start hvd.init()")
        hvd.init()
        return True
    except Exception:
        logger.warning("error hvd.init()!")
        return False


def wait_rendezvous_server(env, timeout=3600):
    logger.info("start wait_rendezvous_server")
    elapse_time = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((env["MASTER_ADDR"], int(env["MASTER_PORT"])))
            s.close()
            break
        except Exception:
            pass
        if elapse_time > timeout:
            logger.warning("wait rendezvous server failed!")
            s.close()
            return False
        time.sleep(10)
        elapse_time += 10
    return True


def start_rendezvous_server(env, host_alloc_plan, timeout=300):
    rendezvous_server = RendezvousServerFixedPort(
        int(env["MASTER_PORT"]), verbose=True
    )
    elapse_time = 0
    while True:
        try:
            rendezvous_server.start()
            break
        except Exception:
            pass
        if elapse_time > timeout:
            rendezvous_server.stop()
            logger.warning("start rendezvous server outtime")
            return False
        time.sleep(10)
        elapse_time += 10

    try:
        rendezvous_server.init(host_alloc_plan)
        _HorovodContext.RENDEZVOUS_SERVER = rendezvous_server
        return True
    except Exception:
        logger.warning("Failed to start rendezvous server")
        return False


def get_host_plan(hosts_slots, nproc_per_node):
    logger.info("start get_host_plan")
    host_infos = parse_hosts(_HOST_SEP.join(hosts_slots))
    host_alloc_plan = get_host_assignments(host_infos, nproc_per_node)
    return host_alloc_plan


def get_all_hosts_slots(env):
    """podname: {job_name}-ptjob-{pod_name}
    example: for node=3, nproc_per_node=8, world_size = 16,
    host plan will be:
    job_name-ptjob-master-0:8
    job_name-ptjob-worker-0:8
    job_name-ptjob-worker-1:8
    """
    logger.info("start get_all_hosts_slots")
    nnodes = int(env["NODE_SIZE"])
    nproc_per_node = int(env["NPROC_PER_NODE"])
    job_name = os.getenv("APP_ID")
    if not job_name:
        return False

    hosts_slots = []
    if nnodes < 1:
        logger.error("NODE_SIZE setting wrong!")
    elif nnodes == 1:
        hosts_slots.append(str(env["MASTER_ADDR"]) + ":" + str(nproc_per_node))
    else:
        hosts_slots.append(
            str(job_name) + "-ptjob-master-0:" + str(nproc_per_node)
        )
        for i in range(nnodes - 1):
            hosts_slots.append(
                str(job_name)
                + "-ptjob-worker-"
                + str(i)
                + ":"
                + str(nproc_per_node)
            )
    return hosts_slots


def reset_horovod():
    logger.info("reset_horovod")
    if _HorovodContext.RENDEZVOUS_SERVER is not None:
        _HorovodContext.RENDEZVOUS_SERVER.stop()
    hvd.shutdown()


class RendezvousServerFixedPort(RendezvousServer, object):
    def __init__(self, rendezvous_port, verbose=0):
        super().__init__(verbose)
        self._rendezvous_port = rendezvous_port

    def start(self, handler_cls=RendezvousHandler):
        self._httpd, port = self.fixed_port(
            lambda addr: RendezvousHTTPServer(addr, handler_cls, self._verbose)
        )
        if self._verbose:
            logger.info(
                "Rendezvous INFO: HTTP rendezvous server started.\n \
                func start() start the listening port:{}".format(
                    port
                )
            )

        # start the listening loop
        self._listen_thread = in_thread(target=self._httpd.serve_forever)

        return port

    def fixed_port(self, server_factory):
        logger.info("fixed_port:{}".format(self._rendezvous_port))
        try:
            port = self._rendezvous_port
            addr = ("", port)
            server = server_factory(addr)
            return server, port
        except Exception:
            raise Exception("Unable to find a port to bind to.")
