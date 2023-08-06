Anaml Python SDK
================

The Anaml Python SDK makes it easy to interact with the [Anaml][1] feature
engineering platform from Python. The SDK provides several sets of features:

1. Methods and data types to interact with the Anaml server REST API.

2. Methods to load Anaml feature data in Spark and/or Pandas.

3. Methods to graph Anaml features in an interactive notebook.

Dependencies
------------

If you plan to use (2) or (3) you will need to install the optional dependencies
used to implement the additional functionality. The available "extras" are:

- `plotting` includes graphing libraries to support the `preview_feature()`
  method.

- `pandas` includes libraries to support loading feature data with Pandas.

- `spark` includes libraries to support loading feature data with Spark.

- `aws` includes additional libraries to support loading data from AWS data
  storage platforms like S3.

- `google` includes additional libraries to support loading data from Google
  Cloud data storage platforms like BigQuery and Google Cloud Storage.

You can install these extra dependencies when you install the Python SDK with
PIP. Just include one or more of the extras described above when you run
`pip install`:

```shell
$ pip install "anaml-python-sdk[data,google]"
```

Do note, however, that you should almost install a full Spark distribution with
the additional libraries and configuration required in your environment. In that
case you should not use the `[spark]` extra.

Developing
----------

If you are working on recent versions of macOS, you will need to install Python
3.7 using Homebrew or some other tool.

Make sure you upgrade `pip` when warned. Newer versions of `pip` know about
binary compatibility between macOS versions. This allows it to download binary
wheel packages for large libraries (like scipy, numpy, and pandas) that would
otherwise require you to install FORTRAN and C++ compilers and libraries.

Docker Containers
-----------------

The Dockerfile allows you to build an image containing the Anaml Python SDK

```bash
$ docker build --target sdk --tag anaml-sdk .
```

### Python SDK Image

The Anaml Python SDK image can be used as base image or as a way to access a
Python interpreter with the SDK and all the libraries pre-installed.

```bash
$ docker run --rm -ti anaml-sdk
Python 3.9.6 (default, Jul 22 2021, 15:24:21)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import anaml_client
>>> client = anaml_client.Anaml(url="...", apikey="...", secret="...")
>>>
```

## Webhook Server

See `examples/webhook-server/README.md` for more details.

## Integration tests:

To run integration tests locally, you must ensure there is a running instance of anaml-server running on port 8080, and
with a full (Enterprise) license. For this, you can check out the [anaml][2] project, then issue the following commands
from the project directory:
```bash
export ANAML_LICENSE_KEY=<insert your license key here>
source .envrc
docker-compose pull
docker-compose up -d anaml-server anaml-spark-server anaml-demo-setup
```

You then need to copy the test data across into the services you just started.
From the anaml-python-sdk project directory:
```bash
docker cp tests/data anaml-server:/data/tests
docker cp tests/data anaml_spark-worker_1:/data/tests
```

After that, you need the jar to support bigquery with spark:
```bash
export jars="$(pip show pyspark | awk '/Location:/{print $2}')/pyspark/jars"
curl -o "${jars}/spark-bigquery-with-dependencies_2.12-0.22.0.jar" \
  https://storage.googleapis.com/spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.22.0.jar
```

Finally, you can perform the following:
1. Install dependencies
   1. `pip install pyarrow`
   2. `pip install -r requirements.txt -e ".[testing,google,data]"`
2. Install google cloud sdk `pip install google-cloud`
3. Authenticate using `gcloud auth application-default login`
4. `export GCLOUD_PROJECT="anaml-dev-nonprod"`
5. Run all integration tests `python -m pytest -S integration tests/`

[1]: https://www.anaml.com/
[2]: https://github.com/simple-machines/anaml
