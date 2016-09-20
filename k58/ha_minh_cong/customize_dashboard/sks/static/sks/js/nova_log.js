/**
 * Created by cong on 28/08/2016.
 */

current_date_from = $("#date_from").val();
current_date_to = $("#date_to").val();
$( function() {
    $( "#date_from" ).datepicker();
    $( "#date_to" ).datepicker();
} );

$(document).ready(function(){
    $("#date_from").focusout(function(){
        handle_date_from_event();
    });
    $("#date_to").focusout(function(){
        console.log("helog");
        handle_date_to_event();
    });
});
$("#date_to").datepicker({
  onSelect: function(dateText) {
      handle_date_to_event()
  }
});
$("#date_from").datepicker({
  onSelect: function(dateText) {
      handle_date_from_event();
  }
});
function handle_date_from_event() {
    data_date_from = $("#date_from").val();
      if(data_date_from!=current_date_from){
          current_date_from=data_date_from;
          update_chart();
          clearInterval(timer);
          reset_timer_interval();
      }
}
function handle_date_to_event() {
    data_date_to = $("#date_to").val();
    if(data_date_to!=current_date_to){
        current_date_to=data_date_to;
        update_chart();
        clearInterval(timer);
        reset_timer_interval();
      }

}

function getCfrsCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCfrsCookie('csrftoken');
console.log(csrftoken);

function update_chart(){
        var data = {
            'date_from': current_date_from,
            'date_to':current_date_to
        }
        console.log("date from:"+current_date_from+" date to:"+current_date_to);
        $.ajax({
            beforeSend: function (request)
            {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            "type": "POST",
            "dataType": "json",
            "url": "/sks/pie_chart_nova_log/nova_log_api/" ,
            "data": data,
            "success": function(result) {
                nova_log_data_used="";
                log_data = result.log_list;
                for (var i = 0; i <( log_data.length); i++) {
                    if(log_data[i].count>0){
                        nova_log_data_used+=log_data[i].name+":"+log_data[i].count+"="+log_data[i].count+"|";
                    }
                }
                nova_log_data_used = nova_log_data_used.substring(0, nova_log_data_used.length - 1);
                // nova_log_data_used+=log_data[].name+":"+log_data[i].count+"="+log_data[i].count;
                console.log(nova_log_data_used);
                $("#d3_pie_chart_distribution_nova_log").data("used",nova_log_data_used);

                $("#d3_pie_chart_distribution_nova_log svg").remove();
                $("#d3_pie_chart_distribution_nova_log div").remove();

                var log_info = "";
                for (var i = 0; i <( log_data.length); i++) {
                        log_info+=log_data[i].name+" logs = "+log_data[i].count+"   ";
                }
                $("#log_info").text(log_info);
                if(nova_log_data_used!=""){
                     setTimeout(function(){
                         d3_pie_chart_distribution_nova_summary.init();
                     },200);
                }
            },error: function (ajaxContext) {
                $('#display-error span').text(ajaxContext.responseText);
                $('#display-error').fadeIn().delay(1500).fadeOut();
            }
        });

}

function check_and_update_chart() {
    if(current_date_to!="" &&current_date_from!=""){
        update_chart();
      }
}
var timer;
 var reset_timer_interval = function(){
 timer = setInterval(function(){
     console.log("now is: "+ Date());
     update_chart();
 },6000);
};

reset_timer_interval();
update_chart();
$('#btn_test').click(function(){
   clearInterval(timer);
   reset_timer_interval();
});
