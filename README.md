# kubernetes-db-oneshot

Create multiple databases and users on postgres databases as a kube Job.

**DEV ENVS ONLY PLEASE**
Define a MASTER_DB_URL with the permissions to create dbs (root/postgres)
and then a set of dbs to be created alone with their user:pass which will then be created using the MASTER_DB_URL settings
you are also able to perform statements like privileges

## Building

```
make build

brew install kind kustomize kubectl
kind create cluster
make k8s | kubectl apply -f -
```

## Setup

1. create a kustomize module

*kustomization.yaml*

```
resources:
- github.com/rosscdh/kubernetes-db-oneshot/k8s/?ref=HEAD

secretGenerator:
- name: oneshot-secret
  behavior: replace
  files:
  - oneshot.yaml=oneshot.yaml
```

*oneshot.yaml*

```
cat <<EOF > $PWD/oneshot.yaml
MASTER_DB_URL: postgres://postgres:postgres@postgres.dev.svc.cluster.local:5432/postgres

# perform statements using the master_db_url privs before any other actions
pre_statements:
  - DROP role 'monkey' CASCADE;

# will create the dbs and the user/passwords using the MASTER_DB_URL
create_dbs:
- url: postgres://dbuserA:passwordA@postgres.dev.svc.cluster.local:5432/dba
- url: postgres://dbuserB:passwordB@postgres.dev.svc.cluster.local:5432/dbb

# will use the MASTER_DB_URL to execute the statements
statements:
  - GRANT SELECT ON ALL TABLES IN SCHEMA public TO dbuserBReader;
  - ALTER DEFAULT PRIVILEGES IN SCHEMA public
      GRANT SELECT ON TABLES TO dbuserBReader;
EOF
```

## Using

* Will install into default ns by default, but feel free to override with `namespace: whatever`

```
kustomize build --load_restrictor none k8s | kubectl apply -f -
or
make k8s | kubectl apply -f -

>
apiVersion: v1
data:
  ONESHOT_YAML: /tmp/oneshot/oneshot.yaml
kind: ConfigMap
metadata:
  name: oneshot-cm-hc72ffgcfh
---
apiVersion: v1
data:
  oneshot.yaml: TUFTVEVSX0RCX1VSTDogcG9zdGdyZXM6Ly9wb3N0Z3Jlczpwb3N0Z3Jlc0AxOTIuMTY4LjAuMjQ6NTQzMi9wb3N0Z3JlcwpjcmVhdGVfZGJzOgotIHVybDogcG9zdGdyZXM6Ly9kYnVzZXJBOnBhc3N3b3JkQUAxOTIuMTY4LjAuMjQ6NTQzMi9kYmEKLSB1cmw6IHBvc3RncmVzOi8vZGJ1c2VyQjpwYXNzd29yZEJAMTkyLjE2OC4wLjI0OjU0MzIvZGJiCnN0YXRlbWVudHM6CiAgLSBHUkFOVCBTRUxFQ1QgT04gQUxMIFRBQkxFUyBJTiBTQ0hFTUEgcHVibGljIFRPIGRidXNlckJSZWFkZXI7CiAgLSBBTFRFUiBERUZBVUxUIFBSSVZJTEVHRVMgSU4gU0NIRU1BIHB1YmxpYwogICAgICBHUkFOVCBTRUxFQ1QgT04gVEFCTEVTIFRPIGRidXNlckJSZWFkZXI7
kind: Secret
metadata:
  name: oneshot-secret-tdb6f5t54t
type: Opaque
---
apiVersion: batch/v1
kind: Job
metadata:
  name: oneshot
spec:
  activeDeadlineSeconds: 120
  backoffLimit: 50
  template:
    spec:
      containers:
      - envFrom:
        - configMapRef:
            name: oneshot-cm-hc72ffgcfh
        image: rosscdh/kubernetes-db-oneshot
        imagePullPolicy: Always
        name: oneshot
        volumeMounts:
        - mountPath: /tmp/oneshot
          name: oneshot-yaml
          readOnly: true
      restartPolicy: Never
      volumes:
      - name: oneshot-yaml
        secret:
          items:
          - key: oneshot.yaml
            path: oneshot.yaml
          secretName: oneshot-secret-tdb6f5t54t
```
