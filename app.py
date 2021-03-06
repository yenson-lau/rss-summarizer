import json, os, re
import mlflow.pyfunc
import pandas as pd
from flask import Flask, request, jsonify, flash, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from rss_summarizer import summarize, rss_summarize, parse_soup_tgts



# Name of the apps module package
app = Flask(__name__)
app.config['SECRET_KEY'] = 'any secret string'

# Load in the model at app startup
model = mlflow.pyfunc.load_model('models/textrank')



class RequestForm(FlaskForm):
  rss_url = StringField('URL to RSS feed',
                        validators=[DataRequired()],
                        default='https://www.cbc.ca/cmlink/rss-technology')
  html_tgts = StringField('Target elements',
                          validators=[DataRequired()],
                          default="[[('div', {'class': 'story'}), ('p',)]]")
  submit = SubmitField('Summarize')



@app.route('/', methods=['GET', 'POST'])
def rss_demo():
  form = RequestForm()

  if form.validate_on_submit():
    flash(f'Summary requested for URL {form.rss_url.data}...')

    # [ [('div', {'class': 'story'}), ('p',)] ]
    tgts = parse_soup_tgts(form.html_tgts.data)
    if tgts is None:
      return "Error!"
    else:
      rss = {1: {'url':form.rss_url.data, 'tgts':tgts}}
      summary = rss_summarize(rss , model=model, tWidth=85, aLim=5)
      summary = summary.split('\n\n')
      summary = [re.sub(r'\n', r'<br/>', p) for p in summary]
      return render_template( 'rss-summary.html', title='Summary',
                              summary=summary)

  return render_template('rss-summarize.html',
                         title='Summarize', form=form)


@app.route('/rss', methods=['POST'])
def flask_rss_summary():
  req = request.get_json()
  print({'request': req})


  summary = rss_summarize(req['rss'],
                          model=model,
                          mode=req['mode'], length=req['length'],
                          tWidth=85, aLim=req['article_lim'])

  print({'response': summary})
  return summary


@app.route('/texts', methods=['POST'])
def flask_text_summary():
  req = request.get_json()
  print({'request': req})

  summary = summarize(req['data'], model=model, mode=req['mode'], length=req['length'])

  print({'response': summary})
  return jsonify(summary)


# app.run(host='0.0.0.0', port=5000, debug=True)
if __name__ == '__main__':
  # Get port from Heroku to avoid error
  port = int(os.environ.get("PORT", 5000))
  print(f'*** Using port {port}. ***')
  app.run(host='0.0.0.0', debug=True, port=port)
