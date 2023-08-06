# Detect number of threads to build with.
ifndef CPU_COUNT
	NUM_THREADS = 1
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		NUM_THREADS = $(shell nproc || 1)
	endif
	ifeq ($(UNAME_S),Darwin)
		NUM_THREADS = $(shell sysctl -n hw.physicalcpu)
	endif
	ifeq ($(findstring MSYS_NT,$(UNAME_S)),MSYS_NT)
		NUM_THREADS = ${NUMBER_OF_PROCESSORS}
	endif
else
	NUM_THREADS = $(CPU_COUNT)
endif

# Ideally we should use a packaging tool command like pip here instead of just `python
# setup.py build_ext` because calling `setup.py` directly does not respect PEP 517 and
# does not regenerate version.py when it's deleted (e.g. with a `make realclean`) and
# does not build in an isolated environment. Unfortunately the pip command is far
# slower, and rebuilds extensions even if nothing has changed, so for now we keep the
# `setup.py` command and instead just make sure that the build dependencies specified in
# `pyproject.toml` are present in the local environment, which seems to allow version.py
# to get rebuilt.
BUILD_CMD = python setup.py build_ext -j $(NUM_THREADS) --inplace

default:
	$(BUILD_CMD)

debug:
	CYTHON_DEBUG=1 $(BUILD_CMD)

# Build Cython extensions with the CYTHON_TRACE flag enabled to allow coverage tracking.
coverage:
	CYTHON_COVERAGE=1 $(BUILD_CMD)

clean:
	find . -name "*.so" -type f -delete
	find . -name "*.dll" -type f -delete

realclean: clean
	git clean -fX

lint:
	pylint --rcfile=.pylintrc ./src/finesse/

# Install/reinstall Finesse as a local editable package.
# NOTE: normally installing the development environment via conda will automate this
# step, but this can be useful to install new dependencies when `setup.cfg` or
# `pyproject.toml` change, or where you intend to manage the non-Python environment
# dependencies yourself (looking at you, Phil).
develop:
	pip install -e .[test,docs,lint,inplacebuild]
