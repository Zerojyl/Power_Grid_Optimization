// 创建 EventSource 对象，指定服务器路径
const eventSource = new EventSource('http://127.0.0.1:5000/data');
// wind_power_index=1;
// loads_index=1;
change=-1;
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
    score(data);
    inverse_power(data);
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
  document.querySelector('.line_cost').innerHTML=data.line_cost.toFixed(2);
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
    fontFamily:'STFangsong',  
    toolbox: {
      right: 'right',
      top: 'top',
      show: true,
      feature: {
        saveAsImage: {
          title: '保存',
          name: 'wind_power',
        },        
      }
    },
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
    grid: {
      top: "15%",
      left: '0%',
      right: '4%',
      bottom: '1%',
      containLabel: true,
      show: true, // 显示边框
      borderColor: '#012f4a' // 边框颜色
    },
    xAxis: {
      type: 'category',
      boundaryGap: false, // 去除轴间距
      data: ['-7', '-6', '-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4'],
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
    //'#00f2f1', '#ed3f35'
    visualMap: {
      show: false,
      dimension: 0,
      pieces: [
        {
          lt: 8,
          color: 'green'
        },
        {
          gte: 8,
          lte: 12,
          color: '#ed3f35'
        },
      ]
    },
    series: [
      {
        name: 'wind_power',
        type: 'line',
        smooth: true,
        // prettier-ignore
        // data: wind_power['wind_power'+toString(wind_power_index)],
        data: wind_power['wind_power1'],
        markArea: {
          itemStyle: {
            color: 'rgba(255, 173, 177, 0.4)'
          },
          data: [
            [
              {
                name: 'PREDICT',
                xAxis: '1'
              },
              {
                xAxis: '4'
              }
            ]
          ]
        }
      }
    ]
  };

  myChart.setOption(option);

  // 4.让图表随屏幕自适应
  window.addEventListener('resize', function () {
    myChart.resize();
  })

  // // 5.点击切换数据
  // $('.wind_power h2 a').on('click', function () {
  //   wind_power_index=$(this).index();
  //   wind_power_index+=1;
  //   var obj = wind_power['wind_power' + wind_power_index.toString()];
  //   option.series.data = obj;
  //   // 选中高亮
  //   $('.wind_power h2 a').removeClass('a-active');
  //   $(this).addClass('a-active');

  //   // 需要重新渲染
  //   myChart.setOption(option);
  // })
  $('.wind_power h2 a').on('click', function () {
    var wind_power_index=$(this).index();
    wind_power_index+=1;
    // console.log('wind_power_index:', wind_power_index);  // 输出 wind_power_index 的值
    var obj = wind_power['wind_power' + wind_power_index.toString()];
    // console.log('obj:', obj);  // 输出 obj 的值
    option.series[0].data = obj;
    // 选中高亮
    $('.wind_power h2 a').removeClass('a-active');
    $(this).addClass('a-active');

    // 需要重新渲染
    myChart.setOption(option);
   // console.log('option:', option);  // 输出 option 的值
})
};

