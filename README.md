docker build -t rss_summarizer .
docker run -it --name rss_summarizer -p 5000:5000 --rm rss_summarizer
https://devcenter.heroku.com/articles/container-registry-and-runtime
