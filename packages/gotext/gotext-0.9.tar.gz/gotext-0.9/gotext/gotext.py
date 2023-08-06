import os
from mimetypes import init
import textractplus as tp
from .stopwords import stop_words
import re

class GoDocument:
    """GoText Document Constructor
       
       arguments-

       doc_path : specify document path incase of single document
       docs_dir : specify documents directory incase of multiple documents in a directory

       attributes-

       _supported: returns list of all the supported document formats
       _docs: returns list of documents path
       _text: returns extacted text of documents
       _preprocessed: returns list of preprocessed text, constructed after .preprocess() method call

       methods- 

       preprocess() : preprocess the extracted text and returns a list of preprocessed text
       preprocess(stopwords=True) : preprocess the extracted text as well as remove the stopwords and returns a list of preprocessed text
    """

    _supported=["doc" , "docx" , "dot" , "dotx" , "docm" , "pdf", "pptx" , "pptm" , "txt"]
    _stop_words=stop_words

    def __init__(self,doc_path=None,docs_dir=None) -> None:
        if doc_path and docs_dir:
            raise Exception("GoConstructorError: Please Specify only one argument. (doc_path or docs_dir)")
        if doc_path:
            self._docs=list(doc_path)
            self._text=list(self._extract(doc_path))
        if docs_dir:
            self._docs=list(map(lambda f:os.path.join(docs_dir,f),os.listdir(docs_dir)))
            self._text=list(map(self._extract,self._docs))
        
    def _extract(self,doc_path):
        if not os.path.isfile(doc_path):
                raise Exception("FileError: Specified path is not a file.")
        return tp.process(doc_path).decode('utf-8')

    def _clean(self,text):
            text=text.lower()
            text=re.sub("''"," ",text) 
            text=re.sub(r'[0-9]', ' ', text)
            text=re.sub("_"," ",text)
            text=re.sub("(\\W)+"," ",text)
            text=re.sub('(\\b[a-z] \\b|\\b [a-z]\\b)','',text)
            return text

    def _remove_stopword(self,text):
        text_tokens=text.split(' ')
        for w in self._stop_words:
            if w in text_tokens:
                text_tokens = list(filter((w).__ne__, text_tokens))
        return " ".join(list(filter(lambda val:len(val)>3, text_tokens)))

    def preprocess(self,stopwords=False):
        self._preprocessed=list(map(self._clean,self._text))
        if stopwords:
            self._preprocessed=list(map(self._remove_stopword,self._preprocessed))
        return self._preprocessed
        