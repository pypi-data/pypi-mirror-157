"""
Recursively searches folders below the location of this file. 
Runs any unittest class that begins with test_

examples:
python3 KungFu.py                          #Run all tests, automatically decide if gui is available.

python3 KungFu.py -sleep 1.0               #Run tests with a sleeptime of 1.0 seconds.
python3 KungFu.py -filter test_0           #Run only tests with names that begin with 'test_0'
python3 KungFu.py -casefilter test_A       #Run only testcases with names that begin with 'test_A'
python3 KungFu.py -folder Python/Qt        #Run all tests in the Python/Qt folder.
python3 KungFu.py -folders Python,AWS      #Run all tests in the Python and AWS folders.
python3 KungFu.py --create                 #Run tests that provision real cloud resources. THIS WILL COST MONEY!
python3 KungFu.py --destroy                #Run tests that destroy real cloud resources. THIS IS POTENTIALLY DESTRUCTIVE!
python3 KungFu.py --install                #Run all installers. You probably shouldn't do this in the full KungFu library!
python3 KungFu.py --skip                   #Skip all installers. Turn this on for CI.
"""

# Standard Imports#################################
import sys, os
import unittest, inspect, argparse, json
from importlib import util
from datetime import datetime
import threading
import subprocess, shlex
import traceback
import functools, copy
import io
import contextlib
import types
from pprint import pprint, pformat


# Write Back#######################################
ExpectedTestCount = {
    "aws": 7,
    "conda": 0,
    "conda.pyside2": 9,
    "conda.qt.py": 9,
    "docker": 0,
    "go": 14,
    "gui": 9,
    "java": 0,
    "kubectl": 0,
    "lxml": 3,
    "maya": 0,
    "msgpack": 1,
    "msgpack_numpy": 1,
    "nodejs": 7,
    "npm.jest": 7,
    "nuke": 0,
    "numpy": 4,
    "pandas": 8,
    "static-frame": 3,
    "terraform": 7,
    "unreal": 11,
    "yfinance": 3,
}


def WriteBack():
    """
    Writes back TestCount data into this module so that any machine
    can count the tests it skipped from unfulfilled dependencies
    anywhere this module is run.

    Only successful runs of any dependency on a machine will update
    the dictionary. This allows for graceful updates via git as new
    tests are added, while still keeping the testkit logic in a
    single file for maximum portability.
    """
    for key, value in DependencyHandler().TestCount.items():
        skey = key.replace("actual_", "")
        ExpectedTestCount[skey] = value
    with open(__file__, "r", newline="\n") as file:
        filetext = file.read()
    with open(__file__, "w", newline="\n") as file:
        # TODO: Find a cleaner way of implementing this
        flist = filetext.split("ExpectedTestCount = {\n", 1)
        f0 = flist[0] + "ExpectedTestCount = {\n"
        f1 = flist[1].split("}", 1)[1]
        newfiletext = (
            f0
            + " "
            + pformat(ExpectedTestCount).replace("{", "", 1).replace("}", ",\n}")
            + f1
        )
        file.write(newfiletext)


# Test##############################################
class test_TestRunner(unittest.TestCase):
    def setUp(self):
        self.tr = TestRunner()

    def tearDown(self):
        pass

    def test_collect_foldertree_filelist(self):
        foldertree, filelist = TestRunner.collect_foldertree_filelist()
        assert len(foldertree) > 0
        assert len(filelist) > 0

    def test_convert_foldertree_to_nested_dict(self):
        foldertree, filelist = TestRunner.collect_foldertree_filelist()
        nested_dict = TestRunner.convert_foldertree_to_nested_dict(foldertree, filelist)
        assert type(nested_dict) == dict

    def test_create_suites(self):
        testsuites = TestRunner.create_suites()
        assert len(testsuites) > 0
        for k in list(testsuites.keys())[1:]:  # skip first key which will always be ""
            print(k)
            assert k[0] not in [".", "_"]

    def test_discover_tests(self):
        return
        discovered_tests = self.tr.discover_tests()
        for test in discovered_tests.values():
            assert type(test) == unittest.TestSuite


# Decorators#######################################
def cloud(func):
    """
    KungFu.cloud decorator is for marking functions that will simulate
    the creation of cloud resources.
    """
    if not sys.TestArgs.create:
        print("Skipping cloud Test")
        return None
    else:
        return func


def create(func):
    """
    KungFu.create decorator is for marking functions that will create
    cloud resources and cost money. Any function marked with this
    decorator will not run unless the --create flag is passed into
    argparse.
    """
    if not sys.TestArgs.create:
        print("Skipping create Test")
        return None
    else:
        return func


def destroy(func):
    """
    KungFu.create decorator is for marking functions that will destroy
    cloud resources. Any function marked with this decorator will not
    run unless the --destroy flag is passed into argparse.
    """
    if not sys.TestArgs.destroy:
        print("Skipping destroy Test")
        return None
    else:
        return func


