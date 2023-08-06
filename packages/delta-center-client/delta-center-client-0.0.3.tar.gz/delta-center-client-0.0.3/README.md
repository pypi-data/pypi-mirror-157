# DeltaCenter python client
## pypi package

### build

```python
python3 -m pip install --upgrade build
python3 -m build
```

### install

```shell
pip install ./dist/delta_center_client-0.0.3-py3-none-any.whl --force-reinstall
```

## Use in python
```python
from DeltaCenter import OssClient
# upload
OssClient.upload(base_dir=path)
# download
OssClient.download(oss_path)
```

## Login in the shell
```
python -m DeltaCenter login
```

## Uploading files
```
python -m DeltaCenter upload dirPath
```

## Downloading files
```
python -m DeltaCenter download deltaName
```

