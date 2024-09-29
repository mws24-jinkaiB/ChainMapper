# ChainMapper
```
   ___ _           _                                          
  / __\ |__   __ _(_)_ __   /\/\   __ _ _ __  _ __   ___ _ __ 
 / /  | '_ \ / _` | | '_ \ /    \ / _` | '_ \| '_ \ / _ \ '__|
/ /___| | | | (_| | | | | / /\/\ \ (_| | |_) | |_) |  __/ |   
\____/|_| |_|\__,_|_|_| |_\/    \/\__,_| .__/| .__/ \___|_|   
                                       |_|   |_|    
```

## Overview
**ChainMapper**は、迅速なWindowsフォレンジックのためのツールである[Chainsaw](https://github.com/WithSecureLabs/chainsaw)の強化モジュールです。  
調査対象のイベントログから情報を抽出して、Chainsawでイベントログを分析するために必要なMappingを生成します。

### 背景
近年、セキュリティインシデントは増加傾向にあり、それに伴い分析するデータ量も増加し続けています。  
インシデントの原因調査・対策のためには、早い段階での事実確認や影響範囲特定が必要であり、それにはログの分析が重要になります。  

そうした取り組みとしては、[Sigma](https://github.com/SigmaHQ/sigma) や Detection as Code のような、静的ルールで検知する仕組みがあります。  
Sigmaベースでの検知ツールである[Chainsaw](https://github.com/WithSecureLabs/chainsaw)などが広く使われていますが、Windows標準で実装されている以外のイベント(例として、アンチウイルスソフト関連)などを検知するためには、あらかじめ適切なMappingを定義する必要があります。

### ツールの目的
インシデントの迅速な調査のために、調査対象に記録された未定義のイベントを検知するためのMappingを自動生成します。

## QuickStart
### 実行環境
次の実行環境で動作を確認しています。
```
Python: 3.12
```
その他の依存環境は `pyproject.toml`, `requirements.txt` をご参照ください。


### セットアップ手順
`poetry`, `pip` のいずれかを使ってセットアップしてください。

#### poetryを使ったセットアップ(推奨)
関連パッケージのインストール
```bash
$ poetry install
```

スクリプトの実行
```bash
$ chainmapper {イベントログ.evtx}
```

#### pipを使ったセットアップ
関連パッケージのインストール
```bash
$ pip install -r requirements.txt
```

スクリプトの実行
```bash
$ python src/chainmapper/convert.py {イベントログ.evtx}
```


## Usage
詳細な引数, オプションは以下のコマンドでヘルプを確認してください。

```
$ chainmapper -h
```

### 引数
```
evtx_file:
    input evtx file
```

### オプション
```
-h, --help:
    show this help message and exit
```

## Future Plans
- 他のログ分析製品に対するMappingの自動生成
- Chainsawでの解析時により詳細な情報を表示
    - visibleオプションが無効時、検知ルール一覧で何件ヒットしたかを確認できない点の改善

## License
このプロダクトは、以下のパッケージを使用しています。

|Package|License|
|-|-|
|lxml|BSD 3.0|
|python-evtx|Apache 2.0|
|PyYAML|MIT|

## Author
人海戦術Bチーム / Jinkai-2024-B
