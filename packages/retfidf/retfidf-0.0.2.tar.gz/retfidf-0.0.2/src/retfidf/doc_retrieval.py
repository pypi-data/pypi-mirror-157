from gensim.models import Word2Vec
import pandas as pd
from gensim.utils import simple_preprocess
from gensim.models import TfidfModel
from gensim import corpora
from scipy import spatial
from tqdm import tqdm
import numpy as np
import math


class doc_retrieval(object):

    # Class that at start-up creates tf-idf weighted document embeddings
    # and then can be used to perform saturation on the basis of a query

    def __init__(self, corpus, size = 300, window = 5, min_count = 5, workers = 4, model = None):
        """

        :param corpus: list of strings
        :param size: size of the embedding vectors (for training)
        :param window: size of the window for the Word2Vec model
        :param min_count: minimum number of times a word must appear in the corpus to be included in the model
        :param workers: number of workers for the Word2Vec model
        :param model: a pretrained Word2Vec model (optional)
        """
        # preprocess
        self.tokenized_documents = [simple_preprocess(doc) for doc in corpus]
        if model is None:
            print('Training the word embeddings')
            # train the word embeddings
            self.model = Word2Vec(sentences = self.tokenized_documents, vector_size=size, window=window, min_count=min_count, workers=workers)
        else:
            self.model = model
        print('Computing the TF-IDF scores')
        # self.scores = self.tfidf(corpus)
        self.dictionary = corpora.Dictionary()
        # create a bag of words for each document
        self.bow = [self.dictionary.doc2bow(doc, allow_update=True) for doc in self.tokenized_documents]
        # create a tf-idf model
        self.tfidf_scores = TfidfModel(self.bow, smartirs='ntc')
        # creaste a dataframe out of the corpus
        print('Creating the Document Embeddings')
        self.df = pd.DataFrame(corpus, columns=['text'])
        # create the tf-idf weighted doc embeddings
        self.df['embeddings'] = self.create_embeddings(self.model, self.tokenized_documents)


    def calculate_similarity(self, query):
        """
        Calculate the similarity between a query and all the documents in the corpus
        :param query: single or multiple words string
        :return: a list of tuples (document, similarity)
        """
        if len(query.split()) > 1:
            embeddings = []
            retained = ''
            # for each word in the query
            for q in query.split():
                try:
                    # get the embedding of the word
                    try:
                        emb = self.model[q]
                    except:
                        emb = self.model.wv[q]
                    retained = retained + q + ' '
                    # add the embedding weighted by the idf to the embedding set
                    embeddings.append(emb * self.idf(q, self.tokenized_documents))

                except:
                    print(f"{q} is not in the vocabulary. It will be omitted.")
            # average the embeddings
            query_embedding = np.mean(embeddings, axis=0)
            print(f'Performing saturation for the following query: {retained}')
        else:
            try:
                try:
                    query_embedding = self.model[query]
                except:
                    query_embedding = self.model.wv[query]
                print(f'Performing saturation for the following query: {query}')
            except:
                print('The query is not in the vocabulary.')
                return
        # create a list of cosine similarities
        similarities = self.df['embeddings'].apply(lambda row: self.cosine_similarity(query_embedding, row))
        # return the cosine similarity
        return similarities

    def cosine_similarity(self, embedding1, embedding2):
        """
        Calculate the cosine similarity between two embeddings
        :param embedding1: a vector
        :param embedding2: another vector
        :return: the cosine similarity
        """
        return 1 - spatial.distance.cosine(embedding1, embedding2)


    def create_embeddings(self, model, corpus):
        """
        Create the embeddings for the documents
        :param model: a trained Word2Vec model
        :param corpus: a list of strings
        :return: a list of vectors
        """
        embedding_set = []
        # for each document in the corpus
        for i in tqdm(range(len(corpus))):
            # create a dictionary of tf-idf scores and words
            temponary = dict(zip([self.dictionary[number[0]] for number in self.tfidf_scores[self.bow][i]],
                                 [number[1] for number in self.tfidf_scores[self.bow][i]]))
            # pick the document
            words = corpus[i]

            # create a list of word embeddings for each word in the document
            embeddings = []
            for word in words:
                try:
                    try:
                        embeddings.append(model[word] * temponary[word])
                    except:
                        embeddings.append(model.wv[word] * temponary[word])
                except:
                    continue
            # create an embedding by averaging the word embeddings
            embedding = np.mean(embeddings, axis=0)

            # add the embedding to the embedding set
            embedding_set.append(embedding)
        # return the embedding set
        return embedding_set

    def idf(self, word, tokenized_documents):
        """
        Calculate the inverse document frequency for a word
        :param word: a single word string
        :param tokenized_documents: a list of strings
        :return: the inverse document frequency
        """
        n = len(tokenized_documents)
        df = 0
        for doc in tokenized_documents:
            if word in doc:
                df += 1
        return math.log(n / df)