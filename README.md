# Skies

A quick way to have object composition to your Troposphere

## Ideal

```python
class AppTemplate(skies.templates.BaseTemplate):
   load_balancer = skies.HTTPS_LB(public=True, to=5000)
   tag = 'pypi'
   scaling_group = skies.SimpleScaler()

   # maybe run a command?


template = AppTemplate()
template.bind(atlas)
template.to_json()
```
