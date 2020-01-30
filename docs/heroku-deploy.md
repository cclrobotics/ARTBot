# Deploying to Heroku
### prerequisites
- [sign up](https://signup.heroku.com/) for a Heroku account (if you don't already have one)
- install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli#download-and-install) 

### deployment steps
Create a new app (optional) and take note of the app name:
```bash
$ heroku create
```

Set the stack of your app to `container`:
```bash
$ heroku stack:set container
```

Add the `heroku` remote to your git repository:
```bash
$ heroku git:remote -a <app>
```
Replace `<app>` with the name of your Heroku app 

Deploy your code to Heroku using Git:
```bash
$ git push heroku master
```
