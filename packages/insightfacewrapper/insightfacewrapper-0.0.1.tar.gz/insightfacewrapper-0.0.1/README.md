# insightfaceWrapper
Wrapper for easier inference for insightface

## Install
```
pip install -U insightfacewrapper 
```

## Models

* `ms1mv3_arcface_r18`
* `ms1mv3_arcface_r34`
* `ms1mv3_arcface_r50`
* `ms1mv3_arcface_r100`
* `glint360k_cosface_r18`
* `glint360k_cosface_r34`
* `glint360k_cosface_r50`
* `glint360k_cosface_r100`


```python
from insightfacewrapper.get_model import get_model
model = get_model(<model_name>)
```