Calibration Client
==================

Calcat is the Web App design for Calibration Constants Data Management
at European XFEL.

This library (calibration_client) is a client for the RESTful APIs exposed
by the European XFEL Calibration Constants Catalogue Web Application - calCat
(https://in.xfel.eu/calibration).

*Repository:*

- https://git.xfel.eu/gitlab/ITDM/calibration_client

*Dependencies:*

- oauthlib (https://pypi.python.org/pypi/oauthlib)
- requests (https://github.com/psf/requests)
- requests-oauthlib (https://github.com/requests/requests-oauthlib)
- oauth2_xfel_client (https://git.xfel.eu/gitlab/ITDM/oauth2_xfel_client)
- pytz (https://pypi.org/project/pytz/)

Installation
------------

Python project
""""""""""""""

1. Install requirements, if never done before

 1.1. For OS X distributions::

  1.1.1. Homebrew

        brew install python3

  1.1.2 Port

        sudo port install python36

        sudo port select --set python3 python36

        sudo port install py36-pip
        sudo port select --set pip pip36

 1.2. For Linux distributions::

    sudo apt-get update
    sudo apt-get install python3.9


2. Make calibration_client library available in your python environment

 2.1. Install it via pip::

    # Install dependencies from local wheels files
    pip install . --no-index --find-links ./external_dependencies/

    # Install dependencies from the pypi
    pip install .

    # Force re-installation of packages
    pip install --ignore-installed

 Installing it will place two folders under the current Python installation
 site-packages folder:

 - `calibration_client` with the sources;
 - `calibration_client-11.0.0.dist-info/` with Wheels configuration files.

 To identify your Python site-packages folder run::

    python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"


Usage
-----

To use this project you need to import it::

    from calibration_client import CalibrationClient


1. Connection to the MdC (Metadata Catalog)::

    from calibration_client import CalibrationClient

    # Necessary configuration variables to establish a connection
    # Go to https://in.xfel.eu/calibration/oauth/applications to make a token for
    # the calibration catalogue.
    user_id = 'PUT_HERE_YOUR_CLIENT_KEY'
    user_secret = 'PUT_HERE_YOUR_SECRET_KEY'
    user_email = 'luis.maia@xfel.eu'
    #
    metadata_web_app_url = 'https://in.xfel.eu/calibration'
    token_url = 'https://in.xfel.eu/calibration/oauth/token'
    refresh_url = 'https://in.xfel.eu/calibration/oauth/token'
    auth_url = 'https://in.xfel.eu/calibration/oauth/authorize'
    scope = ''
    base_api_url = 'https://in.xfel.eu/calibration/api/'

    # Authentication via OAUTH2
    # Generate the connection (example with minimum parameter options)
    client_conn = CalibrationClient(client_id=user_id,
                                    client_secret=user_secret,
                                    user_email=user_email,
                                    token_url=token_url,
                                    refresh_url=refresh_url,
                                    auth_url=auth_url,
                                    scope=scope,
                                    base_api_url=base_api_url)

    # Authentication via OAUTH2
    # Generate the connection (example with all parameter options)
    client_conn = CalibrationClient(use_oauth2=True
                                    client_id=user_id,
                                    client_secret=user_secret,
                                    user_email=user_email,
                                    token_url=token_url,
                                    refresh_url=refresh_url,
                                    auth_url=auth_url,
                                    scope=scope,
                                    base_api_url=base_api_url,
                                    session_token=None,
                                    max_retries=3,
                                    timeout=12,
                                    ssl_verify=True)

    # Authentication via Proxy Service
    # Generate the connection (example with minimum parameter options)
    client_conn = CalibrationClient(use_oauth2=False,
                                    base_api_url="http://HOSTNAME:PORT/api/")


2. Interaction with the CalCat (Calibration Catalog):

 2.1 Example data_group_types::

    params_h = { 'detector_identifier': 'TEST_DET_CI-2',
                 'snapshot_at': '' }

    resp = client_conn.get_all_phy_det_units_from_detector(params_h)

    resp
    # >>> {'success': True,
    #      'data': [ { "id":-1,
    #                  "physical_name":"PHYSICAL_DETECTOR_UNIT-1_DO_NOT_DELETE",
    #                  "karabo_da":"TEST_DAQ_DA_01",
    #                  "virtual_device_name":"Q1M1",
    #                  "uuid":1000,
    #                  "float_uuid":4.94e-321,
    #                  "detector_type_id":-1,
    #                  "detector_id":-2,
    #                  "flg_available":true,
    #                  "description":"None",
    #                  "detector":{
    #                     "id":-2,
    #                     "name":"DET_TEST-2_DO_NOT_DELETE",
    #                     "identifier":"TEST_DET_CI-2",
    #                     "karabo_name":"TEST_DET_CI_-2",
    #                     "karabo_id_control":"TEST_DET_CI-2_CTRL00",
    #                     "flg_available":true,
    #                     "description":"None"
    #                  },
    #                  "detector_type":{
    #                     "id":-1,
    #                     "name":"UNIT_TEST_DETECTOR_TYPE-1_DO_NOT_DELETE",
    #                     "flg_available":true,
    #                     "description":"None"
    #                  }
    #                },
    #                { ... },
    #                { ... } ],
    #      'app_info': {},
    #      'info': 'Got physical_detector_unit successfully'}

    resp['success']
    # >>> True

    resp['data'][0]['karabo_da']
    # >>> 'TEST_DAQ_DA_01'

For additional examples, please take a look in the tests/ folder.


Development & Testing
---------------------

When developing, and before commit changes, please validate that:

1. All tests continue passing successfully (to validate that run *pytest*)::

    # Go to the source code directory
    cd calibration_client

    # Upgrade package and all its required packages
    pip install . -U --upgrade-strategy eager

    # Install test dependencies
    pip install '.[test]' -U --upgrade-strategy eager

    # Run all tests using pytest
    pytest

    # When running all tests against the standard http application
    OAUTHLIB_INSECURE_TRANSPORT=1 pytest

    # Run all tests and get information about coverage for all files inside calibration_client package
    pytest --cov calibration_client --cov-report term-missing

2. Code keeps respecting pycodestyle code conventions (to validate that run **pycodestyle**)::

    pycodestyle .
    pycodestyle . --exclude venv

3. To generate all the wheels files for the dependencies, execute::

    # Generate Wheels to itself and dependencies
    pip wheel --wheel-dir=./external_dependencies .
    pip wheel --wheel-dir=./external_dependencies --find-links=./external_dependencies .

4. Check that you have the desired dependency versions in ``external_dependencies`` folder, since no versions are now set in ``setup.py``.


Registering library on https://pypi.org
---------------------------------------

To register this python library, the following steps are necessary::

    # Install twine
    python -m pip install --upgrade twine

    # Generates source distribution (.tar.gz) and wheel (.whl) files in the dist/ folder
    python setup.py sdist
    python setup.py bdist_wheel

    # Upload new version .egg and .whl files
    twine upload dist/*

    # In case a test is necessary, it is possible to test it against test.pypi.org
    twine upload --repository-url https://test.pypi.org/legacy/ dist/* --verbose

