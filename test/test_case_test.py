import unittest

from testify import class_setup
from testify import class_teardown
from testify import run
from testify import setup
from testify import teardown
from testify import setup_teardown
from testify import class_setup_teardown
from testify import TestCase
from testify import test_runner


class TestMethodsGetRun(TestCase):
    def test_method_1(self):
        self.test_1_run = True

    def test_method_2(self):
        self.test_2_run = True

    @class_teardown
    def assert_test_methods_were_run(self):
        assert self.test_1_run
        assert self.test_2_run


class DeprecatedClassSetupFixturesGetRun(TestCase):
    def classSetUp(self):
        self.test_var = True

    def test_test_var(self):
        assert self.test_var


class DeprecatedSetupFixturesGetRun(TestCase):
    def setUp(self):
        self.test_var = True

    def test_test_var(self):
        assert self.test_var


class DeprecatedTeardownFixturesGetRun(TestCase):
    COUNTER = 0

    def tearDown(self):
        self.test_var = True

    def test_test_var_pass_1(self):
        self.COUNTER += 1
        if self.COUNTER > 1:
            assert self.test_var

    def test_test_var_pass_2(self):
        self.COUNTER += 1
        if self.COUNTER > 1:
            assert self.test_var


class DeprecatedClassTeardownFixturesGetRun(TestCase):
    def test_placeholder(self):
        pass

    def class_teardown(self):
        self.test_var = True

    @class_teardown
    def test_test_var(self):
        assert self.test_var


class ClassSetupFixturesGetRun(TestCase):
    @class_setup
    def set_test_var(self):
        self.test_var = True

    def test_test_var(self):
        assert self.test_var


class SetupFixturesGetRun(TestCase):
    @setup
    def set_test_var(self):
        self.test_var = True

    def test_test_var(self):
        assert self.test_var


class TeardownFixturesGetRun(TestCase):
    COUNTER = 0

    @teardown
    def set_test_var(self):
        self.test_var = True

    def test_test_var_first_pass(self):
        self.COUNTER += 1
        if self.COUNTER > 1:
            assert self.test_var

    def test_test_var_second_pass(self):
        self.COUNTER += 1
        if self.COUNTER > 1:
            assert self.test_var


class TestRegisterFixtureMethodsParentClass(TestCase):
    """A parent class to test the ability to register fixture methods"""

    @setup
    def parent_setup_1(self):
        """Set an instance variable to test that this method gets called"""
        self.parent_setup_exists = 1

    @setup
    def __parent_setup_2(self):
        """Set an instance variable to test that this method gets called"""
        self.parent_setup_exists += 1


class TestRegisterFixtureMethodsChildClass(TestRegisterFixtureMethodsParentClass):
    """A child class to test the ability to register fixture methods"""

    @setup
    def __zchild_setup_1(self):
        self.child_setup_exists = self.parent_setup_exists + 1

    @setup
    def __child_setup_2(self):
        self.child_setup_2_exists = self.child_setup_exists + 1

    def test_things_exist(self):
        """Check for instance variable set by fixture method from parent class"""
        self.failUnless(self.parent_setup_exists == 2)
        assert self.child_setup_exists == 3
        assert self.child_setup_2_exists == 4


class FixtureMethodRegistrationOrderTest(TestCase):
    """Test that registered fixtures execute in the expected order, which is:
     - class_setup
     - enter class_setup_teardown
     - setup
     - enter setup_teardown

     - test

     - exit setup_teardown, in Reverse of definition
     - teardown
     - exit class_setup_teardown in Reverse order of definition
     - class_teardown
    """
    def __init__(self, *args, **kwargs):
        super(FixtureMethodRegistrationOrderTest, self).__init__(*args, **kwargs)
        self.counter = 0

    @class_setup
    def __class_setup_prerun_1(self):
        assert_equal(self.counter, 0)
        self.counter += 1

    @class_setup
    def __class_setup_prerun_2(self):
        assert_equal(self.counter, 1)
        self.counter += 1

    @class_setup
    def third_setup(self):
        assert_equal(self.counter, 2)
        self.counter += 1

    @class_setup_teardown
    def __class_context_manager_1(self):
        assert_equal(self.counter, 3)
        self.counter += 1
        yield
        assert_equal(self.counter, 17)
        self.counter += 1

    @class_setup_teardown
    def __class_context_manager_2(self):
        assert_equal(self.counter, 4)
        self.counter += 1
        yield
        assert_equal(self.counter, 16)
        self.counter += 1

    @setup
    def __setup_prerun_1(self):
        assert_equal(self.counter, 5)
        self.counter += 1

    @setup
    def __setup_prerun_2(self):
        assert_equal(self.counter, 6)
        self.counter += 1

    @setup
    def real_setup(self):
        assert_equal(self.counter, 7)
        self.counter += 1

    @setup_teardown
    def __context_manager_1(self):
        assert_equal(self.counter, 8)
        self.counter += 1
        yield
        assert_equal(self.counter, 12)
        self.counter += 1

    @setup_teardown
    def __context_manager_2(self):
        assert_equal(self.counter, 9)
        self.counter += 1
        yield
        assert_equal(self.counter, 11)
        self.counter += 1

    def test_fixture_registration_order(self):
        assert_equal(self.counter, 10)
        self.counter += 1

    @teardown
    def do_some_teardown(self):
        assert_equal(self.counter, 13)
        self.counter += 1

    @teardown
    def __zteardown_postrun_1(self):
        assert_equal(self.counter, 14)
        self.counter += 1

    @teardown
    def __teardown_postrun_2(self):
        assert_equal(self.counter, 15)
        self.counter += 1

    @class_teardown
    def jsut_class_teardown(self):
        assert_equal(self.counter, 18)
        self.counter += 1

    @class_teardown
    def __class_teardown_postrun_1(self):
        assert_equal(self.counter, 19)
        self.counter += 1

    @class_teardown
    def __class_teardown_postrun_2(self):
        assert_equal(self.counter, 20)


