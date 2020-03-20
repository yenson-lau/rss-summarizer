# Deploy on Heroku with git
**Add Heroku remote:** `heroku git:remote -a <app_name>`

**Push to Heroku repo:** `git push heroku master`

# Deploy with docker
**Locally**
```
docker build -t rss_summarizer .
docker run -it --name rss_summarizer -p 5000:5000 --rm rss_summarizer
```

**On Heroku**

https://devcenter.heroku.com/articles/container-registry-and-runtime

Assuming Heroku remote already exists:
```
heroku container:login

# this will take a long time and push a large image
heroku container:push web  

heroku container:release web

heroku open  # open Heroku app on browser
```
