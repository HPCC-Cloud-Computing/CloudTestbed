from horizon import forms
from docker import Client

def listImage():
    cli = Client(base_url='unix://var/run/docker.sock')
    images = cli.images()
    images_name = []
    for img in images:
        repo = img['RepoTags']
        repoTags = repo[0]
        images_name.append(repoTags)
    return images_name
class CreateContainer(forms.SelfHandlingForm):
    image = forms.CharField(label='Image',required=True)
    command = forms.CharField(label='Command')
    name = forms.CharField(label='Name')

    def handle(self, request, data):
        cli = Client(base_url='unix://var/run/docker.sock')
        cli.create_container(image=data['image'],name=data['name'],command=data['command'])
