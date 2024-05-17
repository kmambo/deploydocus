# A quick and dirty uninstall script for this example app pkg
# Assumes the current context is set to the test cluster.
# In my case, it is `kind` cluster

kubectl delete svc dummy-svc -v 9
kubectl delete deployments.apps dummy-deploy -v 9
kubectl delete configmaps dummy-cf -v 9
kubectl delete ns dummy-ns2 -v 9
