Bài viết này sẽ bao gồm các nội dung sau:
- Cài đặt Horizon
- Tạo dashboard
- Tạo panel
- Tạo Table với DataTable
- Tạo View class với DataTableView và MultiTableView

# Cài Đặt Horizon
**Yêu cầu hệ thống**

 - Python 2.7
 - Django 1.7 hoặc 1.8
 - Yêu cầu tối thiểu các dịch vụ đang chạy trên OpenStack sau:
     - Nova: OpenStack Compute
     - Keystone: OpenStack Identity
     - Glance: OpenStack Image service
     - Neutron: OpenStack Networking (unless nova-network is used)

**Cài đặt**

Cài đặt các gói bắt buộc bằng câu lệnh sau:

    > sudo apt-get install git python-dev python-virtualenv libssl-dev libffi-dev
Sau khi cài đặt xong môi trường, thực hiện clone horizon từ github bằng câu lệnh sau:

    > git clone https://github.com/openstack/horizon.git

mặc định comand này sẽ clone về bản master, để clone một phiên bản horizon khác sử dụng thêm flag -b. Ví dụ, clone phiên bản mitaka:

    > git clone -b stable/mitaka https://github.com/openstack/horizon.git

Sau đó, thực hiện câu lệnh sau để build virtualenv (virtualenv là nơi mà các phụ thuộc python cho horizon được cài đặt):

    > cd horizon
    > ./run_tests.sh
Tiếp theo, thực hiện thiết lập cấu hình cho horizon để refer đến host đang triển khai OpenStack (Horizon và OpenStack có thể nằm trên cùng một host). Thực hiện câu lệnh sau:

    > cp openstack_dashboard/local/local_settings.py.example openstack_dashboard/local/local_settings.py

Trong file 'openstack_dashboard/local/local_settings.py' Thay đổi trường **OPENSTACK_HOST** để refer horizon đến host triển khai OpenStack (Theo mặc định, trường này được thiết lập là 127.0.0.1 có nghĩa là Horizon và OpenStack được triển khai trên cùng một host).

Sau đó, thực hiện update file openstack_dashboard/local/local_settings.py bằng câu lệnh sau:

    > python manage.py migrate_settings

Cuối cùng, sử dụng câu lệnh sau để chạy horizon:

    > ./run_tests.sh --runserver localhost:8000

Có thể thay đổi port để tránh bị trùng với các tiến trình khác. Ví dụ, mặc định chạy DevStack sẽ sử dụng port 8000, thì phải đổi port chạy horizon sang gía trị khác.

Bây giờ chúng ta sẽ bắt đầu customize horizon.

# Tạo Dashboard sử dụng horizon
---------

Để tạo một dashboard, horizon cung cấp một câu lệnh để tạo ra một cấu trúc thư mục mặc định của Dashboard cho developer. Chạy câu lệnh sau trên cùng thư mục với runtest.sh, nó sẽ tạo ra tất cả cấu trúc thư mục của một dashboard bạn cần:

    > mkdir openstack_dashboard/dashboards/mydashboard
    > ./run_tests.sh -m startdash mydashboard \
              --target openstack_dashboard/dashboards/mydashboard

 Sau khi tạo xong dashboard, thực hiện câu lệnh sau để tạo ra một panel bên trong dashboard vừa được tạo ra:
 

    > mkdir openstack_dashboard/dashboards/mydashboard/mypanel
    > ./run_tests.sh -m startpanel mypanel \
               --dashboard=openstack_dashboard.dashboards.mydashboard \
               --target=openstack_dashboard/dashboards/mydashboard/mypanel
Kết thúc hai câu lệnh trên, bạn sẽ thu được một cấu trúc cây thư mục như sau:

    mydashboard
    ├── dashboard.py
    ├── dashboard.pyc
    ├── __init__.py
    ├── __init__.pyc
    ├── mypanel
    │   ├── __init__.py
    │   ├── panel.py
    │   ├── templates
    │   │   └── mypanel
    │   │       └── index.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── static
    │   └── mydashboard
    │       ├── css
    │       │   └── mydashboard.css
    │       └── js
    │           └── mydashboard.js
    └── templates
        └── mydashboard
            └── base.html
# Tạo Panel 

Để thực hiện các bước này, bắt buộc bạn phải hoàn thành các bước trên.
Sau bước trên, ta thu được thư mục *mypanel* có cấu trúc như sau:

    mypanel
     ├── __init__.py
     ├── models.py
     ├── panel.py
     ├── templates
     │   └── mypanel
     │     └── index.html
     ├── tests.py
     ├── urls.py
     └── views.py

### Định nghĩa panel
Trước khi đi vào định nghĩa panel, chúng ta cần hiểu được dashboard là gì trên horizon? panel là gì? Cụ thể, dashboard chứa các panel

Panel chứa các tab

