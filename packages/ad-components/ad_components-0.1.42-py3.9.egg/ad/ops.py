from ad.step import DaprStep
from ad.storage import download, upload
from kfp.components import func_to_container_op


def download_op_func(
    src: str,
    dest: str,
    binding: str = "s3-state",
    timeout: int = 300,
):
    with DaprStep(timeout=timeout):
        resp = download(src, dest, binding_name=binding)

    return resp


def upload_op_func(
    src: str,
    dest: str,
    binding: str = "s3-state",
    timeout: int = 300,
):
    with DaprStep(timeout=timeout):
        resp = upload(src, dest, binding_name=binding)

    return resp


download_op = func_to_container_op(
    func=download_op_func,
    base_image="image-registry.openshift-image-registry.svc:5000/kubeflow/ad",
)

upload_op = func_to_container_op(
    func=upload_op_func,
    base_image="image-registry.openshift-image-registry.svc:5000/kubeflow/ad",
)
