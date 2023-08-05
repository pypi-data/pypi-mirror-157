### Cái méo gì đây ??? ###

Đây là một trading frame work bao gồm các modules:
    - Crawler: -> lấy data tài chính, giá, ... từ nhiều nguồn để thực hiện nghiên cứu
    - Backtest: -> kiểm thử phương pháp giao dịch

### Pytest ###
```
TEST nghiệp vụ vui lòng vào TradingFrameWorkConfig và thêm fiin_cookie
python -m pytest tests/*.py
```

```
TEST selenium & authen
python -m pytest tests/auth/*.py
```

### Publish packages ###
```
    - python3 -m pip install build twine
    - python3 -m build
    - python -m twine upload --verbose dist/*
```