//负载功率
function loads(data) {

  var loads = data.loads;

  var myChart = echarts.init(document.querySelector(".loads .chart"));

  var option = {
    fontFamily:'STFangsong',  
    toolbox: {
      right: 'right',
      top: 'top',
      show: true,
      feature: {
        saveAsImage: {
          title: '保存',
          name: 'loads',
        },        
      }
    },
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
    grid: {
      top: "15%",
      left: '0%',
      right: '4%',
      bottom: '1%',
      containLabel: true,
      show: true, // 显示边框
      borderColor: '#012f4a' // 边框颜色
    },
    xAxis: {
      type: 'category',
      boundaryGap: false, // 去除轴间距
      data: ['-7', '-6', '-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4'],
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
    //'#00f2f1', '#ed3f35'
    visualMap: {
      show: false,
      dimension: 0,
      pieces: [
        {
          lt: 8,
          color: 'green'
        },
        {
          gte: 8,
          lte: 12,
          color: '#ed3f35'
        },
      ]
    },
    series: [
      {
        name: 'loads',
        type: 'line',
        smooth: true,
        // prettier-ignore
        data: loads['load_1'],
        markArea: {
          itemStyle: {
            color: 'rgba(255, 173, 177, 0.4)'
          },
          data: [
            [
              {
                name: 'PREDICT',
                xAxis: '1'
              },
              {
                xAxis: '4'
              }
            ]
          ]
        }
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
    loads_index= document.getElementById("mainNumber").textContent;
    option.series[0].data = loads['load_'+loads_index.toString()];

    // 需要重新渲染
    myChart.setOption(option);
  })
};

//倒送功率
function inverse_power(data) {

  var inverse_power = data.inverse_power;

  var myChart = echarts.init(document.querySelector(".inverse_power .chart"));

  var option = {
    fontFamily:'STFangsong',  
    toolbox: {
      right: 'right',
      top: 'top',
      show: true,
      feature: {
        saveAsImage: {
          title: '保存',
          name: 'inverse_power',
        },        
      }
    },
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
    grid: {
      top: "15%",
      left: '0%',
      right: '4%',
      bottom: '1%',
      containLabel: true,
      show: true, // 显示边框
      borderColor: '#012f4a' // 边框颜色
    },
    xAxis: {
      type: 'category',
      boundaryGap: false, // 去除轴间距
      data: ['-11','-10','-9','-8','-7', '-6', '-5', '-4', '-3', '-2', '-1', '0'],
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
    //'#00f2f1', '#ed3f35'
    visualMap: {
      show: false,
      dimension: 0,
      color:['green']
      // pieces: [
      //   {
      //     lt: 8,
      //     color: 'green'
      //   },
      //   {
      //     gte: 8,
      //     lte: 12,
      //     color: '#ed3f35'
      //   },
      // ]
    },
    series: [
      {
        name: 'inverse_power',
        type: 'line',
        smooth: true,
        // prettier-ignore
        data: inverse_power,
        // markArea: {
        //   itemStyle: {
        //     color: 'rgba(255, 173, 177, 0.4)'
        //   },
        //   data: [
        //     [
        //       {
        //         name: 'PREDICT',
        //         xAxis: '1'
        //       },
        //       {
        //         xAxis: '4'
        //       }
        //     ]
        //   ]
        // }
      }
    ]
  };

  myChart.setOption(option);

  // 4.让图表随屏幕自适应
  window.addEventListener('resize', function () {
    myChart.resize();
  })
};

//右侧数据
//总稳定节点
function stable_point_sum(data) {

  var stable_point_sum = data.stable_point_sum;

  var myChart = echarts.init(document.querySelector(".stable_point_sum .chart"));

  var option = {
    fontFamily:'STFangsong',  
    toolbox: {
      right: 'right',
      top: 'top',
      show: true,
      feature: {
        saveAsImage: {
          title: '保存',
          name: 'stable_point_sum',
        },        
      }
    },
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
    grid: {
      top: "15%",
      left: '0%',
      right: '4%',
      bottom: '1%',
      containLabel: true,
      show: true, // 显示边框
      borderColor: '#012f4a' // 边框颜色
    },
    xAxis: {
      type: 'category',
      boundaryGap: false, // 去除轴间距
      data: [ '-11', '-10', '-9', '-8','-7', '-6', '-5', '-4', '-3', '-2', '-1', '0'],
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
    //'#00f2f1', '#ed3f35'
    visualMap: {
      show: false,
      dimension: 0,
      color:['green']
      // pieces: [
      //   {
      //     lt: 8,
      //     color: 'green'
      //   },
      //   {
      //     gte: 8,
      //     lte: 12,
      //     color: '#ed3f35'
      //   },
      // ]
    },
    series: [
      {
        name: 'stable_point_sum',
        type: 'line',
        smooth: true,
        // prettier-ignore
        data: stable_point_sum,
        markArea: {
          itemStyle: {
            color: 'rgba(255, 173, 177, 0.4)'
          },
          // data: [
          //   [
          //     {
          //       name: 'PREDICT',
          //       xAxis: '1'
          //     },
          //     {
          //       xAxis: '4'
          //     }
          //   ]
          // ]
        }
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
    fontFamily:'STFangsong',  
    fontFamily:'STFangsong',  
    toolbox: {
      right: 'right',
      top: 'top',
      show: true,
      feature: {
        saveAsImage: {
          title: '保存',
          name: 'line_cost_sum',
        },        
      }
    },
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
    grid: {
      top: "15%",
      left: '0%',
      right: '4%',
      bottom: '1%',
      containLabel: true,
      show: true, // 显示边框
      borderColor: '#012f4a' // 边框颜色
    },
    xAxis: {
      type: 'category',
      boundaryGap: false, // 去除轴间距
      data: [ '-11', '-10', '-9', '-8','-7', '-6', '-5', '-4', '-3', '-2', '-1', '0'],
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
    //'#00f2f1', '#ed3f35'
    visualMap: {
      show: false,
      dimension: 0,
      pieces: [
        {
          lt: 8,
          color: 'green'
        },
        {
          gte: 8,
          lte: 12,
          color: 'green'
        },
      ]
    },
    series: [
      {
        name: 'line_cost_sum',
        type: 'line',
        smooth: true,
        // prettier-ignore
        data: line_cost_sum,
        // markArea: {
        //   itemStyle: {
        //     color: 'rgba(255, 173, 177, 0.4)'
        //   },
        //   data: [
        //     [
        //       {
        //         name: 'PREDICT',
        //         xAxis: '1'
        //       },
        //       {
        //         xAxis: '4'
        //       }
        //     ]
        //   ]
        // }
      }
    ]
  };

  myChart.setOption(option);

  // 4.让图表随屏幕自适应
  window.addEventListener('resize', function () {
    myChart.resize();
  })
};

//得分
function score(data) {

  var score = data.score.toFixed(2);
  var origin_score = data.origin_score.toFixed(2);
  var myChart = echarts.init(document.querySelector(".score .chart"));
  // option = {
  //   series: [
  //     {
  //       fontFamily:'STFangsong',
  //       color:['green','red'],
  //       type: 'gauge',
  //       startAngle: 90,
  //       endAngle: -270,
  //       pointer: {
  //         show: false
  //       },
  //       progress: {
  //         show: true,
  //         overlap: false,
  //         roundCap: true,
  //         clip: false,
  //         itemStyle: {
  //           borderWidth: 1,
  //           borderColor: '#464646'
  //         }
  //       },
  //       axisLine: {
  //         lineStyle: {
  //           width: 40,
  //           color:[[1, '#a7a7a7']],
  //         }
  //       },
  //       splitLine: {
  //         show: false,
  //         distance: 0,
  //         length: 10
  //       },
  //       axisTick: {
  //         show: false
  //       },
  //       axisLabel: {
  //         show: false,
  //         distance: 50
  //       },
  //       data: [
  //         {
  //           value: origin_score,
  //           name: '原始得分',
  //           title: {
  //             offsetCenter: ['0%', '-30%'],
  //             color:'green'
  //           },
  //           detail: {
  //             valueAnimation: true,
  //             offsetCenter: ['0%', '-20%']
  //           }
  //         },
  //         {
  //           value: score,
  //           name: '得分',
  //           title: {
  //             offsetCenter: ['0%', '0%'],
  //             color:'red'
  //           },
  //           detail: {
  //             valueAnimation: true,
  //             offsetCenter: ['0%', '10%']
  //           }
  //         }
  //       ],
  //       title: {
  //         fontSize: 14,
  //         color:'white',
  //       },
  //       detail: {
  //         width: 50,
  //         height: 14,
  //         fontSize: 14,
  //         color: 'inherit',
  //         borderColor: 'inherit',
  //         borderRadius: 20,
  //         borderWidth: 1,
  //         formatter: '{value}%'
  //       }
  //     }
  //   ]
  // };
  // 声明颜色数组
  var myColor = [ "#F57474","green",];
  // 2.指定配置项和数据
  var option = {
    toolbox: {
      right: 'right',
      top: 'top',
      show: true,
      feature: {
        saveAsImage: {
          title: '保存',
          name: 'score',
        },        
      }
    },
    tooltip: {
      trigger: 'axis',
      textStyle: {
        fontFamily:'STFangsong',
        fontSize:15
      }
    },
    grid: {
      top: "10%",
      left: '23%',
      bottom: '10%',
      // containLabel: true
    },
    xAxis: {
      // 不显示x轴相关信息
      show: false
    },
    yAxis: [{
      type: 'category',
      // y轴数据反转，与数组的顺序一致
      inverse: true,
      // 不显示y轴线和刻度
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      // 将刻度标签文字设置为白色
      axisLabel: {
        color: "white",
        fontSize: 15,
        fontFamily:'STFangsong'
      },
      data: ["score", "origin_score"]
    }, {
      // y轴数据反转，与数组的顺序一致
      inverse: true,
      show: true,
      // 不显示y轴线和刻度
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      // 将刻度标签文字设置为白色
      axisLabel: {
        color: 'white',
        fontSize: 13,
        fontFamily:'STFangsong'
      },
      data: ['100%', '100%']
    }],
    series: [{
        // 第一组柱子（条状）
        name: '分数',
        type: 'bar',
        // 柱子之间的距离
        barCategoryGap: 20,
        // 柱子的宽度
        barWidth: 20,
        // 层级 相当于z-index
        yAxisIndex: 0,
        // 柱子更改样式
        itemStyle: {
          barBorderRadius: 10,
          // 此时的color可以修改柱子的颜色
          color: function (params) {
            // params 传进来的是柱子的对象
            // dataIndex 是当前柱子的索引号
            // console.log(params);
            return myColor[params.dataIndex];
          }
        },

        data: [score,origin_score],
        // 显示柱子内的百分比文字
        label: {
          show: true,
          position: "inside",
          fontFamily:'STFangsong',
          fontSize: 15,
          // {c} 会自动解析为数据（data内的数据）
          formatter: "{c}%"
        } 
      },
      {
        // 第二组柱子（框状 border）
        name: '最大值',
        type: 'bar',
        // 柱子之间的距离
        barCategoryGap: 50,
        // 柱子的宽度
        barWidth: 20,
        // 层级 相当于z-index
        yAxisIndex: 1,
        // 柱子修改样式
        itemStyle: {
          color: "none",
          borderColor: "#00c1de",
          borderWidth: 2,
          barBorderRadius: 15,
        },
        data: [100, 100]
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
