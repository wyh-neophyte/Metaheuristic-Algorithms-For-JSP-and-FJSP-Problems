### 🚀 Get started
#### 1. Installation
#### 2. Data Preparation
Convert your data into Json file, which can be read into {partid:{processid:[[available machine id1, time1], [available machine id2, time2]]}}. Ta01, Ta40, Ta60 and realcase.json have been processed as demos.
#### 3. Run Metaheuristic Algorithms
To run the metaheauristic algorithms, you may simp main.py.
```
python main.py --solver
```



├──System_Dispatch：
    ├── data: 关于数据与数据处理的文件夹；
        ├──{“realcase”, ”ta01”, ”ta40”, ”ta60” + “.txt” ,”.xlsx”, “.json”}用于存储各类数据信息；
        └── read-json.py 读取数据并转换格式的Python代码；
    ├── main:主程序文件夹；
        └── main.py 用于运行PSO算法的代码；
    ├── methods:各类算法实现文件夹；
    ├── output: 关于计算各项变量并输出图片的算法实现文件夹；
    ├── results: 结果存储文件夹；
        ├── PSO: 存储粒子群算法的运行结果；
        ├── SA+PSO: 存储融合算法的运行结果；
        ├── SA: 模拟退火算法的运行结果；
        └── GA: 遗传算法的运行结果；
    └──solutions: 最终输出的符合格式要求的解文件。
