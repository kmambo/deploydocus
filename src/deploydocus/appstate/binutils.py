from plumbum import local

helm = local["helm"]
git = local["git"]
kubectl = local["kubectl"]
kustomize = local["kustomize"] or kubectl["kustomize"]
cp = local["cp"]
