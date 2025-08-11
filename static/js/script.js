 // Store chart instances globally
 var charts = {};

 // Function to fetch data and update charts dynamically
 function fetchChartData() {
     $.ajax({
         url: '/home/api/chart1-data',
         method: 'GET',
         success: function(response) {
             updateMultiDatasetChart('chart1', response.labels, response.datasets, 'line');
         }
     });

     $.ajax({
         url: '/home/api/chart2-data',
         method: 'GET',
         success: function(response) {
             updateChart('chart2', response.labels, response.values, 'pie', response.colors);
         }
     });

     $.ajax({
         url: '/home/api/chart3-data',
         method: 'GET',
         success: function(response) {
             updateMultiDatasetChart('chart3', response.labels, response.datasets, 'bar');
         }
     });

     $.ajax({
         url: '/home/api/chart4-data',
         method: 'GET',
         success: function(response) {
             updateChart('chart4', response.labels, response.values, 'radar');
         }
     });
 }

 // Function to create or update a multi-dataset chart
 function updateMultiDatasetChart(chartId, labels, datasets, chartType) {
     if (charts[chartId]) {
         // Update existing chart
         charts[chartId].data.labels = labels;
         charts[chartId].data.datasets = datasets.map(dataset => ({
             label: dataset.label,
             data: dataset.data,
             backgroundColor: dataset.color,
             borderColor: dataset.color,
             borderWidth: 1
         }));
         charts[chartId].update(); // Refresh chart
     } else {
         // Create new chart
         var ctx = document.getElementById(chartId).getContext('2d');
         charts[chartId] = new Chart(ctx, {
             type: chartType,
             data: {
                 labels: labels,
                 datasets: datasets.map(dataset => ({
                     label: dataset.label,
                     data: dataset.data,
                     backgroundColor: dataset.color,
                     borderColor: dataset.color,
                     borderWidth: 1
                 }))
             },
             options: {
                 responsive: true,
                 maintainAspectRatio: false
             }
         });
     }
 }

 // Function to create or update a simple chart
 function updateChart(chartId, labels, values, chartType, colors = null) {
     if (charts[chartId]) {
         // Update existing chart
         charts[chartId].data.labels = labels;
         charts[chartId].data.datasets[0].data = values;
         charts[chartId].data.datasets[0].backgroundColor = colors || 'rgba(75, 192, 192, 0.2)';
         charts[chartId].update(); // Refresh chart
     } else {
         // Create new chart
         var ctx = document.getElementById(chartId).getContext('2d');
         charts[chartId] = new Chart(ctx, {
             type: chartType,
             data: {
                 labels: labels,
                 datasets: [{
                     label: 'Traffic Data',
                     data: values,
                     backgroundColor: colors || 'rgba(75, 192, 192, 0.2)',
                     borderColor: 'rgba(75, 192, 192, 1)',
                     borderWidth: 1
                 }]
             },
             options: {
                 responsive: true,
                 maintainAspectRatio: false
             }
         });
     }
 }

 // Call function to load chart data when the page loads
 $(document).ready(function() {
     fetchChartData();
     setInterval(fetchChartData, 3000);
 });
