import io
import pytest
import itertools
from pathlib import Path
from setuptools_github import tools


class REFilter:
    def __init__(self, expr):
        from re import compile

        self.expr = compile(expr)

    def __repr__(self):
        return self.expr.pattern


class RESearch(REFilter):
    "build an object with a .search method, useable to filter"

    def __init__(self, expr, invert=False):
        super().__init__(expr)
        self.invert = invert

    def search(self, txt):
        out = self.expr.search(txt)
        return (not out) if self.invert else out


class REMatch(REFilter):
    def __eq__(self, actual):
        return bool(self.expr.match(actual))


# this is the output from ${{ toJson(github) }}
GITHUB = {
    "beta": {
        "ref": "refs/heads/beta/0.0.4",
        "sha": "2169f90c22e",
        "run_number": "8",
    },
    "release": {
        "ref": "refs/tags/release/0.0.3",
        "sha": "5547365c82",
        "run_number": "3",
    },
    "master": {
        "ref": "refs/heads/master",
        "sha": "2169f90c",
        "run_number": "20",
    },
}


def test_abort_exception():
    a = tools.AbortExecution(
        "a one-line error message",
        """
        A multi line
          explaination of
           what happened
         with some detail
    """,
        """
    Another multiline hint how
      to fix the issue
    """,
    )

    assert a.message == "a one-line error message"
    assert (
        f"\n{a.explain}\n"
        == """
A multi line
  explaination of
   what happened
 with some detail
"""
    )
    assert (
        f"\n{a.hint}\n"
        == """
Another multiline hint how
  to fix the issue
"""
    )

    assert (
        f"\n{str(a)}\n"
        == """
a one-line error message
  A multi line
    explaination of
     what happened
   with some detail
hint:
  Another multiline hint how
    to fix the issue
"""
    )

    a = tools.AbortExecution("hello world")
    assert a.message == "hello world"
    assert a.explain == ""
    assert a.hint == ""
    assert str(a) == "hello world"


def test_indent():
    txt = """
    This is a simply
       indented text
      with some special
         formatting
"""
    expected = """
..This is a simply
..   indented text
..  with some special
..     formatting
"""

    found = tools.indent(txt[1:], "..")
    assert f"\n{found}" == expected


def test_hubversion():
    "extracts from a GITHUB a (version, hash) tuple"

    pytest.raises(
        tools.InvalidGithubReference,
        tools.hubversion,
        {"ref": "", "run_number": "", "sha": ""},
        "",
    )

    fallbacks = [
        "123",
        "",
    ]

    expects = {
        ("beta", ""): ("0.0.4b8", "2169f90c22e"),
        ("beta", "123"): ("0.0.4b8", "2169f90c22e"),
        ("release", "123"): ("0.0.3", "5547365c82"),
        ("release", ""): ("0.0.3", "5547365c82"),
        ("master", "123"): ("123", "2169f90c"),
        ("master", ""): ("", "2169f90c"),
    }

    itrange = itertools.product(GITHUB, fallbacks)
    for key, fallback in itrange:
        gdata = GITHUB[key]
        expected = expects[(key, fallback)]
        assert expected == tools.hubversion(gdata, fallback)


def test_get_module_var(tmp_path):
    "pulls variables from a file"
    path = tmp_path / "in0.txt"
    path.write_text(
        """
# a test file
A = 12
B = 3+5
C = "hello"
# end of test
"""
    )
    assert 12 == tools.get_module_var(path, "A")
    assert "hello" == tools.get_module_var(path, "C")
    pytest.raises(AssertionError, tools.get_module_var, path, "B")
    pytest.raises(tools.MissingVariable, tools.get_module_var, path, "X1")


def test_set_module_var_empty_file(tmp_path):
    "check if the set_module_var will create a bew file"
    path = tmp_path / "in1.txt"

    assert not path.exists()
    tools.set_module_var(path, "__version__", "1.2.3")

    assert path.exists()
    path.write_text("# a fist comment line\n" + path.read_text().strip())

    tools.set_module_var(path, "__hash__", "4.5.6")
    assert (
        path.read_text().strip()
        == """
# a fist comment line
__version__ = "1.2.3"
__hash__ = "4.5.6"
""".strip()
    )


def test_set_module_var(tmp_path):
    "handles set_module_var cases"
    path = tmp_path / "in2.txt"

    path.write_text(
        """
# a fist comment line
__hash__ = "4.5.6"
# end of test
"""
    )

    version, txt = tools.set_module_var(path, "__version__", "1.2.3")
    assert not version
    assert (
        txt.rstrip()
        == """
# a fist comment line
__hash__ = "4.5.6"
# end of test
__version__ = "1.2.3"
""".rstrip()
    )

    version, txt = tools.set_module_var(path, "__version__", "6.7.8")
    assert version == "1.2.3"
    assert (
        txt.rstrip()
        == """
# a fist comment line
__hash__ = "4.5.6"
# end of test
__version__ = "6.7.8"
""".rstrip()
    )

    version, txt = tools.set_module_var(path, "__hash__", "9.10.11")
    assert version == "4.5.6"
    assert (
        txt.rstrip()
        == """
# a fist comment line
__hash__ = "9.10.11"
# end of test
__version__ = "6.7.8"
""".rstrip()
    )
    return


