import os, shutil
import mlflow
import nltk
import pip
import summa.summarizer
import sumy
from mlflow import pyfunc
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer

import warnings
warnings.filterwarnings('ignore')


CONDA_ENV = { 'name': 'mlflow-env',
              'channels': ['defaults'],
              'dependencies': ['python=3.6.10', {
                'pip':[ f'mlflow=={mlflow.__version__}',
                        f'cloudpickle==1.3.0',
                        f'pip=={pip.__version__}',
                        f'nltk=={nltk.__version__}',
                        f'pandas==1.0.3',
                        f'summa==1.2.0',
                        f'sumy=={sumy.__version__}' ]
              } ] }

def save_pyfunc(model_path, model, artifacts, code_path):
  if os.path.isdir(model_path):
    shutil.rmtree(model_path)

  pyfunc.save_model(path=model_path, python_model=model,
                    conda_env=CONDA_ENV, artifacts=artifacts,
                    code_path=code_path)


# Any downloading that needs to happen
nltk.download('punkt')


class TextRank:
  def __init__(self):
    self.tokenizer = Tokenizer("english")
    self.parser = lambda t: PlaintextParser.from_string(t, self.tokenizer)
    self.sent_summarizer = summarizer = TextRankSummarizer()

  def get_words(self, text, words=50):
    return summa.summarizer(text, words=words)

  def get_sents(self, text, sentences=3):
    summary = self.sent_summarizer(self.parser(text).document, sentences)
    summary = ' '.join(map(str, summary))
    return summary

  def __call__(self, text, mode='sentences', length=3):
    assert mode in ['words', 'sentences'], \
      "mode must either be 'words' or 'sentences."
    assert type(length) is int, 'length must be an integer.'

    method = self.get_words if mode=='words' else self.get_sents
    return method(text, length)


  def package(self, model_path='models/textrank'):
    class ModelWrapper(pyfunc.PythonModel):
      def load_context(self, context):
        import nltk
        from models import TextRank

        self.model = TextRank()

      def predict(self, context, model_input):
        preds = []
        for row in model_input.iloc:
          text, mode, length = row['text'], row['mode'], int(row['length'])
          preds.append(self.model(text, mode, length))
        return preds

    artifacts = {'example': 'assets/example.txt'}
    code_path = ['models.py']
    save_pyfunc(model_path, ModelWrapper(), artifacts, code_path)


if __name__ == '__main__':
  TextRank().package()
