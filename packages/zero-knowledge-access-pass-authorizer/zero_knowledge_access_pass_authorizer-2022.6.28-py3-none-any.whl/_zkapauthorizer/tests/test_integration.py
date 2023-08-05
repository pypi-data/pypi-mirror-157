from testresources import setUpResources, tearDownResources
from testtools import TestCase
from testtools.twistedsupport import AsynchronousDeferredRunTest

from .fixtures import Treq
from .resources import TahoeClientManager, client_manager


class RecoverIntegrationTests(TestCase):
    """
    Integration tests for the recovery endpoint.
    """

    # Support test methods that return a Deferred.
    run_tests_with = AsynchronousDeferredRunTest.make_factory(timeout=60.0)

    # Get a Tahoe-LAFS client node connected to a storage node.
    resources = [
        ("source_client", client_manager),
        ("destination_client", TahoeClientManager()),
    ]

    def setUp(self):
        super().setUp()
        setUpResources(self, self.resources, None)
        self.addCleanup(lambda: tearDownResources(self, self.resources, None))
        # AsynchronousDeferredRunTest sets reactor on us.
        self.httpclient = self.useFixture(Treq(self.reactor, case=self)).client()

    def test_replicate_and_recover(self):
        """
        ZKAPAuthorizer voucher and token state is replicated to a Tahoe-LAFS grid
        and can then be recovered into a blank ZKAPAuthorizer database using
        the recovery endpoint.
        """
        # Create some state in the "source" client node.

        # Replication is not implemented yet so do it ourselves here.