def test_update_version(tmp_path):
    "test the update_version processing"
    from hashlib import sha224

    def writeinit(path):
        path.write_text(
            """
# a test file
__version__ = "1.2.3"
__hash__ = "4.5.6"

# end of test
"""
        )
        return sha224(path.read_bytes()).hexdigest()

    initfile = tmp_path / "__init__.py"
    hashval = writeinit(initfile)

    # verify nothing has changed
    assert "1.2.3" == tools.update_version(initfile)
    assert hashval == sha224(initfile.read_bytes()).hexdigest()

    # we update the __version__/__hash__ from a master branch
    tools.update_version(initfile, GITHUB["master"])
    assert (
        initfile.read_text()
        == """
# a test file
__version__ = "1.2.3"
__hash__ = "2169f90c"

# end of test
"""
    )

    # we update __version__/__hash__ from a beta branch (note the b<build-number>)
    writeinit(initfile)
    tools.update_version(initfile, GITHUB["beta"])
    assert (
        initfile.read_text()
        == """
# a test file
__version__ = "0.0.4b8"
__hash__ = "2169f90c22e"

# end of test
"""
    )

    writeinit(initfile)
    tools.update_version(initfile, GITHUB["release"])
    assert (
        initfile.read_text()
        == """
# a test file
__version__ = "0.0.3"
__hash__ = "5547365c82"

# end of test
"""
    )


def test_bump_version():
    "bump version test"
    assert tools.bump_version("0.0.1", "micro") == "0.0.2"
    assert tools.bump_version("0.0.2", "micro") == "0.0.3"
    assert tools.bump_version("0.0.2", "minor") == "0.1.0"
    assert tools.bump_version("1.2.3", "major") == "2.0.0"
    assert tools.bump_version("1.2.3", "release") == "1.2.3"


@pytest.mark.parametrize("method", ["no-force-no-keep", "no-force-keep"])
def test_gitwrapper_init(tmp_path, method):
    repo = tools.GitWrapper(tmp_path / "wow")
    assert repo.workdir == tmp_path / "wow"
    assert not repo.workdir.exists()

    def no_force_no_keep():
        repo.init(force=False, keepfile=False)
        assert repo.workdir.exists()
        assert not [
            p
            for p in repo.workdir.rglob("*")
            if not str(p.relative_to(repo.workdir)).startswith(".git")
        ]
        pytest.raises(FileExistsError, repo.init, force=False, keepfile=False)

    def no_force_keep():
        repo.init(force=False, keepfile=True)
        assert repo.workdir.exists()
        assert [
            p.relative_to(repo.workdir)
            for p in repo.workdir.rglob("*")
            if not str(p.relative_to(repo.workdir)).startswith(".git")
        ] == [Path(".keep")]
        pytest.raises(FileExistsError, repo.init, force=False, keepfile=True)

    locals()[method.replace("-", "_")]()
    assert repo.workdir == tmp_path / "wow"
    assert repo.workdir.exists()


def test_gitwrapper_clone(tmp_path):
    repo = tools.GitWrapper(tmp_path / "repo").init()
    assert repo(["rev-parse", "--abbrev-ref", "HEAD"]).strip() == "master"

    repo(["checkout", "-b", "a-branch"])
    assert repo(["rev-parse", "--abbrev-ref", "HEAD"]).strip() == "a-branch"

    # clone into project
    project = repo.clone(tmp_path / "project", force=False)
    assert project(["rev-parse", "--abbrev-ref", "HEAD"]).strip() == "a-branch"

    # clone without and with the force flag
    pytest.raises(ValueError, repo.clone, tmp_path / "project", force=False)
    repo.clone(tmp_path / "project", force=True)

    # re-clone the master branch
    project = repo.clone(tmp_path / "project", branch="master", force=True)
    assert project(["rev-parse", "--abbrev-ref", "HEAD"]).strip() == "master"


def test_gitwrapper_dump(tmp_path):
    repo = tools.GitWrapper(tmp_path / "repo2").init()

    # adds a file
    path = repo / "abc.txt"
    path.write_text("hello")
    repo(["add", path])
    repo(["commit", "-m", "initial", path])
    assert repo(["rev-parse", "--abbrev-ref", "HEAD"]).strip() == "master"

    # clone the project
    project = repo.clone(tmp_path / "wow-cloned", force=True)

    # check the output
    expected = REMatch(
        r"""
REPO: .*
 .status.
  On branch master
  Your branch is up to date with 'origin/master'.
\s+
  nothing to commit, working tree clean

 .branch.
  . master               \s+[0-9a-f]{7} .origin/master. initial
    remotes/origin/HEAD  \s+-> origin/master
    remotes/origin/master\s+[0-9a-f]{7} initial

 .tags.
\s+
 .remote.
  origin\s.*[(]fetch[)]
  origin\s.*[(]push[)]
""".strip()
    )
    assert project.dump(io.StringIO) == expected


def test_gitcli(tmp_path):
    repo = tools.GitCli(tmp_path / "wow1").init(force=True)
    assert repo.branch() == "master"
    assert (repo.branch(name="opla"), repo.branch()) == ("master", "opla")
    assert repo.branches() == (["master", "opla"], {})

    project = repo.clone(tmp_path / "wow1-cloned", force=True)
    assert project.branch() == "opla"

    project = repo.clone(tmp_path / "wow1-cloned", branch="master", force=True)
    assert project.branch() == "master"
    assert (project.branch(name="wow"), project.branch()) == ("master", "wow")

    assert project.branches() == (
        ["master", "wow"],
        {"origin": ["HEAD", "master", "opla"]},
    )
    assert project.branches(RESearch("[A-Z]", True)) == (
        ["master", "wow"],
        {"origin": ["master", "opla"]},
    )

    path = project.workdir / "abc.txt"
    path.write_text("hello")
    project.commit(path, "a commit")
