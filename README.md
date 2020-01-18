# kubernetes-db-oneshot

Create multiple databases and users on postgres databases as a kube Job

## Building

```
make build
```

## Using

* Will install into default ns by default, but feel free to override with `namespace: whatever`

```
kustomize build --load_restrictor none k8s | kubectl apply -f
>
apiVersion: v1
data:
  MASTER_DB_URL: postgres://postgres:postgres@postgres.svc.default:5432/postgres
kind: ConfigMap
metadata:
  name: oneshot-cm-dcd942hkht
---
apiVersion: v1
data:
  oneshot.yaml: ZGJzOgotIHVybDogcG9zdGdyZXM6Ly9kYnVzZXJBOnBhc3N3b3JkQUBsb2NhbGhvc3Q6NTQzMi9kYmEKICAjIGJlZm9yZTogW10KLSB1cmw6IHBvc3RncmVzOi8vZGJ1c2VyQjpwYXNzd29yZEJAbG9jYWxob3N0OjU0MzIvZGJiCiAgIyBwZXJtaXNzaW9uczoKICAjICAgLSBhbGwgcHJpdmlsZWdlcwogICMgYWZ0ZXI6IFtdCi0gdXJsOiBwb3N0Z3JlczovL2RidXNlckJSZWFkZXI6cGFzc3dvcmRCUmVhZGVyQGxvY2FsaG9zdDo1NDMyL2RiYgogICMgcGVybWlzc2lvbnM6CiAgIyAgIC0gU0VMRUNUCiAgIyAgIC0gVVBEQVRFCiAgIyAgIC0gQ1JFQVRFCiAgIyBhZnRlcjogW10=
kind: Secret
metadata:
  name: oneshot-secret-ct96f4m9gt
type: Opaque
---
apiVersion: batch/v1
kind: Job
metadata:
  name: oneshot
spec:
  activeDeadlineSeconds: 100
  backoffLimit: 15
  template:
    spec:
      containers:
      - envFrom:
        - secretRef:
            name: oneshot-cm
        image: rosscdh/kubernetes-db-oneshot
        name: oneshot
        volumeMounts:
        - mountPath: /oneshot/oneshot.yaml
          name: oneshot-yaml
          readOnly: true
      restartPolicy: Never
      volumes:
      - name: oneshot-yaml
        secret:
          items:
          - key: oneshot.yaml
          secretName: oneshot-secret-ct96f4m9gt
```