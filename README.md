# `deploydocus`

## What can `deploydocus` do?

`deploydocus`, in its first phase, seeks to combine the capabilities of `helm` and `kustomize` under one roof.

## `deploydocus`, in a nutshell

1. It is a Python application. It will do everything that `helm` v3.x does except it will do it in a Pythonic way.
2. You don't have to deal with YAML or Go-templates if you don't want to. You can spec the exact same thing using
a Python `dict`
3. It provides sane starting points for applications meant to be deployed to Kubernetes. They can be
   re-configured/tweaked by changing only a few keys.
4. It can deploy applications to clusters in steps. If a deployment process fails, the application deployer can
continue from the last failed point.
5. Instead of a chart - as in `helm` -, everything is spec-ed as `dict`s so erroneous specifications
are easier to debug - they show up as a stack trace.

## Why `deploydocus`?

_or why not stick with `helm`, `kustomize` et al_

1. `helm` does plenty well but reusing a helm chart is hard. Here are some examples.
   1. Swapping out one container image for another is not easy: for example,
       not all images have the same liveness and readiness.
   2. Not everyone uses secrets or configmaps and also not in the same ways: some use it to mount .env files,
      others to set environment variables.
   3. Once the base chart changes, the dependent chart breaks easily. This is because hard as YAML is, Go templates are
      even harder. The tiniest change in indentation using `nindent` and good luck figuring out what went wrong.
   4. Tooling around Helm charts
2. Expressing an `kustomize` idea in it is really really verbose.
   1. On top of that, try chaining a helm post-render hook with kustomize and you will see that the slightest change in what helm renders - say based on what the values are set for a helm chart - the changes you may need to the kustomize patches can be very different. i
   2. Debugging `kustomize build` failures are difficult in the best of circumstances. Coupled with `helm`, you will have even more trouble understanding if the failure happened because of `helm` or because of the kustomize patch.

`deploydocus` on the other hand, expresses Kubernetes manifests as Python object. Yes, even though behind the scenes, it has no choice but to deal in YAML (or JSON), every Kubernetes manifest is encapsulated in a Python object. 
To change a deployment, say, to insert an init container, to the deployment spec, is as simple as

```python
deployment["spec"]["template"]["spec"]["initContainers"].append(initContainersList)
```

## `deploydocus` FAQs?

- Q. **Why is this in Python?**

  A. This could have been done using a number of languages but they had to be a scripted language. So `C/C++`/`Go`/`Rust`/`Java` and the like were out. Any one of the likes of `Ruby`, `Python` and `Javascript` could have fixed the bill.

