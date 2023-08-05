from dapr.clients import DaprClient

from ad.helpers import get_logger


logger = get_logger("Step Component Manager")


class Step(object):
    def __init__(self) -> None:
        self.in_context = False
        self.launch()

    def launch(self) -> None:
        """Wait for dependencies to be live, Dapr sidecar for example, and
        make sure we got everything ready for the user.
        """
        raise NotImplementedError()

    def shutdown(self) -> None:
        """Make sure all resources that are no longer needed are
        cleaned up and/or ejected gracefully.
        """
        raise NotImplementedError()

    def __enter__(self) -> "Step":
        """Do stuff when we are in context

        Returns:
            Step: an instance of this class
        """
        self.in_context = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Do stuff when object is no longer in a context"""
        self.shutdown()

    def __del__(self) -> None:
        """Do stuff when all references to object are removed"""
        self.shutdown()


class DaprStep(Step):
    def __init__(self, timeout: int = 300, *args, **kwargs) -> None:
        """Initializes dapr step

        Args:
            timeout (int, optional): Value in seconds we should wait for sidecar to come up. Defaults to 300.
        """
        self.client = DaprClient(*args, **kwargs)
        self.timeout = timeout

        super().__init__()

    def launch(self) -> None:
        logger.debug(f"Waiting for dapr sidecar...")
        self.client.wait(self.timeout)
        logger.info(f"Successfully connected to dapr sidecar!")

    def shutdown(self) -> None:
        logger.debug(f"Closing dapr sidecar connection...")
        self.client.close()

        logger.debug(f"Shutting dapr sidecar down...")
        self.client.shutdown()

        logger.info(f"All dapr resources have been cleaned up!")


class MlFlowStep(Step):
    pass
