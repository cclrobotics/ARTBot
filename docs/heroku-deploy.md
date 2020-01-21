# Deploying to Heroku
### prerequisites
- [sign up](https://signup.heroku.com/) for a Heroku account (if you don't already have one)
- install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli#download-and-install) 

### deployment steps
Create a new app (optional) and take note of the app name:
```bash
$ heroku create
```
Log in to the Heroku container registry:
```bash
$ heroku container:login
```
Build the production image and tag it:
```bash
$ docker build -f Dockerfile.prod -t registry.heroku.com/<app>/web:$(git rev-parse
--short HEAD) .
```
Make sure to replace `<app>` with the name of the Heroku app that you created in the first step.

Push the image to the registry:
```bash
$ docker push registry.heroku.com/<app>/web:$(git rev-parse --short HEAD)
```
Release the image to the registry:
```bash
$ heroku container:release web
```

Check your logs for errors:
```bash
heroku logs
```
