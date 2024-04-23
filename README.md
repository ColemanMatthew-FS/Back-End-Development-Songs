# Songs API

## Written in Flask, hosted via Red Hat OpenShift

### How to run (part 1):
1. Access your OpenShift console
2. Enter administrator mode
3. Go to builds > imagestreams > create imagestream
4. Paste this code:

```
apiVersion: image.openshift.io/v1
kind: ImageStream
metadata:
  name: mongo
spec:
  lookupPolicy:
    local: false
  tags:
    - name: latest
      from:
        kind: DockerImage
        name: docker.io/library/mongo:latest
```
5. Click "create"
6. Go to developer > add > container images
7. Choose the “Image stream tag from internal registry” option, then within the imagestream, select “mongo” and for the tag, choose “latest”
8. Leave the remaining options as-is, and select "create"
9. This has created a MongoDB server in your OpenShift namespace

### Part 2:
1. Clone repo to your local machine
2. Open project directory
3. Execute `bash ./bin/setup.sh`
4. Export your namespace as an environment variable using `export OPENSHIFT_PROJECT={your namespace here}`
5. Do the same for your GitHub account
6. Run `oc new-app https://github.com/${GITHUB_ACCOUNT}/Back-End-Development-Songs --strategy=source --name=songs --env MONGODB_SERVICE=mongo.${OPENSHIFT_PROJECT}.svc.cluster.local --name songs` to create a new app
7. You should be able to see the deployment in your OpenShift topology view
8. Expose the application to external requests using `oc expose service/songs`
9. It should be deployed! Test the application's health using

```
curl -X GET http://songs-sn-labs-captainfedo1.labs-prod-openshift-san-a45631dc5778dc6371c67d206ba9ae5c-0000.us-east.containers.appdomain.cloud/health
{
  "status": "OK"
}
```
