[![Build Status](https://travis-ci.org/tethysplatform/tethys_dask_scheduler.svg?branch=master)](https://travis-ci.org/tethysplatform/tethys_dask_scheduler)
[![Coverage Status](https://coveralls.io/repos/github/tethysplatform/tethys_dask_scheduler/badge.svg?branch=master)](https://coveralls.io/github/tethysplatform/tethys_dask_scheduler?branch=master)
# tethys_dask_scheduler
A Dask scheduler with custom SchedulerPlugins to support integration with Tethys Platform.

# Installation

```
pip install tethys_dask_scheduler
```

OR

```
conda install -c conda-forge tethys_dask_scheduler
```

# Start Scheduler

Start a scheduler that reports status updates to Tethys Portal.

```
$ dask-scheduler --preload tethys_dask_scheduler.plugin --tethys-host http://localhost:8000

distributed.preloading - INFO - Import preload module: tethys_dask_scheduler.plugin
distributed.scheduler - INFO - -----------------------------------------------
distributed.preloading - INFO - Import preload module: tethys_dask_scheduler.plugin
distributed.http.proxy - INFO - To route to workers diagnostics web server please install jupyter-server-proxy: python -m pip install jupyter-server-proxy
distributed.scheduler - INFO - -----------------------------------------------
distributed.scheduler - INFO - Clear task state
distributed.scheduler - INFO -   Scheduler at: tcp://192.168.10.100:8786
distributed.scheduler - INFO -   dashboard at:                     :8787
distributed.scheduler - INFO - Tethys Host at:     http://localhost:8000
distributed.preloading - INFO - Run preload setup click command: tethys_dask_scheduler.plugin
distributed.scheduler - INFO - Register worker <WorkerState 'tcp://192.168.10.100:34297', name: tcp://192.168.10.100:34297, status: running, memory: 0, processing: 0>
distributed.scheduler - INFO - Starting worker compute stream, tcp://192.168.10.100:34297
distributed.core - INFO - Starting established connection
```

# Start Worker

Start a Dask distributed worker as usual:

```
$ dask-worker tcp://192.168.10.100:8786

distributed.nanny - INFO -         Start Nanny at: 'tcp://192.168.10.100:34359'
distributed.worker - INFO -       Start worker at: tcp://192.168.10.100:39569
distributed.worker - INFO -          Listening to: tcp://192.168.10.100:39569
distributed.worker - INFO -          dashboard at:       192.168.10.100:34857
distributed.worker - INFO - Waiting to connect to:  tcp://192.168.10.100:8786
distributed.worker - INFO - -------------------------------------------------
distributed.worker - INFO -               Threads:                          6
distributed.worker - INFO -                Memory:                   7.77 GiB
distributed.worker - INFO -       Local Directory: /home/tethys/tethysdev/tethys_dask_scheduler/dask-worker-space/worker-4j_bj5hv
distributed.worker - INFO - -------------------------------------------------
distributed.worker - INFO -         Registered to:  tcp://192.168.10.100:8786
distributed.worker - INFO - -------------------------------------------------
distributed.core - INFO - Starting established connection
```

## Tests

Tests are executed using tox:

```
pip install .[tests]
tox
```
