from __future__ import division, print_function, unicode_literals
from abipy.core.testing import AbipyTest
from HTGW.plotting.collection import Collection
from pymongo.errors import ServerSelectionTimeoutError
import logging

logger = logging.getLogger()


class ColTest(AbipyTest):
    """
    testing the Collection class for integration with the database
    """

    def test_collection(self):
        try:
            col = Collection()
            self.assertGreater(len(col.all_systems), 100)
            col.get_data_set(query={'system': 'Ne'}, sigresdata=True)
            col.get_property_lists()
            self.assertEqual(col.systems[0], 'Ne')
            self.assertEqual(col.functionals[0], 'PBE')
            self.assertEqual(col.ps[0], 'GGA_PBE-JTH-paw')
            self.assertEqual(col.extra[0], 'default')
        except ServerSelectionTimeoutError:
            logger.warning('no database connection could be made, some tests could not be executed')
