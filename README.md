# kubernetes-db-oneshot

Create multiple databases and users on postgres databases as a kube Job.

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

## Using

* Will install into default ns by default, but feel free to override with `namespace: whatever`

```
kustomize build --load_restrictor none k8s | kubectl apply -f
>
apiVersion: v1
data:
  MAKER_YAML: /tmp/oneshot/oneshot.yaml
  MASTER_DB_URL: postgres://postgres:postgres@192.168.0.24:5432/postgres
kind: ConfigMap
metadata:
  name: oneshot-cm-g2d5g4dtmc
---
apiVersion: v1
data:
  oneshot.yaml: Y3JlYXRlX2RiczoKLSB1cmw6IHBvc3RncmVzOi8vZGJ1c2VyQTpwYXNzd29yZEFAMTkyLjE2OC4wLjI0OjU0MzIvZGJhCi0gdXJsOiBwb3N0Z3JlczovL2RidXNlckI6cGFzc3dvcmRCQDE5Mi4xNjguMC4yNDo1NDMyL2RiYgpzdGF0ZW1lbnRzOgotIHVybDogcG9zdGdyZXM6Ly9kYnVzZXJCUmVhZGVyOnBhc3N3b3JkQlJlYWRlckAxOTIuMTY4LjAuMjQ6NTQzMi9kYmIKICBzdGF0ZW1lbnRzOgogIC0gR1JBTlQgU0VMRUNUIE9OIEFMTCBUQUJMRVMgSU4gU0NIRU1BIHB1YmxpYyBUTyBkYnVzZXJCUmVhZGVyOwogIC0gQUxURVIgREVGQVVMVCBQUklWSUxFR0VTIElOIFNDSEVNQSBwdWJsaWMKICAgICAgR1JBTlQgU0VMRUNUIE9OIFRBQkxFUyBUTyBkYnVzZXJCUmVhZGVyOw==
kind: Secret
metadata:
  name: oneshot-secret-7b8fhdcmhg
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
            name: oneshot-cm-g2d5g4dtmc
        image: rosscdh/kubernetes-db-oneshot
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
          secretName: oneshot-secret-7b8fhdcmhg
```