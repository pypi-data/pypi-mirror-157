from RhcsQeSdk.core.utilities.metadata import Metadata
from RhcsQeSdk.core.utilities.test_config_run import ConfigRun


def run(kw):
    test_data = kw.get("test_data")
    cluster_name = kw.get("cluster_name")
    output = {"cluster_names": [], "rc": 1}
    if cluster_name:
        output["cluster_names"].append(cluster_name)
    for step in test_data.get("configs"):
        for role in step.get("role"):
            if len(role.split(":")) == 2:
                output["cluster_names"].append(role.split(":")[0])
    ceph_cluster_dict = kw.get("ceph_cluster_dict")
    metadata = Metadata()
    metadata.ceph_cluster_dict = ceph_cluster_dict
    if not ConfigRun(cluster_name, ceph_cluster_dict, is_root=True).run_config(
        test_data.get("configs")
    ):
        return output
    output["rc"] = 0
    return output
