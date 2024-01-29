# Deploydocus

## Run a private Pypi-compatible server

### Using helm
There is a helm chart available at https://owkin.github.io/charts/
I am going to give you the cookbook approach. 
1. `helm repo add owkin https://owkin.github.io/charts/`
2. `helm repo update`
3. ```shell
   helm install pypiserver \
    owkin/pypiserver \
    --set image.tag=latest 
   ```
4. Get the application URL by running these commands:
   ```shell
   export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=pypiserver,app.kubernetes.io/instance=pypiserver" -o jsonpath="{.items[0].metadata.name}")
   echo "Visit http://127.0.0.1:8080 to use your application"
   kubectl port-forward --namespace default $POD_NAME 8080:8080
   ```
*Note: unfortunately the chart only deploys to default namespace*