Để định nghĩa panel, mở file *panel.py* với nội dung mặc định như sau:
```python
    from django.utils.translation import ugettext_lazy as _
    
    import horizon
    
    from openstack_dashboard.dashboards.mydashboard import dashboard
    
    
    class Mypanel(horizon.Panel):
        name = _("Mypanel")
        slug = "mypanel"
    
    
    dashboard.Mydashboard.register(Mypanel)
```
File *panel.py* được sử dụng để đăng ký với dashboard một panel. Bên trong file này, khởi tạo một lớp kế thừa từ class *horion.Panel*, với tên của panel hiển thị trên giao diện được chứa trong thuộc tính *name* và một thuộc tính *slug* là tên được dùng để gọi đến panel này trong quá trình code( bạn có thể thay đổi gía trị của các thuộc tính này) . 
Mở file *dashboard.py*, với các nội dung mặc định sau:
```python
    from django.utils.translation import ugettext_lazy as _

    import horizon
    
    
    class Mydashboard(horizon.Dashboard):
       name = _("Mydashboard")
       slug = "mydashboard"
       panels = ()           # Add your panels here.
       default_panel = ''    # Specify the slug of the dashboard's default panel.
    
    horizon.register(Mydashboard)
```
Thuộc tính *panels* sẽ list ra các group panel được chứa trong dashboard này. Các thành phần trong thuộc tính *panel* này sẽ được mặc định tìm đến file *panel.py* trong thư mục tương ứng.
Mỗi Dashboard có thể có nhiều group panel, mỗi group panel có thể có nhiều panel. Vì vậy, trước tiên cần tạo ra một lớp kế thừa từ lớp *horizon.PanelGroup* để đăng ký một group panel. 

    class Mygroup(horizon.PanelGroup):
        slug = "mygroup"
        name = _("My Group")
        panels = ('mypanel',)
Thuộc tính *panels* sẽ list ra các panel sẽ được chứa trong group panel này.
Sau khi định nghĩa xong class *Mygroup*, thực hiện đăng ký group panel này đến dashboard bằng cách thêm vào thuộc tính *panels* trong class MyDashboard tên của lớp *Mygroup*.  Khi đó, class MyDashboard sẽ thu được như sau:

```python
    from django.utils.translation import ugettext_lazy as _

    import horizon
    
    class Mygroup(horizon.PanelGroup):
        slug = "mygroup"
        name = _("My Group")
        panels = ('mypanel',)
    
    class Mydashboard(horizon.Dashboard):
        name = _("My Dashboard")
        slug = "mydashboard"
        panels = (Mygroup,)  # Add your panels here.
        default_panel = 'mypanel'  # Specify the slug of the default panel.
    
    horizon.register(Mydashboard)
```
Thuộc tính *default_panel* sẽ quy định panel nào sẽ xuất hiện đầu tiên khi click chọn dashboard.

Như vậy là chúng ta đã tạo ra được một dashboard, đăng ký được một group panel chứa một panel.

# Table

