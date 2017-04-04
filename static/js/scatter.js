queue()
    .defer(d3.json, "/lab2/scatter")
    //.await(makeGraphs)
    .await(makeScatter);

function makeScatter(error, dataJ) {
  var width = 960,
    size = 230,
    padding = 20;

  var x = d3.scale.linear()
      .range([padding / 2, size - padding / 2]);

  var y = d3.scale.linear()
      .range([size - padding / 2, padding / 2]);

  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")
      .ticks(6);

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")
      .ticks(6);

  var color = d3.scale.category10();

  //d3.csv("static/data/top3.csv", function(error, data) {
    //if (error) throw error;
    var data = new Array;
    for(var i=0;i<Object.keys(dataJ).length;i++) {
      data[i] = dataJ[i]
    }
    console.log(data)
    var domainByCluster = {},
        clusters = d3.keys(data[0]).filter(function(d) { return d !== "label"; }),
        n = clusters.length;

    clusters.forEach(function(cluster) {
      domainByCluster[cluster] = d3.extent(data, function(d) { return d[cluster]; });
    });

    xAxis.tickSize(size * n);
    yAxis.tickSize(-size * n);

    var svg = d3.select("body").append("svg")
        .attr("width", size * n + padding)
        .attr("height", size * n + padding)
      .append("g")
        .attr("transform", "translate(" + padding + "," + padding / 2 + ")");

    svg.selectAll(".x.axis")
        .data(clusters)
      .enter().append("g")
        .attr("class", "x axis")
        .attr("transform", function(d, i) { return "translate(" + (n - i - 1) * size + ",0)"; })
        .each(function(d) { x.domain(domainByCluster[d]); d3.select(this).call(xAxis); });

    svg.selectAll(".y.axis")
        .data(clusters)
      .enter().append("g")
        .attr("class", "y axis")
        .attr("transform", function(d, i) { return "translate(0," + i * size + ")"; })
        .each(function(d) { y.domain(domainByCluster[d]); d3.select(this).call(yAxis); });

    var cell = svg.selectAll(".cell")
        .data(cross(clusters, clusters))
      .enter().append("g")
        .attr("class", "cell")
        .attr("transform", function(d) { return "translate(" + (n - d.i - 1) * size + "," + d.j * size + ")"; })
        .each(plot);

    // Titles for the diagonal.
    cell.filter(function(d) { return d.i === d.j; }).append("text")
        .attr("x", padding)
        .attr("y", padding)
        .attr("dy", ".71em")
        .text(function(d) { return d.x; });

    function plot(p) {
      var cell = d3.select(this);

      x.domain(domainByCluster[p.x]);
      y.domain(domainByCluster[p.y]);

      cell.append("rect")
          .attr("class", "frame")
          .attr("x", padding / 2)
          .attr("y", padding / 2)
          .attr("width", size - padding)
          .attr("height", size - padding);

      cell.selectAll("circle")
          .data(data)
        .enter().append("circle")
          .attr("cx", function(d) { return x(d[p.x]); })
          .attr("cy", function(d) { return y(d[p.y]); })
          .attr("r", 4)
          .style("fill", function(d) { return color(d.label); });
    }
  //});

  function cross(a, b) {
    var c = [], n = a.length, m = b.length, i, j;
    for (i = -1; ++i < n;) for (j = -1; ++j < m;) c.push({x: a[i], i: i, y: b[j], j: j});
    return c;
  }

};
