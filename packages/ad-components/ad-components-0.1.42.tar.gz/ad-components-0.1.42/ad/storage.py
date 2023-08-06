from dapr.clients import DaprClient
from dapr.clients.grpc._response import BindingResponse

from ad.helpers import get_logger


logger = get_logger("Storage Component Manager")


def upload(src: str, dest: str, binding_name: str = "s3-state") -> BindingResponse:
    """Uploads a file to a bucket.

    Args:
        src (str): The path of the file on local machine.
        dest (str): The path of the file in the destination bucket.
        binding_name (str, optional): The dapr binding name. Defaults to "s3-state".

    Returns:
        BindingResponse: The dapr invoke_binding response.
    """
    logger.debug(f"Reading file '{src}' content...")
    with open(src, "r") as f:
        data = f.read()

    with DaprClient() as d:
        try:
            logger.info(f"Uploading file '{src}' to '{dest}'")
            resp = d.invoke_binding(
                binding_name,
                operation="create",
                data=data,
                binding_metadata={"key": dest},
            )

            logger.debug(f"Upload file response is: {resp.text()}")
            logger.info(f"Successfully uploaded '{src}' to '{dest}'")
        except Exception:
            logger.error(f"Failed to upload: {src}")
            raise

    logger.info(f"Upload process completed successfully!")
    return resp


def download(src: str, dest: str, binding_name: str = "s3-state") -> BindingResponse:
    """Downloads a file from bucket to a local destination.

    Args:
        src (str): The path in bucket of the file we want to download.
        dest (str): The file destination path.
        binding_name (str, optional): The dapr binding name. Defaults to "s3-state".

    Returns:
        BindingResponse: The dapr invoke_binding response.
    """
    with DaprClient() as d:
        logger.debug(f"Successfully connected to daprd")

        try:
            logger.info(f"Downloading file '{src}' to '{dest}'")
            resp = d.invoke_binding(
                binding_name, operation="get", data="", binding_metadata={"key": src}
            )

            logger.debug(f"Fetched file content: {resp.text()}")
            logger.debug(f"Writing file content to '{dest}'...")
            with open(dest, "w") as f:
                f.write(resp.text())

            logger.info(f"Successfully downloaded '{src}' to '{dest}'")
        except Exception:
            logger.error(f"Failed to download: {src}")
            raise

    logger.info(f"Download process completed successfully!")
    return resp


def delete():
    raise NotImplementedError()


def list():
    raise NotImplementedError()
