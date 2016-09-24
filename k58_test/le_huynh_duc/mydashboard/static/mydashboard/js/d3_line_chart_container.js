

line_chart_container={
  line_chart: function(selector,setting){
    $(selector).each(function () {
      var self = this;
      self.selector = selector;
      self.setting = setting;
      self.set_time_to_update(self.selector);
      self.bind_command(self.selector,setting);
      // self.set_time_to_update(self.selector);
    });
  } ,
  refresh: function(html_element, settings){
    var chart = new horizon.d3_line_chart.LineChart(this, html_element, settings);
    chart.refresh();
  },

  set_time_to_update : function (selector) {
    var self = this;
    self.time_to_up = setInterval(function(){
       console.log("now is: "+ Date());
       self.update_charts(selector);
    },10000);
  },
  update_charts:function(selector){
    var self =this;
    $(selector).each(function(){
      self.refresh(this,self.setting);
    });
  },

  bind_command:function(selector,setting){
    var date_picker_chage = 'input[data-line-chart-command-v2="date_picker_change"]';
    var select_box_change='select[data-line-chart-command="select_box_change"]';
    var self = this;

    var connect_forms_to_chart = function(){
      $(selector).each(function () {
        var chart = $(this);
        $(chart.data("form-selector")).each(function () {
          var form = $(this);
          var chart_identifier = 'div[chart_selector="'+chart.data("form-seclector")+'"]';
          if(!form.data("chart_selector")){
            form.data("chart_selector",chart_identifier);
          }else{
            form.data('chart_selector', form.data('chart_selector') + ', ' + chart_identifier);
          }
        })
      })
    };

    var delegate_event_and_fresh_chart = function(selector,event_name,setting){
      $('form').delegate(selector,event_name,function () {
        var input = $(this);
        var form = input.parents('form').first();
        $(form.data('chart_selector')).each(function () {
          self.refresh(this,setting);
        });
        clearInterval(self.time_to_up);
      })
    };
    var event_change_date_picker = function (setting) {
      horizon.datepickers.add(date_picker_chage);
      delegate_event_and_fresh_chart(date_picker_chage,"changeDate",setting);
    };
    var event_change_select_box = function (setting) {
      delegate_event_and_fresh_chart(select_box_change,'change',setting);
    };

    connect_forms_to_chart();
    event_change_date_picker(self.setting);
    event_change_select_box(self.setting);

  }
};
line_chart_container.line_chart('div[data-line-chart-type-v2 = "container_line_chart"]');