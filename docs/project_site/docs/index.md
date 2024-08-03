# `deploydocus`

The programmable alternative to Helm+Kustomize for devs.

## Why `deploydocus`?

*Or why choose it over `helm` and `kustomize`?*

## My pet peeves about Helm charts.

These are just a few of the highlights but my list of peeves is almost endless.

1. Take the unreadability of Kubernetes YAML-manifests and templatize it, you have Helm charts.
2. The _dev_ tooling around Helm is not great. Emphasis on _dev_.
    1. If you are developing a Helm chart, sooner or later you will hit an error that is near-about impossible to debug
       because the existing tools are not good and they will, more-often than not, issue a cryptic message and just crap
       out.
    2. Try refactoring a Helm chart. Say you feel you have added a variable that requires deeply-nested entries
       in `values.yaml` and you realize the error of your ways and you want to refactor it, heaven help you! Even the
       simple task of renaming a variable is an exercise in `grep`/`awk`/`sed`/`perl`-programming.
    3. All said, Helm has been around for a while. If there has been little done to provide this sort of tooling around
       Helm till now, it's not about to happen.
3. It's more than just about YAML. There's not a markup language out there that cuts muster and to use any markup
   language to describe a system as complicated as Kubernetes resources was never going to work out.

## And as for `kustomize` ...

It works fine for small changes to be applied to Kubernetes manifests but just about everything I have said about Helm
charts applies to kustomizations as well - cryptic error messages, lack of dev tooling. If anything, I find the error
messages that `kustomize` spits out to be even more cryptic.

## Nothing to do with YAML (but YAML doesn't help)

There's little to be done about how complicated Kubernetes resources can be - and this is outside of whether it is
expressed in YAML (or even JSON) but that complexity can be abstracted away to a great extent if general-purpose
languages are used. I understand that this does not square with
the [rule of least power](https://en.wikipedia.org/wiki/Rule_of_least_power) but this rule has hurt many projects over
the course of their lifetimes.

Projects start out small but the more successful ones evolve over time to handle more and more scenarios. The
expressiveness of the language chosen to meet the project's needs in its starting period becomes less and less adequate
as the project's scope and complexity expand. So let's just cut to the chase and why not go to a general-purpose
language? The tooling is better anyways - IDEs, plugins, libraries the lot which makes:-

1. error detection easier.
2. code refactoring.
3. richer, easier unit testing

## Raison d'être for `deploydocus`?

1. Python. That is the language of choice for a number of reasons which I will expand on later but yes, I wanted to
   ditch the Rule of Least Power and I went with Python.
2. `deploydocus` is a Python application and a library. It will do everything that `helm` v3.x does and `kustomize` does
   except it will do it in a Pythonic way.
    1. It provides a level of abstraction from the underlying YAML descriptors with fewer attributes to tune for any
       application.
    2. It provides sane starting points for applications meant to be deployed to Kubernetes. They can be
       re-configured/tweaked by changing only a few keys. *Note:* I am not moving away from `Deployment`s and `Service`
       s, `Ingress`es et al but the aim is to provide Pythonic base classes that will ultimately be rendered to YAMl or
       JSON which are subsequently applied to the clusters.
    3. When used as a library, it can be used with additional code to interact with other cloud provider-specific
       components or notify asset trackers. For example, you can write code logic to check for the existence of a
       database before deploying your application.
3. The Python base classes can be derived from, the code inspected and modified. Ultimately, I expect the community will
   provide libraries that can serve as a good starting points for application developers to build application packages.
4. Practicality over purity: While `deploydocus` focuses on abstracting, it is not too proud and will happily work
   with `helm`-rendered manifests, `kustomize`-altered manifests and `kubectl`-rendered (client-side or server-side)
   manifests.

`deploydocus` on the other hand, expresses Kubernetes manifests as Python object. Yes, even though behind the scenes, it
has no choice but to deal in YAML (or JSON), every Kubernetes manifest is encapsulated in a Python object.
To change a deployment, say, to insert an init container, to the deployment spec, is as simple as

```python
deployment.insert_init_container(0, init_container_obj)
```