class OverrideTest(TestCase):
    def test_method_1(self):
        pass

    def test_method_2(self):
        pass


@class_setup
def test_incorrectly_defined_fixture():
    """Not a true test, but declarations like this shouldn't crash."""
    pass


class FixtureMixin(object):
    @class_setup
    def set_attr(cls):
        cls.foo = True

    @property
    def get_foo(self):
        # properties dependent on setup shouldn't crash our dir() loop when
        # determining fixures on a class
        return self.foo

    def test_foo(self):
        self.foo_ran = self.get_foo


class TestFixtureMixinsGetRun(TestCase, FixtureMixin):
    # define the teardown here in case the mixin doesn't properly apply it
    @class_teardown
    def make_sure_i_ran(self):
        assert self.foo_ran


class TestSubclassedCasesWithFeatureMixinsGetRun(TestFixtureMixinsGetRun):
    pass


class TestOtherCasesWithSameFixtureMixinsGetRun(TestCase, FixtureMixin):
    @teardown
    def make_sure_i_ran(self):
        assert self.foo_ran


class NewerFixtureMixin(object):
    @class_setup
    def set_another_attr(cls):
        # this setup should run after FixtureMixin's
        assert cls.foo
        cls.bar = True

    def test_bar(self):
        self.bar_ran = self.bar


class TestFixtureMixinOrder(TestCase, FixtureMixin, NewerFixtureMixin):
    @class_teardown
    def make_sure_i_ran(self):
        assert self.foo_ran
        assert self.bar_ran


class UnitTest(unittest.TestCase):
    # a compact way to record each step's completion
    status = [False] * 6

    def classSetUp(self):
        self.status[0] = True

    def setUp(self):
        self.status[1] = True

    def test_i_ran(self):
        self.status[2] = True

    def tearDown(self):
        self.status[3] = True

    def classTearDown(self):
        self.status[4] = True

    @teardown
    def no_really_i_tore_down(self):
        """Fixture mixins should still work as expected."""
        self.status[5] = True


class UnitTestUntested(UnitTest):
    __test__ = False
    status = [False] * 6


class UnitTestTestYoDawg(TestCase):
    """Make sure we actually detect and run all steps in unittest.TestCases."""
    def test_unit_test_status(self):
        runner = test_runner.TestRunner(UnitTest)
        assert runner.run()
        assert UnitTest.status == [True] * 6, UnitTest.status

        runner = test_runner.TestRunner(UnitTestUntested)
        assert runner.run()
        assert UnitTestUntested.status == [False] * 6, UnitTestUntested.status


# The following cases test unittest.TestCase inheritance, fixtures and mixins

class BaseUnitTest(unittest.TestCase):
    done = False

    def __init__(self):
        super(BaseUnitTest, self).__init__()
        self.init = True

    def setUp(self):
        assert self.init
        assert not self.done
        self.foo = True

    def tearDown(self):
        assert self.init
        assert not self.done
        self.done = True


class DoNothingMixin(object):
    pass


class DerivedUnitTestMixinWithFixture(BaseUnitTest):
    @setup
    def set_bar(self):
        assert self.foo # setUp runs first
        self.bar = True

    @teardown
    def not_done(self): # tearDown runs last
        assert not self.done

    @class_teardown
    def i_ran(cls):
        cls.i_ran = True


class DerivedUnitTestWithFixturesAndTests(DerivedUnitTestMixinWithFixture, DoNothingMixin):
    def test_foo_bar(self):
        assert self.foo
        assert self.bar
        assert not self.done


class DerivedUnitTestWithAdditionalFixturesAndTests(DerivedUnitTestMixinWithFixture):
    @setup
    def set_baz(self):
        assert self.foo
        assert self.bar
        self.baz = True

    @teardown
    def clear_foo(self):
        self.foo = False

    def test_foo_bar_baz(self):
        assert self.foo
        assert self.bar
        assert self.baz


class TestDerivedUnitTestsRan(TestCase):
    def test_unit_tests_ran(self):
        assert DerivedUnitTestMixinWithFixture.i_ran
        assert DerivedUnitTestWithFixturesAndTests.i_ran
        assert DerivedUnitTestWithAdditionalFixturesAndTests.i_ran


if __name__ == '__main__':
    run()
