# HTTP Functions are not App Engine.

You know Functions are not App Engine. But at times, the HTTP trigger makes it look more equivalent to App Engine. 

Let us look at the features of the App Engine and Function before go further into our topic.

## App Engine:
App Engine is a fully managed, serverless platform for developing and hosting web applications at scale. You can choose from several popular languages, libraries, and frameworks to develop your apps, then let App Engine take care of provisioning servers and scaling your app instances based on demand.
 - Build your application in Node.js, Java, Ruby, C#, Go, Python, or PHP—or bring your language runtime.
 - Custom runtimes allow you to bring any library and framework to App Engine by supplying a Docker container.
 - A fully managed environment lets you focus on code while App Engine manages infrastructure concerns.
 - Google Stackdriver gives you powerful application diagnostics to debug and monitor the health and performance of your app.
 - Easily host different versions of your app, easily create development, test, staging, and production environments.
 - Route incoming requests to different app versions, A/B test, and do incremental feature rollouts.
 - Help safeguard your application by defining access rules with App Engine firewall and leverage managed SSL/TLS certificates* by default on your custom domain at no additional cost.
 - Tap a growing ecosystem of GCP services from your app, including an excellent suite of cloud developer tools.

## Cloud Functions:
Google Cloud Functions is a lightweight compute solution for developers to create single-purpose, stand-alone functions that respond to cloud events without the need to manage a server or runtime environment.
 - The simplest way to run your code in the cloud
 - Automatically scales, highly available and fault-tolerant
 - No servers to provision, manage, patch or update
 - Pay only while your code runs
 - Connects and extends cloud services

## Requirement:
The requirement was to build a rest endpoint which returns random characters. In the real world problem, it could be getting value from Cloud SQL  or any of your backend systems.
I have created the application both in Cloud Functions and App Engine. 

### Function Code:

main.py

```py
import random
import string
	 
def randomString(stringLength=10):
"""Generate a random string of fixed length """
letters = string.ascii_lowercase
return ''.join(random.choice(letters) for i in range(stringLength))
	 
def random_string(request):
return randomString()

```

Pretty simple, stuff. Deployment is pretty easy as well.

### App Engine Code:

main.py

```py
import random
import string
from flask import Flask

app = Flask(__name__)

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return randomString()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

```

app.yaml
```yaml
runtime: python37
```
requirements.txt
```
Flask==1.1.1
```

## Deployment

Before we go further to do the analysis application, here the commands you would need to know to deploy your apps.

### Deploy the Cloud Functions
```
gcloud functions deploy randomstring --entry-point random_string --runtime python37 --trigger-http
```

gcloud GROUP | COMMAND. As we are deploying a Function Group is Functions, while Command is deploy. Followed by Function name you want to deploy or update, randomstring. The entry-point is the function name, random_string. The Runtime, as we are deploying the py app, I have made it as python37. The Trigger Type, trigger-http for the HTTP Trigger.

Enable the API,
```
gcloud services enable cloudfunctions.googleapis.com
```

Clone the repo,
```
git clone https://github.com/srcsakthivel/tantheta-func-versus-app.git
```

Change directory to the functions directory,
```
cd tantheta-func-versus-app/random-string-cloud-functions/
```

Deploy,
```
gcloud functions deploy randomstring --entry-point random_string --runtime python37--trigger-http
```

```
You may get this prompt
Allow unauthenticated invocations of new function [randomstring]?
(y/N)?  Y
Yes, as it is a demo app. May not be recommended for your Production application.
```

HTTPs URL, https://us-central1-your-project-name.cloudfunctions.net/randomstring

### Deploy the App Engine
```
gcloud app deploy app.yaml
```

gcloud GROUP | COMMAND, As we are deploying a App Engine Group is App, while Command is deploy. Unlike the Functions, app.yaml file carries the configuration for App Engine. 

Enable the API,
```
gcloud services enable appengine.googleapis.com
```

Clone the repo,
```
git clone https://github.com/srcsakthivel/tantheta-func-versus-app.git
```

Change directory to the functions directory,
```
cd tantheta-func-versus-app/random-string-appengine/
```

Deploy,
```
gcloud app deploy app.yaml
```

HTTPs URL, https://your-project-name.appspot.com

```
You see a prompt for deployment confirmation. Please confirm with Y.
Do you want to continue (Y/n)?  Y
```

## Let's Test while Deploying new feature

I'm able to access my HTTP Function and APP Engine. 

Now, I want to test the applications while deploying using Apache Bench (AB), AB is a tool for benchmarking Apache Hypertext Transfer Protocol (HTTP) server.

### Install
sudo apt-get install apache2-utils

### Test
#### Cloud Function,

```
ab -n 100 -c 10 https://us-central1-tantheta-demo-project.cloudfunctions.net/randomstring
```

```
Concurrency Level:      10
Time taken for tests:   2.006 seconds
Complete requests:      100
Failed requests:        0
Total transferred:      24504 bytes
HTML transferred:       1000 bytes
Requests per second:    49.85 [#/sec] (mean)
Time per request:       200.588 [ms] (mean)
Time per request:       20.059 [ms] (mean, across all concurrent requests)
Transfer rate:          11.93 [Kbytes/sec] received
```

It took just 2 seconds for 100 requests with 10 concurrent requests.

#### App Engine:
```
ab -n 100 -c 10 https://tantheta-demo-project.appspot.com/
```

