#!/bin/sh
if [ "$1" = "build" ]; then
  echo Building docker image.
  docker build -t rss_summarizer .
fi
docker run -it --name rss_summarizer -p 5000:5000 --rm rss_summarizer
