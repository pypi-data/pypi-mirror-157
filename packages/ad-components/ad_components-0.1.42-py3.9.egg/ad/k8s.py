from os.path import exists

def get_pod_namespace():
    """Assuming that the code is running inside a Kubernetes pod, get the pod namespace

    Returns:
        The namespace name
    """

    ns_file = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
    if exists(ns_file):
        with open(ns_file) as f:
            return f.read()
