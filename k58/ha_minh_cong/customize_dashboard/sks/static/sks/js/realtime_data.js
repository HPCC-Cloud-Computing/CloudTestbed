/*
 * Real-time data generators for the example graphs in the documentation section.
 */

(function() {

    /*
     * Class for generating real-time data for the area, line, and bar plots.
     */
    var RealTimeData = function(layers, ranges, bounds) {
        this.layers = layers;
        this.bounds = bounds || [];
        this.ranges = ranges || [];
        this.timestamp = ((new Date()).getTime() / 1000-60)|0;
    };

    RealTimeData.prototype.rand = function(bound) {
        bound = bound || 100;
        return parseInt(Math.random() * bound) + 50;
    };

    RealTimeData.prototype.history = function(entries) {
        if (typeof(entries) != 'number' || !entries) {
            entries = 60;
        }

        var history = [];
        for (var layer_index = 0; layer_index < this.layers; layer_index++) {
            var config = { values: [],label: "Series "+ (layer_index+1).toString() };
            if(this.ranges[layer_index]) {
                config.range = this.ranges[layer_index];
            console.log(config);
            }
            history.push(config);
        }
        $.ajax({
            beforeSend: function (request)
            {            
            },
            method: "GET",
            dataType: "json",
            url: "/sks/realtime/data_history/" ,
            data: {entries_number:60},
            async:false,
            success: function(result) {
                //format for result: 
                // class HistoryResult:{
                // time_stamp:int    
                //data_value:int}
                for(index = 0;index < entries;index++){
                    for (var layer_index = 0; layer_index < this.layers; layer_index++) {
                        history[layer_index].values.push({
                            time: result[layer_index][index].time_stamp,
                             y: result[layer_index][index].data_value
                            });
                    }
                }
            },error: function (ajaxContext) {
                horizon.alert('error', gettext('An error occurred. Please try again later.'));
                //stop timer interval
            }
        });
        return history;
    };

    RealTimeData.prototype.next = function() {
        var entry = [];
        for (var i = 0; i < this.layers; i++) {
            entry.push({ time: this.timestamp, y: this.rand(this.bounds[i]) });
        }
        this.timestamp++;
        return entry;
    }

    window.RealTimeData = RealTimeData;


    /*
     * Gauge Data Generator.
     */
    var GaugeData = function() {};

    GaugeData.prototype.next = function() {
        return Math.random();
    };

    window.GaugeData = GaugeData;



    /*
     * Heatmap Data Generator.
     */

    var HeatmapData = function(layers) {
        this.layers = layers;
        this.timestamp = ((new Date()).getTime() / 1000)|0;
    };
    
    window.normal = function() {
        var U = Math.random(),
            V = Math.random();
        return Math.sqrt(-2*Math.log(U)) * Math.cos(2*Math.PI*V);
    };

    HeatmapData.prototype.rand = function() {
        var histogram = {};

        for (var i = 0; i < 1000; i ++) {
            var r = parseInt(normal() * 12.5 + 50);
            if (!histogram[r]) {
                histogram[r] = 1;
            }
            else {
                histogram[r]++;
            }
        }

        return histogram;
    };

    HeatmapData.prototype.history = function(entries) {
        if (typeof(entries) != 'number' || !entries) {
            entries = 60;
        }

        var history = [];
        for (var k = 0; k < this.layers; k++) {
            history.push({ values: [] });
        }

        for (var i = 0; i < entries; i++) {
            for (var j = 0; j < this.layers; j++) {
                history[j].values.push({time: this.timestamp, histogram: this.rand()});
            }
            this.timestamp++;
        }

        return history;
    };

    HeatmapData.prototype.next = function() {
        var entry = [];
        for (var i = 0; i < this.layers; i++) {
            entry.push({ time: this.timestamp, histogram: this.rand() });
        }
        this.timestamp++;
        return entry;
    }

    window.HeatmapData = HeatmapData;


})();

        