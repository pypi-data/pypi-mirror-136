# bag

```bash
# install
pip install robobag

# install protobuf
brew install protobuf

# generate profile_pb2.py
cd robobag
protoc -I=./ --python_out=./ ./profile.proto

# build package
python3 setup.py sdist

# publish to pypi
pip install twine
twine upload dist/*
```
