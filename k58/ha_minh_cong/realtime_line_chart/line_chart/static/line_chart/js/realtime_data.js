/*
 * Real-time data generators for the example graphs in the documentation section.
 */
function  convert_time_stamp_to_int_date_value(time_stamp){
    var date_data = new Date(parseInt(time_stamp.substring(0,4)),parseInt(time_stamp.substring(5,7))-1,
        parseInt(time_stamp.substring(8,10)), parseInt(time_stamp.substring(11,13)),
        parseInt(time_stamp.substring(14,16)),parseInt(time_stamp.substring(17,19))
    );
    return date_data.getTime();
}

(function() {

    /*
     * Class for generating real-time data for the area, line, and bar plots.
     */
    var RealTimeData = function(layers, ranges, bounds) {
        this.layers = layers;
        this.bounds = bounds || [];
        this.ranges = ranges || [];
        this.timestamp = ((new Date()).getTime() / 1000)|0;
        this.expired  = false;
    };

    RealTimeData.prototype.rand = function(bound) {
        bound = bound || 100;
        return parseInt(Math.random() * bound) + 50;
    };

    RealTimeData.prototype.history = function(entries) {
        var data_ajax ={entries_number:60};

        $("form input[type='checkbox']").each(function () {
// {#           console.log($(this).attr('name')+ $(this).is(":checked").toString());#}
            if( $(this).is(":checked")){
                data_ajax[$(this).attr('name')]="true";
            }
        });
        var data_history_list = []
        console.log(data_ajax);
        $.ajax({
                beforeSend: function ()
                {
                },
                method: "GET",
                dataType: "json",
                url: "/realtime_history_data/" ,
                data: data_ajax,
                async: false,
                success: function(result) {
                    //format for result:
                    // class HistoryResult:{
                    // time_stamp:int
                    //data_value:int}
                    console.log("history_result");
                    // console.log(result);
                    for(i =0; i< result.length;i++){
                        var data_history ={label:result[i].data_type,values:[] };
                        for (j = 0; j< result[i].data_list.length;j++){
                            var data_entry = result[i].data_list[j];
                            // console.log(data_entry.time_stamp);
                            data_history.values.push({time: convert_time_stamp_to_int_date_value(data_entry.time_stamp)/1000,
                                y: data_entry.value});
                        }
                        data_history_list.push(data_history);
                    }
                    console.log("1");
                    console.log(data_history_list);
                    // console.log(Date.now());
                },
                error: function (ajaxContext) {
                    console.log("Error"+ajaxContext.toString());
                    //stop timer interval
                    clearInterval(timer_loop);
                    //show error
                },
                timeout: 400
        });

        //
        // if (typeof(entries) != 'number' || !entries) {
        //     entries = 60;
        // }
        //
        // var history = [];
        // for (var k = 0; k < this.layers; k++) {
        //     var config = { values: [] };
        //     if(this.ranges[k]) {
        //         config.range = this.ranges[k];
        //     console.log(config);
        //     }
        //
        //     history.push(config);
        // }
        //
        // for (var i = 0; i < entries; i++) {
        //     for (var j = 0; j < this.layers; j++) {
        //         history[j].values.push({time: this.timestamp, y: this.rand(this.bounds[j])});
        //     }
        //     this.timestamp++;
        // }
        // console.log(history);
        // console.log(data_history_list);
        this.timestamp = data_history_list[0].values[data_history_list[0].values.length-1].time+1;
        return data_history_list;
    };

    RealTimeData.prototype.next = function() {
        var entry = [];
        for (var i = 0; i < this.layers; i++) {
            entry.push({ time: this.timestamp, y: this.rand(this.bounds[i]) });
        }
        this.timestamp++;
        return entry;
    };

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
    };

    window.HeatmapData = HeatmapData;


})();
