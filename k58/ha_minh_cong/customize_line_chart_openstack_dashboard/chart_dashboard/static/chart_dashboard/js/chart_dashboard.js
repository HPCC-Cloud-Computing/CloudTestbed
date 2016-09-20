/* Additional JavaScript for chart_dashboard. */
// setup  ajax and handle select_date event

d3_chart_nova_log = {
  chart_timers:[],
  setup_line_chart: function(selector, settings) {
    var self = this;
    this.setting = settings;
    this.charts_selector = selector;
    // this.charts_selector = selector;
    self.set_timer_for_charts(selector);
    self.bind_input_events(selector, settings);
    // self.reset_timer_interval(selector);
  },
  /**
   * Function for creating chart objects, saving them for later reuse
   * and calling their refresh method.
   * @param html_element HTML element where the chart will be rendered.
   * @param settings An object containing settings of the chart.
   */
  refresh: function(html_element, settings){
    var chart = new horizon.d3_line_chart.LineChart(this, html_element, settings);
    chart.refresh();
  },

  bind_input_events: function (selector, settings){
    // connecting controls of the charts
    var select_box_selector = 'select[data-input-nova-log="select_box_change"]';
    var date_picker_selector = 'input[data-input-nova-log="date_picker_change"]';
    var self = this;

    var connect_forms_to_charts = function(){
      $(selector).each(function() {
        var chart = $(this);
        $(chart.data('form-selector')).each(function(){
          var form = $(this);
          // each form is building a jquery selector for all charts it affects
          var chart_identifier = 'div[data-form-selector="' + chart.data('form-selector') + '"]';
          if (!form.data('nova_log_charts_selector')){
            form.data('nova_log_charts_selector', chart_identifier);
          } else {
            form.data('nova_log_charts_selector', form.data('nova_log_charts_selector') + ', ' + chart_identifier);
          }
        });
      });
    };

    /**
     * A helper function for delegating form events to charts, causing their
     * refreshing.
     * @param selector JQuery selector contains event (i.e. date_picker or select box)
     * @param event_name Event name we want to delegate.
     * @param settings An object containing settings of the chart.
     */
    var delegate_event_and_refresh_charts = function(selector, event_name, settings) {
      $('form').delegate(selector, event_name, function() {
        /*
          Registering 'any event' on form element by delegating. This way it
          can be easily overridden / enhanced when some special functionality
          needs to be added. Like input element showing/hiding another element
          on some condition will be defined directly on element and can block
          this default behavior.
        */
        var invoker = $(this);
        var form = invoker.parents('form').first();
        // console.log(form.data('charts_selector'));
        // console.log(form.data('nova_log_charts_selector'));
        $(form.data('nova_log_charts_selector')).each(function(){
          // refresh the chart connected to changed form
          // console.log("trigger!");
          var chart_index =$(this).attr("timer_index");
          clearInterval(self.chart_timers[parseInt(chart_index)].timer);
          self.refresh(this, settings);
          self.chart_timers[parseInt(chart_index)].timer = setInterval(function(){
            d3_chart_nova_log.update_charts("div[timer_index="+chart_index+"]");
          },8000);
        });
        // self.reset_timer_interval(self.charts_selector);
      });
    };

    /**
     * A helper function for catching change event of form selectboxes
     * connected to charts.
     */
    var bind_select_box_and_date_picker_change = function(settings) {
      set_up_date_picker(date_picker_selector);
      delegate_event_and_refresh_charts(select_box_selector, 'change', settings);
      delegate_event_and_refresh_charts(date_picker_selector, 'changeDate', settings);
    };
    var set_up_date_picker =function(selector){
      $(selector).each(function () {
        var el = $(this);
        el.datepicker({
          format: 'yyyy-mm-dd',
          timeFormat: "HH:mm:ss",
          setDate: new Date(),
          showButtonPanel: true,
          language: horizon.datepickerLocale
        });
      });
    }
    connect_forms_to_charts();
    bind_select_box_and_date_picker_change(settings);
  },

  check_for_update_chart:function(chart_selector){

  },
  // reset_timer_interval : function(chart_identifier){
  //   var self = this;
  //   self.timer = setInterval(function(){
  //     console.log('reset'+$(chart_identifier).data('name'));
  //     console.log("now is: "+ Date());
  //      self.update_charts(chart_identifier);
  //   },6000);
  // },
  //
  update_charts:function(selector){
    var self =this;
    var updated = false;
    $($(selector).data('form-selector')).each(function(){
      console.log($(this).attr("id"));
          var form = $(this);
          $(this).find('input').each(function () {
            if ($(this).attr("name").indexOf("date_to") !== -1){
              var date_string = $(this).val();
              if(date_string !=''){
                console.log(date_string);
                var date_now =new Date();
                var date_to_input = new Date(parseInt(date_string.substr(0, 4)),
                    parseInt(date_string.substr(5,2))-1, parseInt(date_string.substr(8,2)),23,59,59);
                console.log(date_to_input);
                console.log(date_now)
                if (date_to_input>= date_now){
                  // alert("true");
                  updated=true;
                }
              }else {
                updated=true;
              }
            }
          });
    });
    // console.log("updating"+$(selector).data('name'));
    if(updated==true){
      $(selector).each(function(){
        self.refresh(this,self.setting);
      });
    }
  },

  set_timer_for_charts:function (charts_selector) {
    var self = this;
    var timer_index = 0;
    console.log(charts_selector);
    $(charts_selector).each(function () {
      // $(this).data("timer_index",timer_index);
      // console.log(this);
      $(this).attr("timer_index",timer_index);
      // console.log($(this).data("name"));
      self.chart_timers.push(new d3_chart_nova_log.ChartTimer(timer_index,this));
      timer_index++;
    })
  },
  ChartTimer: function (index,chart_identifier) {
    this.index = index;
    this.timer = setInterval(function(){
      // console.log("now is: "+ Date());
      // console.log($(chart_identifier).data('name'));
      // console.log(chart_identifier);
      d3_chart_nova_log.update_charts("div[timer_index="+index.toString()+"]");
    },6000);
  }
};
d3_chart_nova_log.setup_line_chart('div[data-chart-setup-type="nova_log"]');

