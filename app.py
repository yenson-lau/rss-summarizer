import json, re
import mlflow.pyfunc
import pandas as pd
from flask import Flask, request, jsonify, flash, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from rss_summarizer import rss_summarize, parse_soup_tgts


class RequestForm(FlaskForm):
  rss_url = StringField('URL to RSS feed',
                        validators=[DataRequired()],
                        default='https://www.cbc.ca/cmlink/rss-technology')
  html_tgts = StringField('Target elements',
                          validators=[DataRequired()],
                          default="[[('div', {'class': 'story'}), ('p',)]]")
  submit = SubmitField('Summarize')

# Name of the apps module package
app = Flask(__name__)
app.config['SECRET_KEY'] = 'any secret string'

# Load in the model at app startup
model = mlflow.pyfunc.load_model('models/textrank')



# Meta data endpoint
@app.route('/', methods=['GET', 'POST'])
def hello_world():
  return "Hello World!"



@app.route('/rss', methods=['GET', 'POST'])
def req_rss_sum():
  form = RequestForm()

  if form.validate_on_submit():
    flash(f'Summary requested for URL {form.rss_url.data}...')

    # [ [('div', {'class': 'story'}), ('p',)] ]
    tgts = parse_soup_tgts(form.html_tgts.data)
    if tgts is None:
      return "Error!"
    else:
      rss = {1: {'url':form.rss_url.data, 'tgts':tgts}}
      summary = rss_summarize(rss , tWidth=85, aLim=5)
      summary = summary.split('\n\n')
      summary = [re.sub(r'\n', r'<br/>', p) for p in summary]
      return render_template( 'rss-summary.html', title='Summary',
                              summary=summary)

  return render_template('rss-summarize.html',
                         title='Summarize', form=form)



# Prediction endpoint
@app.route('/predict', methods=['POST'])
def predict():
  req = request.get_json()

  # Log the request
  print({'request': req})

  # Format the request data in a DataFrame
  inf_df = pd.DataFrame(req['data'])

  # Get model prediction - convert from np to list
  pred = model.predict(inf_df).tolist()

  # Log the prediction
  print({'response': pred})

  # Return prediction as reponse
  return jsonify(pred)

# app.run(host='0.0.0.0', port=5000, debug=True)
if __name__ == '__main__':
  app.run(debug=True)
