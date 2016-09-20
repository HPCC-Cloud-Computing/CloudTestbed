**Ứng dụng Horizon vào Docker**
=======
Bài viết này sẽ hướng dẫn mọi người cách làm các task về Docker trong Horizon sau:

 - Tạo 1 panel **container** chứa bảng hiển thị thông tin các container và có các action **create container**, **delete container**, **filter container**
 -  Các biểu đồ biểu diễn **resource usage** của container.

Ở hướng dẫn này mình chỉ giải thích tác dụng của các đoạn code quan trọng, mọi người nên đọc trước bài hướng dẫn về luông hoạt động khi tạo ra một **Table** trong Horizon tại [đây](#) 

[Source code](#)

1. Cài đặt và thiết lập ban đầu
-------
### 1.1 Cài đặt docker-py
Để có thể lấy thông tin về các container cũng như thông tin về resource usage chúng ta cần cài đặt **docker-py**
**Docker-py** là một thư viện Python cho phép chúng ta quản lí, điều khiển Docker thông qua API. 

    pip install docker-py
   Đọc [document](https://docker-py.readthedocs.io/en/latest/api/) để biết cách sử dụng **docker-py** cũng như các command và tham số để tùy biến cho phù hợp với mục đích của đề bài.

### 1.2 Tạo dashboard mới
Chúng ta cần tạo một [dashboard](https://github.com/openstack/horizon/blob/stable/mitaka/doc/source/tutorials/dashboard.rst) mới theo hướng dẫn sau:

    mkdir openstack_dashboard/dashboards/custom_horizon 

    ./run_tests.sh -m startdash custom_horizon \
    --target openstack_dashboard/dashboards/custom_horizon
    
    mkdir openstack_dashboard/dashboards/custom_horizon/container
    
    ./run_tests.sh -m startpanel images_OPS \
    --dashboard=openstack_dashboard.dashboards.custom_horizon \
    --target=openstack_dashboard/dashboards/custom_horizon/container
   Sau đó, thư mục custom_horizon của chúng ta sẽ có định dạng thư mục như sau:
   

    custom_horizon
    ├── dashboard.py
    ├── dashboard.pyc
    ├── __init__.py
    ├── __init__.pyc
    ├── container
    │   ├── __init__.py
    │   ├── panel.py
    │   ├── templates
    │   │   └── container
    │   │       └── index.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── static
    │   └── container
    │       ├── css
    │       │   └── custom_horizon.css
    │       └── js
    │           └── custom_horizon.js
    └── templates
        └── custom_horizon
            └── base.html

2. Tạo bảng hiển thị thông tin về các container
-------
Tạo một file `tables.py` dưới thư mục `container` và copy đoạn code sau:
```
from horizon.utils import filters as filters_horizon
from django.utils.translation import ugettext_lazy as _

import horizon

class ContainerDockerTable(tables.DataTable):
    id = tables.Column('id', verbose_name='Container Id')
    image = tables.Column('image', verbose_name='Image')
    command = tables.Column('command', verbose_name='Command')
    created = tables.Column('created', verbose_name='Created',
                            filters=(filters_horizon.parse_isotime,filters_horizon.timesince_sortable),)
    state = tables.Column('state', verbose_name='State')
    name = tables.Column('name', verbose_name='Name')

    class Meta(object):
        name = "container_docker"
        verbose_name = _("Container Docker")
```
 Ở đây, chúng ta định nghĩa một lớp **ContainerDockerTable** gồm 6 thuộc tính là `id` , `image`, `command`, `create`, `state` và `name`.
 
 Trong cột **create** ta có đoạn code: 
 

    filters=(filters_horizon.parse_isotime,filters_horizon.timesince_sortable)

Đoạn code này có tác dụng format lại thời gian. Ví dụ `2016-09-13 17:41:17` sẽ được format thành `5 days, 21 hours`.

Tiếp theo, trong file `views.py` ta tạo một lớp**Container** gồm các thuộc tính như sau:
```
class Container:
    def __init__(self, containerId, image, command, created, state, name):
        self.id = containerId
        self.image = image
        self.command = command
        self.created = created
        self.state = state
        self.name = name
```
Trong lớp **IndexView** chúng ta cần phương thức `get_data(self)` trả về một list các đối tương **Container**:
```
class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'custom_horizon/container/index.html'
    table_class = tbl_container.ContainerDockerTable
    page_title = _("Container")

    def get_data(self):
        # Add data to the context here...
        cli = Client(base_url='unix://var/run/docker.sock')
        containers = []
        
        for ct in cli.containers(all=True):
            # convert data
            created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ct['Created']))
            name = ct['Names'][0][1:]
            
            containers.append(
                Container(ct['Id'][:12], ct['Image'], ct['Command'], created, ct['State'], name))
                
        return containers
```
Chúng ta sẽ sử dụng command [cli.containers(all=True)](https://docker-py.readthedocs.io/en/latest/api/#containers) để  lấy thông tin về các container được trả về dưới dạng 1 **dict**. Tham số `all = True` sẽ show tất cả các container kể cả các container đã exited , theo mặc định chỉ có các container đang chạy mới được show.

Ngoài ra ta cần convert lại 2 thuộc tính là `create` và `name`  để nội dung hiển thị lên bảng dễ hiểu hơn.
 
 Ta cũng cần có một `url` và một file `index.html` để có thể render được dữ liệu sang dạng bảng.  Các bạn xem code để biết thêm chi tiết.

3. Tạo actions cho table Container
-------
### 3.1 Action **Delete**
Để tạo action **delete**, trong file `tables.py` ta cần định nghĩa lớp `DeleteContainerAction` như sau:
```
class DeleteContainerAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Image",
            u"Delete Images",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Image",
            u"Deleted Images",
            count
        )

    def delete(self, request, obj_id):
        cli = Client(base_url='unix://var/run/docker.sock')

        for container in cli.containers(all=True):
            if (container['Id'][:12] == obj_id):
                cli.remove_container(image=container['Names'][0][1:])
                break;
```

Hàm `action_past` có tác dụng hiển thị thông báo nếu delete thành công, nếu xóa 1 container nó sẽ hiển thị **Deleted Image**, còn nếu xóa nhiều hơn 1 image nó sẽ thông báo **Deleted Images** :)

Việc xóa container sẽ được viết trong hàm `delete(self, request, obj_id)` được overrides từ lớp **DeleteAction**. Tham số `obj_id` chính là thuộc tính `id` trong lớp **Container** đã được tạo ở trên. 

Chúng ta sẽ sử dụng command [cli.remove_container(image = "name contaier)](https://docker-py.readthedocs.io/en/latest/api/#remove_container)  để  delete container.

Cuối cùng ta quy đinh lớp **DeleteContainerAction** này trong thuộc tính **table_actions** tại class **Meta**

    table_actions = (DeleteContainerAction,)

### 3.2 Action **Filter**
Trong bài viết này chúng ta sẽ xem xét 3 loại filter, do mỗi bảng chỉ có thể sử dụng 1 loại filter nên tùy vào mục đích mà chúng ta sẽ sử dụng chúng cho phù hợp . 

Client API filter container đọc ở [đây](https://docker-py.readthedocs.io/en/latest/api/#containers)

### Basic Filter
![Basic filter](http://i.imgur.com/YUq6XuW.png)

Trong file `tables.py` chúng ta chỉ cần thêm đoạn code sau và quy định nó trong `table_actions` ở class **Meta** là đã có 1 filter đơn giản
```
class ContainerBasicFilter(tables.FilterAction):
    name = "container_filter"
```

### Choice Filter
![Choice Filter](http://i.imgur.com/w4quNpU.png)

**Choice Filter** là loại filter theo thuộc tính của bảng. Trong bài viết này ta sẽ filter theo **Name Container** và theo **Id Container**. Để tạo ra loại filter này chúng ta làm theo những bước sau:

Trong file `tables.py` chúng ta định nghĩa class **ContainerChoiceFilter**:
```
class ContainerChoiceFilter(tables.FilterAction):
    filter_type = "server"
    filter_choices = (('name', _("Container Name ="), True),
                      ('id', _("Id ="), True),)
```

Trong class này ta cần ít nhất 2 thuộc tính:

 - **filter_type**: kiểu filter
 - **filter_choices**: là một tuple các tuple chứa các option filter. 


```
class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'custom_horizon/container/index.html'
    table_class = tbl_container.ContainerDockerTable
    page_title = _("Container")

    def get_data(self):
        # Add data to the context here...
        filters = self.get_filters()
        cli = Client(base_url='unix://var/run/docker.sock')
        containers = []
        for ct in cli.containers(all=True, filters=filters):
            # convert data
            created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ct['Created']))
            name = ct['Names'][0][1:]

            containers.append(
                Container(ct['Id'][:12], ct['Image'], ct['Command'], created, ct['State'], name))
        return containers

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
Trong class **IndexView** ở file `views.py` chúng ta định nghĩa phương thức `get_filters` . Nhiệm vụ của phương thức này là mỗi khi click vào button **Filter** nó sẽ trả về một dict với **key** là option filter tướng ứng với tham số đầu tiên trong `filter_choices` và **value** là chuối bạn bạn muốn filter. Ví dụ như trong hình dưới đây:
![Choice Filter](http://i.imgur.com/w4quNpU.png)
thì nó sẽ return về 1 dict = {'name' : 'demo'}. Trong đó `filter_field` = 'name' và `filter_string` = 'demo'.

Sau khi đã có được option và giá trị người dùng muốn filter thì điều tiếp theo thật đơn giản. Trong phương thức `get_data` bạn chỉ cần gọi phương thức `filters = self.get_filters()` và sử dụng command `cli.containers(all=True, filters=filters)`  là có thế lấy được thông tin các container bạn filter.

Cuối cùng ta quy đinh lớp **ContainerChoiceFilter** này trong thuộc tính **table_actions** tại class **Meta**

    table_actions = (ContainerChoiceFilter,)


### Fix Button Filter 
![Fix Button Filter](http://i.imgur.com/12O7aqd.png)

**Fix Button Filter** là loại filter theo gía trị của thuộc tính. Ví dụ mỗi container có một trạng thái khác nhau như **exited**, **running**, **created**. Khi click vào filter button nào, nó sẽ lọc ra các container có gía trị tương ứng .

Để tạo ra loại filter này, chúng ta làm theo những bước sau:

Đầu tiên, chúng ta cần định nghĩa class **tables.ContainerFixedFilter** kế thừa từ class **FixedFilterAction**.  Sau đó overrider 2 phương thức là `get_fixed_buttons`  và `categorize` sau:

 - **get_fixed_buttons(self)**:  làm nhiệm vụ return một list các dictionnaries mô tả các button hiển thị trên giao diện. Mỗi một **dict** đại diện cho một button bao gồm những **key** sau:
	 - `text`: text hiển thị trên button
	 - `value`: giá trị trả về khi button được click
	 - `icon`: icon hiển thị trên mỗi button. Thư viện các icon được lấy tại [Font Awesome](http://fontawesome.io/icons/).
 - **categorize(self, table, containers)**: trả về một dict với **key** là gía trị của mỗi button ta đã quy định trong `value` và **value** là một list các instance Container tương ứng. 

```
class ContainerFixedFilter(tables.FixedFilterAction):
    def get_fixed_buttons(self):
        def make_dict(text, value, icon):
            return dict(text=text, value=value, icon=icon)

        buttons = [make_dict(_('Exited'), 'exited', 'fa-stop')]
        buttons.append(make_dict(_('Running'), 'running', 'fa-play'))
        buttons.append(make_dict(_('Created'), 'created', 'fa-check-square'))
        return buttons

    def categorize(self, table, containers):

        tenants = defaultdict(list)
        for container in containers:
            state = get_container_categories(container)
            tenants[state].append(container)

        return tenants
```

Trong phương thức `categorize(self, table, containers)` ta có gọi đến phương thức `get_container_categories(container)` . Phương thức này làm nhiệm vụ trả về chuỗi là **state** của mỗi instance **Container**. 

Các bạn để ý đối số `containers` trong phương thức `categorize(self, table, containers)`, đó là một list các instance **Container** tương ứng với mỗi hàng trong bảng.
```
def get_container_categories(container):
    categories = ''
    if (container.state == 'running'):
        categories = 'running'
    elif(container.state == 'exited'):
        categories = 'exited'
    elif(container.state == 'created'):
        categories = 'created'
    return categories
```

Tiếp theo ta cần 	định nghĩa class **UpdateRow ** kế thừa class  **tables.Row** có nhiệm vụ update và render lại bảng mỗi lần ta filter.

```
class UpdateRow(tables.Row):
    ajax = True

    def load_cells(self, container=None):
        super(UpdateRow, self).load_cells(container)
        # Tag the row with the image category for client-side filtering.
        container = self.datum
        category = get_container_categories(container)
        self.classes.append('category-' + category)
```

Cuối cùng ta quy đinh class **ContainerFixedFilter** này trong thuộc tính **table_actions**  và  class **UpdateRow** trong thuộc tính **row_class** tại class **Meta**

    table_actions = (ContainerFixedFilter,)
    row_class = UpdateRow

### 3.3 Action **Create**
Trong bài viết này, ta sẽ tạo một action **Create Container** đơn giản với form gồm 2 trường là **Image Resouce ** và **Name Container**.

Đầu tiên, trong file `tables.py` ta định nghĩa class **CreateContainer** kế thừa class **tables.LinkAction** 

```
class CreateContainer(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Container")
    url = "horizon:custom_horizon:container:create"
    classes = ("ajax-modal",)
    icon = "plus"
```

Tiếp theo trong file `views.py` ta định nghĩa class **CreateView** như sau:

```
from openstack_dashboard.dashboards.custom_horizon.container import forms as create_forms
...

class CreateView(forms.ModalFormView):
    form_class = create_forms.CreateContainerForm
    form_id = "create_image_form"
    modal_header = _("Create An Container")
    # submit_label = _("Create Image")
    submit_url = reverse_lazy('horizon:custom_horizon:container:create')
    template_name = 'custom_horizon/container/create.html'
    success_url = reverse_lazy("horizon:custom_horizon:container:index")
    page_title = _("Create An Container")
```

Form hiển thị để nhập thông tin khi **Create Container** sẽ được quy định tại thuộc tính `form_class`. Ở đây ta cần tạo một file `forms.py` trong thư mục `openstack_dashboard/dashboards/custom_horizon/container`. File này có nhiệm vụ tạo form **Create**, đồng thời xử lí sự kiện.

```
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from docker import Client


def get_name_images():
    IMAGES = [('-1', _('Select Image'))]
    cli = Client(base_url='unix://var/run/docker.sock')
    for image in cli.images():
        repo = image['RepoTags']
        repoTags = repo[0]
        IMAGES.append((repoTags, _(repoTags)))

    return IMAGES


class CreateContainerForm(forms.SelfHandlingForm):


    image = forms.ChoiceField(
        label=_('Image Source'),
        choices=get_name_images(),
        )
    name = forms.CharField(max_length=255, label=_("Name Container"),required=False)
    def handle(self, request, data):
        try:
            cli = Client(base_url='unix://var/run/docker.sock')
            cli.create_container(image=data['image'], name=data['name'])
        except Exception:
            exceptions.handle(request, _('Unable to create container.'))
            return False
        return True
```
Phương thức `get_name_images()` trả về một list tên các image docker, được dùng trong thuộc tính `choices` của class **forms.ChoiceField**.

Ta xem xét phương thức `handle(self, request, data)` , phương thức này làm nhiệm vụ xử lí khi người dùng click vào button **Submit** trong form.  Command [cli.create_container()](https://docker-py.readthedocs.io/en/latest/api/#create_container) được sử dụng để create container.

Tiếp theo, chúng ta cũng cần tạo ra 2 file `create.html` và `_create.html` trong thư mục `custom_horizon/container/templates/container` để render form sang hmtl hiển thi lên giao diện.

Cuối cùng ta quy đinh class **CreateContainer** này trong thuộc tính **table_actions** tại class **Meta**

    table_actions = (CreateContainer,)

4. Biểu đồ biểu diễn resource usage container
-------
Phần này sẽ được mình trình bày trong [bài tiếp theo](#) cụ thể hơn. Bài đó sẽ giới thiệu mọi người **cAdvisor - công cụ giám sát tài nguyên sử dụng của Google** và cách dùng RESTful API để lấy các thông tin sử dụng tài nguyên từ các máy ảo OpenStack triển khai Docker.


Như vậy mình đã hướng dẫn xong mọi người cách tạo **Table** hiển thị các thông tin đơn giản về Docker cũng như tạo các action cho nó. Còn rất nhiều chức năng và thuộc tính hay trong Horizon và Docker, bạn có thể tự custom các dashboard khác dựa trên những gì mình đã trình bày ở trên :)) 
