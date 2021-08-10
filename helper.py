import os
from re import sub
import sys
from git import Repo
import PyPDF2
# import docx2txt
import pandas as pd
import docx
# from win32com import client as wc
from presidio_analyzer import AnalyzerEngine

# w = wc.Dispatch('Word.Application')

TEMP_PATH = './temp'

entities = ["PHONE_NUMBER", "PERSON", "EMAIL_ADDRESS",
            "DATE_TIME", "LOCATION", "DOMAIN_NAME", "NRP"],


def clone_repo(url):
    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_PATH)

    repo_name = os.path.basename(url).split('.')[0]

    local_repo_path = os.path.join(TEMP_PATH, repo_name)

    if not os.path.exists(local_repo_path):
        Repo.clone_from(url, local_repo_path)

    return local_repo_path


def getDocxText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)


def get_text_from_repo_files(path):
    df = pd.DataFrame(columns=['PATH', 'filename', 'Type', 'Page No.', 'Text'])

    exclude = ['.git']
    for path, subdirs, files in os.walk(path):
        subdirs[:] = [dirs for dirs in subdirs if dirs not in exclude]
        for file in files:
            # if file.endswith('.doc'):
            #     print(file)
            #     doc=w.Documents.Open(os.path.join(path, file), )
            #     doc.SaveAs(os.path.join(path, file),16)
            if file.endswith('.pdf'):
                pdf = PyPDF2.PdfFileReader(
                    open(os.path.join(path, file), 'rb'))
                for page in range(pdf.numPages):
                    pageObj = pdf.getPage(page)
                    df.loc[len(df.index), :] = [path, file,
                                                'pdf', page, pageObj.extractText()]
            if file.endswith('.docx'):
                type = file.split('.')[-1]
                text = getDocxText(os.path.join(path, file))
                df.loc[len(df.index), :] = [path, file, type, 0, text]
    return df


def get_annotations(text, entity, analyzer):
    results = analyzer.analyze(text=text, entities=[entity], language='en')
    return [text[result.start: result.end] for result in results]


def get_pii_data(df):
    analyzer = AnalyzerEngine()
    entities = ["PHONE_NUMBER", "PERSON", "EMAIL_ADDRESS",
                "DATE_TIME", "LOCATION", "DOMAIN_NAME", "NRP"]
    for entity in entities:
        df[entity] = df['Text'].apply(
            lambda x: get_annotations(x, entity, analyzer))
    return df.drop('Text', axis=1)
