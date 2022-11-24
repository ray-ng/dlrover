# Copyright 2022 The DLRover Authors. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict

from dlrover.python.common.constants import DistributionStrategy, NodeType
from dlrover.python.master.watcher.base_watcher import Node


def set_critical_node(
    job_nodes: Dict[str, Dict[int, Node]],
    ps_is_critical=True,
    critical_worker_index={},
    ps_relaunch_max_num=0,
):
    """
    pod_info is a dict, where pod_info[type][id] is a PodInfo instance
    Set is_critical_pod values accordingly
    """
    if NodeType.PS in job_nodes:
        for node in job_nodes[NodeType.PS].values():
            node.critical = ps_is_critical
            if node.critical:
                node.max_relaunch_count = ps_relaunch_max_num
    if NodeType.WORKER in job_nodes:
        for i, node in job_nodes[NodeType.WORKER].items():
            if node.id not in critical_worker_index:
                continue
            node.critical = True
            node.max_relaunch_count = critical_worker_index[i]
    if NodeType.EVALUATOR in job_nodes:
        for node in job_nodes[NodeType.EVALUATOR].values():
            node.critical = True
    if NodeType.TF_MASTER in job_nodes:
        for node in job_nodes[NodeType.TF_MASTER].values():
            node.critical = True


def get_critical_worker_index(args):
    critical_worker_index = {}

    if args.critical_worker_index == "default":
        # for default, worker0 is critical if PS strategy with custom training
        if args.distribution_strategy == DistributionStrategy.PARAMETER_SERVER:
            critical_worker_index[0] = args.relaunch_on_worker_failure
    elif args.critical_worker_index == "all":
        for i in range(args.num_workers):
            critical_worker_index[i] = args.relaunch_on_worker_failure
    elif args.critical_worker_index != "none":
        for pod_relaunch_conf in args.critical_worker_index.split(","):
            # The conf is "pod_index:relaunch_times"
            pod_relaunch = pod_relaunch_conf.strip().split(":")
            critical_worker_index[int(pod_relaunch[0])] = int(pod_relaunch[1])

    return critical_worker_index
