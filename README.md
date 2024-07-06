### 🚀 Get started
#### 1. Installation
You may install the dependencies by the following command.
```
pip install -e .
```
#### 2. Data Preparation
You may use the demo jsonfiles in the data direction. Or you need to convert your custom data into Json file, which can be read into 
```
{partid:
    {processid:
        [[available machine id1, time1],
         [available machine id2, time2],
         ...
        ],
    ...
    },
...
}
```

#### 3. Run Metaheuristic Algorithms
To run the metaheauristic algorithms, you may simp main.py.
```
python main.py --solver select/a/solver/from/GA/SA/PSO --datapath path/to/json/file
```
