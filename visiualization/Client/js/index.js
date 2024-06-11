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

//中间数据

//头部数据
function head(data)
{
  // 更新头部内容
  document.querySelector('.line_cost').innerHTML=data.line_cost;
  document.querySelector('.stable_points').innerHTML=data.stable_points;
}
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

//左侧数据

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

//负载功率
function loads(data) {

  var loads = data.loads;

  var myChart = echarts.init(document.querySelector(".loads .chart"));

  var option = {
    // 修改两条线的颜色
    color: ['#00f2f1', '#ed3f35'],
        textStyle: {
      fontFamily:'STFangsong',
      fontSize:15
    },
    tooltip: {
      trigger: 'axis',
      textStyle: {
        fontFamily:'STFangsong',
        fontSize:15
      }
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
        data: loads[loads_index][0]
      },
      {
        type: 'line',
        smooth: true, // 圆滑的线
        name: '预测功率',
        data: loads[loads_index][1]
      }
    ]
  };

  myChart.setOption(option);

  // 4.让图表随屏幕自适应
  window.addEventListener('resize', function () {
    myChart.resize();
  })

  // 5.点击切换数据
  $(document).on('DOMSubtreeModified', '#mainNumber', function() {
    loads_index= document.getElementById("mainNumber").textContent-1;
    var obj = loads[loads_index];
    option.series[0].data = obj[0];
    option.series[1].data = obj[1];

    // 需要重新渲染
    myChart.setOption(option);
  })
};

//右侧数据
//总稳定节点
function stable_point_sum(data) {

  var stable_point_sum = data.stable_point_sum;

  var myChart = echarts.init(document.querySelector(".stable_point_sum .chart"));

  var option = {
    // 修改两条线的颜色
    color: ['#00f2f1', '#ed3f35'],
    textStyle: {
      fontFamily:'STFangsong',
      fontSize:15
    },
    tooltip: {
      trigger: 'axis',
      textStyle: {
        fontFamily:'STFangsong',
        fontSize:15
      }
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
        name: '实时稳定节点',
        data: stable_point_sum[0]
      },
      {
        type: 'line',
        smooth: true, // 圆滑的线
        name: '优化稳定节点',
        data: stable_point_sum[1]
      }
    ]
  };

  myChart.setOption(option);

  // 4.让图表随屏幕自适应
  window.addEventListener('resize', function () {
    myChart.resize();
  })
};
//总线路耗散
function line_cost_sum(data) {

  var line_cost_sum = data.line_cost_sum;

  var myChart = echarts.init(document.querySelector(".line_cost_sum .chart"));

  var option = {
    // 修改两条线的颜色
    color: ['#00f2f1', '#ed3f35'],
    textStyle: {
      fontFamily:'STFangsong',
      fontSize:15
    },
    tooltip: {
      trigger: 'axis',
      textStyle: {
        fontFamily:'STFangsong',
        fontSize:15
      }
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
        name: '实时耗散',
        data: line_cost_sum[0]
      },
      {
        type: 'line',
        smooth: true, // 圆滑的线
        name: '优化耗散',
        data: line_cost_sum[1]
      }
    ]
  };

  myChart.setOption(option);

  // 4.让图表随屏幕自适应
  window.addEventListener('resize', function () {
    myChart.resize();
  })
};

//下拉栏设计

function showSelect() {
  var selectDiv = document.getElementById("numberSelect");
  if (selectDiv.style.display === "none") {
    selectDiv.style.display = "block";
  } else {
    selectDiv.style.display = "none";
  }
}

function changeNumber(selectedNumber) {
  document.getElementById("mainNumber").innerHTML = selectedNumber;
  document.getElementById("numberSelect").style.display = "none";
}
