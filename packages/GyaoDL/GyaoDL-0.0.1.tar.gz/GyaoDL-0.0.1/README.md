# [gyaodl](https://xpadev.net/gyaodl/)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/xpadev-net/niconicomments/blob/master/LICENSE)  
GYAO!から動画をダウンロードするコマンド兼モジュールです  
This is a script to download videos from GYAO!    
Reference： https://xpadev.net/gyaodl/docs/  
Github： https://github.com/xpadev-net/gyaodl

## ATTENTION
実行にはFFmpegが必要です

## Installation
```
pip install gyaodl
```

## Examples
```python
import GyaoDL from gyaodl
GyaoDL("61dd2b7a-981b-4d40-b972-53fec67debe9", "/path/to/save/mp4")
```
```bash
python -m gyaodl "61dd2b7a-981b-4d40-b972-53fec67debe9" "/path/to/save/mp4"
```
