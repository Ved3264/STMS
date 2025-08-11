
        var charts = {};

        // Function to fetch report data
        function fetchReportData() {
            var startDate = document.getElementById('start_date').value;
            var endDate = document.getElementById('end_date').value;

            if (!startDate || !endDate) {
                alert("Please select both start and end dates!");
                return;
            }

            $.ajax({
                url: `/report/api/data?start_date=${startDate}&end_date=${endDate}`,
                method: 'GET',
                success: function(response) {
                    updateMultiDatasetChart('lineChart', response.labels, response.vehicleData, 'line');
                    updateChart('barChart', response.labels, response.vehicleCounts, 'bar', response.colors);
                    updateChart('areaChart', response.labels, response.totalVehicles, 'line', response.areaChartColor, true);
                    updatePieChart('pieChart', response.vehicleData);
                }
            });
        }

        // Function to update multi-dataset chart (Line Chart)
        function updateMultiDatasetChart(chartId, labels, datasets, chartType) {
            if (charts[chartId]) {
                charts[chartId].data.labels = labels;
                charts[chartId].data.datasets = datasets.map(dataset => ({
                    label: dataset.label,
                    data: dataset.data,
                    backgroundColor: dataset.color,
                    borderColor: dataset.color,
                    borderWidth: 1,
                    fill: false
                }));
                charts[chartId].update();
            } else {
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
                            borderWidth: 1,
                            fill: false
                        }))
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }
        }

        // Function to update a simple chart (Bar Chart and Area Chart)
        function updateChart(chartId, labels, values, chartType, colors = null, fill = false) {
            if (charts[chartId]) {
                charts[chartId].data.labels = labels;
                charts[chartId].data.datasets[0].data = values;
                charts[chartId].data.datasets[0].backgroundColor = colors || 'rgba(75, 192, 192, 0.2)';
                charts[chartId].update();
            } else {
                var ctx = document.getElementById(chartId).getContext('2d');
                charts[chartId] = new Chart(ctx, {
                    type: chartType,
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Vehicle Data',
                            data: values,
                            backgroundColor: colors || 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1,
                            fill: fill
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }
        }

        // Function to update Pie Chart
        function updatePieChart(chartId, vehicleData) {
            var pieData = vehicleData.map(item => {
                return item.data.reduce((acc, curr) => acc + curr, 0); // Summing all vehicle counts
            });

            if (charts[chartId]) {
                charts[chartId].data.datasets[0].data = pieData;
                charts[chartId].update();
            } else {
                var ctx = document.getElementById(chartId).getContext('2d');
                charts[chartId] = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: vehicleData.map(item => item.label),
                        datasets: [{
                            data: pieData,
                            backgroundColor: vehicleData.map(item => item.color),
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
