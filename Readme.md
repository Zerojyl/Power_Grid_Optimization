# Power_Grid_Optimization
power grid optimization by reinforcement and deep learning

程序树状图：
```bash
.
├── Agent
│   ├── agent_test.py
│   ├── agent_train.py
│   ├── EEEIC_agent.zip
│   └── PPOAgent.py
├── Contrast
│   ├── modified_IEEE33bus_powersystem.py
│   ├── PSO_cycle.py
│   ├── PSO_main.py
│   ├── PSO_net.py
│   ├── PSO_Switch.py
│   ├── PSO_test.py
│   ├── st_test.py
│   └── violence_test.py
├── Data
│   ├── load_data
│   │   ├── load_data.csv
│   │   └── scale1.pkl
│   └── power_data
│       ├── merged_power_data1.csv
│       ├── merged_power_data2.csv
│       ├── merged_power_data3.csv
│       ├── merged_power_data4.csv
│       ├── pre_process.ipynb
│       ├── scale1.pkl
│       ├── scale2.pkl
│       ├── scale3.pkl
│       └── scale4.pkl
├── Forecasting
│   ├── load_forecast
│   │   ├── load_forecasting_evaluating.py
│   │   └── load_forecast_training.py
│   ├── power_forecast
│   │   ├── power_forecasting_evaluating.py
│   │   ├── power_forecasting.ipynb
│   │   └── power_forecast_training.py
│   ├── debug.ipynb
│   └── debug.py
├── Models
│   ├── __init__.py
│   └── lstm_net.py
├── Power_Grid_Virtual_Environment
│   ├── action_space.py
│   ├── PowerSystem.py
│   └── TrainEnv.py
├── results
│   ├── compute.py
│   └── test_data.md
├── tensorboard_log
│   ├── load_forecasting_eval
│   │   └── 20240610-124418
│   │       └── events.out.tfevents.1717994658.Inspiration.30808.0
│   ├── load_forecasting_training
│   │   ├── 20240610-123347
│   │   │   └── events.out.tfevents.1717994027.Inspiration.25344.0
│   │   ├── 20240610-123640
│   │   │   └── events.out.tfevents.1717994200.Inspiration.16756.0
│   │   └── 20240610-123759
│   │       └── events.out.tfevents.1717994279.Inspiration.12248.0
│   ├── power_forecasting_training
│   │   └── 20240610-124456
│   │       └── events.out.tfevents.1717994696.Inspiration.3128.0
│   └── PPO_training
│       ├── PPO_1
│       │   └── events.out.tfevents.1718072426.Inspiration.8656.0
│       ├── PPO_2
│       │   └── events.out.tfevents.1718072718.Inspiration.5368.0
│       └── PPO_3
│           └── events.out.tfevents.1718072800.Inspiration.5480.0
├── utils
│   ├── configs
│   │   ├── agent
│   │   │   └── ppo_agent.yaml
│   │   ├── environment
│   │   │   └── env.yaml
│   │   ├── load_forecasting
│   │   │   └── lstm_load_forecasting.yaml
│   │   └── power_forecasting
│   │       ├── debug.ipynb
│   │       └── lstm_power_forecasting.yaml
│   ├── data_process
│   │   ├── data_read.py
│   │   ├── load_data_process.py
│   │   ├── make_dataset.py
│   │   ├── power_data_process.py
│   │   └── test.ipynb
│   └── __init__.py
├── visiualization
│   ├── Client
│   │   ├── css
│   │   │   ├── index.css
│   │   │   └── index.less
│   │   ├── font
│   │   │   └── DS-DIGIT.TTF
│   │   ├── images
│   │   │   ├── bg.jpg
│   │   │   ├── head_bg.png
│   │   │   ├── line.png
│   │   │   └── weather.png
│   │   ├── js
│   │   │   ├── echarts.min.js
│   │   │   ├── flexible.js
│   │   │   ├── index.js
│   │   │   └── jquery.js
│   │   ├── _config.yml
│   │   └── index.html
│   ├── Server
│   │   ├── data.json
│   │   └── main.py
│   └── README.md
├── debug.py
└── Readme.md
```