```
Concurrency Level:      10
Time taken for tests:   0.930 seconds
Complete requests:      100
Failed requests:        0
Total transferred:      20804 bytes
HTML transferred:       1000 bytes
Requests per second:    107.51 [#/sec] (mean)
Time per request:       93.018 [ms] (mean)
Time per request:       9.302 [ms] (mean, across all concurrent requests)
Transfer rate:          21.84 [Kbytes/sec] received
```

It took less than 1 seconds for 100 requests with 10 concurrent requests.

As our goal is not load testing, I'm bringing down the concurrent request 
to one.

#### Cloud Function

ab -n 1000 -c 1 https://us-central1-tantheta-demo-project.cloudfunctions.net/randomstring

Concurrency Level:      1
Time taken for tests:   49.350 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      245020 bytes
HTML transferred:       10000 bytes
Requests per second:    20.26 [#/sec] (mean)
Time per request:       49.350 [ms] (mean)
Time per request:       49.350 [ms] (mean, across all concurrent requests)
Transfer rate:          4.85 [Kbytes/sec] received

I am updating the function code to return 20 char random string.

def randomString(stringLength=20):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

Let us see how many requests fail while deploying the function.

Step 1: Start the test, ab -n 1000 -c 1 https://us-central1-tantheta-demo-project.cloudfunctions.net/randomstring
Step 2: Trigger the deployment, gcloud functions deploy randomstring --entry-point random_string --runtime python37 --trigger-http

AB Test Response:
Concurrency Level:      1
Time taken for tests:   50.034 seconds
Complete requests:      1000
Failed requests:        233
   (Connect: 0, Receive: 0, Length: 233, Exceptions: 0)
Total transferred:      247358 bytes
HTML transferred:       12330 bytes
Requests per second:    19.99 [#/sec] (mean)
Time per request:       50.034 [ms] (mean)
Time per request:       50.034 [ms] (mean, across all concurrent requests)
Transfer rate:          4.83 [Kbytes/sec] received

I see 233 requests failed. You may see a different number based on your when you trigger the deployment.

#### App Engine

ab -n 1000 -c 1 https://tantheta-demo-project.appspot.com/

Concurrency Level:      1
Time taken for tests:   48.122 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      208020 bytes
HTML transferred:       10000 bytes
Requests per second:    20.78 [#/sec] (mean)
Time per request:       48.122 [ms] (mean)
Time per request:       48.122 [ms] (mean, across all concurrent requests)
Transfer rate:          4.22 [Kbytes/sec] received

I am updating the app engine main.py code to return 20 char random string.

def randomString(stringLength=20):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

Let us see how many requests fail while deploying the app engine, this time.

Step 1: Start the test, ab -n 1000 -c 1 https://tantheta-demo-project.appspot.com/
Step 2: Trigger the deployment, gcloud app deploy app.yaml -q

AB Test Response:
Concurrency Level:      1
Time taken for tests:   44.991 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      251020 bytes
HTML transferred:       30000 bytes
Requests per second:    22.23 [#/sec] (mean)
Time per request:       44.991 [ms] (mean)
Time per request:       44.991 [ms] (mean, across all concurrent requests)
Transfer rate:          5.45 [Kbytes/sec] received

Yes, zero failures. I tried multile times all the time the failure. User might get route until close the session, but won't see any downtime.

#### App Engine - No-Promote & Split


##### Promote
Promote the deployed version to receive all traffic. Overrides the default app/promote_by_default property value for this command invocation. Use --no-promote to disable

##### Splitting Traffic
You can use traffic splitting to specify a percentage distribution of traffic across two or more of the versions within a service. Splitting traffic allows you to conduct A/B testing between your versions and provides control over the pace when rolling out features.

So, I am bumping the default length to 30, triggering test and deployment again. But this time no-promote, so there won't be any disturbance to the end user during the deployment.

```
gcloud app deploy app.yaml -q --no-promote
```
```
Concurrency Level:      1
Time taken for tests:   48.466 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      241020 bytes
HTML transferred:       20000 bytes
Requests per second:    20.63 [#/sec] (mean)
Time per request:       48.466 [ms] (mean)
Time per request:       48.466 [ms] (mean, across all concurrent requests)
Transfer rate:          4.86 [Kbytes/sec] received
```

Though Zero failure, but our updates are not live yet. The lever to pull a no-downtime deployment is the set-traffic splits.

```
gcloud app services set-traffic --splits 20191124t211222=.5,20191124t215758=.5
```
```
Concurrency Level:      1
Time taken for tests:   51.987 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      241024 bytes
HTML transferred:       20000 bytes
Requests per second:    19.24 [#/sec] (mean)
Time per request:       51.987 [ms] (mean)
Time per request:       51.987 [ms] (mean, across all concurrent requests)
Transfer rate:          4.53 [Kbytes/sec] received
```

Set traffic for 100%,
```
Concurrency Level:      1
Time taken for tests:   47.821 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      251020 bytes
HTML transferred:       30000 bytes
Requests per second:    20.91 [#/sec] (mean)
Time per request:       47.821 [ms] (mean)
Time per request:       47.821 [ms] (mean, across all concurrent requests)
Transfer rate:          5.13 [Kbytes/sec] received
```

### Conclusion:
Yeah, the HTTP trigger function makes it a candidate for simple web-api. But in reality, it lacks some of the necessary capability of no-downtime deployments, when you need it.
On the other hand, we have given appengine with all the necessary capability for a complete web-api/app.
