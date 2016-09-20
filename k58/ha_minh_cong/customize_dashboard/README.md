#Log management and chart_customization version 1.0
##Component
sks dashboard for openstack dashboard, include:

 1. Bar chart for project usage
 2. Line chart for nova log summary
 3. pie chart for nova log summary
 
pie chart and line chart can refresh each 30 second if date to input > today


will be build time picker in nextweek

##How to install

 1. Install openstack dashboard enviroment -mitaka version  follow [this tutorial](https://github.com/openstack/horizon/blob/stable/mitaka/doc/source/quickstart.rst)
 2. add my dashboard folder (sks) to openstack dashboard in folder location **openstack_dashboard/dashboards/**
 3. build a virtual machine then install devstack on that VM, with VM's IP is 192.168.122.10
 4. put my Django API folder (nova_log_REST) to this VM and run it in port 9090
 5. add file _50_sks.py to folder **openstack_dashboard/enabled/**
 6. start openstack

if any error has occured, contact with me.