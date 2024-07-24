// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// function number_format(number, decimals, dec_point, thousands_sep) {
//   // *     example: number_format(1234.56, 2, ',', ' ');
//   // *     return: '1 234,56'
//   number = (number + '').replace(',', '').replace(' ', '');
//   var n = !isFinite(+number) ? 0 : +number,
//     prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
//     sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
//     dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
//     s = '',
//     toFixedFix = function(n, prec) {
//       var k = Math.pow(10, prec);
//       return '' + Math.round(n * k) / k;
//     };
//   // Fix for IE parseFloat(0.55).toFixed(0) = 0;
//   s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
//   if (s[0].length > 3) {
//     s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
//   }
//   if ((s[1] || '').length < prec) {
//     s[1] = s[1] || '';
//     s[1] += new Array(prec - s[1].length + 1).join('0');
//   }
//   return s.join(dec);
// }

function number_format(number, decimals, dec_point, thousands_sep) {
  // Mengeluarkan nomor yang sama persis seperti data asli tanpa format tambahan
  // number = (number + '').replace('.', ',')
  return number;
}

var tempValues = [];
var phValues = [];
var tdsValues = [];
var doValues = [];
var orpValues = [];
var salinityValues = [];
var water_h_Values = [];
var water_cl_Values = [];
var dateTime = [];
// Loop through each data point
for (var i = 0; i < deviceData.length; i++) {
    // Access the pH value of the current data point and push it to phValues array
    tempValues.push(deviceData[i].temp);
    phValues.push(deviceData[i].ph);
    tdsValues.push(deviceData[i].tds);
    doValues.push(deviceData[i].do);
    orpValues.push(deviceData[i].orp);
    salinityValues.push(deviceData[i].salinity);
    water_h_Values.push(deviceData[i].water_h);
    water_cl_Values.push(deviceData[i].water_cl);
    dateTime.push(deviceData[i].time);
}

// Area Chart 1
var ctx1 = document.getElementById("myAreaChart1");
var myLineChart1 = new Chart(ctx1, {
  type: 'line',
  data: {
    labels: dateTime,
    datasets: [{
      label: "Temperature",
      lineTension: 0.3,
      backgroundColor: "rgba(78, 115, 223, 0.05)",
      borderColor: "rgba(78, 115, 223, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(78, 115, 223, 1)",
      pointBorderColor: "rgba(78, 115, 223, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
      pointHoverBorderColor: "rgba(78, 115, 223, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: tempValues,
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 6,
          fontSize: 10,
          callback: function(value, index, values) {
            var firstLine = value.substring(0,10);
            var secondLine = value.substring(10);
        
            return [firstLine, secondLine];
          }
        }
      }],
      yAxes: [{
        ticks: {
          min: 15,
          max: 45,
          maxTicksLimit: 10,
          padding: 10,
          fontSize: 10,
          callback: function(value, index, values) {
            return '' + number_format(value) + '°C';
          }
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      intersect: false,
      mode: 'index',
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': ' + number_format(tooltipItem.yLabel) +'°C';
        }
      }
    }
  }
});

// Area Chart 2
var ctx2 = document.getElementById("myAreaChart2");
var myLineChart2 = new Chart(ctx2, {
  type: 'line',
  data: {
    labels: dateTime,
    datasets: [{
      label: "pH",
      lineTension: 0.3,
      backgroundColor: "rgba(28,200,138,0.05)",
      borderColor: "rgba(28,200,138, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(28,200,138, 1)",
      pointBorderColor: "rgba(28,200,138, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(28,200,138,1)",
      pointHoverBorderColor: "rgba(28,200,138,1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: phValues,
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 6,
          fontSize: 10,
          callback: function(value, index, values) {
            var firstLine = value.substring(0,10);
            var secondLine = value.substring(10);
        
            return [firstLine, secondLine];
          }
        }
      }],
      yAxes: [{
        ticks: {
          min: 4,
          max: 10,
          maxTicksLimit: 10,
          padding: 10,
          fontSize: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            return '' + number_format(value);
          }
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      intersect: false,
      mode: 'index',
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
        }
      }
    }
  }
});

// Area Chart 3
var ctx3 = document.getElementById("myAreaChart3");
var myLineChart3 = new Chart(ctx3, {
  type: 'line',
  data: {
    labels: dateTime,
    datasets: [{
      label: "TDS",
      lineTension: 0.3,
      backgroundColor: "rgba(54,185,204, 0.05)",
      borderColor: "rgba(54,185,204, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(54,185,204, 1)",
      pointBorderColor: "rgba(54,185,204, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(54,185,204, 1)",
      pointHoverBorderColor: "rgba(54,185,204, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: tdsValues,
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 6,
          fontSize: 10,
          callback: function(value, index, values) {
            var firstLine = value.substring(0,10);
            var secondLine = value.substring(10);
        
            return [firstLine, secondLine];
          }
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: 3000,
          maxTicksLimit: 10,
          padding: 10,
          fontSize: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            return '' + number_format(value) + ' ppm';
          }
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      intersect: false,
      mode: 'index',
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': ' + number_format(tooltipItem.yLabel) + ' ppm';
        }
      }
    }
  }
});

