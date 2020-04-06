# RSS Summarizer
Capstone project for [Aggregate Intellect's](https://ai.science/) NLP and MLOps workshop: see [slides](bit.ly/2xzUbny) and [video](youtu.be/mVaSX-C38GA).

Currently deployed on [Heroku](volatile-steel.herokuapp.com).

<br/>

## Using the POST methods `texts` and `rss`
See the example JSON POST queries `example_texts_*.json` and `example_rss.json` in the `demo` folder, and run something like

```
curl --header "Content-Type: application/json" \
  --request POST \
  --data \'$(cat demo/example_texts_1.json)\' \
  https://volatile-steel.herokuapp.com/texts

curl -X POST -H "Content-Type: application/json" -d @demo/example_texts.json https://volatile-steel.herokuapp.com/texts
```

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
