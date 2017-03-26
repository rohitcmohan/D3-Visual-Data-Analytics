queue()
    .defer(d3.json, "/lab2/produce")
    .await(makeGraphs);

function makeGraphs(error, projectsJson) {
  console.log('hi')
  //console.log(projectsJson)
};