Horizon cung cấp thành phần [horizon.table](http://docs.openstack.org/developer/horizon/ref/tables.html#module-horizon.tables) để tạo ra một API tiện lợi cho việc xây dựng dữ liệu hiển thị và giao diện. Các thành phần chính của API này tập trung vào 3 phần: DataTables, Actions và Class-bass Views

### DataTables

Thành phần [tables.DataTables](http://docs.openstack.org/developer/horizon/ref/tables.html#horizon.tables.DataTable) được sử dụng để định nghĩa tất cả các trường dữ liệu và hành động liên kết cho bảng. 
Để định nghĩa một bảng, thực hiện những bước cơ bản sau:

 - Tạo một subclass của tables.DataTables
 - Định nghĩa các column cho bảng
 - Tạo một inner Meta class chứa các tuỳ chọn cụ thể của bảng
 - Định nghĩa các hành động tác động lên bảng và liên kết các hành động đến bảng.

Đây là một ví dụ về định nghĩa một table với thông tin về user của OpenStack. Class này được định nghĩa trong file *tables.py* trong thư mục *mypanel* đã tạo ra ở trên:
```python
    class UsersTable(tables.DataTable):
    STATUS_CHOICES = (
        ("true", True),
        ("false", False)
    )
    name = tables.Column('name',link="horizon:identity:users:detail",verbose_name=_('User Name'),
                         form_field=forms.CharField(required=False),update_action=UpdateCell)
    description = tables.Column(lambda obj: getattr(obj, 'description', None),verbose_name=_('Description'),
                                hidden=KEYSTONE_V2_ENABLED,
                                form_field=forms.CharField(
                                    widget=forms.Textarea(attrs={'rows': 4}),
                                    required=False),
                                update_action=UpdateCell)
    email = tables.Column(lambda obj: getattr(obj, 'email', None),
                          verbose_name=_('Email'),
                          form_field=forms.EmailField(required=False),
                          update_action=UpdateCell,
                          filters=(lambda v: defaultfilters
                                   .default_if_none(v, ""),
                                   defaultfilters.escape,
                                   defaultfilters.urlize)
                          )
    # Default tenant is not returned from Keystone currently.
    # default_tenant = tables.Column('default_tenant',
    #                                verbose_name=_('Default Project'))
    id = tables.Column('id', verbose_name=_('User ID'),
                       attrs={'data-type': 'uuid'})
    enabled = tables.Column('enabled', verbose_name=_('Enabled'),
                            status=True,
                            status_choices=STATUS_CHOICES,
                            filters=(defaultfilters.yesno,
                                     defaultfilters.capfirst),
                            empty_value="False")

    if api.keystone.VERSIONS.active >= 3:
        domain_name = tables.Column('domain_name',
                                    verbose_name=_('Domain Name'),
                                    attrs={'data-type': 'uuid'})

    class Meta(object):
        name = "users"
        verbose_name = _("Users")
        row_actions = (EditUserLink, ChangePasswordLink, ToggleEnable,DeleteUsersAction)
        table_actions = (UserFilterAction, CreateUserLink, DeleteUsersAction)
        row_class = UpdateRow
```
Chúng ta sẽ đi phân tích từng phần trong đoạn code trên.
Mỗi thuộc tính class trong lớp (hay là mỗi cột trong bảng) phải được đại diện bằng một lớp được gọi là tables.Column. Lớp này sẽ cung cấp những tùy chọn đến cột trong bảng.  

Có rất nhiều tùy chọn được cung cấp cho các cột của table. Ở đây, mình chỉ giai thích những tùy chọn hay sử dụng và được sử dụng trong ví dụ này, để tìm hiểu chi tiết thì tham khảo [tables.DataTable](http://docs.openstack.org/developer/horizon/ref/tables.html#horizon.tables.DataTable). 
Các tùy chọn được cung cấp trong ví dụ trên được giai thích cụ thể như sau: 
 - *transform*: (tham số đầu tiên trong cột *name*) Là tên của thuộc tính trong lớp dữ liệu cơ bản. Tên này được dùng để ánh xạ đến thuộc tính.
 - *verbose_name*: Tên được sử dụng để hiển thị trên  hàng tiêu đề của bảng. Theo mặc đinh, giá trị của thuộc tính này là gía trị của *transform* với ký tự ban đầu của mỗi từ được in hoa, nếu không có *tranform* thì mặc định là rỗng.
 - *link*: chứa url sẽ được gọi đến khi click vào gía trị của column này. Tương tự như thẻ *a* trong html
 - *form_field*: là một form cho phép thay đổi giá trị của cột ngay trên dòng. Sau khi thiết lập thuộc tính này, khi hover chuột qua column sẽ xuất hiện biểu tượng cho phép thay đổi giá trị thuộc tính.
 - *update_action*:  lớp kế thừa từ lớp tables.actions.UpdateAction, phương thức update_cell của lớp này sẽ lưu lại các giá trị thay đổi trong trường *form_field* trên giao diện và phương thức *get_data()* cuả lớp kế thừa tables.Row được kết nối đến để lấy dữ liệu từ form_field này.
 - *hidden*: Boolean xác định có hay không cột này được hiển thị khi render bảng. Mặc định là *False*.
 - *attrs*: Một list các chuỗi thuộc tính html mà sẽ được thêm vào cột này.
 - *filters*: dùng để thay đổi cách hiển thị các giá trị của cột trên giao diện. ví dụ như cột *cpu* chỉ trả về giá trị số như 1024 và chúng ta muốn hiển thị lên giao diện là 1024 MB thì sẽ sử dùng filters. Có thẻ sử dụng filters theo 2 cách:
 Thứ nhất: Tự định nghĩa hàm filters. vd:
 ```python

    def add_unit(val){
        return val+"GB";
    }
    ...
    cpu = tables.Column("cpu",filters=(add_unit,))
```
Thứ hai: sử dụng các hàm được định nghia sẵn trong django là [https://github.com/django/django/blob/master/django/template/defaultfilters.py](https://github.com/django/django/blob/master/django/template/defaultfilters.py). Ví dụ:
```python
    form_field=forms.EmailField(required=False),
                          update_action=UpdateCell,
                          filters=(lambda v: defaultfilters
                                   .default_if_none(v, ""),
                                   defaultfilters.escape,
                                   defaultfilters.urlize)
                          )
 ```
 - Note:  filters là một tuple chứa các hàm và được thực hiện theo thứ tự từ trái qua phải. Kết quả trả về của hàm này sẽ là input của hàm tiếp theo. Nếu filter chỉ chưa một hàm thì sẽ có dạng như sau:
```python
    filters=(add_unit,)
```
 -*status*: Boolean xác định có hay không một status đại diện cho cột này.
 -*status_choices*: Một tuple chứa cac tuple khác đại diện cho các giá trị có sẵn trong cột status. Xem xét đoạn code trong ví dụ trên:
```python
    STATUS_CHOICES = (
        ("true", True),
        ("false", False)
    )
    ...
    enabled = tables.Column('enabled', verbose_name=_('Enabled'),
                            status=True,
                            status_choices=STATUS_CHOICES,
                            filters=(defaultfilters.yesno,
                                     defaultfilters.capfirst),
                            empty_value="False")
                            
```
Cột *enable* thiết lập tùy chọn *status* bằng True, cho biết cột này sẽ được đại diện bằng một status (vd: enable/disable, active/deactive,...). Sau đó, tùy chọn *status_choices* cho biết cột này chỉ được mang hai gía trị "True" hoặc "False". Cụ thể là gía trị của cột này sẽ chỉ có thể được nhận là *true* hoặc *false* và sẽ được hiển thị lên giao diện với giá tri *True* hay *False* tương ứng.
 Tiếp theo, tùy chọn *filters* sẽ thay đổi gía trị hiển thị của cột sang giá trị *yes* hoặc *no* tương ứng với *True* hoặc *False* lên giao diện bằng hàm *defaultfilters.yesno* và in hoa chữ cái đầu tiên bằng hàm *defaultfilters.capfirst*

 -*empty_value*: giá trị đại diện cho cột khi không có dữ liệu. Mặc định là "-".

##inline editing##

 Trong trường hợp bạn muốn thay đổi giá trị của một phần tử ngay trên giao diện. Horizon cung cấp một kỹ thuật gọi là inline editing. 
 Để xây dựng inline editing, chúng ta cần phải định nghĩa tùy chon *form_field* trên các cột muốn thay đổi. *form_field* là một instance của django.form.field, vì vậy chúng ta có thể sử dụng validation của django. Dưới đây là một ví dụ:
 
```python
    description = tables.Column(lambda obj: getattr(obj, 'description', None),
                                verbose_name=_('Description'),
                                hidden=KEYSTONE_V2_ENABLED,
                                form_field=forms.CharField(
                                    widget=forms.Textarea(attrs={'rows': 4}),
                                    required=False),
                                update_action=UpdateCell)
```
Sau khi định nghĩa tùy chọn *form_field*, chúng ta cần liên kết các lớp *UpdateRow* và *UpdateCell* đến bảng.
Lớp *UpdateRow* là một subclass cuả lớp tables.Row. Định nghĩa phương thức get_data() của lớp này sẽ này đóng vai trò lấy dữ liệu của tất cả các phần tử của hàng. ví dụ:
```python
    class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, user_id):
        user_info = api.keystone.user_get(request, user_id, admin=True)
        return user_info
```
Lớp *UpdateCell* là một subclass của tables.UpdateAction. Định nghĩa phương thức update_cell()  của lớp này sẽ thực hiện thay đổi và cập nhật dữ liệu của các phần tử của hàng. Lớp *UpdateCell* được định nghĩa trong các column của bảng với tùy chọn *update_cell* = UpdateCell. Vậy, một column sẽ có một phương thức update của chính nó.
```python
    class UpdateCell(tables.UpdateAction):
    # Determines whether given cell or row will be inline editable
    # for signed in user.
    def allowed(self, request, user, cell):
        return api.keystone.keystone_can_edit_user() and \
            policy.check((("identity", "identity:update_user"),),
                         request)

    def update_cell(self, request, datum, user_id,
                    cell_name, new_cell_value):
        try:
            user_obj = datum
            setattr(user_obj, cell_name, new_cell_value)
            if ((not new_cell_value) or new_cell_value.isspace()) and \
                    (cell_name == 'name'):
                message = _("The User Name field cannot be empty.")
                messages.warning(request, message)
                raise django_exceptions.ValidationError(message)
            kwargs = {}
            attr_to_keyword_map = {
                'name': 'name',
                'description': 'description',
                'email': 'email',
                'enabled': 'enabled',
                'project_id': 'project'
            }
            for key in attr_to_keyword_map:
                value = getattr(user_obj, key, None)
                keyword_name = attr_to_keyword_map[key]
                if value is not None:
                    kwargs[keyword_name] = value
            api.keystone.user_update(request, user_obj, **kwargs)

        except horizon_exceptions.Conflict:
            message = _("This name is already taken.")
            messages.warning(request, message)
            raise django_exceptions.ValidationError(message)
        except Exception:
            horizon_exceptions.handle(request, ignore=True)
            return False
        return True

```  
Sau khi định nghĩa xong các cột, chúng ta định nghĩa lớp *meta* nhắm cung câp metadata cho table.
 ```python

       class Meta(object):
            name = "users"
            verbose_name = _("Users")
            row_actions = (EditUserLink, ChangePasswordLink, ToggleEnabled,
                           DeleteUsersAction)
            table_actions = (UserFilterAction, CreateUserLink, DeleteUsersAction)
            row_class = UpdateRow
```
Trong lớp metadata này có các tùy chonj sau:

 - name: Tên của bảng được sử dụng để gọi đến bảng trong qúa trình lập trinh.
 - verbose_name: Tên hiển thij của bảng.
 - row_actions : danh sách các action sẽ xử lý các nhiệm vụ chẳng hạn như chỉnh sửa, xóa đối tượng. Action naỳ chỉ thực hiện trên một đối tượng duy nhất tại một thời điểm. Các action này phải được định nghĩa để xử lý các nhiệm vụ và phần xử lý này sẽ được nói đến trong phần sau.
 - table_actions: tương tự như row_actions, là danh sách các action sẽ xử lý các nhiệm vụ như xóa, tạo đối tượng. Nhưng các action naỳ thực hiện trên nhiều đối tượng cùng một thời điểm.
 - row_class: xác định lớp được dùng cho việc render các hàng của bảng này. trong ví dụ trên, row_class bằng updateRow, hàm updateRow này có nhiệm vụ là lấy dữ liệu của hàng phục vụ cho mục đích thay đổi nội dòng (inline editing) trên các phần tử của một hàng trong bảng. Một ví dụ của hàm updateRow như sau:
```python
        class UpdateRow(tables.Row):
            ajax = True
        
            def get_data(self, request, user_id):
                user_info = api.keystone.user_get(request, user_id, admin=True)
                return user_info
```
Phương thức get_data() của hàm này sẽ lấy tất cả dữ liệu của các thành phần trong hàng để phục vụ mục đích update nội dung của hàng.
 - multi_select: gía trị Boolean xác định có hay không tạo ra một cột cho phép hành động chọn một hay nhiều các cột.

Vậy là chúng ta đã định nghĩa xong các cột cũng như metadata cho table.
Trong phần định nghĩa này, chúng ta nên chú ý vào hai phần, đó là filters và inline editing. Filters dùng để lọc dữ liệu hiển thị lên giao diện, inline editing dùng để chỉnh sửa gía trị của phần tử ngay trên giao diện.
Sau khi đã định nghĩa được table, chúng ta cần định nghĩa một lớp view để điểu khiển việc hiển thị table lên giao diện.

# Class-Based Views
--------
Một trong thành phần cốt lõi của *horizon.tables* là class-base view, thành phần này được cung cấp để làm việc dễ dàng hơn với *DataTable* trong việc hiển thị nội dung bảng lên giao diện.
 Horizon.tables bao gồm hai lớp view cơ bản là: DataTableView và MultiTableView. Trong đó, DataTableView được dùng trong trường hợp chỉ có 1 table trong panel, còn MultiTableView được sử dụng trong trường hợp muốn hiển thị 2 table hoặc nhiều trong cùng một panel (chưa xét đến trường hợp trong panel có nhiều tabs).
 ## DataTableView ##
 
Để sử dụng DataTableView, chúng ta định nghĩa một lớp là subclass của DataTableView. Sau đó, chúng ta phải thực hiện tối thiểu 3 yêu cầu sau :

 - get_data(): override phương thức này để lấy dữ liệu cho bảng. Dữ liệu này là một list các đối tượng đại diện cho bảng.
 - table_class: thiết lập thuộc tính này là lớp DataTable muốn hiển thị lên giao diện.
 - template_name: thuộc tính này xác định template sẽ được dùng để show dữ liệu

Bây giờ, chúng ta hãy bắt đầu định nghĩa lớp IndexView cho Datable đã được định nghĩa ở phần trước. Mở file *views.py* trong thư mục *mypanel* và thay đổi nội dung của file này với nội dung như sau:
```python
    
from openstack_dashboard import api
from openstack_dashboard import policy

from openstack_dashboard.dashboards.identity.users \
    import forms as project_forms
from openstack_dashboard.dashboards.identity.users \
    import tables as project_tables

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = project_tables.UsersTable
    template_name = 'identity/users/index.html'
    page_title = _("Users")

    def get_data(self):
        users = []

        if policy.check((("identity", "identity:list_users"),),self.request):
            domain_context = api.keystone.get_effective_domain_id(self.request)
            try:
                users = api.keystone.user_list(self.request,domain=domain_context)
            except Exception:
                exceptions.handle(self.request,_('Unable to retrieve user list.'))
        elif policy.check((("identity", "identity:get_user"),),self.request):
            try:
                user = api.keystone.user_get(self.request,self.request.user.id)
                users.append(user)
            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user information.'))
        else:
            msg = _("Insufficient privilege level to view user information.")
            messages.info(self.request, msg)

        if api.keystone.VERSIONS.active >= 3:
            domain_lookup = api.keystone.domain_lookup(self.request)
            for u in users:
                u.domain_name = domain_lookup.get(u.domain_id)
        return users
```
Sau khi định nghĩa xong class IndexView với các yều cầu tối thiểu trên, Chúng ta phải chỉnh sửa file*index.html* trong thư mục theo đường dẫn được định nghĩa trong thuộc tính *template_name* với nội dung như sau:
```python
    {% extends 'base.html' %}
    {% load i18n %}
    {% block title %}{% trans "Users" %}{% endblock %}
    
    {% block page_header %}
      {% include "horizon/common/_domain_page_header.html" with title=page_title %}
    {% endblock page_header %}
    
    {% block main %}
        {{ table.render }}
    {% endblock %}
```python
Chú ý phần main, chúng ta thêm vào câu lệnh *table.render*. Câu lệnh này có nhiệm vụ tạo ra bảng với nội dung là được lấy từ dữ liệu trả về của phương thức *get_data()* trong class IndexView liên kết với nó.
Tiếp theo, Chúng ta cần đăng ký url cho IndexView vừa tạo ra . Để đăng ký, thêm vào file *urls.py* trong cùng thư mục chứa file *views.py* với nội dung sau:
```python
    
    from django.conf.urls import url
    
    from openstack_dashboard.dashboards.mydashboard.mypanel import views
    
    urlpatterns = [
        url(r'^$', views.IndexView.as_view(), name='index'),
    ]
```
Như trên đã giải thích, chúng ta sẽ có khai báo thuộc tính *table_class*, *template_name* và override phương thức  get_data(). Nhưng có một câu hỏi đặt ra là: Làm thế nào để dữ liệu có thể hiển thị lên giao diện chỉ với một câu lệnh *table.render* ? Vì sao dữ liệu render lại là dữ liệu của phương thức get_data() mà không phải là cuả một phương thức khác?

**Xử lý request**

Để trả lời câu hỏi trên, chúng ta sẽ xem xét quá trình xử lý một request từ client cho việc hiển thị nội dung bảng user trên giao diện. Cụ thể như sau:

Đầu tiên, Khi một request gửi đến yêu cầu hiển thị bảng các user. Request này sẽ được xem xét để tìm đến đúng phương thức xử lý. Việc này sẽ dựa trên url đã được đăng ký của các View trong file *urls.py*.
Xét file *urls.py* ta có:
```python
    from openstack_dashboard.dashboards.mydashboard.mypanel import views
    
    urlpatterns = [
        url(r'^$', views.IndexView.as_view(),name='index'),
        ]
```
Như vậy, request sẽ được xử lý bởi phương thức as_view() của IndexView. Chúng ta sẽ đi đến phương thức as_view():
```python
    def as_view(cls, **initkwargs):
        """
        Main entry point for a request-response process.
        """
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            self.request = request
            self.args = args
            self.kwargs = kwargs
            return self.dispatch(request, *args, **kwargs)

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.dispatch, assigned=())
        return view
```
Phương thức as_view() này lại trả về phương thức view() để tiếp tục xử lý request. Hãy xem xét phương thức view():
```python
    def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            self.request = request
            self.args = args
            self.kwargs = kwargs
            return self.dispatch(request, *args, **kwargs)
```
Phương thức này sẽ khởi tạo đối tượng view **cls(**initkwargs)**. Sau đó, gán các tham số request, args và kwargs vào các thuộc tính của đối tượng này. Hàm view trả về phương thức dispatch() của đối tượng view vừa tạo ra. 
Xem xét phương thức này:
```python
    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
```
Phương thức dispatch() trả về phương thức handler(). Cụ thể, handler là sẽ được khởi tạo như sau:
```python
    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
```
Câu lệnh này sẽ lấy một thuộc tính từ self. Ở đây là đối tượng IndexView. 
Thuộc tính này là request.method.lower(), trong đó: request.method là GET or POST và sau đó dùng phương thức lower() để lower case GET hoặc POST về thành "get" hoặc "post"
Lúc này, handler chính là phương thức get() hoặc post() được định nghĩa của IndexView. Trong trường hợp request hiển thị biểu đồ, thì handler ở đây sẽ là phương thức get(). 
Như vậy, phương thức dispatch() trả về phương thức get() của IndexView. Ta hãy xem xét phương thức get() này:
```python
    def get(self, request, *args, **kwargs):
        handled = self.construct_tables()
        if handled:
            return handled
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
```
Phương thức này gọi tới phương thức construct_tables() của IndexView
Xem xét construct_tables():
```python
    def construct_tables(self):
        tables = self.get_tables().values()
        # Early out before data is loaded
        for table in tables:
            preempted = table.maybe_preempt()
            if preempted:
                return preempted
        # Load data into each table and check for action handlers
        for table in tables:
            handled = self.handle_table(table)
            if handled:
                return handled

        # If we didn't already return a response, returning None continues
        # with the view as normal.
        return None
```
Câu lệnh tables = self.get_tables().values(); trả về danh sách các table có trong IndexView. Sau đó, xử lý tất cả các table với phương thức handle_table(table).
Phương thức handle_table kế thừa từ lớp MultiTableMixin:
```python
    def handle_table(self, table):
        name = table.name
        data = self._get_data_dict()
        self._tables[name].data = data[table._meta.name]
        self._tables[name]._meta.has_more_data = self.has_more_data(table)
        self._tables[name]._meta.has_prev_data = self.has_prev_data(table)
        handled = self._tables[name].mayableultibe_handle()
        return handled
```python
Như ta có thể thấy, data có thể được lấy từ phương thức self._get_data_dict().
Từ đây, chúng ta sẽ có 2 trường hợp: IndexView kế thừa từ DataTableView và IndexView kế thừa từ MultiTableView. Trong phần này, mình sẽ nói đến trường hợp thứ nhất. Còn trường hợp 2 thì phần sau khi nói về MultiTableView mình sẽ đề cập đến.
Khi IndexView kế thừa từ DataTableView, phương thức get_data_dict() được gọi đến có nội dung như sau:
```python
     def _get_data_dict(self):
        if not self._data:
            self.update_server_filter_action(self.request)
            self._data = {self.table_class._meta.name: self.get_data()}
        return self._data
```
Trong phương thức trên ta thể thấy, gía trị trả về là self._data với:
```python
    self._data = {self.table_class._meta.name: self.get_data()}
```
Như vậy, chúng ta sẽ implement phương thức get_data() để lấy dữ liệu của bảng sau đó thêm vào self._Chúng ta cần phải override lại phương thức get_data() để lấy dữ liệu của bảng.
Trong ví dụ này, chúng ta yêu cầu hiển thị bảng về các user. Khi đó, self._data() trả về sẽ là :
```python
    self._data['user']= self.get_data()
Quay trở lại với phương thức handle_table():

    def handle_table(self, table):
        name = table.name
        data = self._get_data_dict()
        self._tables[name].data = data[table._meta.name]
        self._tables[name]._meta.has_more_data = self.has_more_data(table)
        self._tables[name]._meta.has_prev_data = self.has_prev_data(table)
        handled = self._tables[name].maybe_handle()
        return handled
```
Sau khi lấy được data của table,  thiết lập các gía trị cho self._tables. Trong ví dụ hiển thị bảng user, ta có:
```python
    self._tables['user'].data = self._data = self.get_data()
```
Quay về phương thức construct_tables(),
```python
    def construct_tables(self):
        tables = self.get_tables().values()
        # Early out before data is loaded
        for table in tables:
            preempted = table.maybe_preempt()
            if preempted:
                return preempted
        # Load data into each table and check for action handlers
        for table in tables:
            handled = self.handle_table(table)
            if handled:
                return handled
    
        # If we didn't already return a response, returning None continues
        # with the view as normal.
        return None
```
Sau khi các table đã được gán dữ liệu, quay trở về hàm gọi nó là phương thức get():
```python
    def get(self, request, *args, **kwargs):
        handled = self.construct_tables()
        if handled:
            return handled
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
```
Sau khi handled = self.constuct_tables() được thực hiện, chúng ta bắt đầu lấy context để render bằng phương thức:
```python
    context = self.get_context_data(**kwargs)
```
Ở đây tiếp tục xảy ra 2 trường hợp : Lớp IndexView kế thừa từ DataTableView và lớp IndexView kế thừa từ MultiTableView. 
Đối với trường hợp kế thừa từ MultiTableView, phương thức self.get_context_data() sau sẽ được gọi:
```python
    def get_context_data(self, **kwargs):
        context = super(MultiTableMixin, self).get_context_data(**kwargs)
        tables = self.get_tables()
        for name, table in tables.items():
            context["%s_table" % name] = table
        return context
```
Ta có thể thấy, phương thức này lấy các tables ra:
```python
    tables = self.get_tables()
phương thức get_tables():

    def get_tables(self):
        if not self._tables:
            self._tables = {}
            if has_permissions(self.request.user,
                               self.table_class._meta):
                self._tables[self.table_class._meta.name] = self.get_table()
        return self._tables
```
như vậy tables ở đây chính là self._tables.
Sau đó, duyệt qua các table và thực hiện câu lệnh sau:
```python
    context["%s_table" % name] = table
```
ví dụ trong trường hợp có 2 table là user và project, thì ta sẽ có:
```python
    context["user_name"] = self._tables['user']
    context['project_name']=self._tables['project']
```
Trong trường hợp kế thừa từ lớp DataTableView, phương thức get_context_data() của lớp này sẽ được gọi đến:
```python
    def get_context_data(self, **kwargs):
        context = super(DataTableView, self).get_context_data(**kwargs)
        if hasattr(self, "table"):
            context[self.context_object_name] = self.table
        return context
```
Trong ví dụ hiển thị bảng user, phương thức này kế thừa phương thức get_context_data() của lớp MultiTableView ở trên được gọi tới, có nghĩa là chúng ta sẽ thu được:
```python
    context['user_table']= self._tables['user']
```
sau đó thực hiện tiếp câu lệnh sau:
```python
    context[self.context_object_name] = self.table
```
Cụ thể, self.context_object_name = 'table' như vậy ta sẽ có:
```python
    context['table'] = context['user_table'] = dữ liệu của table
```
Cuối cùng, ở template ta có thể thấy:
```python
    {% extends 'base.html' %}
    {% load i18n %}
    {% block title %}{% trans "Users" %}{% endblock %}
    
    {% block page_header %}
      {% include "horizon/common/_domain_page_header.html" with title=page_title %}
    {% endblock page_header %}
    
    {% block main %}
        {{ table.render }}
    {% endblock %}
```
trong block *main* ta có thể sử dụng 2 cách để render dữ liệu đối với trường hợp kế thừa DataTableView:
```python
    user_table.render
```
hoặc:
```python
    table.render
```
Trong trường hợp kế thừa MultiTableView, chúng ta có thể render dữ liệu theo cách sau:
```python
    <div class="row">
      <div class="col-sm-12">
        <hr>
        <div id="user">
          {{ user_table.render }}
        </div>
        <div id="project">
          {{ project_table.render }}
        </div>
      </div>
    </div>
```
## MultiTableView ##
MultiTableView được sử dụng trong trường hợp bạn muốn hiển thị nhiều hơn một bảng cùng hiển thị trên một panel (chưa xét đến trường hợp trong panel có nhiều tabs).
Để sử dụng lớp này, đầu tiên bạn phải định nghĩa một subclass của MultiTableView. Định nghĩa subclass này yêu cầu định nghĩa các nội dung sau:

 - table_classes: Là một tuple chứa các lớp DataTable muốn hiển thị
 - get_{{ table_name }}_data : định nghĩa các phương thức để lấy dữ liệu cho các table. *table_name* là gía trị của thuộc tính *name* trong lớp meta của lớp DataTable tương ứng.
 - template_name: thuộc tính này chỉ đến template được sử dụng để hiển thị các table.

Tiếp theo, chúng ta sẽ giải thích vì sao lại phải định nghĩa các phương thức get_{{ table_name }}_data() cho từng table?
Tương tự như phần **xử lý request** ở trên, qúa tình xử lý request thực hiện đến phương thức handle_table kế thừa từ lớp MultiTableMixin:
```python
    def handle_table(self, table):
        name = table.name
        data = self._get_data_dict()
        self._tables[name].data = data[table._meta.name]
        self._tables[name]._meta.has_more_data = self.has_more_data(table)
        self._tables[name]._meta.has_prev_data = self.has_prev_data(table)
        handled = self._tables[name].mayableultibe_handle()
        return handled
```
Như ta có thể thấy, data có thể được lấy từ phương thức self._get_data_dict().
Trong trường hợp lơp View kế thừa từ MultiTableView, phương thức get_data_dict() cuả lớp này sẽ được gọi đến:
```python
    def _get_data_dict(self):
        if not self._data:
            for table in self.table_classes:
                data = []
                name = table._meta.name
                func_list = self._data_methods.get(name, [])
                for func in func_list:
                    data.extend(func())
                self._data[name] = data
        return self._data
```
Phương thức này sẽ lấy data về cho self._data bằng cách: quét các table đang có trong đối tượng view:
```python
    for table in self.table_classes:
```
lấy các phương thức get_{{table_name}}_data cho table đang xét đã được thiết lập bằng phương thức:
```python
    func_list = self._data_methods.get(name, [])
```
Vậy, self._data_methods.get() là gì?
Chúng ta xem lại hàm init() của lớp MultiTableMixin mà MultiTableView kế thừa:
```python
    data_method_pattern = "get_%s_data"
    def __init__(self, *args, **kwargs):
        super(MultiTableMixin, self).__init__(*args, **kwargs)
        self.table_classes = getattr(self, "table_classes", [])
        self._data = {}
        self._tables = {}
        self._data_methods = defaultdict(list)
        self.get_data_methods(self.table_classes, self._data_methods)
        self.admin_filter_first = getattr(settings,
                                          'ADMIN_FILTER_DATA_FIRST',
                                          False)
```
Ta có thể thấy, self._data_methods được thiết lập bởi phương thức self.get_data_methods:
```python
    self.get_data_methods(self.table_classes, self._data_methods)
```
Xét phương thức get_data_methods:
```python
     def get_data_methods(self, table_classes, methods):   
        for table in table_classes:
            name = table._meta.name
            if table._meta.mixed_data_type:
                for data_type in table._meta.data_types:
                    func = self.check_method_exist(self.data_method_pattern,
                                                   data_type)
                    if func:
                        type_name = table._meta.data_type_name
                        methods[name].append(self.wrap_func(func,
                                                            type_name,
                                                            data_type))
            else:
                func = self.check_method_exist(self.data_method_pattern,
                                               name)
                if func:
                    methods[name].append(func)
```
Phương thức này sẽ xét từng table của đối tượng và kiểm tra xem có tồn tại phương thức get data cho table không bằng câu lệnh sau:
```python
    func = self.check_method_exist(self.data_method_pattern,name)
```
phương thức check exist  với tham số truyền vào là self.data_method_pattern = "get_%s_data" và name là tên của table
Phương thức này có đặc tả như sau:
```python
        def check_method_exist(self, func_pattern="%s", *names):
        func_name = func_pattern % names
        func = getattr(self, func_name, None)
        if not func or not callable(func):
            cls_name = self.__class__.__name__
            raise NotImplementedError("You must define a %s method "
                                      "in %s." % (func_name, cls_name))
        else:
            return func
```
Đầu tiên, ví dụ ta có table là user thì func_name cho table sẽ là :
```python
    func_name = get_user_data
```
sau đó kiểm tra xem có tồn tại phương thức get_user_data() hay không?
```python
    if not func or not callable(func):
            cls_name = self.__class__.__name__
            raise NotImplementedError("You must define a %s method "
                                      "in %s." % (func_name, cls_name))
        else:
            return func
```
Nếu không thì báo lỗi, ngược lại là trả về phương thức get data. Điều này lý giải vì sao chúng ta cần phải định nghĩa phương thức get data cho từng table.
Quay trở lại phương thức get_data_method() sau khi trả lại func thì add vaò methods:
```python
    func = self.check_method_exist(self.data_method_pattern,
                                               name)
                if func:
                    methods[name].append(func)
```
thực hiện xong get_data_method() chúng ta sẽ thu được một list có phương thức get data tương ứng với từng table.
Quay trở laị phương thức get_data_dict():
```python
        def _get_data_dict(self):
        if not self._data:
            for table in self.table_classes:
                data = []
                name = table._meta.name
                func_list = self._data_methods.get(name, [])
                for func in func_list:
                    data.extend(func())
                self._data[name] = data
        return self._data
```
thực hiện nạp dữ liệu của từng bảng tương ứng vào self._data. Khi đó ta có:
```python
    self._data['user']= get_user_data()
    self._data['project']=get_project_data()
```
Tiếp theo, sẽ thực hiện tương tự như trong phần **xử lý request**.

# Kết luận
Bài viết này tập trung viết về DataTable và Class-base view của horizon.tables. Ngoài ra, trong các kiến thức về table còn có Forms. Forms dùng để định nghĩa các action cho tables. Forms sẽ được nói đến trong bài viết khác.
