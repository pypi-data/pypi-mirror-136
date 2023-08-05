var data = [
  {
    group: "video",
    data: [
      {
        label: "gopro",
        data: [
          {
            timeRange: [new Date(2019, 10, 25, 13), new Date(2019, 10, 26, 02)],
            val: "puddl://4c016f98-209d-4476-a6f6-fdd07b2b3d9e"
          },
          {
            timeRange: [new Date(2019, 10, 27, 13), new Date(2019, 10, 28, 02)],
            val: "puddl://68fe2b9d-b725-4f11-b720-c348c2853f53"
          }
        ]
      }
    ]
  }
];

var uri2meta = {
  "puddl://4c016f98-209d-4476-a6f6-fdd07b2b3d9e": { "foo": "bar" },
  "puddl://68fe2b9d-b725-4f11-b720-c348c2853f53": { "bar": "baz" }
}
var element = document.getElementById("chart");

myChart = TimelinesChart();
myChart.data(data)(element);
myChart.onSegmentClick(function(segment) {
  console.log(segment);
  var uri = segment.val;
  meta = uri2meta[uri];
  window.location.replace(uri);
});