def depends(*args):
    """
    KungFu.depends decorator provides a generic way for any test
    function to specify any arbitrary dependency. DependencyHandler
    will automatically check the _installers folder to run a
    _check.sh file if it's available.
    """
    dependencies = args

    def ActualDecorator(cls):
        if "base" in dependencies:
            setattr(cls, "dependencies", dependencies)
            return cls
        count = 0
        for FunctionName, Function in inspect.getmembers(cls):
            if "test_" == FunctionName.lower()[:5]:
                count += 1
        rNone = False
        for dependency in dependencies:
            if not DependencyHandler().Check(dependency):
                rcount = count
                if rcount == 0 and dependency in ExpectedTestCount.keys():
                    rcount = ExpectedTestCount[dependency]
                print("Skipping " + str(rcount) + " " + dependency + " test(s).")
                DependencyHandler().SkipCount += rcount
                rNone = True
            else:
                DependencyHandler().CountTests(dependency, count)
        else:
            if rNone or cls == None:
                return None
            setattr(cls, "dependencies", dependencies)
            return cls

    return ActualDecorator


def fast():
    pass  # TODO: create some separation between fast and slow tests


def slow():
    pass  # TODO: create some separation between fast and slow tests


# Base Classes#####################################
class TimedTest(unittest.TestCase):
    """
    Takes care of timing each test, and printing output.
    GetPartial passes any arbitrary argparse kwarg into each test
    function
    """

    def __init__(self, *args):
        super(TimedTest, self).__init__(*args)
        for FunctionName, Function in inspect.getmembers(self.__class__):
            if Function and "test_" == FunctionName.lower()[:5]:
                partial = functools.partial(self.GetPartial, Function)
                setattr(self.__class__, FunctionName, partial)

    def GetPartial(self, func):
        if type(func) == functools.partial:
            return func()
        if func.__defaults__:
            arglist = list(func.__defaults__)
            for key in sys.TestArgs.kwargs:
                if key in func.__code__.co_varnames:
                    i = func.__code__.co_varnames.index(key)
                    arglist[i - 1] = sys.TestArgs.kwargs[key]
            func.__defaults__ = tuple(arglist)
        return func(self)

    def setUp(self):
        self.starttime = datetime.now()

    def tearDown(self):
        t = self.getTime()
        # print(str(t), self.id())

    def getTime(self):
        return datetime.now() - self.starttime


class PrototypeTestParser(unittest.TestCase):
    """
    Prototype class for turning test data output into test_ methods
    that unittest can count. parsercls must be provided by the
    module.
    See:
        CPPTestParser.py
        NPMTestParser.py
        GoTestParser.py
    """

    def Prototest(self, *args, testname=""):
        (result, testtime) = self.parser.results[testname]
        self.assertEqual(result, True)

    @classmethod
    def AddTests(cls, parsercls):
        if sys.TestArgs.filter and sys.TestArgs.filter not in cls.__name__:
            return
        cls.parser = parsercls()
        cls.parser.run()
        for testname in cls.parser.results:
            newtest = cls.CopyFunc(cls.Prototest, testname)
            newtest.__name__ = "test_" + testname[5:]
            setattr(cls, newtest.__name__, newtest)
        DependencyHandler().CountTests(cls.dependencies, len(cls.parser.results))

    @classmethod
    def CopyFunc(cls, func, testname):
        newfunc = types.FunctionType(func.__code__, func.__globals__)
        newfunc = functools.update_wrapper(newfunc, func)
        newfunc.__kwdefaults__ = {"testname": testname}
        return newfunc


