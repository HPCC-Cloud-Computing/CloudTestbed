#Customize Openstack Dashboard
Bài viết này trình bày về cách xây dựng đồ thị trong openstack dashboard, cùng với các tùy chỉnh đề có thể xây dựng các đồ thị riêng.

##1 Nhúng các file customize css, customize javascript vào dashboard
Để có một dashboard có nhúng các file customize css, javascript, chúng ta làm theo hướng dẫn sau [create new dashboard in horizon](https://github.com/openstack/horizon/blob/stable/mitaka/doc/source/tutorials/dashboard.rst) để có 1 dashboard mới. 

---------
    mkdir openstack_dashboard/dashboards/mydashboard

    mkdir openstack_dashboard/dashboards/chart_dashboard

    ./run_tests.sh -m startdash chart_dashboard --target openstack_dashboard/dashboards/chart_dashboard

    mkdir openstack_dashboard/dashboards/chart_dashboard/pie_chart

    ./run_tests.sh -m startpanel pie_chart --dashboard=openstack_dashboard.dashboards.chart_dashboard --target=openstack_dashboard/dashboards/chart_dashboard/pie_chart


Sau đó, chúng ta xây dựng cây thư mục trong dashboard mới có định dạng như trong hướng dẫn trên:

---------
    chart_dashboard
    ├── dashboard.py
    ├── dashboard.pyc
    ├── __init__.py
    ├── __init__.pyc
    ├── pie_chart
    │   ├── __init__.py
    │   ├── panel.py
    │   ├── templates
    │   │   └── pie_chart
    │   │       └── index.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── static
    │   └── chart_dashboard
    │       ├── css
    │       │   └── chart_dashboard.css
    │       └── js
    │           └── chart_dashboard.js
    └── templates
        └── chart_dashboard
            └── chart_base.html

Sau khi xây dựng xong cây thư mục, chúng ta tiến tới cấu hình các tệp cần thiết để xây dựng nên các trang chứa biểu đồ mà chúng ta muốn tạo nên:

Đầu tiên, chúng ta tạo file file chart_base.html trong đường dẫn templates/chart_dashboard/chart_base.html để include các file customize css và javascript mà chúng ta sẽ xây dựng ở phần sau:

    {% extends 'base.html' %}
	{% block css %}
	  {% include "_stylesheets.html" %}
	  <link href='{{ STATIC_URL}}chart_dashboard/css/chart_dashboard.css' type='text/css' media='screen' rel='stylesheet' />
	{% endblock %}
	{% block js %}
	    {% include "chart_dashboard/_scripts.html" %}
	{% endblock %}

file này sẽ được dùng làm base cho các trang html chứa biểu đồ của chúng ta. Khi các trang html chứa biểu đồ được extends **chart_base.html**, thì các trang html đó sẽ được sử dụng các file css và javascript được khai báo trong chart_base.html, mà cụ thể là file chart_dashboard.css và các file javascript được khai báo trong 1 file mới mà chúng ta sẽ xây dựng ngay sau đây, file **templates/chart_dashboard/_scripts.html**.

Tại sao chúng ta phải xây dựng file này mà không include luôn các file custom js của chúng ta vào block js ?

Vấn đề nằm ở chỗ, trong file base.html dùng block **{% block js %}** để nhúng các file js vào trong base.html. Nếu chúng ta chỉ khai báo file custom js của chúng ta vào trong block này, chúng ta sẽ nhúng thiếu các file js khác cần thiết cho hệ thống.
Để giải quyết vấn đề này, chúng ta cần nhúng file **templates/chart_dashboard/_scripts.html**  vào **{% block js %}** trong base.html, sau đó cho file trên kế thừa file _script.html có sẵn của horizon. Khi đó thì các file js có sẵn của hệ thống cũng sẽ được nhúng vào trong base.html:

    {% extends 'horizon/_scripts.html' %}
	{% block custom_js_files %}
	    <script src="{{STATIC_URL}}chart_dashboard/js/chart_dashboard.js"></script>
	{% endblock %}

trong file _script.html, các file custom js sẽ được đặt vào trong block **{% block custom_js_files %}**. Ở đây chúng ta thêm file js là **chart_dashboard.js**

sau khi xây dựng xong cây thư mục cho dashboard của chúng ta, hệ thống các tệp của chart_dashboard sẽ có dạng như sau:

---------
    chart_dashboard
    ├── dashboard.py
    ├── dashboard.pyc
    ├── __init__.py
    ├── __init__.pyc
    ├── pie_chart
    │   ├── __init__.py
    │   ├── panel.py
    │   ├── templates
    │   │   └── pie_chart
    │   │       └── index.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── static
    │   └── chart_dashboard
    │       ├── css
    │       │   └── chart_dashboard.css
    │       └── js
    │           └── chart_dashboard.js
    └── templates
        └── chart_dashboard
            └── chart_base.html
            └── _script.html

Tiếp theo, trước khi đi vào tạo các biểu đồ riêng cho chart_dashboard, chúng ta cùng xem lại các biểu đồ đã có sẵn trong openstack_dashboard, và tìm hiểu xem chúng đã được xây dựng như thế nào ?
##2 Phân tích các mã nguồn vẽ đồ thị có sẵn trong openstack dashboard:

Trong openstack dashboard, các biểu đồ bao gồm 3 thành phần chính:

 1. Trang chứa biểu đồ, là nơi mà biểu đồ được hiển thị. Quy định vị trí hiển thị biểu đồ và các cài đặt liên quan tới biểu đồ như: kích thước, định dạng, vị trí của nguồn cấp dữ liệu.
 2. Mã nguồn javascript: Thực hiện việc khai báo các class dùng để vẽ biểu đồ và thực hiện vẽ biểu đồ, xử lý sự kiện, xử lý dữ liệu
 3. Nguồn cấp dữ liệu: cấp dữ liệu cho biểu đồ.  
 
Trung tâm của các xử lý là mã nguồn javascript, do đó, đầu tiên chúng ta sẽ xem mã nguồn script vẽ biểu đồ đường (line_chart) như thế nào. 

###2.1 Javascript
Chúng ta sẽ xem mã nguồn của file **horizon.d3linechart.js**, file này nằm trong thư mục **horizon/static/horizon/js/horizon.d3linechart.js**

Để thể hiện biểu đồ hình đường lên màn hình, hệ thống sử dụng lệnh sau:

    /* Init the graphs */
	horizon.addInitFunction(function () {
	  horizon.d3_line_chart.init('div[data-chart-type="line_chart"]', {});
	});

Lệnh này gọi tới hàm `horizon.d3_line_chart.init()`. Hàm này thực hiện công việc khởi tạo và render các biểu đồ đường lên màn hình tại vị trí là tag html được truyền vào hàm (mà ở đây là **'div[data-chart-type="line_chart"]'**. Điều này có nghĩa là biểu đồ sẽ được khởi tạo ở các vị trí thẻ div thỏa mãn tag html trên. Dưới đây là phương thức init của đối tượng horizon.d3_line_chart ( khi các bạn vào file này sẽ thấy, horizon.d3_line_chart thực tế là một đối tượng có các thuộc tính và phương thức, và chúng ta sẽ sử dụng các thuộc tính và phương thức của đối tượng này để xây dựng nên các biểu đồ đường.)

```javascript
  init: function(selector, settings) {
    var self = this;
    $(selector).each(function() {
      self.refresh(this, settings);
    });

    if (settings !== undefined && settings.auto_resize) {
      /*
        I want to refresh chart on resize of the window, but only
        at the end of the resize. Nice code from mr. Google.
      */
      var rtime = new Date(1, 1, 2000, 12, 0, 0);
      var timeout = false;
      var delta = 400;
      $(window).resize(function() {
        rtime = new Date();
        if (timeout === false) {
          timeout = true;
          setTimeout(resizeend, delta);
        }
      });

      var resizeend = function() {
        if (new Date() - rtime < delta) {
          setTimeout(resizeend, delta);
        } else {
          timeout = false;
          $(selector).each(function() {
            self.refresh(this, settings);
          });
        }
      };
    }

    self.bind_commands(selector, settings);
  },
```

Như các bạn thấy trong định nghĩa của phương thức, phương thức này thực hiện các lệnh sau:
string đại diện cho html (selector) và setting(ở đây là null) sẽ được truyền vào phương thức. Sau đó phương thức sẽ gọi đến phương thức **refresh( )** cũng cũng của chính đối tượng **horizon.d3_line_chart** và thực hiện một số các thiết lập với setting. Cuối cùng phương thức **bind_commands()** của **horizon.d3_line_chart** được gọi tới. Ở đây chúng ta sẽ tìm hiểu chủ yếu về 2 phương thức **refresh()** và **bind_commands()** trong đối tượng **horizon.d3_line_chart**.

ta có thể thấy, đoạn mã:

```javascript
    var self = this;
    $(selector).each(function() {
      self.refresh(this, settings);
    });
```
sẽ chọn ra từng thẻ html phù hợp với selector để thực hiện phương thức **self.refresh()**. Tức là trên trang dashboard của chúng ta có bao nhiêu thẻ html phù hợp với selector ( mà ở đây là string **'div[data-chart-type="line_chart"]'**) sẽ có bấy nhiêu lần phương thức **self.refresh()** được gọi 
Phương thức refresh() sẽ thực hiện các công việc sau:
```javascript
  /**
   * Function for creating chart objects, saving them for later reuse
   * and calling their refresh method.
   * @param html_element HTML element where the chart will be rendered.
   * @param settings An object containing settings of the chart.
   */
  refresh: function(html_element, settings){
    var chart = new this.LineChart(this, html_element, settings);
    /*
      FIXME save chart objects somewhere so I can use them again when
      e.g. I am switching tabs, or if I want to update them
      via web sockets
      this.charts.add_or_update(chart)
    */
    chart.refresh();
  },
```
Chúng ta có thể thấy, với mỗi đối tượng html DOM được chọn (mỗi thẻ html phù hợp với selector tương ứng với 1 đối tượng html DOM, được truyền vào phương thức **refresh()** với cái tên là **html_element**), phương thức này sẽ tạo ra một đối tượng **chart** thuộc class **LineChart** tương ứng với đối tượng html DOM này. Sau đó đối tượng **chart** được tạo ra sẽ được kích hoạt phương thức **refresh()**. 2 phương thức tạo mới đối tượng **new LineChart()** và phương thức **chart.fresh()** sẽ tạo mới một đối tượng biểu đồ đường, xác định vị trí render biểu đồ thông qua **html_element**, thiết lập các thiết đặt cho biểu đồ thông qua các setting đặt sẵn trong **html_element**, gọi ajax để lấy dữ liệu của biểu đồ về và render biểu đồ ra trang dashboard. Chúng ta sẽ sử dụng luôn 2 phương thức này trong dashboard của chúng ta, do đó chúng ta sẽ không đi sâu vào việc các công việc trên được thực hiện chi tiết như thế nào.

Tiếp theo chúng ta sẽ xem phương thức **self.bind_commands(selector, settings);** thực hiện những hành động gì ?:
```javascript
  /**
   * Function for binding controlling commands to the chart. Like changing
   * timespan or various parameters we want to show in the chart. The
   * charts will be refreshed immediately after the form element connected
   * to them is changed.
   * @param selector JQuery selector of charts we are initializing.
   * @param settings An object containing settings of the chart.
   */
  bind_commands: function (selector, settings){
    // connecting controls of the charts
    var select_box_selector = 'select[data-line-chart-command="select_box_change"]';
    var datepicker_selector = 'input[data-line-chart-command="date_picker_change"]';
    var self = this;

    /**
     * Connecting forms to charts it controls. Each chart contains
     * JQuery selector data-form-selector, which defines by which
     * html Forms is a particular chart controlled. This information
     * has to be projected to forms. So when form input is changed,
     * all connected charts are refreshed.
     */
    var connect_forms_to_charts = function(){
      $(selector).each(function() {
        var chart = $(this);
        $(chart.data('form-selector')).each(function(){
          var form = $(this);
          // each form is building a jquery selector for all charts it affects
          var chart_identifier = 'div[data-form-selector="' + chart.data('form-selector') + '"]';
          if (!form.data('charts_selector')){
            form.data('charts_selector', chart_identifier);
          } else {
            form.data('charts_selector', form.data('charts_selector') + ', ' + chart_identifier);
          }
        });
      });
    };

    /**
     * A helper function for delegating form events to charts, causing their
     * refreshing.
     * @param selector JQuery selector of charts we are initializing.
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

        $(form.data('charts_selector')).each(function(){
          // refresh the chart connected to changed form
          self.refresh(this, settings);
        });
      });
    };

    /**
     * A helper function for catching change event of form selectboxes
     * connected to charts.
     */
    var bind_select_box_change = function(settings) {
      delegate_event_and_refresh_charts(select_box_selector, 'change', settings);
    };

    /**
     * A helper function for catching changeDate event of form datepickers
     * connected to charts.
     */
    var bind_datepicker_change = function(settings) {
      horizon.datepickers.add(datepicker_selector);
      delegate_event_and_refresh_charts(datepicker_selector, 'changeDate', settings);
    };

    connect_forms_to_charts();
    bind_select_box_change(settings);
    bind_datepicker_change(settings);
  }
};
```

chúng ta cần lưu ý các hàm phía trên là các định nghĩa hàm, các hành động chính là các lệnh gọi các hàm này, chúng được thực hiện ở dưới cùng hàm  **self.bind_commands(selector, settings);** 

```javascript
    connect_forms_to_charts();
    bind_select_box_change(settings);
    bind_datepicker_change(settings);
```

chúng ta cùng xem lần luợt 3 hàm này thực hiện những hành động gì. Đầu tiên là hàm **connect_forms_to_charts();**
```javascript

    // connecting controls of the charts
    var select_box_selector = 'select[data-line-chart-command="select_box_change"]';
    var datepicker_selector = 'input[data-line-chart-command="date_picker_change"]';
    var self = this;

    /**
     * Connecting forms to charts it controls. Each chart contains
     * JQuery selector data-form-selector, which defines by which
     * html Forms is a particular chart controlled. This information
     * has to be projected to forms. So when form input is changed,
     * all connected charts are refreshed.
     */
    var connect_forms_to_charts = function(){
      $(selector).each(function() {
        var chart = $(this);
        $(chart.data('form-selector')).each(function(){
          var form = $(this);
          // each form is building a jquery selector for all charts it affects
          var chart_identifier = 'div[data-form-selector="' + chart.data('form-selector') + '"]';
          if (!form.data('charts_selector')){
            form.data('charts_selector', chart_identifier);
          } else {
            form.data('charts_selector', form.data('charts_selector') + ', ' + chart_identifier);
          }
        });
      });
    };
```

phương thức này thực hiện nhiệm vụ kết nối các chart vào các form được đăng ký để điều khiển chúng. Tham số selector trong **\$(selector).each(function()** chính là parameter được truyền vào bên trong phương thức bao  **self.bind_commands(selector, settings);** . Mà tham số truyền vào  **self.bind_commands(selector, settings);**  lại chính là **selector** của hàm init() ban đầu mà chúng ta xét. Như đã nói ở phần trước, selector truyền vào hàm **init()** chính là định danh html của các đối tượng html DOM.Do đó, dòng lệnh   **\$(selector).each(function()** sẽ thực hiện n vòng lặp các lệnh bên trong thân , mỗi vòng lệnh tương ứng với 1 biểu đồ sẽ được vẽ. 

Ta thấy rằng chart sẽ được tham chiếu tới đối tượng html DOM đang được xử lý. sau đó, người ta sẽ lấy gía trị **chart.data('form-selector')**. Gía trị này tượng trưng cho điều gì ? Đây chính là định danh html của các biểu đồ điều khiển chart này, được khai báo trong thẻ html nơi đặt biểu đồ. Ví dụ, khi ta đặt biểu đồ vào file html của dashboard với thông số như sau
```html
			<div>
                 data-chart-setup-type="nova_log"
                 data-chart-type="line_chart"
                 data-url="{% url "horizon:sks:line_chart_nova_log:samples" %}"
                 data-form-selector='#line_chart_nova_log_form'
                 data-legend-selector="#legend"
                 data-smoother-selector="#smoother"
                 data-slider-selector="#slider">
            </div>
```

thì gía trị **chart.data('form-selector')** sẽ là string **'#line_chart_nova_log_form'**. Điều này có nghĩa tất cả các thẻ html có định danh html thỏa mãn string trên sẽ là form điều khiển của biểu đồ này. Gía trị lấy ví dụ ở trên là 1 id, nhưng nếu muốn có nhiều form điều khiển biểu đồ này, ta có thể sử dụng định danh là class, ví dụ **'.line_chart_nova_log_form'**. 

Do đó, câu lệnh $(chart.data('form-selector')).each(function() sẽ lần lượt áp dụng các hành động lên các form điều khiển đối tượng DOM **chart** đang xét. Khi xét 1 form bất kỳ trong số các form này, người ta sẽ lấy gía trị sau :

	 var chart_identifier = 'div[data-form-selector="' + chart.data('form-selector') + '"]';

ta có thể thấy gía trị này chính là định danh html thỏa mãn đối tượng đồ thị chúng ta đang xét. Thật vậy, xem xét ví dụ trên, đối tượng chart của chúng ta có gía trị **chart.data('form-selector')** là **'#line_chart_nova_log_form'**. Do đó 
	chart_identifier = 'div[data-form-selector="' +**'#line_chart_nova_log_form'** + '"]';
	=>chart_identifier = 'div[data-form-selector="#line_chart_nova_log_form"]';
đây chính là định danh html của đối tượng DOM **chart** chúng ta đang xét (bạn có thể xem ví dụ ở trên, do thẻ div đang xét trong ví dụ có cả 2 thuộc tính **data-chart-type="line_chart"** và data-**form-selector='#line_chart_nova_log_form'**, do đó thực chất cả 2 định danh này thẻ div này đều thỏa mãn.

Các hành động sau khi lấy được chart identifier, hay lấy được định danh của biểu đồ đang xét, đó là thêm định danh này vào dãy các định danh của các biểu đồ mà form đang xét điều khiển. 
```javascript
	if (!form.data('charts_selector')){
	            form.data('charts_selector', chart_identifier);
	          } else {
	            form.data('charts_selector', form.data('charts_selector') + ', ' + chart_identifier);
	          }
```
Điều này có nghĩa là không chỉ 1 biểu đồ có thể được nhiều form điều khiển, mà 1 form cũng có thể  điều khiển nhiều biểu đồ.

Như vậy sau khi thực hiện các bước này, kết qủa chúng ta thu được sẽ là các form trong trang view của chúng ta sẽ biết được nó sẽ điều khiển các biểu đồ nào.

việc tiếp theo chúng ta cần xét đến, đó chính là 2 hàm **bind_select_box_change(settings);**  và  **bind_datepicker_change(settings);** sẽ thực hiện những hành động gì.
```javascript
    var bind_select_box_change = function(settings) {
      delegate_event_and_refresh_charts(select_box_selector, 'change', settings);
    };

    /**
     * A helper function for catching changeDate event of form datepickers
     * connected to charts.
     */
    var bind_datepicker_change = function(settings) {
      horizon.datepickers.add(datepicker_selector);
      delegate_event_and_refresh_charts(datepicker_selector, 'changeDate', settings);
    };
```

ta thấy rằng 2 hàm này đều gọi tới hàm **delegate_event_and_refresh_charts()**. Đồng thời phương thức **bind_datepicker_change** thiết lập **datepicker** cho **datepicker_selector**
```javascript
horizon.datepickers = {
  add: function(selector) {
    $(selector).each(function () {
      var el = $(this);
      el.datepicker({
        format: 'yyyy-mm-dd',
        setDate: new Date(),
        showButtonPanel: true,
        language: horizon.datepickerLocale
      });
    });
  }
};
```
Rõ ràng, chúng ta cần biết **select_box_selector** và **datepicker_selector** là gì , chúng được định nghĩa ở phần đầu phương thức  **self.bind_commands(selector, settings);** 
```javascript
    var select_box_selector = 'select[data-line-chart-command="select_box_change"]';
    var datepicker_selector = 'input[data-line-chart-command="date_picker_change"]';
```
2 câu lệnh này định nghĩa 2 tham chiếu trên. ta có thể thấy đây là 2 string định danh các thẻ input html phù hợp với 2 định danh này, tức là có các thuộc tính **data-line-chart-command="select_box_change** và  **data-line-chart-command="date_picker_change"**
chúng ta sẽ xem xem hàm **delegate_event_and_refresh_charts()** thực hiện những hành động gì với đầu vào là 2 phương thức này.
```javascript
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

        $(form.data('charts_selector')).each(function(){
          // refresh the chart connected to changed form
          self.refresh(this, settings);
        });
      });
    };
```

ta có thể thấy, phương thức này thực hiện đăng ký cách xử lý  nếu các các sự kiện tương ứng xảy ra đối với các thẻ html có định danh phù hợp với **selector** được truyền vào. Chi tiết về hàm delegate có thể xem tại [jquery delegate](http://api.jquery.com/delegate/).
Ví dụ, khi câu lệnh này được thực hiện 
```javascript 
delegate_event_and_refresh_charts(datepicker_selector, 'changeDate', settings);
```
thì có nghĩa là, tất cả các đối tượng DOM phù hợp với string **"form"** (nghĩa là các thẻ html ```<form> ```) sẽ tìm xem bên trong nó có đối tượng con html nào phù hợp với **datepicker_selector**, tức là phù hợp với **'input[data-line-chart-command="date_picker_change"]'** hay không. Nếu có, thì các đối tượng con phù hợp với  string **datepicker_selector** sẽ được đăngký  cách xử lý sự kiện **'changeDate'**. Đây là sự kiện xảy ra khi người dùng chọn vào input 1 ngày khác bằng datepicker. Sự kiện này được xử lý như thế nào ?

```javascript
        var invoker = $(this);
        var form = invoker.parents('form').first();

        $(form.data('charts_selector')).each(function(){
          // refresh the chart connected to changed form
          self.refresh(this, settings);
        });
      });
```

ta có thể thấy cách xử lý sự kiện này được diễn ra như sau:
đầu tiên, ta xác định xem thẻ html nào bắt sự kiện: ```var invoker = $(this);```. Sau đó, chúng ta tìm xem form nào chứa thẻ bắt sự kiện.
```var form = invoker.parents('form').first();```.  Sau đó, hàm này sẽ lấy ra toàn bộ các biểu đồ mà form này đang điều khiển và refresh lại các biểu đồ này (vì chúng ta có sử dụng  **each** để duyệt qua toàn bộ các biểu đồ mà form này đang điều khiển).

Ta sẽ xem xem các biểu đồ được làm mới (refresh) như thế nào ?
```javascript
  /**
   * Function for creating chart objects, saving them for later reuse
   * and calling their refresh method.
   * @param html_element HTML element where the chart will be rendered.
   * @param settings An object containing settings of the chart.
   */
  refresh: function(html_element, settings){
    var chart = new this.LineChart(this, html_element, settings);
    /*
      FIXME save chart objects somewhere so I can use them again when
      e.g. I am switching tabs, or if I want to update them
      via web sockets
      this.charts.add_or_update(chart)
    */
    chart.refresh();
  },
```
phương thức này cũng chính là phương thức đựoc gọi khi các biểu đồ được vẽ lần đầu.

một câu hỏi được đặt ra là tại sao các  đối tượng chart cũ không bị hủy bỏ trước khi đối tượng chart mới được tạo ra ?
Lý do là các tham chiếu tới các chart chỉ là tham chiếu cục bộ, do đó sau khi hàm thực hiện xong, GC sẽ tự động hủy các đối tượng chart đi, còn phần đồ thị hiển thị trên html thì đã được nạp vào trong các thẻ html trên view rồi.

Lưu ý, là khi chart mới được tạo ra, 1 ajax sẽ được gọi lên server để lấy dữ liệu tương ứng với tham số trong các form.  Lý do là khi đối tượng LineChart được tạo ra, các lệnh sau được thực hiện:
```javascript
  LineChart: function(chart_module, html_element, settings){
    var self = this;
    var jquery_element = $(html_element);

    self.chart_module = chart_module;
    self.html_element = html_element;
    self.jquery_element = jquery_element;

    /************************************************************************/
    /*********************** Initialization methods *************************/
    /************************************************************************/
    /**
     * Initialize object
     */
    self.init = function() {
      var self = this;
      /* TODO(lsmola) make more configurable init from more sources */
      self.legend_element = $(jquery_element.data('legend-selector')).get(0);
      self.slider_element = $(jquery_element.data('slider-selector')).get(0);

      self.url = jquery_element.data('url');
      self.url_parameters = jquery_element.data('url_parameters');

      self.final_url = self.url;
      if (jquery_element.data('form-selector')){
        $(jquery_element.data('form-selector')).each(function(){
          // Add serialized data from all connected forms to url.
          if (self.final_url.indexOf('?') > -1){
            self.final_url += '&' + $(this).serialize();
          } else {
            self.final_url += '?' + $(this).serialize();
          }
        });
      }

      self.data = [];
      self.color = d3.scale.category10();

      // Self aggregation and statistic attrs
      self.stats = {};
      self.stats.average = 0;
      self.stats.last_value = 0;

      // Load initial settings.
      self.init_settings(settings);
      // Get correct size of chart and the wrapper.
      self.get_size();
    };
```
đây là lệnh init() của hàm khởi tạo đối tượng **LineChart**. Như các bạn có thể thấy, chúng ta sẽ lấy gía trị **jquery_element.data('form-selector')** để khởi tạo url cho ajax query. Truy ngược lại, ta thấy ```var jquery_element = $(html_element);``` mà html element là tham số được truyền vào khi khởi tạo đối tượng **LineChart**. Khi các bạn tiếp tục truy ngược, chúng ta sẽ thấy html_element  này chính là định danh html của các đối tượng DOM, nơi sẽ hiển thị các biểu đồ. Do đó  **jquery_element.data('form-selector')** sẽ có vai trò lấy ra tất cả các form đang điều khiển biểu đồ sẽ vẽ. Khi xét từng form này, các hoạt động sau sẽ được thực hiện :
```javascript
      self.final_url = self.url;
      if (jquery_element.data('form-selector')){
        $(jquery_element.data('form-selector')).each(function(){
          // Add serialized data from all connected forms to url.
          if (self.final_url.indexOf('?') > -1){
            self.final_url += '&' + $(this).serialize();
          } else {
            self.final_url += '?' + $(this).serialize();
          }
        });
      }
```
chúng ta có thể thấy là từng form sẽ được lấy dữ liệu các input ** \$(this).serialize();**. Sau đó dữ liệu của các form sẽ được đưa vào final url. Đến lượt mình, **final url** sẽ được chuyển tới AJAX query để gửi các input từ các form lên server. Sau đó dữ liệu phù hợp với truy vấn (input) trong form được trả về và được đối tượng chart mới (LineChart) hiển thị thành biểu đồ lên màn hình thay thế cho biểu đồ cũ. Do đó, nếu muốn tái sử dụng đối tượng LineChart trong custom js, chúng ta cần tuân theo các format để lấy các form và lấy các dữ liệu trong form khi các lệnh trên đây được chạy.

Như vậy chúng ta đã hiểu được qúa trình vẽ biểu đồ và qúa trình thiết lập các xử lý khi thay đổi các input trên form điểu khiển. Phần tiếp theo chúng ta sẽ xem các thành phần trong view của dashboard chúng ta sẽ được thiết kế như thế nào để tương thích với đoạn java script vẽ biểu đồ này.

###2.2 HTML

Để lấy ví dụ về 1 view có sử dụng line_chart trong openstack dashboard, chúng ta sẽ lấy ví dụ về dịch vụ timeline chart của ceilormeter
```html
<div id="ceilometer-stats">
  <form class="form-horizontal"
        id="linechart_general_form">
    <div class="form-group">
      <label for="stats_attr" class="col-sm-2 control-label">{% trans "Value:" %}</label>
      <div class="col-sm-2">
        <select data-line-chart-command="select_box_change"
                id="stats_attr" name="stats_attr" class="form-control">

          <option selected="selected" value="avg">{% trans "Avg." %}</option>
          <option value="min">{% trans "Min." %}</option>
          <option value="max">{% trans "Max." %}</option>
          <option value="sum">{% trans "Sum." %}</option>
        </select>
      </div>
    </div>
    <div class="form-group">
      <label for="date_options" class="col-sm-2 control-label">{% trans "Period:" %}</label>
      <div class="col-sm-2">
        <select data-line-chart-command="select_box_change"
                id="date_options" name="date_options" class="form-control">
          <option value="1">{% trans "Last day" %}</option>
          <option value="7" selected="selected">{% trans "Last week" %}</option>
          <option value="{% now 'j' %}">{% trans "Month to date" %}</option>
          <option value="15">{% trans "Last 15 days" %}</option>
          <option value="30">{% trans "Last 30 days" %}</option>
          <option value="365">{% trans "Last year" %}</option>
          <option value="other">{% trans "Other" %}</option>
        </select>
      </div>
    </div>
    <div class="form-group" id="date_from">
      <label for="date_from" class="col-sm-2 control-label">{% trans "From:" %}</label>
      <div class="col-sm-10">
        <input data-line-chart-command="date_picker_change"
               type="text" id="date_from" name="date_from" class="form-control example"/>
      </div>
    </div>
    <div class="form-group" id="date_to">
      <label for="date_to" class="col-sm-2 control-label">{% trans "To:" %}</label>
      <div class="col-sm-10">
        <input data-line-chart-command="date_picker_change"
               type="text" name="date_to" class="form-control example"/>
      </div>
    </div>

  </form>
</div>
<div class="info row detail">
  <div class="col-sm-12">
    <h4>{% trans "Statistics of all resources" %}</h4>
    <hr class="header_rule" />
    <div class="info row detail">
      <div class="col-sm-9 chart_container">
        <div class="chart"
             data-chart-type="line_chart"
             data-url="{% url 'horizon:admin:metering:samples'%}"
             data-form-selector='#linechart_general_form'
             data-legend-selector="#legend"
             data-smoother-selector="#smoother"
             data-slider-selector="#slider">
        </div>
        <div id="slider"></div>
        <div class="col-sm-3 legend_container">
          <div id="smoother" title="Smoothing"></div>
          <div id="legend"></div>
        </div>
      </div>
    </div>
  </div>
</div>
```
trong file html ở trên, chúng ta có 2 thành phần chính, 
đầu tiên là thành phần chứa data đầu vào cho biểu đồ và cũng là nơi biểu đồ được render ra,
```html
      <div class="col-sm-9 chart_container">
        <div class="chart"
             data-chart-type="line_chart"
             data-url="{% url'horizon:admin:metering:samples'%}"
             data-form-selector='#linechart_general_form'
             data-legend-selector="#legend"
             data-smoother-selector="#smoother"
             data-slider-selector="#slider">
        </div>
        <div id="slider"></div>
        <div class="col-sm-3 legend_container">
          <div id="smoother" title="Smoothing"></div>
          <div id="legend"></div>
        </div>
      </div>
```
chúng ta có thể thấy đặc trưng của thành phần này là chứa thẻ ```<div>```  có định danh phù hợp với định danh của biểu đồ đường 
```javascript
	<div class="chart"
	             data-chart-type="line_chart"
```
chúng ta nhìn vào thẻ html này, có thể thấy được các thuộc tính quan trọng sau:

 1. nguồn cấp dữ liệu cho biểu đồ : ```data-url="{% url 'horizon:admin:metering:samples'%}"```
 2. định danh của form điều khiển biểu đồ: ```data-form-selector='#linechart_general_form'```

bên cạnh đó, thành phần này chứa 1 số thuộc tính quy định về chú thích của biểu đồ (legend....)

thành phần thứ 2 chính là form điều khiển biểu đồ này:

```html
<div id="ceilometer-stats">
  <form class="form-horizontal"
        id="linechart_general_form">
    <div class="form-group">
      <label for="stats_attr" class="col-sm-2 control-label">{% trans "Value:" %}</label>
      <div class="col-sm-2">
        <select data-line-chart-command="select_box_change"
                id="stats_attr" name="stats_attr" class="form-control">

          <option selected="selected" value="avg">{% trans "Avg." %}</option>
          <option value="min">{% trans "Min." %}</option>
          <option value="max">{% trans "Max." %}</option>
          <option value="sum">{% trans "Sum." %}</option>
        </select>
      </div>
    </div>
    <div class="form-group">
      <label for="date_options" class="col-sm-2 control-label">{% trans "Period:" %}</label>
      <div class="col-sm-2">
        <select data-line-chart-command="select_box_change"
                id="date_options" name="date_options" class="form-control">
          <option value="1">{% trans "Last day" %}</option>
          <option value="7" selected="selected">{% trans "Last week" %}</option>
          <option value="{% now 'j' %}">{% trans "Month to date" %}</option>
          <option value="15">{% trans "Last 15 days" %}</option>
          <option value="30">{% trans "Last 30 days" %}</option>
          <option value="365">{% trans "Last year" %}</option>
          <option value="other">{% trans "Other" %}</option>
        </select>
      </div>
    </div>
    <div class="form-group" id="date_from">
      <label for="date_from" class="col-sm-2 control-label">{% trans "From:" %}</label>
      <div class="col-sm-10">
        <input data-line-chart-command="date_picker_change"
               type="text" id="date_from" name="date_from" class="form-control example"/>
      </div>
    </div>
    <div class="form-group" id="date_to">
      <label for="date_to" class="col-sm-2 control-label">{% trans "To:" %}</label>
      <div class="col-sm-10">
        <input data-line-chart-command="date_picker_change"
               type="text" name="date_to" class="form-control example"/>
      </div>
    </div>

  </form>
</div>
```
chúng ta có thể thấy form naỳ chứa các input có định danh phù hợp với phương thức **bind_commands()** mà chúng ta đã phân tích ở phần trên. Lưu ý là chỉ những input sau mới kích họat được các sự kiện đã đăng ký ở phương thức **bind_commands()**:

 1. Các input là các thẻ ```<select >``` có chứa thuộc tính ```data-line-chart-command="select_box_change"```. Các input này sẽ là các select bõx, được đăng ký sự kiện kích hoạt khi chúng ta chọn 1 gía trị khác trong input
 2. Các input là các thẻ  ```<input>``` có chứa thuộc tính ``` data-line-chart-command="date_picker_change" ```. Input này sẽ là các input giúp chúng ta chọn các trường có định dạng và gía trị là "date". Sự kiện kích hoạt event là khi chúng ta lựa chọn 1 ngày khác  trong lịch. (sự kiện changeDate)
 
lưu ý, các input khác nằm trong form đang xét mà không thỏa mãn các điều kiện trên sẽ không kích hoạt event. Đồng thời gía trị của các input mà form nạp vào AJAX query sẽ là string có dạng "name=value". Trong đó, **name** là thuộc tính **name** của thẻ input, **value** là gía trị của input tại thời điểm sự kiện được kích hoạt.
Ví dụ, ta có 1 form điều khiển có chứa 2 trường sau:
```html
<input data-line-chart-command="date_picker_change"
               type="text" name="date_to" class="form-control example"/>
<select data-line-chart-command="select_box_change"
                id="date_options" name="date_options" class="form-control">
...
</select>                              
```
tại thời điểm kích hoạt, input thứ nhất có gía trị là **2016-21-2**, input thứ 2 có gía trị là **7**, khi đó query gửi lên server sẽ là
```{root_url}/?date_to=2016-21-2&date_options=7```
với ```root_url``` là địa chỉ url mà chúng ta truyền vào thuộc tính 
 ``data-url``` của phần tử chart mà form điều khiển, mà trong ví dụ đang xét của chúng ta là 
 
```html
data-url="{% url 'horizon:admin:metering:samples'%}"  
```

lưu ý, những input có gía trị là None (tức rỗng) sẽ không được đưa vào AJAX query.

Khi query gửi lên server, hàm xử lý requesst tương ứng với data-url mà chúng ta xét ở trên sẽ có trách nhiệm là thu thập các parameter mà AJAX request gửi lên, xử lý và trả về dữ liệu mà biểu đồ sẽ hiển thị. Chúng ta sẽ xem cấu trúc của hàm xử lý request này là như thế nào.

###2.3 AJAX request processing in server
Như đã thảo luận ở trên, chúng ta cần phải cấp dữ liệu cho biểu đồ thông qua url. ajax sẽ gửi HTTP GET hoặc POST request lên url này kèm theo các tham số lấy từ các form điều khiển. Nhiệm vụ của phương thức xử lý request được gửi lên là tiếp nhận request, kiểm tra các gía trị đầu vào, sau đó lấy dữ liệu, định dạng và gửi về cho client.
Tiếp tục ví dụ ở phần trên, địa chỉ url cấp dữ liệu cho biểu đồ là 
```data-url="{% url'horizon:admin:metering:samples'%}"``` địa chỉ tương ứng là **{server_ip}/horizon/admin/metering/samples**, các request gửi tới địa chỉ này được phương thức  sau xử lý:
```python
class SamplesView(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        date_options = request.GET.get('date_options', None)
        date_from = request.GET.get('date_from', None)
        date_to = request.GET.get('date_to', None)
        stats_attr = request.GET.get('stats_attr', 'avg')
        group_by = request.GET.get('group_by', None)

        try:
            date_from, date_to = metering_utils.calc_date_args(date_from,
                                                               date_to,
                                                               date_options)
        except Exception:
            exceptions.handle(self.request, _('Dates cannot be recognized.'))

        if group_by == 'project':
            query = metering_utils.ProjectAggregatesQuery(request,
                                                          date_from,
                                                          date_to,
                                                          3600 * 24)
        else:
            query = metering_utils.MeterQuery(request, date_from,
                                              date_to, 3600 * 24)

        resources, unit = query.query(meter)
        series = metering_utils.series_for_meter(request, resources,
                                                 group_by, meter,
                                                 meter_name, stats_attr, unit)

        series = metering_utils.normalize_series_by_unit(series)
        ret = {'series': series, 'settings': {}}
        return HttpResponse(json.dumps(ret), content_type='application/json')
```

Chúng ta có thể thấy, phương thức trến sẽ tiếp nhận AJAX get request, lấy ra các parameter đi kèm(nếu có) sau đó lấy dữ liệu và tái cấu trúc dữ liệu rồi trả về client duới định dạng JSON. 

Một điều lưu ý ở đây là để client vẽ được biểu đồ chính xác, dữ liệu cần tuân theo định dạng tương tự như ví dự sau:
```javascript
  {
    "series": [
      {
        "name": "instance-00000005",
        "data": [
          {"y": 171, "x": "2013-08-21T11:22:25"},
          {"y": 171, "x": "2013-08-21T11:22:25"}
        ]
      }, {
        "name": "instance-00000005",
        "data": [
          {"y": 171, "x": "2013-08-21T11:22:25"},
          {"y": 171, "x": "2013-08-21T11:22:25"}
        ]
      }
    ],
    "settings": {
      'renderer': 'StaticAxes',
      'yMin': 0,
      'yMax': 100,
      'higlight_last_point': True,
      "auto_size": False, 'auto_resize': False,
      "axes_x" : False, "axes_y" : False,
      'bar_chart_settings': {
        'orientation': 'vertical',
        'used_label_placement': 'left',
        'width': 30,
        'color_scale_domain': [0, 80, 80, 100],
        'color_scale_range': ['#00FE00', '#00FF00', '#FE0000', '#FF0000'],
        'average_color_scale_domain': [0, 100],
        'average_color_scale_range': ['#0000FF', '#0000FF']
      }
    },
    "stats": {
      'average': 20,
      'used': 30,
      'tooltip_average': tooltip_average
    }
  }
 
```
chúng ta có thể thấy, ở đây dữ liệu trả về có 2 thành phần chính: 
1. Thành phần **"series"**: chứa dữ liệu của các đường biểu đồ, mỗi đường là một phần tử trong mảng **"series"**, bao gồm 2 trường là **name** : tên đường và **data**: dữ liệu của đường đó theo thời gian. Định dạng dữ liệu như ví dụ.
2. Thành phần setting: là thành phần gửi cấu hình thiết lập (các thuộc tính về đồ họa) của biểu đồ sẽ vẽ.


Sau khi tìm hiểu cách openstack tạo ra các biểu đồ, chúng ta tiến hành xây dựng biểu đồ cho dashboard của chúng ta dựa trên những gì đã có trong horizon.

##3. Xây dựng customize chart cho chart_dashboard
Chúng ta sẽ xây dựng biểu đồ cho chart_dashboard mà chúng ta đã đề cập và xây dựng khung thư mục ở phần trước. Đầu tiên, chúng ta sẽ xác định lại rõ ràng các yêu cầu đối với dashboard của chúng ta là gi :

 1. Tạo dashboard mới trong openstack_dashboard và kích hoạt dashboard này.
 2. xây dựng trên view của dashboard vừa tạo một biểu đồ cho phép theo dõi và thống kê các loại log trong file nova_log.

Các yêu cầu đối với biểu đồ:

 1. Thể hiện được số lượng log của mỗi loại log lên biểu đồ đường
 2. Điều khiển được khoảng thời gian bằng form (ngày bắt đầu, ngày kết thúc)
 3. Điều khiển được loại log sẽ hiển thị.
 4. Tự động cập nhật lại biểu đồ nếu ngày kết thúc được chọn có gía trị không xác định(rỗng) hoặc có gía trị lớn hơn gía trị của ngày hôm nay, sau mỗi 30 giây.
 5. Kiểm tra đầu vào, xử lý các ngoại lệ

Với các yêu cầu trên, ta sẽ thiết kế hệ thống bao gồm các thành phần sau:

 1. Một panel và 1 view cơ bản cho dashboard, có thể dùng TableView, TemplateView hay bất cứ View class nào để xây dựng nên view này.
 2. Mã Javascript để hiển thị biểu đồ, được nhúng vào view vừa xây dựng bên trên
 3. Một view trên server xử lý AJAX request, cấp dữ liệu cho biểu đồ.
 4. Một RESTFul service được triển khai trên controller node để  đọc và cung cấp các dữ liệu về nova-log
Chúng ta tiến hành xây dựng từng thành phần trong 4 thành phần trên.

###3.1 Xây dựng Nova-log-REST service
Đầu tiên, chúng ta cần có 1 REST servcie đặt trên  server chứa file nova-log. Service này có nhiệm vụ cung cấp các thông tin về log ra cho các client kết nối tới nó. Để xây dựng REST service này, chúng ta tạo một project Django mới. Project Django này chính là service chúng ta sẽ xây dựng. 

Kiến trúc của service này bao gồm 2 thành phần chính:
 - ReadFile class, là lớp tạo ra các đối tượng đọc file và thống kê số lượng log theo các tham số truyền vào. Khởi tạo các đối tượng trong lớp này bằng cách truyền vào vị trí file cần đọc
 - Các view method, có vai trò tiếp nhận request gửi tới từ client, lấy các tham số mà client gửi lên cùng request sau đó kiểm tra -xác thực (validation) các gía trị này. Nếu các gía trị này hợp lệ, view method sẽ tạo ra một đối tượng của lớp ReadLog. Ví dụ dưới đây là một service cho phép client nhận về mảng ghi nhận số lượng log mỗi ngày của 1 loại log (log_type), với ngày bắt đầu và ngày kết thúc do client xác định
```python
def nova_log_count_with_period_and_log_type(request):
    """
    Process request with request inputs is log_type, date_to and period

    @:parameter log_type: must be one of ("info", "debug", "other", "warning", "all")
    @:parameter date_to: string type, must be in format YY-mm-dd
    @:parameter period: string represent a int from 10 to 60

    return HTTP 400 if invalid input
    """
    log_type = request.GET.get("log_type")
    if log_type not in log_types_list:
        return HttpResponse(json.dumps({'error': "invalid log_type value"}), status=400)
    log_type = log_types_list[log_type]
    date_to = request.GET.get("date_to")
    if not check_is_valid_date(date_to):
        return HttpResponse(json.dumps({'error': "invalid date_to value"}), status=400)
    try:
        period = get_period_value(request.GET.get("period"))
    except PeriodInputException:
        return HttpResponse(json.dumps({'error': "invalid period value"}), status=400)
    log_reader = readfile.ReadLog("/home/cong/test.log")
    result = log_reader.summary_log_with_period(date_to, log_type, period, period_counts=5)
    result_json_format = [{convert_datetime_to_result_string(elements.time): elements.number_of_logs} for elements in
                          result]
    return HttpResponse(json.dumps(result_json_format), status=200)
```
Chi tiết về các service được xây dựng, các bạn có thể xem ở trong project nova_log_REST_service đi kèm bài viết này.
 
###3.2 Xây dựng custom javascript

Như chúng ta đã thấy, yêu cầu đặt ra là chúng ta phải xử lý được các sự kiện khi nguời dùng thay đối các input đầu vào. Đồng thời sau 30 giây biểu đồ phải được cập nhật 1 lần. Một điểm nữa là chúng ta cần lưu ý, đó là khi người dùng thay đổi đầu vào, bộ đếm thời gian cần phải được đặt lại. Nếu không đặt lại bộ đếm thời gian, thì sẽ không duy trì được tính chất chính xác 30 giaay cập nhật lại biểu đồ 1 lần.

Như vậy qúa trình xử lý sự kiện đầu vào thay đổi của chúng ta bao gồm 2 bước, đó là:

 1. Cập nhật lại các biểu đồ bị điều khiển bởi form chứa input bị thay đổi đầu vào.
 2. Đặt lại bộ đếm thời gian cập nhật cho các biểu đồ này.

Chúng ta thấy rằng, quy trình xử lý sự kiện của chúng ta khác so với quy trình xử lý sự kiện của horizon javascript (chúng ta có thêm bước 2 so với horizon). Do đó, chúng ta cần phải có xây dựng một qúa trình xử lý sự kiện riêng cho các biểu đồ trong dashboard của chúng ta. Phương án mà mình đề xuất để giải quyết yêu cầu này, đó là:

 1. Vẫn sử dụng class LineChart mà horizon đã xây dựng để tạo ra các đối tượng vẽ  biểu đồ.
 2. Thay thế quy trình xử lý sự kiện khi input bị người dùng thay đổi trong horizon bằng một quy trình xử lý mới. Quy trình xử lý này có nền tảng là quy trình xử lý sự kiện của horizon, và phát triển thêm bộ đếm thời gian 30 giây cập nhật lại 1 lần các biểu đồ và cho phép đặt lại các bộ đếm thời gian này khi người dùng thay đổi các input đầu vào.
 
Chúng ta có thể thấy, qua phân tích, theo phương án đề ra, thì chúng ta sẽ vẫn dùng phần lớn mã nguồn cũ của horizon để tạo biểu đồ, tuy nhiên phần xử lý sự kiện input chúng ta sẽ thay thế, đồng thời chúng ta cần tạo các bộ đếm thời gian cho biểu đồ. Để làm được điều này, chúng ta sẽ tạo ra 1 hàm mới, thiết lập các bộ đếm thời gian, và thiết lập quy trình xử lý sự kiện riêng biệt cho biểu đồ của chúng ta. Sau khi định nghĩa hàm này, việc tiếp theo là thực hiện hàm.

Học hỏi cách xử lý của horizon, mình xây dựng đối tượng **d3_chart_nova_log**. Và hàm mà chúng ta vừa đề cập ở trên trở thành phương thức **setup_line_chart()**
```javascript
  setup_line_chart: function(selector, settings) {
    var self = this;
    this.setting = settings;
    this.charts_selector = selector;
    // this.charts_selector = selector;
    self.set_timer_for_charts(selector);
    self.bind_input_events(selector, settings);
    // self.reset_timer_interval(selector);
  },
```
Phương thức này thực hiện các công việc sau: 

 1. Thiết lập các bộ đếm thời gian cho các biểu đồ **self.set_timer_for_charts(selector);**
 2. Thiết lập các quy tắc xử lý mới cho các form khi input nằm trong form kích hoạt sự kiện **self.bind_input_events(selector, settings);**

Lưu ý, selector được truyền vào phương thức chính là định danh html của các biểu đồ trên view của chúng ta. Chúng ta có thể thấy điều này trong câu lệnh thực hiện phương thức **setup_line_chart()**
```javascript
d3_chart_nova_log.setup_line_chart('div[data-chart-setup-type="nova_log"]');

```
 chúng ta có thể thấy rằng, chỉ có các biểu đồ có định danh là 
 **div[data-chart-setup-type="nova_log"]** mới chịu ảnh hưởng của phương thức mà mình xây dựng. Điều này có nghĩa là, nếu bạn muốn biểu đồ của bạn được file javascript của mình tác động vào, bạn thêm định danh trên vào biểu đồ của bạn. Những biểu đồ khác không có định danh này sẽ không bị mã nguồn của mình tác động vào.

Một điều thứ 2 cần quan tâm, đó là đối tượng **d3_chart_nova_log** mà mình vừa đề cập ở phần trên sẽ có một thuộc tính là 1 mảng các đối tượng:   **chart_timers:[],** các bạn sẽ thấy ở các phương thức sau, mình sẽ sử dụng mảng này để lưu lại các đối tượng timer của các biểu đồ. Việc lưu lại các timer trong thuộc tính của đối tượng cho phép các phương thức khác có thể tác động vào được các đối tượng timer này trong thân của các phương thức này.

Phương thức đầu tiên mà javascript sẽ thực thi là phương thức **self.set_timer_for_charts(selector);**
```javascript
  set_timer_for_charts:function (charts_selector) {
    var self = this;
    var timer_index = 0;
    console.log(charts_selector);
    $(charts_selector).each(function () {
      $(this).attr("timer_index",timer_index);
      self.chart_timers.push(new d3_chart_nova_log.ChartTimer(timer_index,this));
      timer_index++;
    })
  },
  ChartTimer: function (index,chart_identifier) {
    this.index = index;
    this.timer = setInterval(function(){
      d3_chart_nova_log.update_charts("div[timer_index="+index.toString()+"]");
    },6000);
  }
```

Phương thức này thực hiện những công việc sau: 
Lần lượt từng biểu đồ được xét tới. Các biểu đồ sẽ được thêm vào 1 thuộc tính là **timer_index**, thuộc tính này cho biết đối tượng timer của biểu đồ nằm ở đâu trong mảng các timer **chart_timers** . Số lượng các timer trong mảng timer  **chart_timers** chính là số lượng biểu đồ đang có trên view.
Mối một phần tử trong mảng timer sẽ lưu  lại tham chiếu tới timer của biểu đồ. Chúng ta có thể thấy, khi các đối tượng timer được tạo ra, javascript sẽ cấu hình để cứ sau 6000 ms = 6s thì đồ thị gắn liền với timer đó sẽ được cập nhật lại.

Như vậy, sau bước này, chúng ta đã tạo được ánh xạ từ một biểu đồ tới timer tương ứng của nó trên mảng các timer. Bước tiếp theo, chúng ta sẽ xây dựng quy tắc xử lý các sự kiện khi input đầu vào thay đổi bằng cách gọi tới phương thức **self.bind_input_events(selector, settings);**

```javascript
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
        $(form.data('nova_log_charts_selector')).each(function(){
          var chart_index =$(this).attr("timer_index");
          clearInterval(self.chart_timers[parseInt(chart_index)].timer);
          self.refresh(this, settings);
          self.chart_timers[parseInt(chart_index)].timer = setInterval(function(){
            d3_chart_nova_log.update_charts("div[timer_index="+chart_index+"]");
          },8000);
        });
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
```
Các bạn có thể thấy, quy tắc xử lý mà mình xây dựng ở đây là một phát triển của phương thức xử lý trong horizon, với 2 khác biệt chủ yếu:

 1. Để các phương thức xử lý trong horizon không tác động tới các sự kiện trong dashboard, cũng như phương pháp xử lý trong dashboard không tác dụng tới các chart khác sử dụng horizon, mình sử dụng định danh khác cho các input:

```javascript
    var select_box_selector = 'select[data-input-nova-log="select_box_change"]';
    var date_picker_selector = 'input[data-input-nova-log="date_picker_change"]';
```
2. Khi sự kiện xảy ra, ngoài việc cập nhật biểu đồ, thì timer tương ức với biểu đồ được tác động cũng được thiết lập lại gía trị mới:
```javascript
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
```

các bạn có thể thấy, ở đây lệnh **self.refresh(this, settings);** được mình sử dụng để cập nhật lại biểu đồ. Vậy tại sao ở timer mình không gọi trực tiếp tới câu lệnh này mà lại gọi tới câu lệnh **d3_chart_nova_log.update_charts("div[timer_index="+chart_index+"]");** ?

Vấn đề nằm ở chỗ, sau 6 phương thức ở trong timer sẽ đóng vai trò kiểm tra các dữ liệu đầu vào hiện tại của biểu đồ. Nếu các dữ liệu đầu vào chỉ ra là sau cập nhật biểu đồ sẽ không thay đổi ( ví dụ biểu đồ đang hiển thị một dữ liệu trong qúa khứ ) thì biểu đồ sẽ không cần phải gọi cập nhật.
```javascript
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
```
ở đây, mình thiết lập là nếu tất cả các  trường input có dạng **date_to** có gía trị nhỏ hơn thời điểm hiện tại, thì dữ liệu đang hiển thị là dữ liệu cũ, nên không cần cập nhật lại. Nhưng nếu có bất kỳ gía trị date_to nào không thỏa mãn điều trên , biểu đồ sẽ được cập nhật.

Như vậy, trên đây là phần mã nguồn javascript được mình triển khai lên custom dashboard. Việc tiếp theo chúng ta sẽ làm là xây dựng html template trên view để xác định các biểu đồ sẽ được hiển thị lên màn hình view và form điều khiển của nó:

###3.3 Thiết kế template cho view

Template cho view sẽ được xây dựng bằng cách thiết kế các thẻ div chứa biểu đồ theo định dạng mà javascript quy định, cũng như các form và các input điều khiển biểu đồ đó:
```html
  <form class="form-horizontal" id = "line_chart_nova_log_form">

      <div class="form-group">
          <label for="date_options" class="col-sm-2 control-label">{% trans "Log type:" %}</label>
          <div class="col-sm-2">
            <select data-input-nova-log="select_box_change"
                    id="log_type" name="log_type" class="form-control">
              <option value="info">{% trans "Info" %}</option>
              <option value="debug" selected="selected">{% trans "Debug" %}</option>
              <option value="error">{% trans "Error" %}</option>
              <option value="warning">{% trans "Warning" %}</option>
              <option value="other">{% trans "Other" %}</option>
              <option value="all">{% trans "All" %}</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label for="date_options" class="col-sm-2 control-label">{% trans "Period:" %}</label>
          <div class="col-sm-2">
            <select data-input-nova-log="select_box_change"
                    id="period" name="period" class="form-control">
              <option value="10">{% trans "10 seconds" %}</option>
              <option value="20" selected="selected">{% trans "20 seconds" %}</option>
              <option value="30">{% trans "30 seconds" %}</option>
            </select>
          </div>
      </div>
      <div class="form-group" id="date_to">
          <label for="date_to" class="col-sm-2 control-label">{% trans "To:" %}</label>
          <div class="col-sm-10">
            <input data-input-nova-log="date_picker_change"
                   type="text" name="date_to" class="form-control example"/>
          </div>
      </div>
  </form>

</div>
    <div class="info row detail">
      <div class="col-sm-12">
        <h4>{% trans "Statistics nova logs" %}</h4>
        <hr class="header_rule" />
        <div class="info row detail">
          <div class="col-sm-9 chart_container">
            <div class="chart"
                 data-chart-setup-type="nova_log"
                 data-chart-type="line_chart"
                 data-url="{% url "horizon:sks:line_chart_nova_log_2:samples" %}"
                 data-form-selector='#line_chart_nova_log_form'
                 data-legend-selector="#legend"
                 data-smoother-selector="#smoother"
                 data-slider-selector="#slider">
            </div>
            <div id="slider"></div>
            <div class="col-sm-3 legend_container">
              <div id="smoother" title="Smoothing"></div>
              <div id="legend"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
```
Như các bạn thấy ở trên, các input trong form điều khiển đều thỏa mãn các ràng buộc của javascript, đồng thời chart được vẽ nên cũng có định danh phù hợp với định danh trong javascript. Tất nhiên, do yêu cầu xây dựng là vẫn có thể sử dụng các biểu đồ nguyên bản của horizon, bạn vẫn có thể sử dụng các biểu đồ do horizon cung cấp mà không sợ bị mã nguồn javascript custom ảnh hưởng.

Cuối cùng, chúng ta cần xây dựng nguồn cấp dữ liệu cho biểu đồ. 

###3.4 Thiết kế nguồn cấp dữ liệu cho biểu đồ
Nguồn cấp dữ liệu cho biểu đồ sẽ là một phương thức xử lý request đặt trên horizon. phương thức này sẽ nhận các gía trị đầu vào của biểu đồ chứa trong AJAX request và kiểm tra xem chúng có hợp lệ hay không. Sau đó, phương thức này sẽ sử dụng **nova_log_api** do mình xây dựng để lấy dữ liệu về các log từ RESTFul API mà mình đã xây dựng ở phần trên. Cuối cùng, dữ liệu nhận về từ REST fult api sẽ được định dạng lại cho phù hợp với định dạng dữ liệu của biểu đồ và trả về.
Trong trường hợp lỗi xảy ra, HTTP 404 sẽ được trả về cho biểu đồ.
```python
class SamplesView(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        period = request.GET.get('period', None)
        date_to_input = request.GET.get('date_to', None)
        date_to = get_date_from_input(date_to_input)
        if date_to is None:
            return HttpResponse("invalid date to input!",
                                status=404)
        log_type = request.GET.get('log_type', None);
        if log_type not in ('info', 'debug', 'error', 'warning', 'other', 'all'):
            return HttpResponse("invalid log type!",
                                status=404)
        if not period.isdigit():
            return HttpResponse("invalid period!",
                                status=404)
        log_count_per_date_list = nova_log_api.get_nova_logs_count_with_period(
            "http://127.0.0.1:9090/nova_log/count_log_with_period/", log_type,
            date_to, period);
        if log_count_per_date_list != 'Error':
            data = []
            for index in log_count_per_date_list:
                for key, value in index.iteritems():
                    data.append({'y': value, 'x': key})
            # series , data_setting = nova_log_api.get_nova_logs_count_by_day()
            series = [{'name': log_type, 'data': data}]
        else:
             return HttpResponse(("Connection Error"), status=404)
        data_setting = {}
        time.sleep(0.5);
        ret = {'series': series, 'settings': data_setting}
        return HttpResponse(json.dumps(ret), content_type='application/json')

```

trong phương thức này, dữ liệu từ RESTFul API được lấy nhờ phương thức này:
```python 
        log_count_per_date_list = nova_log_api.get_nova_logs_count_with_period(
            "http://127.0.0.1:9090/nova_log/count_log_with_period/", log_type,
            date_to, period);
```
phương thức trên đây có đầu vào là địa chỉ của RESTful API, service mà phương thức cần, và các tham số đầu vào. nova_log_api dựa trên các thông số đầu vào này để tạo ra một HTTP GET request gửi tới RESTful service rồi nhận dữ liệu trả về  gửi cho phương thức xử lý AJAX request:
```python
def get_nova_logs_count_with_period(endpoint, log_type, date_to, period):
    method = "GET"
    if date_to != 'none':
        end_date = date_to.strftime('%Y-%m-%d')
    else:
        end_date = date_to
    endpoint += "?log_type=" + log_type + "&date_to=" + end_date + "&period=" + period
    try:
        resp, reply_body = request(endpoint, method, body={})
        status_code = resp.status_code
        if status_code in (requests.codes.ok,
                           requests.codes.created,
                           requests.codes.accepted,
                           requests.codes.no_content):
            data = json.loads(reply_body)
            return data
        else:
            return "Error"
    except ConnectionError:
        return "Error"
```


Như vậy, sau khi thiết lập xong hệ thống, biểu đồ của chúng ta sẽ hiển thị được thông tin về các log trong nova_logs, đồng thời đáp ứng được các yêu cầu đã đề ra. Bạn có thể xây dựng các dashboard khác dựa trên các ý tưởng mà mình đã trình bày khi xây dựng nên dashboard này.
