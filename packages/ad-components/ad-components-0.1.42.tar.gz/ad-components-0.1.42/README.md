# Accelerated Discovery Reusable Components

The central implementation of Accelerated Discover Reusable Components. It serves as a wrapper around client libraries we use locally like Dapr and MLflow.

## 1.Installation
All components will be availble using

```shell
pip install ad-components
```

### CLI
Here's an example usage of the CLI

```
usage: adc [-h] [--verbose] [--version] {<component>} ...

Accelerated Discovery reusable components.

positional arguments:
  <component>    the component that you want to trigger.

optional arguments:
  -h, --help     show this help message and exit.
  --version      show program's version number and exit.
```

## 2. Usage
### 2.0. In your pipeline
To use a component in your pipeline, you need to run it in a Step context

```python
from ad.step import DaprStep
from ad.storage import download, upload

with DaprStep():
    resp = download(download_src, download_dest, binding_name=binding)
    print(f"download resp: {resp}")

    resp = upload(upload_src, upload_dest, binding_name=binding)
    print(f"upload resp: {resp}")
```

Running the components inside a step will make sure the client dependencies are handled correctly.


### 2.1. Storage

#### 2.1.2. Python module
You can invoke the manager using native python. Please note that the package must be present in you python environment.

```python
from ad.storage import download, upload

download_resp = download(
    src, dest,
    # binding_name="s3-state",  # Or any other binding
)

upload_resp = upload(
    src, dest,
    # binding_name="s3-state",  # Or any other binding
)
```

#### 2.1.3. CLI

```shell
usage: adc storage [-h] --src PATH --dest PATH [--binding NAME] [--timeout SEC] {download,upload}

positional arguments:
  {download,upload}     action to be performed on data.

optional arguments:
  -h, --help            show this help message and exit

action arguments:
  --src PATH, -r PATH   path of file to perform action on.
  --dest PATH, -d PATH  object's desired full path in the destination.
  --binding NAME, -b NAME
                        the name of the binding as defined in the components.

dapr arguments:
  --timeout SEC, -t SEC
                        value in seconds we should wait for sidecar to come up.
```

> **Note:** You can replace `adc` with `python ad/main.py ...` if you don't have the package installed in your python environment.

##### Examples
1. To download an object from S3 run
```bash
adc storage download \
    --src test.txt \
    --dest tmp/downloaded.txt
```

2. To upload an object to S3 run
```bash
adc storage upload \
    --src tmp/downloaded.txt \
    --dest local/uploaded.txt
```


## 3. Supported components
### 3.1. Storage
#### 3.1.1. Supported operations
Below is a list of the operations you might intend to perform in your component.

##### Upload
Uploads data from a file to an object in a bucket.

###### Arguments
* `src`: Name of file to download.
* `dest`: Object name in the bucket.
* `binding`: The name of the binding to perform the operation.

##### Download
Downloads data of an object to file.

###### Arguments
* `src`: Object name in the bucket.
* `dest`: Name of file to download.
* `binding`: The name of the binding to perform the operation.


##### Dapr configurations
* `address`: Dapr Runtime gRPC endpoint address.
* `timeout`: Value in seconds we should wait for sidecar to come up


## 4. Publishing
Every change to the python script requires a new version to be pushed PyPi registry.


If you have the right (write) permissions, and a correctly-configured `$HOME/.pypirc` file, run the following command to publish the package

```shell
make
```

### 4.1. Increment the version
To increment the version, go to [adstorage/version.py](adstorage/version.py) and increment the version there. Both the [setup.py](setup.py) and the `CLI` will read the new version correctly.

### 4.2 Configure PyPi registry
To be able to push to the package to our private registry, you need to tell PyPi about it. This one-liner command will take care of it for you

```shell
cat << EOF > $HOME/.pypirc
[distutils]
index-servers =
    pypi

[pypi]
repository: https://upload.pypi.org/legacy/
username: __token__
password: $PYPI_TOKEN
EOF
```

> **Note:** The pip package will fetch the version from `ad/version.py` file, so make sure to increment before pushing.
