gcloud container clusters create cluster1 \
    --zone us-central1-a \
    --num-nodes 2 \
    --machine-type e2-micro \
    --enable-autoscaling \
    --min-nodes 2 \
    --max-nodes 2 \
    --enable-network-policy \
    --enable-ip-alias

gcloud artifacts repositories create metabase \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository"

gcloud auth configure-docker us-central1-docker.pkg.dev

docker tag my-metabase:latest us-central1-docker.pkg.dev/bigdata-2000/metabase/image:latest


helm install prom bitnami/kube-prometheus \
--version 8.2.2 \
--values k8/values.yaml \
--wait