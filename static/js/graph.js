queue()
    .defer(d3.json, "/lab2/sample")
    .await(makeGraphs);

function makeGraphs(error, projectsJson) {
  console.log('hi')
  console.log('hello', projectsJson)
  var data = $.map(projectsJson, function(d) { return d});
  console.log(data)
  var dataset = data.map(function(a) {return a.emp;});
  console.log(dataset)

  var ndx = crossfilter(data)
  console.log(ndx)
  var stateDim = ndx.dimension(function(d) { return d["state"]; });
  var yearDim = ndx.dimension(function(d) { return d["year"]; });
  console.log(stateDim)
  var waterState = stateDim.group().reduceSum(function(d) {
    return d["water"];
  });



};
