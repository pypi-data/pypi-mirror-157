import pytest

import pytest_chunks


def test_validator() -> None:
    assert pytest_chunks.chunks_validator("1-1") == (1, 1)
    assert pytest_chunks.chunks_validator("1-2") == (1, 2)
    assert pytest_chunks.chunks_validator("3-10") == (3, 10)

    with pytest.raises(ValueError):
        pytest_chunks.chunks_validator("a-b")


def test_hello(pytester: pytest.Pytester) -> None:
    """Make sure that our plugin works."""

    # create a temporary conftest.py file
    pytester.makeconftest(
        """
        import pytest

        @pytest.fixture
        def hello(request):
            def _hello(name=None):
                if not name:
                    name = "World"
                return "Hello {name}!".format(name=name)

            return _hello

        @pytest.fixture(params=[
            "Brianna",
            "Andreas",
            "Floris",
            "Him",
            "Her",
            "Cat",
            "Dog",
        ])
        def name(request):
            return request.param
    """
    )

    # create a temporary pytest test file
    pytester.makepyfile(
        """
        import pytest

        def test_hello_default(hello):
            assert hello() == "Hello World!"

        def test_hello_failure(hello):
            assert hello() == "Bye Bye"

        def test_hello_name(hello, name):
            assert hello(name) == "Hello {0}!".format(name)

        @pytest.mark.xfail
        def test_hello_xfailed(hello):
            assert hello() == "Bye Bye"
    """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=8, failed=1, skipped=0, xfailed=1)

    result = pytester.runpytest("--chunk=1-2")
    result.assert_outcomes(passed=4, failed=1, skipped=5, xfailed=0)

    result = pytester.runpytest("--chunk=2-2")
    result.assert_outcomes(passed=4, failed=0, skipped=5, xfailed=1)

    result = pytester.runpytest("--chunk=1-3")
    result.assert_outcomes(passed=3, failed=1, skipped=6, xfailed=0)

    result = pytester.runpytest("--chunk=2-3")
    result.assert_outcomes(passed=4, failed=0, skipped=6, xfailed=0)

    result = pytester.runpytest("--chunk=3-3")
    result.assert_outcomes(passed=1, failed=0, skipped=8, xfailed=1)
