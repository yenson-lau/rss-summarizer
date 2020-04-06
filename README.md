# RSS Summarizer
Currently deployed on [Heroku](volatile-steel.herokuapp.com).

## Using the POST methods `texts` and `rss`
See the example JSON POST queries `example_texts.json` and `example_rss.json`.

<br/>

## Deploy on Heroku with git
**Add Heroku remote**<br/>`heroku git:remote -a <app_name>`

**Push to Heroku repo**<br/>`git push heroku master`

<br/>

## Deploy with docker
**Locally**
```
docker build -t rss_summarizer .
docker run -it --name rss_summarizer -p 5000:5000 --rm rss_summarizer
```

**On Heroku**
<br/>
https://devcenter.heroku.com/articles/container-registry-and-runtime

Assuming Heroku remote already exists:
```
heroku container:login

# this will take a long time and push a large image
heroku container:push web  

heroku container:release web

heroku open  # open Heroku app on browser
```
