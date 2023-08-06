# Q-snippets
https://pypi.org/project/Q-snippets-Qing25/0.0.7/


My working code snippets

```python
.
├── q_snippets
│   ├── adversarial.py
│   ├── data.py
│   ├── __init__.py
│   ├── metrics.py
│   ├── object.py
│   ├── optim.py
│   ├── pretrains.py
│   └── tensor_ops.py
```

### adversarial

- FGM
- PGD

### objects

- RoPE
- CircleLoss
- FocalLoss
- TrainerProcess
- Config
- RNNWrapper
- MultiHeadAttnWrapper

### data

- timeit
- save_json
- load_json
- load_yaml
- BaseData
- MRCSample
- MRCBatch
- load_data
- MRCDataset
- span_decode
- DataProcessor
- gen_uid
- `sequence_padding`
- `dict2list`
- `SegmentUtility`
- `prepare_inputs`
- `prepare_batch_inputs`

### optim

pass

### metrics

pass

### tensor_ops

- safesoftmax
- feature_transform
- select_span_rep
- select_func
- get_max_startend
- label_smoothing
- mean_pooling( seq_vecs, attention_mask)

### Pretrains

- get_model_url     获得本地路径，本地没有则保存到本地后返回
- save_pretrains    查看模型列表中保存到本地的情况
