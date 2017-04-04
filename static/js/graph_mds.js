queue()
    .defer(d3.json, "/lab2/cluster/mds")
    .await(makeGraphs);

function makeGraphs(error, projectsJson) {
  d3.selectAll("#load").remove()
  corr =projectsJson.corr
  euc = projectsJson.euc
  //console.log(projectsJson)
  var dataE = new Array;
  var dataC = new Array;
  for(var i=0;i<Object.keys(euc).length;i++) {
    A = new Array(euc[i].x, euc[i].y, euc[i].label)
    dataE.push(A)
  }
  for(var i=0;i<Object.keys(corr).length;i++) {
    A = new Array(corr[i].x, corr[i].y, corr[i].label)
    dataC.push(A)
  }

  function draw(data) {
    d3.selectAll("svg").remove()

    //console.log(data)
    color = ['red', 'blue', 'green']
    var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

    var xmin = d3.min(data, function(d){return d[0]}),
    xmax = d3.max(data, function(d){return d[0]}),
    ymin = d3.min(data, function(d){return d[1]}),
    ymax = d3.max(data, function(d){return d[1]})
    //var xValue =function(d) { return +d.x};
    var xScale = d3.scale.linear().range([0, width]);
    //xMap = function(d) { return xScale(xValue(d));}, // data -> display
    var xAxis = d3.svg.axis().scale(xScale).orient("bottom");

    //var yValue = function(d) { return +d.y};
    var yScale = d3.scale.linear().range([height, 0]);
    //yMap = function(d) { return yScale(yValue(d));}, // data -> display
    var yAxis = d3.svg.axis().scale(yScale).orient("left");

    xScale.domain([xmin-1, xmax+1]);
    yScale.domain([ymin-1, ymax+1]);

    var svg = d3.select("body").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      // x-axis
      svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis)
        .append("text")
          .attr("class", "label")
          .attr("x", width)
          .attr("y", -6)
          .style("text-anchor", "end")
          .text("M1");

      // y-axis
      svg.append("g")
          .attr("class", "y axis")
          .call(yAxis)
        .append("text")
          .attr("class", "label")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .text("M2");

      // draw dots
      svg.selectAll(".dot")
          .data(data)
          .enter().append("circle")
          .attr("class", "dot")
          .attr("r", 3.5)
          .attr("cx", function(d) {return xScale(d[0])})
          .attr("cy", function(d) {return yScale(d[1])})
          .style("fill", function(d) {return color[d[2]]});
    };
  draw(dataE)
  d3.selectAll("#euc")
	  .on("click", function() {
      draw(dataE)
    });
  d3.selectAll("#corr")
    .on("click", function() {
      draw(dataC)
    });

};
