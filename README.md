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
- https://raw.githubusercontent.com/rosscdh/kubernetes-db-oneshot/master/k8s

configMapGenerator:
  - name: oneshot-cm
    behavior: merge
    literals:
      - MASTER_DB_URL=postgres://postgres:postgres@192.168.0.24:5432/postgres

secretGenerator:
- name: oneshot-secret
  behaviour: replace
  files:
  - oneshot.yaml=my.local.oneshot.yaml
```

*my.local.oneshot.yaml*

```

# will create the dbs and the user/passwords using the MASTER_DB_URL

create_dbs:
- url: postgres://dbuserA:passwordA@192.168.0.24:5432/dba
- url: postgres://dbuserB:passwordB@192.168.0.24:5432/dbb

# will use the MASTER_DB_URL to execute the statements
statements:
  - GRANT SELECT ON ALL TABLES IN SCHEMA public TO dbuserBReader;
  - ALTER DEFAULT PRIVILEGES IN SCHEMA public
      GRANT SELECT ON TABLES TO dbuserBReader;
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
  MASTER_DB_URL: postgres://postgres:postgres@192.168.0.24:5432/postgres
  ONESHOT_YAML: /tmp/oneshot/oneshot.yaml
kind: ConfigMap
metadata:
  name: oneshot-cm-gmhm9f9mb8
---
apiVersion: v1
data:
  oneshot.yaml: Y3JlYXRlX2RiczoKLSB1cmw6IHBvc3RncmVzOi8vZGJ1c2VyQTpwYXNzd29yZEFAMTkyLjE2OC4wLjI0OjU0MzIvZGJhCi0gdXJsOiBwb3N0Z3JlczovL2RidXNlckI6cGFzc3dvcmRCQDE5Mi4xNjguMC4yNDo1NDMyL2RiYgpzdGF0ZW1lbnRzOgogIC0gR1JBTlQgU0VMRUNUIE9OIEFMTCBUQUJMRVMgSU4gU0NIRU1BIHB1YmxpYyBUTyBkYnVzZXJCUmVhZGVyOwogIC0gQUxURVIgREVGQVVMVCBQUklWSUxFR0VTIElOIFNDSEVNQSBwdWJsaWMKICAgICAgR1JBTlQgU0VMRUNUIE9OIFRBQkxFUyBUTyBkYnVzZXJCUmVhZGVyOw==
kind: Secret
metadata:
  name: oneshot-secret-2dtkddcc5g
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
            name: oneshot-cm-gmhm9f9mb8
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
          secretName: oneshot-secret-2dtkddcc5g
```