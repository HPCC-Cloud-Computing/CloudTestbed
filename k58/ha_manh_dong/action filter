###Thêm 1 action cho table


###**FilterAction**
Là 1 base class có các method để thực hiện 1 filter action trong 1 table được kế thừa từ class BaseAction.
Phương thức khởi tạo:
```sh
    def __init__(self, **kwargs):
        super(FilterAction, self).__init__(**kwargs)
        self.method = kwargs.get('method', "POST")
        self.name = kwargs.get('name', self.name)
        self.verbose_name = kwargs.get('verbose_name', _("Filter"))
        self.filter_type = kwargs.get('filter_type', "query")
        self.filter_choices = kwargs.get('filter_choices')
        self.needs_preloading = kwargs.get('needs_preloading', False)
        self.param_name = kwargs.get('param_name', 'q')
        self.icon = "search"

        if self.filter_type == 'server' and self.filter_choices is None:
            raise NotImplementedError(
                'A FilterAction object with the '
                'filter_type attribute set to "server" must also have a'
                'filter_choices attribute.')
```
Trong phương thức khởi tạo trên, chúng ta quan tâm đến thuộc tính filter_type: thuộc tính định dạng kiểu filter sẽ được thực hiện. Filter_typte có thể nhận các giá trị sau: querry (mặc định), server, fixed.

#####**1.1  Basic filter: filter_type = `"query"`**
Đây là kiểu filter mặc định.
Để sử dụng phương thức này, ta chỉ cần tạo 1 class và cho class đó kế thừa từ class FilterAction:
```sh
class MyFilterAction(tables.FilterAction):
    #your code here...
```
Sau đó, ta add thêm action vừa tạo trong class trên vào trong table bằng cách thêm vào thuộc tính table_action như trong ví dụ dưới đây:

Ví dụ: chúng ta có 1 panel về nova_log chứa file tables.py có class table như sau:
```sh
class LogNovaTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"))
    time = tables.Column("time", verbose_name=_("Time"))
    pid = tables.Column("pid", verbose_name=_("Pid"))
    level = tables.Column("level", verbose_name=_("Level"))

    class Meta(object):
        name = "lognovaapi"
        verbose_name = _("Log nova api")
        table_actions = (MyFilterAction,)
```
Để thêm action cho table, chúng ta chỉ cần khai báo tên class chứa action vào trong thuộc tính table_actions (đối với action áp dụng cho toàn bộ table) hoặc trong row_actions (đối với action áp dụng cho từng hàng trong table).

Bây giờ ta cùng tìm hiểu tại sao lại chỉ cần tạo 1 class MyFilterAction kế thừa từ class FilterAction là đã có 1 action filter.
Ta xét phương thức khởi tạo của class FilterAction(BasicAction):
```sh
    def __init__(self, **kwargs):
        super(FilterAction, self).__init__(**kwargs)
        self.method = kwargs.get('method', "POST")
        self.name = kwargs.get('name', self.name)
        self.verbose_name = kwargs.get('verbose_name', _("Filter"))
        self.filter_type = kwargs.get('filter_type', "query")
        self.filter_choices = kwargs.get('filter_choices')
        self.needs_preloading = kwargs.get('needs_preloading', False)
        self.param_name = kwargs.get('param_name', 'q')
        self.icon = "search"

        if self.filter_type == 'server' and self.filter_choices is None:
            raise NotImplementedError(
                'A FilterAction object with the '
                'filter_type attribute set to "server" must also have a '
                'filter_choices attribute.')
```
(Phương thức này được gọi tới ngay từ lúc đăng nhập vào horizon, đối với tất cả các table có action filter (???).)
Sau khi data được lấy từ phương thức get_data trong class IndexView của file vies.py thì nó được nạp vào table thì data này cũng được truyền vào hàm filter của class FilterAction:
```sh
 def filter(self, table, data, filter_string):
        """Provides the actual filtering logic.

        This method must be overridden by subclasses and return
        the filtered data.
        """
        return data
```
Do trong class MyFilterAction trên, ta chỉ kế thừa từ class FilterAction nên theo mặc định, khi ta nhập xâu kí tự là filter_string vào ô filter để filter dữ liệu trên bảng thì nó sẽ lọc ra đúng các trường dữ liệu có xâu khớp với xâu filter_string mà ta muốn filter.

Bây giờ, nếu ta muốn tạo ra 1 action filter có khả năng filter theo ý muốn thì ra phải override lại phương thức filter bên trên.
Ví dụ, ta muốn filter không phân biệt các kí tự hoa và thường trong bảng, ta có thể làm như sau:
```sh
class MyFilterAction(tables.FilterAction):
    name = "nova_log"
    def filter(self, table, logs, filter_string):
        """Really naive case-insensitive search."""
        # FIXME(gabriel): This should be smarter. Written for demo purposes.
        q = filter_string.lower()

        def comp(logs):
            if q in logs.name.lower():
                return True
            return False

        return filter(comp, logs)
```
Trong ví dụ trên, ta override lại phương thức filter, truyền vào 3 tham số là:
+ **table:** table mà chúng ta cần thêm action, ở đây table sẽ được lấy ra từ thuộc tính self.table của class BaseAction(html.HTMLElement) trong tham số **kwargs được truyền vào từ phương thức khởi tạo của class FilterAction(BaseAction). 
+ **logs:** 1 dict chứa data của table, được định nghĩa trong phương thức get_data của class IndexView trong file views.py
 
