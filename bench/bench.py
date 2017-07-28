#!C:\ce\trunk\win32\release\img\python
from abc import ABCMeta
import inspect


class Bench(object):
    _metaclass_ = ABCMeta
    args = {}
    results = []

    def setUp(self):
        """Method called to prepare the test fixture. The default implementation does nothing."""
        pass

    def tearDown(self):
        """Method called immediately after the test method has been called and
        the result recorded.  The default implementation does nothing. """
        pass

    def setUpClass(self):
        """
        This method is called before the first test and is used for preparing all test.
        """
        pass

    def tearDownClass(self):
        """
        This method is called after the last test and is used for cleaning purposes.
        """
        pass

    def storeResult(self, res):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        self.results.append({calframe[1][3]: res})

    def run(self, args):
        """
        This method calls every test in this class. Test are indentified by the prefix 'test_'.
        The setUp-method is called immediately before each test and the tearDown-method is
        called immediately after each test. The result is structured in json format and will be returned.
        """
        self.args = args
        self.results = []
        try:
            self.setUpClass()
            for test, val in self.__class__.__dict__.iteritems():
                if test.find('bench_') == 0:
                    test_method = getattr(self, test)
                    self.setUp()
                    # each test need to return [val, unit]
                    result = test_method()
                    if result:
                        # results.append({test_method.__name__: {'value': result[0], 'unit': result[1]}})
                        self.results.append({test_method.__name__: result})
                    self.tearDown()
            self.tearDownClass()
        except:
            pass
        return self.results
