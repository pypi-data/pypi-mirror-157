import re, nltk, string, TurkishStemmer
import pandas as pd 
import numpy as np 
import fuzzywuzzy

from sklearn.model_selection import train_test_split


# Performance Metrics 
from sklearn.metrics import mean_squared_error

# PLOT 
import matplotlib.pyplot as plt
import seaborn as sns 


pd.set_option("display.max_columns", None)

"""
DOCUMENTATION 

This script aims to automize repetitive text processing jobs that might be useful in Machine Learning processes.  
    
"""


class TestringProcessor: 
    
    
    def getNumbersfromString(self, string, flag = False):
        
        """[Find all the number from string with regestring]

        Inputs : 
            string : [String] 
            flag : [Boolean] to select return all numbers in list or select first number as integer 
                    True : Returns all the integers in the string 
                    False : Returns first consecutive integer
            
        Returns:
            [List or Integer]: [According to flag]
            
        Usage: 
        a = t.getNumbersfromString("abc123d") --> 123 
        
        
            
        """
        if flag : 
            if type(string) == str : 
                number = re.findall('[0-9]+', string)
                return number 
            else :
                # This for deal with missing values None, NaN , etc
                return string 
        else : 
            if type(string) == str : 
                number = re.findall('[0-9]+', string)
                return int(number[0])

            else : 
                # This for deal with missing values None, NaN , etc
                return string 

    def replace_matches_in_column(self, df, column, string_to_match, min_ratio = 53):
        
        """[Helps to match the words looks similar]
        
        Inputs : 

            df : [pandas.DataFrame]
            column : Column that you want to work with 
            string_to_match : [String]
            min_ratio : [Integer] How much similarity is enough for you 
            
    
        Usage: 
        replace_matches_in_column(df = df , column = 'Country', string_to_match = 'australia')
        
         * australia
         * australie
         * australiEs 
         
         To match mispelled word in the dataframe
        
             
        """
    
        # get a list of unique strings 
        strings = df[column].unique()
        
        # get the top 10 closest matcher in our input string 
        matches = fuzzywuzzy.process.extract(string_to_match, strings , limit = 10 ,
                                             scorer = fuzzywuzzy.fuzz.token_sort_ratio)

        # only get matches with a ratio > min_ratio 
        close_matches = [matches[0] for matches in matches if matches[1] >= min_ratio]

        # get the rows of all the close matches in our dataframe 
        rows_with_matches = df[column].isin(close_matches)
        
        # replace all rows with close matches with the input matches 
        df.loc[rows_with_matches, column] = string_to_match




class analyzeModel: 
    
    def plot_learning_curves(self, model, X, y):
        
        """
        Obj : Objective is to decide whether the model is overfitting or underfitting 
        
        Plots learning curves : 
        
        y - axis : RMSE 
        x - axis : Training Set Size 
        """
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=10)
        train_errors, val_errors = [], []
        for m in range(1, len(X_train) + 1):
            model.fit(X_train[:m], y_train[:m])
            y_train_predict = model.predict(X_train[:m])
            y_val_predict = model.predict(X_val)
            train_errors.append(mean_squared_error(y_train[:m], y_train_predict))
            val_errors.append(mean_squared_error(y_val, y_val_predict))

        plt.plot(np.sqrt(train_errors), "r-+", linewidth=2, label="train")
        plt.plot(np.sqrt(val_errors), "b-", linewidth=3, label="val")
        plt.legend(loc="upper right", fontsize=14)   
        plt.xlabel("Training set size", fontsize=14) 
        plt.ylabel("RMSE", fontsize=14)              
        



class TextProcessor: 
    
    """
    This class is prepared for NLP purposes 
    """
    
    def __init__(self) -> None:
        self.stopwordsAll = ["acaba","ama","aslında","az","bazı","belki","biri","birkaç","birşey","biz","bu","çok","çünkü","da","daha",
                             "de","defa","diye","eğer","en","gibi","hem","hep","hepsi","her","hiç","için","ile","ise","kez","ki","kim","mı","mu","mi","nasıl",
                             "ne","be","neden","nerde","nerede","nereye","niçin","nasıl","o","sanki","şey","siz","ben","şu","tüm","ve","veya","ya","yani"]
    
    
    def preprocess(self,text):
        """String Stripper
        
        - Strip the words 
        - Remove Punctuations 
        - Remove numbers
         
        """

        text = text.lower() 
        text = text.strip()
        text = re.compile('<.*?>').sub(' ', text)
        text = re.compile('[%s]' % re.escape(string.punctuation)).sub(' ', text)
        text = re.sub('\s+', ' ', text)
        text = re.sub(r'\[[0-9]*\]', ' ', text)
        text = re.sub(r'[^\w\s]', '', str(text).lower().strip())
        text = re.sub(r'\d', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    
    def turkishStemmerGit(self, text):
        
        stemmer = TurkishStemmer.TurkishStemmer()
        stemmedword  = [stemmer.stem(word) for word in nltk.word_tokenize(text)]
        return ' '.join(stemmedword)

    
    def stopword(self,string):
        
        a = [i for i in string.split() if i not in self.stopwordsAll]
        return ' '.join(a)


    def finalStep(self, string): 
        
        return self.turkishStemmerGit(self.stopword(self.preprocess(string)))
    
    
class TimeReg: 
    
    
    def __init__(self) -> None:
        pass
    
    def laginvestigate(self, df, target_column): 
        
        df["Lag_1"] = df["target_column"].shift(1)
        df = df.reindex(columns = [target_column, "Lag_1"])
        
        fig, ax = plt.subplots()
        ax = sns.regplot(x = 'Lag_1', y = target_column, data = df, ci = None, scatter_kws= dict(color = '0.25'))
        ax.set_aspect('equal')
        ax.set_title('Lag plor of Target columns')
        plt.show()
    
    def makelags(self, ts, lags, lead_time): 
        
        return pd.concat(
            {
                f'y_lag_{i}' : ts.shift(i) for i in range(lead_time, lags + lead_time)
            },
            axis = 1
        )
    
    
    

#### TEST #### 
# t = TestringProcessor()
# a = t.getNumbersfromString("abc123d")
# print(a)

# t = TestringProcessor()
# a = t.replace_matches_in_column()

#### TEST ####








