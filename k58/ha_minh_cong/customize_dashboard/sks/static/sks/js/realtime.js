/**
 * Created by cong on 11/09/2016.
 */
$(function() {
    var data = new RealTimeData(3);

    chart = $('#real_time_line').epoch({
        type: 'time.line',
        data: data.history(),
        windowSize: 60,
        axes: ['left', 'bottom', 'right']
    });

    setInterval(function() {
        t = data.next();
        chart.push(t);
    }, 800);
    chart.push(data.next());
});