```sh
	class IndexView(tables.DataTableView):
	    # A very simple class-based view...
	    table_class = log_nova_api_tables.LogNovaTable
	    template_name = 'mydashboard/line_chart_novalog/index.html'
	
	    def get_context_data(self, **kwargs):
	        context = super(IndexView, self).get_context_data(**kwargs)
	        context['meters'] = ["INFO","WARNING","ERROR","All"]
	        return context
	
	    def get_data(self):
	        dataLog = readFile('/home/ha/Desktop/log.txt')
	        logs =  dataLog[3]
	
	        print (logs)
	        return logs
```
+**filter_string:** chuỗi string mà chúng ta nhập vào khung filter.


#####**1.2  Choice filter: filter_type = `"server"`**
Đây là dạng filter lọc theo từng cột trong table.

![choice filter](http://i.imgur.com/bDFaYQq.png)

Để sử dụng loại filter này, ta phải set cho biến filter_type = "server". Và khi filter_type = "server" thì ta bắt buộc phải khai báo biến filter_choices: là 1 tuple chứa các tubles khác là các option choice. Các tuples bên trong có dạng (string,string,boolean) lần lượt là các tham số tương ứng với (tham số của cột, verbose name - tên sẽ hiển thị lên giao diện, True - False). Nếu để biến boolean là true nghĩa là được áp dụng như là 1 thuộc tính của API query trong API request. Nhưng theo mặc định, thuộc tính này k được cung cấp nên nếu ta để là False thì sẽ k thể thực hiện filter đối với option đó được.
Ta cùng xem code trong ví dụ dưới về tạo 1 class filter với filter_type = "server":
```sh
class FilterLog(tables.FilterAction):
    name = "dong_novalog_filter"
    verbose_name = "filter_server"
    filter_type = "server"
    filter_choices = (("id", _("id ="), True),
                      ("time", _("time ="), True),
                      ("pid", _("process id ="), True),
                      ("level", _("level ="), True))

class LogNovaTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"))
    time = tables.Column("time", verbose_name=_("Time"))
    pid = tables.Column("pid", verbose_name=_("Pid"))
    level = tables.Column("level", verbose_name=_("Level"))

    class Meta(object):
        name = "lognovaapi"
        verbose_name = _("Log nova api")
        table_actions = (FilterLog,)
```
Sau khi thiết lập xong action, bây giờ ta phải xây dựng 1 hàm trong file views.py để lấy được tên cột và giá trị mà ta sẽ dùng để filter như sau:
```sh
    def get_filters(self):
        filters = {}
        filter_action = self.table._meta._filter_action
        if filter_action:
            filter_field = self.table.get_filter_field()
            if filter_action.is_api_filter(filter_field):
                filter_string = self.table.get_filter_string()
                if filter_field and filter_string:
                    filters[filter_field] = filter_string

        return filters
```
Đầu tiên, hàm trên sẽ kiểm tra xem table đó có filter action chưa bằng lệnh `if filter_action` . Nếu table đó có filter action thì biến filter_action sẽ khác null, khi đó sẽ thực hiện các câu lệnh bên trong if để lấy ra filter_field chính là option cột mà chúng ta chọn để filter, và filter_string là xâu mà chúng ta nhập vào để filter. 2 giá trị này sẽ được đưa vào 1 dict là filters tương ứng với cặp key-value:  `filters[filter_field] = filter_string`

Bây giờ khi đã lấy được các giá trị mà chúng ta muốn filter, ta cần xây dựng lại hàm get_data để cật nhật lại data cho table để phù hợp với kết quả ta filter được.
Ví dụ:
```sh
    def get_data(self):
        dataLog = readFile('/home/ha/Desktop/log.txt')
        logs =  dataLog[3]

        string_filter = self.get_filters()
        keys = string_filter.keys()
        if keys:
            key = keys[0]
            print "key: " + key
            print "String filter: " + string_filter[key]
            temp = []
            for log in logs:
                if(isinstance(log.getArg(key),int)):
                    t = str(log.getArg(key))
                    if (string_filter[key] == t):
                        temp.append(log)
                elif (string_filter[key] == log.getArg(key)):
                    temp.append(log)
            return temp

        # print (logs)
        return logs
```
Trong đoạn code trên, ta khai báo 1 biến = giá trị trả về của hàm get_filters() bên trên. Sau đó ta kiểm tra nếu như hàm fget_filters() return về 1 giá trị null nghĩa là không thực hiện filter thì ta bỏ qua,return lại data bình thường, còn nếu là khác null nghĩa là ta đã chọn option và nhập giá trị vào ô filter thì ta sẽ thực hiện lọc các hàng thỏa mãn với giá trị filter đó và return lại 1 list các data mới để đưa vào table.

#####**1.3  Fixed filter: filter_type = `"fixed"`**
Click vào [đây](https://github.com/cloudcomputinghust/CloudTestbed/blob/master/k58/nguyen_van_duc/Docker_in_Horizon.md#fix-button-filter) để ra tài liệu reference 