// Area Chart 4
var ctx4 = document.getElementById("myAreaChart4");
var myLineChart4 = new Chart(ctx4, {
  type: 'line',
  data: {
    labels: dateTime,
    datasets: [{
      label: "DO",
      lineTension: 0.3,
      backgroundColor: "rgba(246,194,62, 0.05)",
      borderColor: "rgba(246,194,62, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(246,194,62, 1)",
      pointBorderColor: "rgba(246,194,62, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(246,194,62, 1)",
      pointHoverBorderColor: "rgba(246,194,62, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: doValues,
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 6,
          fontSize: 10,
          callback: function(value, index, values) {
            var firstLine = value.substring(0,10);
            var secondLine = value.substring(10);
        
            return [firstLine, secondLine];
          }
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: 12,
          maxTicksLimit: 10,
          padding: 10,
          fontSize: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            return '' + number_format(value) + ' mg/L';
          }
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      intersect: false,
      mode: 'index',
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': ' + number_format(tooltipItem.yLabel) + ' mg/L';
        }
      }
    }
  }
});

// Area Chart 5
var ctx5 = document.getElementById("myAreaChart5");
var myLineChart5 = new Chart(ctx5, {
  type: 'line',
  data: {
    labels: dateTime,
    datasets: [{
      label: "ORP",
      lineTension: 0.3,
      backgroundColor: "rgba(133,135,150, 0.05)",
      borderColor: "rgba(133,135,150, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(133,135,150, 1)",
      pointBorderColor: "rgba(133,135,150, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(133,135,150, 1)",
      pointHoverBorderColor: "rgba(133,135,150, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: orpValues,
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 6,
          fontSize: 10,
          callback: function(value, index, values) {
            var firstLine = value.substring(0,10);
            var secondLine = value.substring(10);
        
            return [firstLine, secondLine];
          }
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: 500,
          maxTicksLimit: 10,
          padding: 10,
          fontSize: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            return '+' + number_format(value) + ' mV';
          }
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      intersect: false,
      mode: 'index',
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': +' + number_format(tooltipItem.yLabel) + ' mV';
        }
      }
    }
  }
});

// Area Chart 6
var ctx6 = document.getElementById("myAreaChart6");
var myLineChart6 = new Chart(ctx6, {
  type: 'line',
  data: {
    labels: dateTime,
    datasets: [{
      label: "Salinity",
      lineTension: 0.3,
      backgroundColor: "rgba(231,74,59, 0.05)",
      borderColor: "rgba(231,74,59, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(231,74,59, 1)",
      pointBorderColor: "rgba(231,74,59, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(231,74,59, 1)",
      pointHoverBorderColor: "rgba(231,74,59, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: salinityValues,
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 6,
          fontSize: 10,
          callback: function(value, index, values) {
            var firstLine = value.substring(0,10);
            var secondLine = value.substring(10);
        
            return [firstLine, secondLine];
          }
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: 20,
          maxTicksLimit: 10,
          padding: 10,
          fontSize: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            return '' + number_format(value) + ' ppt';
          }
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      intersect: false,
      mode: 'index',
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': ' + number_format(tooltipItem.yLabel) + ' ppt';
        }
      }
    }
  }
});

// Area Chart 7
var ctx7 = document.getElementById("myAreaChart7");
var myLineChart7 = new Chart(ctx7, {
  type: 'line',
  data: {
    labels: dateTime,
    datasets: [{
      label: "Water Height",
      lineTension: 0.3,
      backgroundColor: "rgba(90,92,105, 0.05)",
      borderColor: "rgba(90,92,105, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(90,92,105, 1)",
      pointBorderColor: "rgba(90,92,105, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(90,92,105, 1)",
      pointHoverBorderColor: "rgba(90,92,105, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: water_h_Values,
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 6,
          fontSize: 10,
          callback: function(value, index, values) {
            var firstLine = value.substring(0,10);
            var secondLine = value.substring(10);
        
            return [firstLine, secondLine];
          }
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: 200,
          maxTicksLimit: 10,
          padding: 10,
          fontSize: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            return '' + number_format(value) + ' cm';
          }
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      intersect: false,
      mode: 'index',
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': ' + number_format(tooltipItem.yLabel) + ' cm';
        }
      }
    }
  }
});

// Area Chart 8
var ctx8 = document.getElementById("myAreaChart8");
var myLineChart8 = new Chart(ctx8, {
  type: 'line',
  data: {
    labels: dateTime,
    datasets: [{
      label: "Water Clarity",
      lineTension: 0.3,
      backgroundColor: "rgba(78, 115, 223, 0.05)",
      borderColor: "rgba(78, 115, 223, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(78, 115, 223, 1)",
      pointBorderColor: "rgba(78, 115, 223, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
      pointHoverBorderColor: "rgba(78, 115, 223, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: water_cl_Values,
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 6,
          fontSize: 10,
          callback: function(value, index, values) {
            var firstLine = value.substring(0,10);
            var secondLine = value.substring(10);
        
            return [firstLine, secondLine];
          }
        }
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: 20,
          maxTicksLimit: 10,
          padding: 10,
          fontSize: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            return '' + number_format(value) + ' NTU';
          }
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      intersect: false,
      mode: 'index',
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': ' + number_format(tooltipItem.yLabel) + ' NTU';
        }
      }
    }
  }
});