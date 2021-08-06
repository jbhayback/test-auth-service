# test-auth-service

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#setup">Setup</a></li>
      </ul>
    </li>
    <li><a href="#auth-service-endpoints">Auth Service Endpoints</a></li>
    <li><a href="#entity-relationship-diagrams">Entity Relationship Diagrams</a></li>
    <li><a href="#user-interface">User Interface</a></li>
    <li><a href="#other-endpoints">Other Endpoints</a></li>
    <li><a href="#testing">Testing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>


## About The Project

**Authentication API Service**

This project is a basic authentication flow service - with roles and permissions.

### Built With
* [Django](https://www.djangoproject.com/) - Web
* [Django Rest Framework](https://www.django-rest-framework.org/) - API
* [Bootstrap](https://getbootstrap.com/) - UI

## Getting Started
- ### Prerequisites
  - Local
    * [Python](https://www.python.org/) (at least version 3.7)
    * [PostgreSQL](https://www.postgresql.org/)
    * [virtualenv](https://virtualenv.pypa.io/en/latest/)
  - Docker Compose
    * [Docker](https://www.docker.com/)
      * [Installation](https://docs.docker.com/engine/install/)
    * [Docker compose](https://docs.docker.com/compose/)
      * [Installation](https://docs.docker.com/compose/install/)
  - Minikube
    * [Minikube](https://minikube.sigs.k8s.io/docs/)
      * [Installation](https://v1-18.docs.kubernetes.io/docs/tasks/tools/install-minikube/)
    * [kubectl](https://kubernetes.io/docs/reference/kubectl/overview/)
      * [Installation](https://kubernetes.io/docs/tasks/tools/)

## Auth Service Endpoints
 - **User Signup**
    * `POST` - signup with a username, password and an email
        * `username`
        * `email`
        * `paswword`
    * ![signup-diagram](https://github.com/jbhayback/test-auth-service/blob/master/UMLDiagrams/signup.png)
 ```
  /api/signup
 ```
 - **User Login**
    * `POST` - Login with username, password or email, password combo. Token will be issued to be used for authorization
        * `username` - can be email or password
        * `paswword`
    * ![login-diagram](https://github.com/jbhayback/test-auth-service/blob/master/UMLDiagrams/login.png)
 ```
  /api/login
 ```
  - **Permissions**
    * `GET` - get all available permissions
    * `POST` - create new permissions
        * `codename` - permission codename
        * `name` - permission verbose name
    * ![permissions-diagram](https://github.com/jbhayback/test-auth-service/blob/master/UMLDiagrams/permissions.png)
 ```
  /api/permissions
 ```
- **Roles**
    * `GET` - get all available roles
    * `POST` - create roles with specific permission
        * `permission_codename` - codename of permission to be associated with the new role
        * `role_name` - role name to be created
    * ![roles-diagram](https://github.com/jbhayback/test-auth-service/blob/master/UMLDiagrams/roles.png)
 ```
  /api/roles
 ```
- **User Roles**
    * `GET` - retrieve all available roles of a specific user
    * `POST` - create roles with certains permission for a specific user
        * `roles` - comma-separated list of roles
        * `id` - user id
     * ![user-roles-diagram](https://github.com/jbhayback/test-auth-service/blob/master/UMLDiagrams/user_roles.png)
 ```
  /api/users/{:id}/roles
 ```
- **User Permissions**
    * `POST` - retrieve all available permissions specific a user
        * `permission_ids` - comma-separated list of permission id to be queried
        * `id` - user id
    * ![user-permissions-diagram](https://github.com/jbhayback/test-auth-service/blob/master/UMLDiagrams/user_permissions.png)
 ```
  /api/users/{:id}/permissions
 ```

 ## Entity Relationship Diagrams
 - You can access the ERDs in [ERDiagrams](https://github.com/jbhayback/test-auth-service/tree/master/ERDiagrams) folder.

 ## User Interface
 - User Signup
 ```
  /signup
 ```
 - User Login
 ```
  /login
 ```
  - User Permissions Dashboard
 ```
  /dashboard
 ```

## Other Endpoints
 - Api Docs - API documentation
 ```
  /api/docs
 ```
 - Api Schema
 ```
  /api/schema/
 ```

## Setup
- ## Local Setup
    - Create python virtual env and activate it
    ```
    $ virtualenv -p python .venv
    ```
    - Install required python modules
    ```
    $ pip install -r api/requirements.txt
    ```
    - Rename .env.to.rename to .env to use already configured env file
    ```
    $ mv .env.to.rename .env
    ```
    - Create database in postgres DB
    ```
    $ sudo su postgres
    $ psql
    postgres=# CREATE USER django WITH PASSWORD 'password';
    postgres=# ALTER ROLE django SET client_encoding TO 'utf8';
    postgres=# ALTER ROLE django SET default_transaction_isolation TO 'read committed';
    postgres=# ALTER ROLE django SET timezone TO 'UTC';
    postgres=# CREATE DATABASE auth_service;
    postgres=# GRANT ALL PRIVILEGES ON DATABASE auth_service TO django;
    postgres=# \q
    $ exit
    ```
    - Run Migrations and the Server
    ```
    $ python api/manage.py migrate && python api/manage.py runserver 0.0.0.0:8000
    ```
    - Perform **`createsuperuser`** before using the API. You will be asked to input email, username and password for the admin you want to create.
    ```
    $ python api/manage.py createsuperuser
    ```

- ## Docker Compose Setup
    - Rename .env.to.rename to .env to use already configured env file
    ```
    $ mv .env.to.rename .env
    ```
    - Build `app` and `db` images
    ```
    $ docker-compose build
    ```
    - Run application and services
    ```
    $ docker-compose up
    ```
    - In another opened terminal instance within the same project directory, perform **`createsuperuser`** before using the API. You will be asked to input email, username and password for the admin you want to create.
    ```
    $ docker-compose run app python ./api/manage.py createsuperuser
    ```
- ## Minikube Deployment Setup
    - Rename .env.to.rename to .env to use already configured env file
    ```
    $ mv .env.to.rename .env
    ```
    - Start minikube
    ```
    $ minikube start
    ```
    - Enable the Ingress and Metric Server in your minikube.
    ```
    $ minikube addons enable ingress
    $ minikube addons enable metrics-server
    ```
    - Configure your docker CLI to point to the minikube VM
    ```
    $ eval $(minikube docker-env)
    ```
    - Build `app` and `db` images
    ```
    $ docker-compose build
    ```
    - Deploy app and db to minikube
    ```
    $ kubectl apply -f kube_deployment/
    ```
    - Check all the pods running after deployment. You should see 2 pods with prefix `app` and `db`. You can see something like on the image below:
      * ![kubectl-get-pods-example](https://github.com/jbhayback/test-auth-service/blob/master/api/static/screenshots/kubectl-get-pods-example.JPG)
    ```
    $ kubectl get pods
    ```
    - Perform **`createsuperuser`** in `app` pod before using the API. You will be asked to input email, username and password for the admin you want to create.
    ```
    $ kubectl exec <app-podname> -it python ./api/manage.py createsuperuser
    ```
    - To access the app, get host and port and use the `URL`(host) provided to access the application. See example image below.
      * ![minikube-service-app-example](https://github.com/jbhayback/test-auth-service/blob/master/api/static/screenshots/minikube-service-app-example.JPG)

    ```
    $ minikube service app
    ```

 ## Testing
 - ### Unit Testing
    - **Local**
    ```
    $ python ./api/manage.py test auth --noinput
    ```
    - **Docker Compose**
    ```
    $ docker-compose run app python ./api/manage.py test auth
    ```
    - **Minikube**
    ```
    $ kubectl exec <app-podname> -it python ./api/manage.py test auth
    ```
- ### Functional Testing
    - Access
        * http:localhost:8000/signup/ - signup
        * http:localhost:8000/login/ - login
        * http:localhost:8000/dashboard/ - user permissions dashboard (you have to be logged in before you can access it)
    - For minikube, the links will be dependent on the host and port (`URL`) that will be provided after executing the code below.
    ```
    $ minikube service app
    ```
    - **IMPORTANT**: For `dashboard` to have values displayed, roles with certain permissions has to be added to the user first. If a user has not been assigned with any role, then he has no permissions yet.

 # Contact
- You can contact me via email:jbhayback@gmail.com for more info or if there are errors during the setup.