# Core Classes#####################################
class DependencyHandler:
    """
    Automates the process of checking, counting, and installing
    dependencies. KungFu will automatically skip any test that your
    machine lacks dependencies for.
    """

    cwd = os.path.dirname(os.path.abspath(__file__))
    Installed = []
    NotInstalled = []
    PMInstalled = []
    PMNotInstalled = []
    SkipCount = 0
    ShellList = ["nodejs"]  # packages that require the shell option to be set
    TestCount = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(sys, "DependencyHandler"):  # Global Singleton
            sys.DependencyHandler = super(DependencyHandler, cls).__new__(
                cls, *args, **kwargs
            )
        return sys.DependencyHandler

    # Checks###########################################
    def Check(self, name):

        manager = None
        if "." in name:
            manager, name = name.split(".", 1)
        if name in self.Installed:
            print("Check Installed", name)
            return True
        elif name in self.NotInstalled:
            print("Check Not Installed", name)
            return False
        else:
            print("Run Checks", name)
            return self.RunChecks(name, manager=manager)

    def RunChecks(self, name, manager=None):
        def pm(nm):
            return self.ShellCheck(nm, pm=True)

        if manager:
            if manager == "conda":
                if pm("conda") and self.CondaCheck(name):
                    return True
                if pm("pip") and self.PipCheck(name):
                    return True
            if manager == "pip":
                if pm("pip") and self.PipCheck(name):
                    return True
                if pm("conda") and self.CondaCheck(name):
                    return True
            if manager in ["nodejs", "npm"]:
                if pm("nodejs") and self.NpmCheck(name):
                    return True
            if manager == "apt":
                if pm("apt") and self.AptCheck(name):
                    return True
            if manager == "yum":
                if pm("yum") and self.YumCheck(name):
                    return True
            if manager == "rpm":
                if pm("rpm") and self.RpmCheck(name):
                    return True
            if manager == "zypper":
                if pm("zypper") and self.ZypperCheck(name):
                    return True
            if manager == "yast":
                if pm("yast") and self.YastCheck(name):
                    return True
            if manager == "snap":
                if pm("snap") and self.SnapCheck(name):
                    return True
            print("Unrecognized package manager: " + manager)
            if manager + "." + name not in self.NotInstalled:
                self.NotInstalled.append(manager + "." + name)
            return False
        else:
            if name == "gui":
                return self.CheckGui()
            if self.ShellCheck(name):
                return True
            if pm("conda") and self.CondaCheck(name):
                return True
            if pm("pip") and self.PipCheck(name):
                return True
            # if pm('apt') and self.AptCheck(name): return True
            # if pm('yum') and self.YumCheck(name): return True
            # if pm('rpm') and self.RpmCheck(name): return True
            # if pm('zypper') and self.ZypperCheck(name): return True
            # if pm('yast') and self.YastCheck(name): return True
            # if pm('snap') and self.SnapCheck(name): return True
            if pm("nodejs") and self.NpmCheck(name):
                return True
            if self.PythonCheck(name):
                return True
            if name not in self.NotInstalled:
                self.NotInstalled.append(name)
            return False

    def ShellCheck(self, name, shellmode=False, pm=False):
        if pm:
            if name in self.PMInstalled:
                return True
            elif name in self.PMNotInstalled:
                return False
        checkpath = self.cwd + "/_installers/" + name + "_check.sh"
        if os.path.exists(checkpath):
            returncodes = 0
            with open(checkpath, "r") as file:
                for line in file.readlines():
                    if name in self.ShellList:
                        shellmode = True
                    output, returncode = RunCmd(line, cwd=self.cwd, shell=shellmode)
                    returncodes += returncode
            returncodes = not bool(returncodes)
            if returncodes and name not in self.Installed:
                if pm:
                    self.PMInstalled.append(name)
                else:
                    self.Installed.append(name)
            elif not returncodes:
                if pm:
                    self.PMNotInstalled.append(name)
            return returncodes

    def CondaCheck(self, name):
        output, returncode = RunCmd("conda list --json " + name)
        # print('output', output)
        # print('returncode', returncode)
        vlist = json.loads(output)
        result = not bool(returncode) and len(vlist) > 0
        if result and name not in self.Installed:
            self.Installed.append(name)
        return result

    def NpmCheck(self, name):
        output, returncode = RunCmd(
            "npm list " + name, cwd=self.cwd + "/Javascript", shell=True
        )
        # print('output', output)
        # print('returncode', returncode)
        result = not bool(returncode)
        if result and name not in self.Installed:
            self.Installed.append(name)
        return result

    def PipCheck(self, name):
        output, returncode = RunCmd("pip show " + name, cwd=self.cwd)
        # print('output', output)
        # print('returncode', returncode)
        result = not bool(returncode)
        if result and name not in self.Installed:
            self.Installed.append(name)
        return result

    def AptCheck(self, name):
        # Untested
        # print('attempting apt check', name)
        output, returncode = RunCmd("apt list " + name, cwd=self.cwd)
        # print('output', output)
        # print('returncode', returncode)
        vcount = len(output.split("\n"))
        result = not bool(returncode) and vcount > 1
        if result and name not in self.Installed:
            self.Installed.append(name)
        return result

    def YumCheck(self, name):
        # Untested
        # print('attempting yum check', name)
        output, returncode = RunCmd("yum list " + name, cwd=self.cwd)
        # print('output', output)
        # print('returncode', returncode)
        vcount = len(output.split("\n"))
        result = not bool(returncode) and vcount > 1
        if result and name not in self.Installed:
            self.Installed.append(name)
        return result

    def RpmCheck(self, name):
        # Untested
        # print('attempting rpm check', name)
        output, returncode = RunCmd("rpm list " + name, cwd=self.cwd)
        # print('output', output)
        # print('returncode', returncode)
        vcount = len(output.split("\n"))
        result = not bool(returncode) and vcount > 1
        if result and name not in self.Installed:
            self.Installed.append(name)
        return result

    def ZypperCheck(self, name):
        # Untested
        # print('attempting zypper check', name)
        output, returncode = RunCmd("zypper list " + name, cwd=self.cwd)
        # print('output', output)
        # print('returncode', returncode)
        vcount = len(output.split("\n"))
        result = not bool(returncode) and vcount > 1
        if result and name not in self.Installed:
            self.Installed.append(name)
        return result

    def YastCheck(self, name):
        # Untested
        # print('attempting yast check', name)
        output, returncode = RunCmd("yast list " + name, cwd=self.cwd)
        # print('output', output)
        # print('returncode', returncode)
        vcount = len(output.split("\n"))
        result = not bool(returncode) and vcount > 1
        if result and name not in self.Installed:
            self.Installed.append(name)
        return result

    def SnapCheck(self, name):
        # Untested
        # print('attempting snap check', name)
        output, returncode = RunCmd("snap list " + name, cwd=self.cwd)
        # print('output', output)
        # print('returncode', returncode)
        vcount = len(output.split("\n"))
        result = not bool(returncode) and vcount > 1
        if result and name not in self.Installed:
            self.Installed.append(name)
        return result

    def PythonCheck(self, name):
        output, returncode = RunCmd("python -c 'import " + name + "'", cwd=self.cwd)
        # print('output', output)
        # print('returncode', returncode)
        result = not bool(returncode)
        if result and name not in self.Installed:
            self.Installed.append(name)
        return result

    @contextlib.contextmanager
    def GetStderrIO(self, stderr=None):
        # Hack
        old = sys.stderr
        if stderr is None:
            stderr = io.StringIO()
        sys.stderr = stderr
        yield stderr
        sys.stderr = old

    def CheckGui(self):
        # Hack
        try:
            with self.GetStderrIO() as stderr:
                from Qt import QtCore
            if stderr.getvalue() == "":
                self.Installed.append("gui")
                installed = True
            else:
                print("X server not available! Disabling gui tests!")
                self.NotInstalled.append("gui")
                installed = False
        except ImportError as exception:
            print("Qt not available! Disabling gui tests!")
            self.NotInstalled.append("gui")
            installed = False
        print("gui installed", installed)
        return installed

    ##################################################

    # Installers#######################################
    def OfferInstallers(self):
        if len(self.NotInstalled) != 0:
            print(
                str(self.SkipCount)
                + " tests couldn't run because the following items are missing:"
            )
            for name in self.NotInstalled:
                print("    " + name)
            if "gui" in self.NotInstalled:
                self.NotInstalled.remove("gui")
            if len(self.NotInstalled) != 0:
                print(
                    "----------------------------------------------------------------------"
                )
                print("AUTOMATED INSTALLERS (UNEXPECTED RESULTS MAY OCCUR!):")
                for name in copy.copy(self.NotInstalled):
                    manager = None
                    if "." in name:
                        manager, name = name.split(".", 1)
                    if manager:
                        answer = input(
                            "    Would you like to try installing "
                            + name
                            + " from "
                            + manager
                            + "? "
                        )
                    else:
                        answer = input(
                            "    Would you like to try installing " + name + "? "
                        )
                    answer = answer.lower() in ["y", "yes", "true"]
                    if answer == True:
                        self.RunInstallers(name, manager=manager)
        else:
            print("Everything OK!")
        print("----------------------------------------------------------------------")
        print("Goodbye!")

    def RunInstallers(self, name, manager=None):
        def pm(nm):
            return self.ShellCheck(nm, pm=True)

        if manager:
            if manager == "conda":
                if pm("conda") and self.CondaInstall(name):
                    return True
                if pm("pip") and self.PipInstall(name):
                    return True
            if manager == "pip":
                if pm("pip") and self.PipInstall(name):
                    return True
                if pm("conda") and self.CondaInstall(name):
                    return True
            if manager in ["nodejs", "npm"]:
                if pm("nodejs") and self.NpmInstall(name):
                    return True
            if manager == "apt":
                if pm("apt") and self.AptInstall(name):
                    return True
            if manager == "yum":
                if pm("yum") and self.YumInstall(name):
                    return True
            if manager == "rpm":
                if pm("rpm") and self.RpmInstall(name):
                    return True
            if manager == "zypper":
                if pm("zypper") and self.ZypperInstall(name):
                    return True
            if manager == "yast":
                if pm("yast") and self.YastInstall(name):
                    return True
            if manager == "snap":
                if pm("snap") and self.SnapInstall(name):
                    return True
            print("Unrecognized package manager: " + name)
            return False
        else:
            if self.ShellInstall(name):
                return True
            if pm("conda") and self.CondaInstall(name):
                return True
            if pm("pip") and self.PipInstall(name):
                return True
            # if pm('apt') and self.AptInstall(name): return True
            # if pm('yum') and self.YumInstall(name): return True
            # if pm('rpm') and self.RpmInstall(name): return True
            # if pm('zypper') and self.ZypperInstall(name): return True
            # if pm('yast') and self.YastInstall(name): return True
            # if pm('snap') and self.SnapInstall(name): return True
            if pm("nodejs") and self.NpmInstall(name):
                return True
            return False

    def MarkInstalled(self, name, checkval):
        if checkval:
            if name in self.NotInstalled:
                self.NotInstalled.remove(name)
            if name in self.PMNotInstalled:
                self.PMNotInstalled.remove(name)
                self.PMInstalled.append(name)
            self.Installed.append(name)
        return checkval

    def ShellInstall(self, name, shellmode=False):
        if name in self.ShellList:
            shellmode = True
        installerpath = self.cwd + "/_installers/" + name + "_install.sh"
        print("installerpath", installerpath)
        if os.path.exists(installerpath):
            returncodes = 0
            with open(installerpath, "r") as file:
                for line in file.readlines():
                    print("line", line)
                    result, returncode = RunCmd(line, cwd=self.cwd)
                    returncodes += returncode
            returncodes = not bool(returncodes)
            return self.MarkInstalled(name, self.ShellCheck(name))

    def CondaInstall(self, name):
        print("attempting conda install " + name)
        # result, returncode = RunCmd('conda install --quiet --name '+name)
        result0, returncode0 = RunCmd("conda config --prepend channels conda-forge")
        result1, returncode1 = RunCmd("conda install -y " + name)
        result2, returncode2 = RunCmd("conda update -y " + name)
        print("result1", result1)
        print("returncode1", returncode1)
        return self.MarkInstalled(name, self.CondaCheck(name))

    def PipInstall(self, name):
        print("attempting pip install " + name)
        result, returncode = RunCmd("pip install " + name, cwd=self.cwd)
        print("result", result)
        print("returncode", returncode)
        return self.MarkInstalled(name, self.PipCheck(name))

    def NpmInstall(self, name):
        print("attempting npm install " + name)
        result, returncode = RunCmd(
            "npm install " + name, cwd=self.cwd + "/Javascript", shell=True
        )
        print("result", result)
        print("returncode", returncode)
        return self.MarkInstalled(name, self.NpmCheck(name))

    def AptInstall(self, name):
        # Untested
        print("attempting apt install", name)
        output, returncode = RunCmd("apt install " + name, cwd=self.cwd)
        print("output", output)
        print("returncode", returncode)
        return self.MarkInstalled(name, self.AptCheck(name))

    def YumInstall(self, name):
        # Untested
        print("attempting yum install", name)
        output, returncode = RunCmd("yum install " + name, cwd=self.cwd)
        print("output", output)
        print("returncode", returncode)
        return self.MarkInstalled(name, self.YumCheck(name))

    def RpmInstall(self, name):
        # Untested
        print("attempting rpm install", name)
        output, returncode = RunCmd("rpm install " + name, cwd=self.cwd)
        print("output", output)
        print("returncode", returncode)
        return self.MarkInstalled(name, self.YumCheck(name))

    def ZypperInstall(self, name):
        # Untested
        print("attempting zypper install", name)
        output, returncode = RunCmd("zypper install " + name, cwd=self.cwd)
        print("output", output)
        print("returncode", returncode)
        return self.MarkInstalled(name, self.YumCheck(name))

    def YastInstall(self, name):
        # Untested
        print("attempting yast install", name)
        output, returncode = RunCmd("yast install " + name, cwd=self.cwd)
        print("output", output)
        print("returncode", returncode)
        return self.MarkInstalled(name, self.YumCheck(name))

    def SnapInstall(self, name):
        # Untested
        print("attempting snap install", name)
        output, returncode = RunCmd("snap install " + name, cwd=self.cwd)
        print("output", output)
        print("returncode", returncode)
        return self.MarkInstalled(name, self.YumCheck(name))

    ##################################################

    def CountTests(self, dependencies, count):
        if isinstance(dependencies, str):
            dependencies = [dependencies]
        for dependency in dependencies:
            actual_dependecy = "actual_" + dependency
            if actual_dependecy not in self.TestCount:
                self.TestCount[actual_dependecy] = 0
            self.TestCount[actual_dependecy] += count


