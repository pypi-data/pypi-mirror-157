import time
from kfp_tekton import TektonClient
from kfp_server_api import ApiException


client = TektonClient()


def get_pipeline(pipeline_id: str = None, pipeline_name: str = None):
    """Gets pipeline details.
    Args:
        pipeline_id: id of the pipeline.
    Returns:
        kfp_server_api.ApiPipeline: ApiPipeline object.
    Raises:
        ValueError: If both of pipeline ID and pipeline
            name were not given.
    """
    if not pipeline_id and not pipeline_name:
        raise ValueError(
            "Either pipeline_id or pipeline_name must be provided to perform the operation."
        )

    try:
        if pipeline_name:
            pipeline_id = client.get_pipeline_id(pipeline_name)

        if pipeline_id:
            return client.get_pipeline(pipeline_id)
    except ApiException:
        pass

    return


def create_experiment(name: str, **kwargs):
    """Create a new experiment.
    Args:
        name: The name of the experiment.
        namespace: The Kubernetes namespace where the experiment should be
            created.
            For single user deployment, leave it as None;
            For multi user, input a namespace where the user is authorized.
    Returns:
        kfp_server_api.ApiExperiment: ApiExperiment object.
    """
    return client.create_experiment(name, **kwargs)


def create_pipeline(pipeline_package_path: str, pipeline_name: str, **kwargs):
    """Uploads (or updates) the pipeline to the Kubeflow Pipelines cluster.

    Args:
        pipeline_package_path: Local path to the pipeline package.
        pipeline_name (Optional): Name of the pipeline to be shown in the UI.

    Returns:
        kfp_server_api.ApiPipeline: ApiPipeline object.
    """
    current_pipeline = get_pipeline(pipeline_name=pipeline_name)
    if current_pipeline:
        now = int(time.time())

        client.upload_pipeline_version(
            pipeline_package_path,
            f"{pipeline_name}_{now}",
            pipeline_id=current_pipeline.id,
            **kwargs
        )

        return current_pipeline

    return client.pipeline_uploads.upload_pipeline(
        pipeline_package_path, name=pipeline_name, **kwargs
    )


def run_pipeline(pipeline, params={}, **kwargs):
    """Runs a specified pipeline."""

    now = int(time.time())
    job_name = f"{pipeline.name}_job_{now}"
    experiment = create_experiment(f"{pipeline.name}_experiment")

    return client.run_pipeline(
        experiment_id=experiment.id,
        job_name=job_name,
        pipeline_id=pipeline.id,
        params=params,
        **kwargs
    )
