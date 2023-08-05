# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 11:19:28 2022

@author: dreji18
"""

# loading the packages
import pandas as pd
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification

import nltk
nltk.download('punkt')
sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
from nltk.tokenize import word_tokenize

# loading the biomedical ner model
tokenizer = AutoTokenizer.from_pretrained("d4data/biomedical-ner-all")
model = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")

# dictionary of common diseases
disease_list = ['covid', 'covid19', 'covid-19', 'coronavirus', 'corona virus']


#%%
def load_model(compute):
    # pass device=0 if using gpu
    if compute == 'gpu':
        pipe = pipeline("ner",
                        model=model,
                        tokenizer=tokenizer,
                        grouped_entities=True,
                        device=0)
    else:
        pipe = pipeline("ner",
                        model=model,
                        tokenizer=tokenizer,
                        grouped_entities=True)
     
    return pipe

def ner_prediction(corpus, compute):

    pipe = load_model(compute)
    
    master_df = pd.DataFrame()
    for sentence in sent_tokenizer.tokenize(corpus):
        pred = pipe(sentence)
    
        pred_df = pd.DataFrame(pred)

        tokenized_sentence = word_tokenize(sentence)
        
        actuall_values_list = []
        for i in range(len(pred_df)):
            pred_text = sentence[pred_df['start'].iloc[i]: pred_df['end'].iloc[i]]
            try:       
                tokenized_pred_text = word_tokenize(pred_text)   
                actual_collection = []
                for i in tokenized_pred_text:
                    for j in tokenized_sentence:
                        if i in j:
                            actual_collection.append(j)
                
                actual_word = ' '.join(actual_collection)
            except:
                actual_word = pred_text
                continue
            
            actuall_values_list.append(actual_word)
            

        pred_df['value'] = actuall_values_list
        
        # checking whether any diseases are missed with disease list
        disease_extraction = []
        for i in disease_list:
            for j in tokenized_sentence:
                if i.lower() in j.strip().lower():
                    disease_extraction.append(j)
                    
        disease_extraction = list(set(disease_extraction))
        disease_df = pd.DataFrame(disease_extraction, columns = ['value'])
        disease_df['score'] = 1
        disease_df['entity_group'] = 'Disease_disorder'
        
        # only if there are predictions for a sentence 
        if len(pred_df) != 0:
            final_df = pred_df[['entity_group', 'value', 'score']]
            
            final_df = final_df.append(disease_df) # adding the disease_df to existing
            
            # final_df = final_df.drop_duplicates(
            #   subset = ['entity_group', 'value'],
            #   keep = 'first')

            master_df = master_df.append(final_df)
            
            master_df = master_df.drop_duplicates(
              subset = ['entity_group', 'value'],
              keep = 'first').reset_index(drop=True)
        
    return master_df






























