# counta
Counta is a light count-management tool.

WIP...

[Counta - stakiran研究所](https://scrapbox.io/sta/Counta)

## Requirements
- [sta-scb - stakiran研究所](https://scrapbox.io/sta/sta-scb)
    - About VSCode, use [vscode-scb](https://github.com/stakiran/vscode-scb)

## How to use

### 1, Create a workspace
mycounters.scb

```
[洗濯] [掃除] [ご飯] [ネットサーフィン]
@counta workspace
```

### 2, Execute "update"

```
$ python counta.py -d "(your-scb-files-directory)" -i mycounters.scb
```

And the counters will be created. In this case, created `洗濯.scb`, `掃除.scb`, `ご飯.scb` and `ネットサーフィン.scb`.

### 3, Add your count and update
1: Add count. For example, if you done 掃除, enter double space to `[掃除]`.

```
[洗濯] [掃  除] [ご飯] [ネットサーフィン]
@counta workspace
```

2: Execute "update".

Then, the workspace files is changed below:

```
[掃除] [洗濯] [ご飯] [ネットサーフィン]
@counta workspace
```

An order of counters in workspace is "date counted".

### How to count
Double space only. (A position of double space is free in the bracket.)

```
[掃  除]
```

```
[  掃除]
```

```
[掃除  ]
```

With comment. (Use `/`)

```
[掃除]/モップ初めて使ったけど床掃除快適すぎる
```

double space and comment is also possible. (But OK about comment only.)

```
[掃  除]/モップ初めて使ったけど床掃除快適すぎる
```

### How to report
Use `--report`.

```
$ python counta.py -d "(your-scb-files-directory)" -i mycounters.scb --report
```

And the report file will be created. Ex: `mycounter_report.scb`.

### How to update automatically
Cannot only counta.

For example, Use watchmedo and watch the workspace file.

install:

```
$ pip install watchdog
```

use:

```
$ cd (counta-directory)
$ watchmedo shell-command -W --recursive --pattern '(your-scb-directory)/(your-workspace-filename).scb' --command 'python counta.py -d (your-scb-directory) -i (your-workspace-filename).scb' (your-scb-directory)
```
