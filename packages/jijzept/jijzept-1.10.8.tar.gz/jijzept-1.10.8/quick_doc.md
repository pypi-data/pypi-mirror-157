# JijZept Quick Start


## How to get started with JijZept

The minimal sample code as follows:

```python
from jijzept import JijSASampler

# define QUBO
qubo = {(0,0): -1, (0, 1): -1, (1, 0): 2}

sampler = JijSASampler(config='config.toml')
result = sampler.sample_qubo(qubo)

print(result)
```

Write a configuration file for connecting to JijZept in `config.toml` and put it in the `config` argument of the Sampler constructor.  
The configuration file should be written in TOML format as follows.

```toml
[default]
url = "***"
token = "****"
```

Copy and paste the assigned API endpoint into the `url` and your token into `token` in the configure file.


またデフォルトでは`同期モード` になっているため、APIに投げて計算が終わるで待ってから解を得ることになります。

`同期モード`をオフにして非同期でJijZeptを使うには以下の手順で答えを得ることができます。



### async mode

非同期モードでAPIを使いたい場合は、`.sample_*` の引数で、`async=False` にして同期モードをオフにする必要があります。

サンプルコード
```python
from jijzept import JijSASampler
from jijzept import api

# define qubo
qubo = {(0, 0): -1, (0, 1): -1, (1, 0): 2}

sampler = JijSASampler(config='config.toml')
# set sync=False
response = sampler.sample_qubo(qubo, sync=False)

# get result
response = response.get_result(config='config.toml')


if response.status == api.SUCESS:
    print(response)
elif response.status == api.PENDING:
    print('Solver status: PENDING')
else:
    print('Error')

```

非同期モードでも `.sample_*` の返り値は `同期モード`と同じく`SampleSet` クラスです。　　
ですが、解が入っていない可能性があります(非同期モードでも一度だけ解を取りに行っているので計算時間が短いと解をもっている可能性もあります)。

解を取りに行くためのコードが
```python
response = response.get_result(config='config.toml')
```
です。`.get_result`の引数`config`に認証情報を記述した設定ファイルを指定するのを忘れないでください。  
また`.get_result`は返り値をもつ非破壊メソッドです。

計算が終了したかどうかは`get_result`の返り値の`.status`変数で確認することができます。
```python
from jijzept import api
if response.status == api.SUCESS:
    print(response)
elif response.status == api.PENDING:
    print('Solver status: PENDING')
else:
    print('Error')
```

## Available solvers

- JijSASampler
    - Hardware: CPU
    - Algorihtm: (Standard) Simulated annealing
    - Problem Type: Binary quadratic model (Ising or QUBO)

- JijSQASampler
    - Hardware: CPU
    - Algorithm: (Standard) Simulated quantum annealing
    - Problem Type: Binary quadratic model (Ising or QUBO)

- JijSBMSampler
    - Hardware: GPU
    - Algorithm: TOSHIBA SBM

- JijDWaveSampler
    - Hardware: D-Wave QPU
    - Algorithm: Quantum annealing