class TestRunner:
    """
    Recursively walks down from the folder in which this module is
    placed running every test that it can find.
    """

    SkippedCount = 0

    def __init__(self, *args):
        super(TestRunner, self).__init__()

        """
        self.TechGroupings = {
            'Languages' : ['Python', 'Go', 'C++', 'Javascript', 'Java', 'C#', 'PHP'],
            #'Libraries' : [],
            #'Cloud Platforms' : ['AWS', 'GCP', 'Azure'],
            #'Game Engines' : ['Unreal', 'Unity', 'CryEngine'],
            #'3D Tools' : ['Houdini', 'Maya', 'Cinema4D', 'Lightwave'],
            #'2D Tools' : ['Nuke', 'Fusion', 'AfterEffects'],
        }
        """
        self.TestLoader = unittest.TestLoader()
        self.TestSuites = {
            "Languages": {
                "Python": unittest.TestSuite(),
                "Go": unittest.TestSuite(),
                "C++": unittest.TestSuite(),
                "Javascript": unittest.TestSuite(),
                "Java": unittest.TestSuite(),
                "C#": unittest.TestSuite(),
                "PHP": unittest.TestSuite(),
                "C#": unittest.TestSuite(),
            },
            #'PythonLibraries' : {
            #    'pandas' : unittest.TestSuite(),
            #    'numpy' : unittest.TestSuite(),
            #    'static-frame' : unittest.TestSuite(),
            # },
            "Cloud Platforms": {
                "AWS": unittest.TestSuite(),
                "GCP": unittest.TestSuite(),
                "Azure": unittest.TestSuite(),
            },
            "Game Engines": {
                "Unreal": unittest.TestSuite(),
                "Unity": unittest.TestSuite(),
                "CryEngine": unittest.TestSuite(),
            },
            "3D Tools": {
                "Houdini": unittest.TestSuite(),
                "Maya": unittest.TestSuite(),
                "Cinema4D": unittest.TestSuite(),
                "Lightwave": unittest.TestSuite(),
                "Lightwave": unittest.TestSuite(),
            },
            "2D Tools": {
                "Nuke": unittest.TestSuite(),
                "Fusion": unittest.TestSuite(),
                "AfterEffects": unittest.TestSuite(),
            },
            "Other": {},
        }
        self.TestResults = {
            "Languages": {},
            #'Libraries' : {},
            #'Cloud Platforms' : {},
            #'Game Engines' : {},
            #'3D Tools' : {},
            #'2D Tools' : {},
            "Other": {},
        }

        # self.TestSuite = unittest.TestSuite()
        self.TestArgs = self.LoadTestVars()

        if len(args) > 0:
            for filepath in args:
                testsuite = unittest.TestSuite()
                print("ImportTests!", filepath)
                self.ImportTests(os.path.abspath(filepath), testsuite)
                self.TestSuites["Other"][filepath] = testsuite
        else:
            print("self.TestArgs.folders", self.TestArgs.folders)
            # self.RecursiveImport(folders=self.TestArgs.folders)

    @staticmethod
    def getcwd():
        # wd = os.path.dirname(os.path.abspath(__file__))
        return os.getcwd()

    @staticmethod
    def collect_foldertree_filelist():
        cwd = os.getcwd()
        foldertree, filelist = [], []
        for root, dirs, files in os.walk(cwd):
            skip = []
            relative_root = root.split(cwd, 1)[-1].strip(os.sep)
            for dir in dirs:
                if dir[0] in [".", "_"]:
                    skip.append(dir)
                    continue
                foldertree.append(os.path.join(relative_root, dir))
            for r in skip:
                dirs.remove(r)  # mutate dirs to skip recursion of hidden folders

            for file in files:
                filelist.append(os.path.join(relative_root, file))
        return foldertree, filelist

    @staticmethod
    def convert_foldertree_to_nested_dict(foldertree, filelist):
        result = {"": {}}
        for dir in foldertree:
            cursor = result
            for part in dir.split(os.sep)[1:]:
                if part not in cursor.keys():
                    cursor[part] = {}
                cursor = cursor[part]
        for filepath in filelist:
            cursor = result
            filename = filepath.split(os.sep)[-1]
            for part in filepath.split(os.sep)[1:-1]:
                cursor = cursor[part]
            if cursor == result:
                cursor = cursor[""]
            cursor[filename] = filepath
        return result

    @staticmethod
    def walk_nested_dict(nested_dict):
        for key in nested_dict.keys():
            if type(nested_dict[key]) == str:
                yield nested_dict[key]
            elif type(nested_dict[key]) == dict:
                for w in TestRunner.walk_nested_dict(nested_dict[key]):
                    yield w

    @staticmethod
    def create_suites():
        cwd = TestRunner.getcwd()
        result = {"": unittest.TestSuite()}
        for pathpart in os.listdir(cwd):
            if pathpart[0] in ['.', '_']:
                continue
            if os.path.isdir(os.path.join(cwd, pathpart)):
                result[pathpart] = unittest.TestSuite()
        return result

    def discover_tests(self):
        foldertree, filelist = TestRunner.collect_foldertree_filelist()
        nested_dict = TestRunner.convert_foldertree_to_nested_dict(foldertree, filelist)
        testsuites = TestRunner.create_suites()
        for filepath in TestRunner.walk_nested_dict(nested_dict):
            if os.sep in filepath:
                suite = testsuites[filepath.split(os.sep)[0]]
            else:
                suite = testsuites[""]
            tests = self.collect_testnames(filepath)
            suite.addTests(tests)
        return testsuites

    def update_display(self):
        pass

    def collect_testnames(self, modulepath: str):
        extension = modulepath.rsplit(".", 1)[-1]
        if extension == "py":
            return self.collect_py(modulepath)
        elif extension == "js":
            return self.collect_js(modulepath)
        elif extension == "go":
            return self.collect_go(modulepath)
        else:
            return []

    # class TestCollector?
    def collect_py(self, modulepath: str):
        return []

    def collect_js(self, modulepath: str):
        return []

    def collect_go(self, modulepath: str):
        return []

    def main(self):
        """
        TODO: add printing of comaprison columns for matching testnames like this

        TestName        python3         c++             javascript      go
        Dijkstras       P-1.000s        P-0.500s        P-0.800s        F-10.000s
        Fibonacci       P-1.000s        P-0.500s        P-0.800s        F-10.000s
        QuickSort       P-1.000s                        P-0.800s        F-10.000s
        Darts           P-1.000s        P-0.500s        P-0.800s        F-10.000s

        TestName        aws             gcp
        CreateCluster   P-300.000s      P-250.000s
        DestroyCluster  P-300.000s      P-250.000s

        TestName        unreal          unity
        PluginCompile   P-50.000s       P-20.000s
        SublevelHell    P-300.000s      P-250.000s
        """
        print("----------------------------------------------------------------------")
        start = datetime.now()

        # run, errors, failures = 0, 0, 0
        testsRun, errors, failures = 0, [], []
        finalresult = True
        self.Runner = unittest.TextTestRunner(stream=open(os.devnull, "w"))
        # self.Runner = unittest.TextTestRunner()
        for groupingname, grouping in self.TestSuites.items():
            print(groupingname + ":\n")
            print("\t\t" + "\t\t".join(grouping.keys()))
            for techname, testsuite in grouping.items():
                testsuite.results = {}
                for test in testsuite:
                    if len(test._tests) == 0:
                        continue
                    testname = test._tests[0].__class__.__name__.replace("test_", "", 1)
                    if not self.TestArgs.discover:
                        starttime = datetime.now()
                        testsuite.results[testname] = self.Runner.run(test)
                        resulttime = datetime.now() - starttime
                        print(testname + "\t\t" + str(resulttime))
                        if not testsuite.results[testname].wasSuccessful():
                            finalresult = False
                        testsRun += testsuite.results[testname].testsRun
                        for e in testsuite.results[testname].errors:
                            errors.append(e)
                        for f in testsuite.results[testname].failures:
                            errors.append(f)
                    else:
                        print("Discovered", testname)
            print("\n")
        if self.TestArgs.discover:
            print("Exiting Discover!")
            sys.exit(0)
        print("----------------------------------------------------------------------")
        t = datetime.now() - start
        print(
            "KungFu ran " + str(testsRun) + " tests in " + str(t.total_seconds()) + "s"
        )
        if len(errors) > 0:
            for e in errors:
                print(e)
            print("KungFu ERRORED (errors=" + str(len(errors)) + ")")
        if len(failures) > 0:
            for f in failures:
                print(f)
            print("KungFu FAILED (failures=" + str(len(failures)) + ")")
        if finalresult == True:
            print("Everything OK!")
            sys.exit(0)
        else:
            sys.exit(1)

    def GetTestSuite(self, foldername):
        print("GetTestSuite", foldername)
        # wd = os.path.dirname(os.path.abspath(__file__))
        fname = foldername.split(os.sep, 1)[0]
        for grouping in self.TestSuites.values():
            print("grouping", grouping.keys())
            if fname in grouping.keys():
                return grouping[fname]
        else:
            testsuite = unittest.TestSuite()
            self.TestSuites["Other"][fname] = testsuite
            return testsuite

    def RecursiveImport(self, folders=None):
        wd = os.path.dirname(os.path.abspath(__file__))
        if folders == None:
            folders = [wd]
        else:
            for i, folder in enumerate(folders):
                folders[i] = folder.replace("\\", os.sep).replace("/", os.sep)
                # folders[i] = wd+os.sep+folder
        for folder in folders:
            # testsuite = unittest.TestSuite()
            testsuite = self.GetTestSuite(folder)
            for root, dirs, files in os.walk(wd + os.sep + folder):
                dirs.sort()
                files.sort()
                for i, dir in reversed(list(enumerate(dirs))):
                    if dir[0] == ".":  # .git .hg etc
                        del dirs[i]
                    elif dir == "__pycache__":
                        del dirs[i]
                    elif dir.rsplit(".", 1)[-1] == "egg-info":
                        del dirs[i]
                for file in files:
                    if file.rsplit(".", 1)[-1] == "py":
                        self.ImportTests(os.path.join(root, file), testsuite)
                        # self.ImportTests(root.replace('\\','/')+'/'+file, testsuite)
            # grouping = 'Other'
            # for group, techlist in self.TechGroupings.items():
            #    if folder in techlist:
            #        self.TestSuites[group][folder] = testsuite
            #        break
            # else:
            #    self.TestSuites['Other'][folder] = testsuite

    def ImportTests(self, ModulePath, TestSuite):
        ModuleName = ModulePath.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        if ModuleName in ["KungFu", "__init__"] or "BaseClasses" in ModuleName:
            return
        if ModuleName in globals().keys():
            raise Exception(
                "Namespace conflict found. Module name already in use, pick another.",
                ModuleName,
            )
        ModuleSpec = util.spec_from_file_location("module.name", ModulePath)
        Module = util.module_from_spec(ModuleSpec)
        try:
            ModuleSpec.loader.exec_module(Module)
        except ImportError as exception:
            pass
        for ClassName, Class in inspect.getmembers(Module):
            if "test_" in ClassName and Class != None:
                if self.TestArgs.filter and self.TestArgs.filter not in ClassName:
                    continue
                if ClassName in globals().keys():
                    raise Exception(
                        "Namespace conflict found. Class Name already in use, pick another.",
                        ClassName,
                        Module.__file__,
                    )
                globals()[ClassName] = Class
                TestSuite.addTest(unittest.makeSuite(Class))
                # tests = self.TestLoader.loadTestsFromTestCase(Class)
                # TestSuite.addTests(tests)

    def LoadTestVars(self):
        parser = argparse.ArgumentParser()

        def csv(val):
            return val.split(",")

        parser.add_argument(
            "-folders", help="Run all tests in the specified folders.", type=csv
        )
        parser.add_argument(
            "-folder", help="Run all tests in the specified folder.", type=str
        )
        parser.add_argument(
            "-filter",
            help="Run only test cases with names that match this filter.",
            type=str,
        )
        parser.add_argument(
            "-sleep", help="Run tests with a sleeptime of n seconds.", type=float
        )
        parser.add_argument(
            "--discover",
            help="Discover all tests in the specified folders.",
            action="store_true",
        )
        parser.add_argument(
            "--cloud",
            help="Run tests that simulate the creation of cloud resources.",
            action="store_true",
        )
        parser.add_argument(
            "--create",
            help="Run tests that provision real cloud resources. THIS WILL COST MONEY!",
            action="store_true",
        )
        parser.add_argument(
            "--destroy",
            help="Run tests that destroy real cloud resources. THIS IS POTENTIALLY DESTRUCTIVE!",
            action="store_true",
        )
        parser.add_argument(
            "--install",
            help="Run all installers. You probably shouldn't do this in the full KungFu library!",
            action="store_true",
        )
        parser.add_argument(
            "--skip",
            help="Skip all installers. Turn this on for CI.",
            action="store_true",
        )

        self.TestArgs, unknown = parser.parse_known_args()
        if self.TestArgs.sleep == None:
            self.TestArgs.sleep = 0.5
        if self.TestArgs.folder != None:
            self.TestArgs.folders = [self.TestArgs.folder]
        self.TestArgs.kwargs = {}
        for (key, value) in self.TestArgs._get_kwargs():
            if key != "kwargs":
                self.TestArgs.kwargs[key] = value

        # arbitrary keyword parsing
        for i in range(0, len(unknown), 2):
            key = unknown[i].replace("-", "")
            value = unknown[i + 1]
            self.TestArgs.kwargs[key] = value

        print(self.TestArgs)
        sys.TestArgs = self.TestArgs
        return self.TestArgs


