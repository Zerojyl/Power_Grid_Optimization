# 实时数据可视化展示与轻量化服务器设计

## 1、 背景介绍

最近参加了高校电气电子工程创新大赛，我的主要任务是前端设计。因为我之前基本没有接触过前端的知识，所以也是在查阅了很多资料后，算是基本完成了这个任务。可能在代码上不是很精简高效，但我认为应该是比较通俗易懂的，如果您和我一样在前端刚刚入门的阶段，想要自己设计一个可以实时刷新数据的、具有交互性能的前后端项目，这篇文章可能会有帮助。此外，不成熟的地方，欢迎大家批评指正。

项目地址：[Y-vic/Large-screen-data-visualization (github.com)](https://github.com/Y-vic/Large-screen-data-visualization)

前端界面如下，您可以点击[这里](https://y-vic.github.io/client-demo/)，在浏览器中查看

![image-20240331141805747](https://raw.githubusercontent.com/Y-vic/Images/master/img/image-20240331141805747.png)

实现功能：

- 后台服务器基于SSE（Server Sent Event）实时传输更新前端数据
- 前端可交互性界面

语言：

- 服务器：python
- 前端：HTML、CSS、Less、JavaScript

使用的主体库：

- 服务器：Flask
- 前端：Vis.js 、EChart.js

## 2、服务器设计

### 2.1 Flask

Flask是一个使用 Python 编写的轻量级 Web 应用框架。其 WSGI 工具箱采用 Werkzeug ，模板引擎则使用 Jinja2 。Flask使用 BSD 授权。Flask也被称为 “microframework” ，因为它使用简单的核心，用 extension 增加其他功能。Flask没有默认使用的数据库、窗体验证工具。Flask是一个轻量级的可定制框架，较其他同类型框架更为灵活、轻便、安全且容易上手。它可以很好地结合MVC模式进行开发，开发人员分工合作，小型团队在短时间内就可以完成功能丰富的中小型网站或Web服务的实现。另外，Flask还有很强的定制性，用户可以根据自己的需求来添加相应的功能，在保持核心功能简单的同时实现功能的丰富与扩展，其强大的插件库可以让用户实现个性化的网站定制，开发出功能强大的网站。

总的来说，Flask 是一个简单、灵活且功能丰富的 Python Web 框架，因此我们选用Flask来搭建服务器。

你可以登录[官网](https://flask.github.net.cn/)学习。

### 2.2 SSE

后端运行过程中，电网以及预测数据将实时发生改变，为了保证客户端数据得到实时更新，同时减少客户端软件运行压力从而降低对于客户端硬件限制，我们在服务器侧引入了SSE机制。

SSE 是一种在基于浏览器的 Web 应用程序中仅从服务器向客户端发送文本消息的技术。SSE基于 HTTP 协议中的持久连接， 具有由 W3C 标准化的网络协议和 EventSource 客户端接口，并作为 HTML5 标准套件的一部分。

客户端在开启时会访问服务器的"/data"路径，得到初始数据，并建立SSE链接。此后，服务器将实时判断用于存储数据的data.json文件是否发生更新，并在每次更新后，向客户端发送SSE数据流实现客户端数据同步。

### 2.3 跨域问题（重点）

**为什么会出现跨域问题**
出于浏览器的同源策略限制。同源策略（Sameoriginpolicy）是一种约定，它是浏览器最核心也最基本的安全功能，如果缺少了同源策略，则浏览器的正常功能可能都会受到影响。可以说Web是构建在同源策略基础之上的，浏览器只是针对同源策略的一种实现。同源策略会阻止一个域的javascript脚本和另外一个域的内容进行交互。所谓同源（即指在同一个域）就是两个页面具有相同的协议（protocol），主机（host）和端口号（port）

**什么是跨域**
当一个请求url的协议、域名、端口三者之间任意一个与当前页面url不同即为跨域

您可以参考这两篇博客：

- [什么是跨域？跨域解决方法-CSDN博客](https://blog.csdn.net/qq_38128179/article/details/84956552)
- [前端手把手配置跨域，CORS，一文解决所有坑(vue) - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/628263030)

**解决跨域的方法**

其实也很简单，就是执行以下代码即可：

```python
app = Flask(__name__)
CORS(app)  # 添加这一行来启用 CORS
```

### 2.4 代码设计与主要逻辑的注释：

```python
//导入相关库，主要是Flask
from flask import Flask, Response
from flask_cors import CORS
import json
import time, os

//开启一个应用，并允许资源跨域
app = Flask(__name__)
CORS(app)  # 添加这一行来启用 CORS
//服务器传输的数据都存储在当前路径下的data.json文件中
data_source = "data.json"

//路由函数，当在浏览器访问‘/’路径时，会看到Server is running提示
@app.route('/')
def index():
    return "Server is running"

/*路由函数，当在浏览器访问‘/data’路径时，会与服务器建立SSE连接，并在后台数据发生改变时接收服务器传来的数据并更新*/
@app.route('/data')
def events():
    return Response(stream_data(), content_type='text/event-stream')

//实现SSE机制的函数，原理是每隔1s，查看data.json的时间戳，如果改变说明发生了更新，就向前端传输数据
def stream_data():
    with open(data_source, "r") as file:
        data = json.load(file)
        yield "data: {}\n\n".format(json.dumps(data))
    last_modified = os.path.getmtime(data_source)
    while True:
        current_modified = os.path.getmtime(data_source)
        if current_modified > last_modified:
            with open(data_source, "r") as file:
                data = json.load(file)
                yield "data: {}\n\n".format(json.dumps(data))
            last_modified = current_modified
        time.sleep(1)


if __name__ == '__main__':
    app.run(debug=True)
```

运行这段代码，就会生成一个本地服务器，网址为：http://127.0.0.1:5000，您可以在浏览器访问

**运行结果如下：**

![image-20240331144545444](https://raw.githubusercontent.com/Y-vic/Images/master/img/image-20240331144545444.png)

当您访问这个网址后：

![image-20240331144651041](https://raw.githubusercontent.com/Y-vic/Images/master/img/image-20240331144651041.png)

## 3、前端设计

## 3.1 主要思路

主体框架我借鉴了B站上的pink老师的思路：[ECharts数据可视化项目-大屏数据可视化展示-bilibili](https://www.bilibili.com/video/BV1v7411R7mp/?spm_id_from=333.337.search-card.all.click&vd_source=5b0abc211b780f80a6bdcbea7764a0c5)

内容上做出了适应性修改，考虑到本项目“区域电网中清洁能源消纳”：

对象电网主体部分由32个负载，4个风力发电机组成。因此在客户端实现数据可视化时，我们分别设计了针对所有负载以及风机的实时功率和预测功率对比（左一、左二）。同时为了更好的展示智能体优化效果，我们引入总线路耗散和总稳定节点数两个指标，展示其在优化前后的数据变化（右一、右二）。此外，为了实时分析当前电网连接，我们对区域电网进行抽象，并将得到的拓扑结构予以展示（中间的拓扑）。

在绘制图表的技术实现上，出于交互性与平台兼容性的考虑，我们主要采用了基于 JavaScript 的开源可视化图表库：Echarts和Vis.js。

Echarts主要用来绘制左一、左二、右一、右二的四张图表，但是因为我在Echarts的社区里没有找到合适的能用于展示拓扑结构的图表，所以我又引入了Vis.js来绘制这一部分。

![image-20240331141805747](https://raw.githubusercontent.com/Y-vic/Images/master/img/image-20240331141805747.png)

细节上：

点击左一位置，“负载功率” 表中的数字 “1”，会出现下拉框，您可以在这里选择展示1-32个负载里的任何一个：

<img src="https://raw.githubusercontent.com/Y-vic/Images/master/img/image-20240331152846434.png" alt="image-20240331152846434" style="zoom:65%;" />



点击左二位置，“风机功率” 表右侧的$W_1,W_2,W_3,W_4$，即可显示对应的风机数据，以$W_3$为例：

<img src="https://raw.githubusercontent.com/Y-vic/Images/master/img/image-20240331153129743.png" alt="image-20240331153129743" style="zoom:67%;" />

## 3.2 代码设计

index.html文件主要用于设计主体的框架，所有的数据的导入与更新都放在了index.js文件中。

### 3.2.1 index.html

index.html文件比较简单，只需要掌握基本的HTML语法即可：

```
<!DOCTYPE html>
<html lang="cmn-Hans">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>区域电网自治运行导航</title>
    <link rel="stylesheet" href="css/index.css" />
  </head>
  <body>
    <!-- 头部 -->
    <header>
      <h1>区域电网自治运行导航</h1>
      <div class="show-time"></div>
      <script>
        var t = null;
        t = setTimeout(time, 1000); //开始运行
        function time() {
          clearTimeout(t); //清除定时器
          dt = new Date();
          var y = dt.getFullYear();
          var mt = dt.getMonth() + 1;
          var day = dt.getDate();
          var h = dt.getHours(); //获取时
          var m = dt.getMinutes(); //获取分
          var s = dt.getSeconds(); //获取秒
          document.querySelector(".show-time").innerHTML =
            "当前时间：" +
            y +
            "年" +
            mt +
            "月" +
            day +
            "日-" +
            h +
            "时" +
            m +
            "分" +
            s +
            "秒";
          t = setTimeout(time, 1000); //设定定时器，循环运行
        }
      </script>
    </header>

    <!-- 页面主体 -->
    <section class="mainbox">
      <!-- 左侧盒子 -->
      <div class="column">
        <div class="panel loads">
          <h2>负载功率(MkW·h)： <button onclick="showSelect()" id="mainNumber" >1</button>
            <a></a>
          </h2>
          <div id="numberSelect">
            <select size="7" onchange="changeNumber(this.value)">
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
              <option value="5">5</option>
              <option value="6">6</option>
              <option value="7">7</option>
              <option value="8">8</option>
              <option value="9">9</option>
              <option value="10">10</option>
              <option value="11">11</option>
              <option value="12">12</option>
              <option value="13">13</option>
              <option value="14">14</option>
              <option value="15">15</option>
              <option value="16">16</option>
              <option value="17">17</option>
              <option value="18">18</option>
              <option value="19">19</option>
              <option value="20">20</option>
              <option value="21">21</option>
              <option value="22">22</option>
              <option value="23">23</option>
              <option value="24">24</option>
              <option value="25">25</option>
              <option value="26">26</option>
              <option value="27">27</option>
              <option value="28">28</option>
              <option value="29">29</option>
              <option value="30">30</option>
              <option value="31">31</option>
              <option value="32">32</option>
            </select>
          </div>
          <!-- 图表放置盒子 -->
          <div class="chart"></div>
          <!-- 伪元素绘制盒子下边角 -->
          <div class="panel-footer"></div>
        </div>
        <div class="panel wind_power">
          <h2>风机功率(MkW·h)
            <a class="a-active" href="javascript:;"><span>W<sub>1</sub></span></a>
            <a href="javascript:;"><span>W<sub>2</sub></span></a>
            <a href="javascript:;"><span>W<sub>3</sub></span></a>
            <a href="javascript:;"><span>W<sub>4</sub></span></a>
          </h2>
          <div class="chart"></div>
          <div class="panel-footer"></div>
        </div>
        <div class="panel pie">
          <h2>unknown</h2>
          <div class="chart"></div>
          <div class="panel-footer"></div>
        </div>
      </div>
      <!-- 中间盒子 -->
      <div class="column">
        <!-- 头部 no模块 -->
        <div class="no">
          <div class="no-hd">
            <ul>
              <li class="line_cost">438</li>
              <li class="stable_points">438</li>
            </ul>
          </div>
          <div class="no-bd">
            <ul>
              <li>当前总线路耗散(MkW·h)</li>
              <li>当前总稳定节点数</li>
            </ul>
          </div>
        </div>
        <!-- map模块 -->
        <div class="topology">
          <div class="chart"></div>
        </div>
      </div>
      <!-- 右侧盒子 -->
      <div class="column">
        <div class="panel stable_point_sum">
          <h2>总稳定节点数</h2>
          <div class="chart"></div>
          <div class="panel-footer"></div>
        </div>
        <div class="panel line_cost_sum">
          <h2>总线路耗散(MkW·h)</h2>
          <div class="chart"></div>
          <div class="panel-footer"></div>
        </div>
        <div class="panel pie2">
          <h2>unknown</h2>
          <div class="chart"></div>
          <div class="panel-footer"></div>
        </div>
      </div>
    </section>
    <script src="js/flexible.js"></script>
    <script src="js/echarts.min.js"></script>
    <script src="js/jquery.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.18.1/vis.min.js"></script>
    <script src="js/index.js"></script>
  </body>
</html>

```

### 3.2.2 index.js

首先建立与服务器的连接，并在服务器每次传输更新后的data.json文件后调用函数更新数据：

```javascript
// 创建 EventSource 对象，指定服务器路径
const eventSource = new EventSource('http://127.0.0.1:5000/data');
wind_power_index=0;
loads_index=0;
change=0;
// 监听服务器发送的消息
eventSource.onmessage = function(event) {
    // 解析 JSON 数据
    const data = JSON.parse(event.data);
    head(data);
    if(change!=data.topology.change)
    {
      change=data.topology.change;
      topology(data);
    };
    wind_power(data);
    loads(data);

    stable_point_sum(data);
    line_cost_sum(data);
};

// 处理连接关闭事件
eventSource.onerror = function(err) {
    alert("cannot connect to the server!")
    console.error('EventSource failed:', err);
    eventSource.close();
};
```

这里的**head(data)、wind_power(data)、loads(data)、stable_point_sum(data)、line_cost_sum(data)**分别为更新头部数据、风机功率、负载功率、总稳定节点数、总线路耗散的函数，它们都是基于ECharts.js可视化库。

您可以在ECharts社区中快速学会如何使用Echarts来绘制图表,点击这里：[快速上手 - 使用手册 - Apache ECharts](https://echarts.apache.org/handbook/zh/get-started/)

以风机功率为例，下面是我的实现：

```javascript
//风机功率
function wind_power(data) {

  var wind_power = data.wind_power;

  var myChart = echarts.init(document.querySelector(".wind_power .chart"));

  var option = {
    // 修改两条线的颜色
    color: ['#00f2f1', '#ed3f35'],
    tooltip: {
      trigger: 'axis',
      textStyle: {
        fontFamily:'STFangsong',
        fontSize:15
      }
    },
    textStyle: {
      fontFamily:'STFangsong',
      fontSize:15
    },
    // 图例组件
    legend: {
      // 当serise 有name值时， legend 不需要写data
      // 修改图例组件文字颜色
      textStyle: {
        color: '#4c9bfd',
        fontFamily:'STFangsong',
        fontSize:15
      },
      right: '10%',
    },
    grid: {
      top: "20%",
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
      show: true, // 显示边框
      borderColor: '#012f4a' // 边框颜色
    },
    xAxis: {
      type: 'category',
      boundaryGap: false, // 去除轴间距
      data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
      // 去除刻度线
      axisTick: {
        show: false
      },
      axisLabel: {
        color: "#4c9bfb" // x轴文本颜色
      },
      axisLine: {
        show: false // 去除轴线
      }
    },
    yAxis: {
      type: 'value',
      // 去除刻度线
      axisTick: {
        show: false
      },
      axisLabel: {
        color: "#4c9bfb" // x轴文本颜色
      },
      axisLine: {
        show: false // 去除轴线
      },
      splitLine: {
        lineStyle: {
          color: "#012f4a"
        }
      }
    },
    series: [{
        type: 'line',
        smooth: true, // 圆滑的线
        name: '实时功率',
        data: wind_power[wind_power_index][0]
      },
      {
        type: 'line',
        smooth: true, // 圆滑的线
        name: '预测功率',
        data: wind_power[wind_power_index][1]
      }
    ]
  };

  myChart.setOption(option);

  // 4.让图表随屏幕自适应
  window.addEventListener('resize', function () {
    myChart.resize();
  })

  // 5.点击切换数据
  $('.wind_power h2 a').on('click', function () {
    wind_power_index=$(this).index();
    var obj = wind_power[wind_power_index];
    option.series[0].data = obj[0];
    option.series[1].data = obj[1];
    // 选中高亮
    $('.wind_power h2 a').removeClass('a-active');
    $(this).addClass('a-active');

    // 需要重新渲染
    myChart.setOption(option);
  })
};
```

除了上面的五个函数之外，还有用于绘制网络拓扑的**topology(data)**函数，这个函数是基于Vis.js可视化库实现的

它的实现与ECharts类似，您也可以在官网上快速了解它的使用：[vis.js (visjs.org)](https://visjs.org/)

下面给出我的实现：

```javascript
//网络拓扑
function topology(data) {
  var data = {nodes: new vis.DataSet(data.topology.nodes), edges: new vis.DataSet(data.topology.edges)};
  var container = document.querySelector(".topology .chart");
  var network = new vis.Network(container, data);
  options={
    nodes: {
      size:20,
      font:{
        size:23,
        color:'#FF6347',
        face:'STFangsong'
      },
      color: {
        border: '		#20B2AA',
        background: '	#D4F2E7',
        highlight: {
          border: '		#20B2AA',
          background: '#D2E5FF'
        },
        hover: {
          border: '		#20B2AA',
          background: '#D2E5FF'
        }
      },
      fixed: {
        x:false,
        y:false
      }
    },
    interaction: {zoomView: true},
    edges: {
      width: 4,
      smooth: {
          type: "continuous"
      }
    },
  };
  network.setOptions(options);
};
```
