import re

from analyzer_base import AnalyzerBase


class NaiveAnalyzer(AnalyzerBase):

    def __init__(self):
        pass

    def analyze(self, text):
        result = re.search('math.', text)
        if result is None:
            return None
        else:
            return re.findall(r"([^.]*?math.[^.]*\.)", text)