def RunCmd(
    CommandString,
    silent=True,
    shell=False,
    cwd=os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"),
):
    """
    Making all system calls via this command.

    TODO: Turn this into CommandRunner class, and add threading
    wrapper to each subprocess so that tests and module level calls
    are automatically parralellized.

    TODO: Create and manage mutex locks for each listed dependency in
    a test.
    """
    if not silent:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("KungFu.RunCmd", CommandString)
        print("run_command", shlex.split(CommandString))
        print("cwd", cwd)
    result = u""
    try:
        with subprocess.Popen(
            shlex.split(CommandString),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            shell=shell,
        ) as proc:
            stdout, stderr = proc.communicate()
            returncode = proc.poll()
            result += stdout.decode("utf8")
            result += stderr.decode("utf8")
    except:
        result += traceback.format_exc()
        returncode = 1
    if not silent:
        print("returncode", returncode)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
    return result, returncode


# Main#############################################
def main(*args):
    """
    KungFu.main() will run recursively
    KungFu.main(__file__) will run a single file
    KungFu.main([file1, file2]) will run a list of files
    """
    print("KungFu.main!")
    import FooFinder

    DependencyHandler()
    TestInstance = TestRunner(*args)
    TestInstance.main()


if __name__ == "__main__":
    unittest.main()
    # main()
    # WriteBack()  # Code will only modify itself when run directly
