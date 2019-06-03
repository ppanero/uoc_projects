var chart = d3.parsets()
    .dimensions(["Organization", "Leak Method", "Data Sensitivity"]);

var vis = d3.select("#vis").append("svg")
    .attr("width", chart.width())
    .attr("height", chart.height());

var partition = d3.layout.partition()
    .sort(null)
    .size([chart.width(), chart.height() * 5 / 4])
    .children(function(d) { return d.children ? d3.values(d.children) : null; })
    .value(function(d) { return d.count; });

var ice = false;

function curves() {
  var t = vis.transition().duration(500);
  if (ice) {
    t.delay(1000);
    icicle();
  }
  t.call(chart.tension(this.checked ? .5 : 1));
}

d3.csv("./data/data_v3.csv", function(error, csv) {
  vis.datum(csv).call(chart);
});


d3.select("#file").on("change", function() {
  var file = this.files[0],
      reader = new FileReader;
  reader.onloadend = function() {
    var csv = d3.csv.parse(reader.result);
    vis.datum(csv).call(chart
        .value(csv[0].hasOwnProperty("Number") ? function(d) { return +d.Number; } : 1)
        .dimensions(function(d) { return d3.keys(d[0]).filter(function(d) { return d !== "Number"; }).sort(); }));
  };
  reader.readAsText(file);
});
