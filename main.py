from __future__ import division
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.cluster import KMeans,DBSCAN,SpectralClustering
from sklearn.manifold import SpectralEmbedding
import jieba
import json
import os
from sklearn.metrics import pairwise_distances,silhouette_score,calinski_harabasz_score,davies_bouldin_score
from scipy.linalg import eigh
import matplotlib.pyplot as plt
import matplotlib
import warnings
import networkx as nx
import tensorflow as tf
from tensorflow.keras import layers, models
from keras.models import Sequential, load_model
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from keras.layers.core import Lambda
from keras.layers import Dense, LSTM, Dropout, Flatten, Activation, Bidirectional, Convolution1D, MaxPool1D, \
    BatchNormalization, GRU
from sklearn.decomposition import LatentDirichletAllocation
from collections import Counter
import math
from datetime import datetime




def cleanse_data(file_name): 
    file=open(file_name+'_new.json','w',encoding='utf8')
    with open(file_name+'.json', 'r',encoding='utf8') as f:
        for item in f.readlines():
            item=item.strip()
            if item[-1]==',':
                item=item[:-1]
            data=json.loads(item)
            data['remark']=data.get('remark','')#change the code here to cleanse your data
            file.write(json.dumps(data,ensure_ascii=False)+'\n')
    file.close()

def check_is_activity():
    cur_path=os.getcwd()
    my_files=os.listdir(cur_path)
    for file in my_files:
        print(file)
        if file[-4:]!='json':
            continue
        elif file=="quotes_guangxi_lib.json" or file=='quotes_henan_lib.json' or file=='quotes_jilin_changchun_lib.json'or file=='quotes_liaoning_dalian_lib.json':#混有新闻数据
            continue
        elif file=='quotes_jiangsu_nanjing_jiangningqu_why.json':#没有activity_name
            continue
        else:
            with open(file, 'r',encoding='utf8') as f:
                for item in f.readlines():
                    item = item.strip()
                    if item[-1] == ',':
                        item = item[:-1]
                    data = json.loads(item)
                    try:
                        my_str=str(data['activity_name'])+str(data['remark'])
                    except Exception as err:
                        print(file+str(err))
                        return

def convert_date():#from timestamp to string
    file=open('quotes_yunnan_qujing_why.json','r',encoding='utf8')
    out_file = open('quotes_yunnan_qujing_why(2).json', 'w', encoding='utf8')
    for item in file.readlines():
        item = item.strip()
        if item[-1] == ',':
            item = item[:-1]
        data = json.loads(item)
        try:
            data['activity_time'] = datetime.fromtimestamp(data['activity_time'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
            out_file.write(json.dumps(data, ensure_ascii=False) + '\n')
        except:
            print(data)




def merge_data():#merges the quotes files 
    cur_path = os.getcwd()
    my_files = os.listdir(cur_path)
    result_file=open('all_quotes_2020.json','w',encoding='utf8')
    count=0
    for file in my_files:
        if file[-4:]!='json':
            continue
        elif file=="quotes_guangxi_lib.json" or file=='quotes_henan_lib.json' or file=='quotes_jilin_changchun_lib.json' or file=='quotes_liaoning_dalian_lib.json':#混有新闻数据
            continue
        elif file=='quotes_jiangsu_nanjing_jiangningqu_why.json':#没有activity_name
            continue
        else:
            with open(file, 'r',encoding='utf8') as f:
                try:
                    for item in f.readlines():
                        item = item.strip()
                        if item[-1] == ',':
                            item = item[:-1]
                        data = json.loads(item)
                        try:
                            year=data['activity_time'].strip()[:4]
                            if(year!='2020'):
                                continue
                            data['geo']=file.split('_')[1]
                            result_file.write(json.dumps(data, ensure_ascii=False) + '\n')
                            count+=1
                        except Exception as err:
                            print("个别数据错误")
                            print(file+str(err))
                except Exception as err:
                    print(file+str(err))
                    print(item)
    print(count)
    result_file.close()

def get_stopwords():#读取停用词表
    "download from:https://github.com/goto456/stopwords"
    file_names=['baidu','cn','scu','hit']
    path='./停用词/'
    my_stopwords=set()
    for file_name in file_names:
        f=open(path+file_name+'_stopwords.txt',encoding='utf8')
        for line in f.readlines():
            line=line.strip()
            if (len(line)>0 and line.isdigit()==False):
                my_stopwords.add(line)
    #2293个停用词
    return my_stopwords

def get_wv():#读取现成词向量
    "download from:https://github.com/Embedding/Chinese-Word-Vectors"
    f=open('sgns.wiki.bigram-char','r',encoding='utf8')
    my_wv={}
    for line in f.readlines():
        line=line.strip().split(' ')
        if(len(line)<=300):
            #print(line[0])
            continue
        #print(len(line))
        my_wv[line[0]]=[]
        for i in range(300):
            my_wv[line[0]].append(float(line[i+1]))
    return my_wv

def k_max_pooling(x, k=3,step=11):
    print("k_max_pooling")
    #print(x.shape)
    x = tf.transpose(x, perm=[1, 0, 2, 3])  # 将步长交换至第一维
    out = []
    for i in range(0,x.shape[0]-step+1,step):
        my_slice = tf.slice(x, begin=[i, 0, 0, 0], size=[step, -1, x.shape[2], x.shape[3]])
        my_slice_converted = tf.transpose(tf.nn.top_k(tf.transpose(my_slice, perm=[3, 1, 2, 0]), k=k).values,
                                          perm=[3, 1, 2, 0])
        out.append(my_slice_converted)
    res = tf.concat(out, axis=0)
    fold = tf.transpose(res, perm=[1, 0, 2, 3])#将步长交换回第二维
    #print(fold.shape)
    return fold

def fold(x):
    print("folding")
    #print(x.shape)
    input_unstack = tf.unstack(x, axis=2)
    #print(len(input_unstack))
    out = []
    with tf.name_scope("fold"):
        for i in range(0,len(input_unstack),2):
            tmp=tf.add(input_unstack[i],input_unstack[i+1])
            out.append(tmp)
        fold = tf.stack(out, axis=2)  # [batch_size, k2, embed_size/2, num_filters[1]]
    #print(fold.shape)
    return fold

def expand(x):
    return tf.expand_dims(x, axis=-1)

def computer_cluster(vec_method='cnn',cluster_method=['kmeans'],num_cluster=3,max_feature=10000):#运行聚类
    "vec_method=tfidf,aver-embedding,cnn; cluster_method:kmeans,dbscan,spectral"
    my_stopwords=get_stopwords()
    my_wv=get_wv()
    all_corpus=[]
    all_labels=[]
    with open('./final/all_quotes_new.json', 'r', encoding='utf8') as f:#读入数据
        for item in f.readlines():
            item = item.strip()
            if item[-1] == ',':
                item = item[:-1]
            data = json.loads(item)
            try:
                my_text=str(data['activity_name'])+" "+str(data['remark'])
            except:
                #print(data['pav_name'])
                continue
            seg_list=jieba.cut(my_text,cut_all=False,HMM=True)
            filtered_text=[]
            for word in seg_list:
                if word not in my_stopwords:
                    filtered_text.append(word)
            all_corpus.append(' '.join(filtered_text))
            all_labels.append(data['geo'])
    matrix=None#向量化后矩阵
    full_data=all_corpus
    all_corpus=all_corpus[:10000]#OOM
    test_size = 3000
    if vec_method=='tfidf':
        vectorizer=CountVectorizer(max_features=max_feature)
        transformer=TfidfTransformer()
        matrix = transformer.fit_transform(vectorizer.fit_transform(all_corpus))
    elif vec_method=='aver-embedding':#average embedding
        vectorizer = CountVectorizer(max_features=max_feature)
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(vectorizer.fit_transform(all_corpus))
        tfidf_word = vectorizer.get_feature_names()
        tfidf_weight = tfidf.toarray()
        matrix=np.zeros((len(all_corpus),300))
        for i in range(len(tfidf_weight)):
            for j in range(len(tfidf_word)):
                try:
                    matrix[i]+=tfidf_weight[i][j]*np.array(my_wv[tfidf_word[i]])
                except Exception as err:
                    print(str(err))
                    continue
    elif vec_method=='cnn':  # training text embeddings with CNN
        vectorizer = CountVectorizer(max_features=max_feature)
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(vectorizer.fit_transform(all_corpus))
        embedding = SpectralEmbedding(affinity='rbf',n_neighbors=3,n_components=64,random_state=0)#Laplacian Eigenmap降维
        LE_embedding = embedding.fit_transform(tfidf)
        print("check LE embedding shape:",LE_embedding.shape)
        median=np.median(LE_embedding.ravel())
        for i in range(len(LE_embedding)):
            #median = np.median(LE_embedding[i])
            for j in range(64):
                if LE_embedding[i][j]<median:#binary code
                    LE_embedding[i][j]=0
                else:
                    LE_embedding[i][j]=1
        ##CNN网络
        ##建立词向量矩阵
        MAX_SEQUENCE_LENGTH=512#可以适当增大
        BATCH_SIZE=64
        EMBEDDING_DIMENSION=300

        test_text=all_corpus[:test_size]
        train_text=all_corpus[test_size:]
        token = Tokenizer(num_words=20000)
        token.fit_on_texts(train_text)
        X_train = token.texts_to_sequences(train_text)
        X_test = token.texts_to_sequences(test_text)
        X_train = sequence.pad_sequences(X_train, maxlen=MAX_SEQUENCE_LENGTH)
        X_test = sequence.pad_sequences(X_test, maxlen=MAX_SEQUENCE_LENGTH)
        word_index=token.word_index
        embedding_matrix = np.zeros((len(my_wv) + 1, EMBEDDING_DIMENSION))
        for word, i in word_index.items():
            embedding_vector = my_wv.get(word)
            if embedding_vector is not None:
                # words not found in embedding index will be all-zeros.
                embedding_matrix[i] = embedding_vector
        embedding_layer = Embedding(len(my_wv) + 1,
                                    EMBEDDING_DIMENSION,
                                    weights=[embedding_matrix],
                                    input_length=MAX_SEQUENCE_LENGTH,
                                    trainable=False)
        model = Sequential()
        model.add(embedding_layer)
        model.add(layers.Lambda(expand))
        model.add(layers.Conv2D(filters=16, kernel_size=(10, 1), activation='relu', padding='valid'))
        model.add(Lambda(k_max_pooling))
        model.add(layers.Conv2D(filters=32, kernel_size=(10, 1), activation='relu', padding='valid'))
        model.add(Lambda(fold))
        model.add(Lambda(k_max_pooling))
        model.add(layers.Dropout(0.5))
        model.add(layers.Flatten())
        model.add(layers.Dense(64, activation='relu'))
        print(model.summary())
        model.compile(optimizer='adagrad',
                      loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                      metrics=['accuracy'])
        history = model.fit(X_train, LE_embedding[test_size:], epochs=10,batch_size=BATCH_SIZE,
                            validation_data=(X_test, LE_embedding[:test_size]))
        #plt.plot(history.history['accuracy'], label='accuracy')
        #plt.plot(history.history['val_accuracy'], label='val_accuracy')
        #plt.xlabel('Epoch')
        #plt.ylabel('Accuracy')
        #plt.legend(loc='lower right')
        #plt.show()
        test_loss, test_acc = model.evaluate(X_test, LE_embedding[:test_size], verbose=2)
        print(test_acc)
        model.save('myModel3.h5')# save the model
        #model= tf.keras.models.load_model('model.h5', compile=False)
        X_all=token.texts_to_sequences(full_data)
        X_all = sequence.pad_sequences(X_all, maxlen=MAX_SEQUENCE_LENGTH)
        matrix = model.predict(X_all)# get text embeddings



    if 'kmeans' in cluster_method:
        print("kmeans cluster")
        kmeans = KMeans(n_clusters=num_cluster, random_state=0).fit(matrix)
        cluster_labels=kmeans.labels_
        save_cluster("kmeans_"+vec_method+"_"+str(num_cluster),cluster_labels)
        evaluate_cluster(matrix, cluster_labels)
    if 'spectral' in cluster_method:
        print("spectral cluster")
        spectral = SpectralClustering(n_clusters=num_cluster,assign_labels = "discretize",random_state = 0).fit(matrix)
        cluster_labels=spectral.labels_
        save_cluster("spectral_" + vec_method+"_"+str(num_cluster), cluster_labels)
        evaluate_cluster(matrix, cluster_labels)
    if 'dbscan' in cluster_method:
        print("dbscan cluster")
        dbscan=DBSCAN().fit(matrix)
        cluster_labels=dbscan.labels_
        save_cluster("dbscan_" + vec_method+"_"+str(num_cluster), cluster_labels)
        evaluate_cluster(matrix,cluster_labels)



def save_cluster(description,labels):#save cluster labels
    f=open("ggwh_cluster"+description+".txt",'w',encoding='utf8')
    for x in labels:
        f.write(str(x)+"\n")
    f.close()


def evaluate_cluster(X,labels):#评估聚类质量  3 cluster metrics
    ##轮廓系数
    print("*" * 50)
    print("start evaluating clusters")
    print("Silhouette score:")
    print(silhouette_score(X, labels, metric='euclidean'))
    print("CH score:")
    print(calinski_harabasz_score(X, labels))
    print("DB score:")
    print(davies_bouldin_score(X,labels))
    print("*"*50)

def plot_top_words(model, feature_names, n_top_words, title):# topics words of LDA
    matplotlib.rc("font", family='MicroSoft YaHei', weight="bold")
    fig, axes = plt.subplots(2, 5, figsize=(30, 15), sharex=True)
    axes = axes.flatten()
    file=open("lda_keywords.txt",'w',encoding='utf8')
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[:-n_top_words - 1:-1]
        top_features = [feature_names[i] for i in top_features_ind]
        for feature in top_features:
            file.write(feature+"\n")
        weights = topic[top_features_ind]

        ax = axes[topic_idx]
        ax.barh(top_features, weights, height=0.7)
        ax.set_title(f'Topic {topic_idx +1}',
                     fontdict={'fontsize': 30})
        ax.invert_yaxis()
        ax.tick_params(axis='both', which='major', labelsize=20)
        for i in 'top right left'.split():
            ax.spines[i].set_visible(False)
        fig.suptitle(title, fontsize=40)
        file.write("\n")
    plt.subplots_adjust(top=0.90, bottom=0.05, wspace=0.90, hspace=0.3)
    plt.show()
    file.close()


def get_topic():#LDA model for topic modelling
    my_stopwords = get_stopwords()
    all_corpus = []
    all_labels = []#地理标签
    lda_results=[]
    with open('./final/all_quotes_new.json', 'r', encoding='utf8') as f:  # 读入数据
        for item in f.readlines():
            item = item.strip()
            if item[-1] == ',':
                item = item[:-1]
            data = json.loads(item)
            try:
                my_text = str(data['activity_name']) + " " + str(data['remark'])
            except:
                # print(data['pav_name'])
                continue
            seg_list = jieba.cut(my_text, cut_all=False, HMM=True)
            filtered_text = []
            for word in seg_list:
                if word not in my_stopwords:
                    filtered_text.append(word)
            all_corpus.append(' '.join(filtered_text))
            all_labels.append(data['geo'])

    vec=CountVectorizer()#使用词频进行转化
    X=vec.fit_transform(all_corpus)
    lda = LatentDirichletAllocation(n_components=10, max_iter=50,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0)
    docres = lda.fit_transform(X)
    for dist in docres:
        dist = dist.tolist()
        review_topic_index = dist.index(max(dist))
        lda_results.append(review_topic_index)
    tf_feature_names = vec.get_feature_names()
    n_top_words=50
    plot_top_words(lda, tf_feature_names, n_top_words, 'Topics in LDA model')
    file=open('lda_results.txt','w',encoding='utf-8')
    for lda_label in lda_results:
        file.write(str(lda_label)+"\n")
    file.close()


def jaccard(counter_a,counter_b):
    "computing the jaccard similarity coefficient"
    #print ("jaccard:",sum((counter_a&counter_b).values())/sum((counter_a|counter_b).values()))
    return sum((counter_a&counter_b).values())/sum((counter_a|counter_b).values())


def count_labels(labels):
    label_dict={}
    for i in labels:
        if i not in label_dict:
            label_dict[i]=1
        else:
            label_dict[i]+=1
    print(label_dict)



def SCAN(sim_dict,geo_set,file_name,threshold_=0.22,epsl_=0.05,u_=8):
    geo_set=list(geo_set)#转化为list
    ###0.22/0.05/8  2个聚类
    ###
    threshold=threshold_#similarity threshold
    epsl=epsl_#density threshold
    u=u_#core threshold
    nodes_num=len(geo_set)
    labels=[0]*nodes_num
    is_core = [0] * nodes_num
    neighbor_dict={}
    for i in range(nodes_num):
        neighbor_dict[i] = set()
    ad_matrix = np.zeros((nodes_num, nodes_num))
    for i in range(nodes_num):
        for j in range(nodes_num):
            if (sim_dict[geo_set[i]][geo_set[j]] >= threshold and j > i):  # set greater threshold if a sparser graph is needed
                ad_matrix[i][j] = 1
                ad_matrix[j][i] = 1
                neighbor_dict[i].add(j)
                neighbor_dict[j].add(i)
            elif (j > i):
                ad_matrix[i][j] = 0
                ad_matrix[j][i] = 0
            elif (j == i):
                ad_matrix[j][i] = 1
                neighbor_dict[i].add(i)
    #print(ad_matrix)  # adjacent matrix
    #print(neighbor_dict)  # neighbors
    sim_matrix = np.zeros((nodes_num, nodes_num))
    # compute similarity matrix
    for i in range(nodes_num):
        for j in range(nodes_num):
            if (j >= i):
                if (len(neighbor_dict[i]) == 0 or len(neighbor_dict[j]) == 0):
                    sim_matrix[i][j] = 0
                # SET SUPPORTS INTERSECTION
                sim_matrix[i][j] = len(neighbor_dict[i].intersection(neighbor_dict[j])) / math.sqrt(
                    len(neighbor_dict[i]) * len(neighbor_dict[j]))
                sim_matrix[j][i] = sim_matrix[i][j]
    for i in range(nodes_num):
        cnt = 0
        for j in neighbor_dict[i]:
            if (sim_matrix[i][j] >= epsl):
                cnt += 1
        if (cnt >= u):
            is_core[i] = 1
    print(is_core)
    ##BEGIN CLUSTERING
    cluster_label = 0
    # ADJUST LABELS FOR HUB AND OUTLIER HERE
    hub_label = -2
    outlier_label = -3
    Q = set()
    for i in range(nodes_num):
        if (labels[i] == 0):  # unclassified
            # check if core or not
            if is_core[i] == 1:
                cluster_label += 1  # generate new label
                for j in neighbor_dict[i]:
                    if (sim_matrix[i][j] >= epsl):
                        Q.add(j)  # add to queue
                while len(Q) > 0:
                    node = Q.pop()
                    R = set()
                    if is_core[node] == 1:  # get accessible vertex
                        for j in neighbor_dict[node]:
                            if (sim_matrix[node][j] >= epsl):
                                R.add(j)
                    for s in R:
                        if (labels[s] == 0):  # DFS for vertexes
                            Q.add(s)
                        if (labels[s] == 0 or labels[s] == -1):  # add to cluster
                            labels[s] = cluster_label

            else:
                labels[i] = -1  # non-member
    for i in range(nodes_num):
        if (labels[i] == -1):  # non-member
            neighbor_set = set()
            for j in range(nodes_num):
                if (i != j and ad_matrix[i][j] == 1 and labels[j] > 0):  # 取出相邻的点
                    neighbor_set.add(labels[j])
            if (len(neighbor_set) > 1):
                labels[i] = hub_label  # hub
            else:
                labels[i] = outlier_label  # outlier
    for a,b in zip(geo_set,labels):#打印聚类结果
        print(a,b)
    print("total clusters:", cluster_label)
    return cluster_label

def cluster_by_region():#clustering on province similarity graph
    n_cluster=4
    cluster_labels=[]
    geo_labels=[]
    geo_dict={}
    geo_set=set()
    sim_dict={}
    cur_path = os.getcwd()
    my_files = os.listdir(cur_path)
    for file in my_files:
        if file[-4:]!='json':
            continue
        else:
            geo_set.add(file.split('_')[1])
    print(geo_set)
    for province in geo_set:
        geo_dict[province]=Counter()
        for i in range(n_cluster):
            geo_dict[province].update({str(i):0})#初始化
    with open('ggwh_clusterkmeans_cnn_'+str(n_cluster)+'.txt','r',encoding='utf8')as f:
        for item in f.readlines():
            item=str(item.strip())
            cluster_labels.append(item)
    with open('./final/all_quotes_new.json', 'r', encoding='utf8') as f:#读入数据
        for item in f.readlines():
            item = item.strip()
            if item[-1] == ',':
                item = item[:-1]
            data = json.loads(item)
            geo_labels.append(data['geo'])
    for a,b in zip(cluster_labels,geo_labels):
        geo_dict[b].update({a:1})
    print(geo_dict)
    ##计算Jaccard相似度
    for prov1 in geo_set:
        for prov2 in geo_set:
            sim=jaccard(geo_dict[prov1],geo_dict[prov2])
            if prov1 not in sim_dict:
                sim_dict[prov1]={}
            if prov2 not in sim_dict[prov1]:
                sim_dict[prov1][prov2]=sim

    """
    #example code for finding appropriate parameters for SCAN algorithm
    threshold_list=[i/100 for i in range(5,70)]
    epsl_list=[i/100 for i in range(3,65)]
    u_list=[i for i in range(3,25)]
    max_cluster=0
    best_epsl=0
    best_threshold=0
    best_u=0
    for threshold in threshold_list:
        for epsl in epsl_list:
            if epsl>threshold:
                continue
            for u in u_list:
                print("threshold:",threshold,"epsl:",epsl,"u:",u)
                res_cluster=SCAN(sim_dict,geo_set,'cnn_kmeans_4_0.5.png',threshold_=threshold,u_=u,epsl_=epsl)
                if res_cluster>max_cluster:
                    max_cluster=res_cluster
                    best_epsl=epsl
                    best_threshold=threshold
                    best_u=u
    print("max clusters computed:",max_cluster)
    print(best_epsl,best_threshold,best_u)#0.45 0.47 3
    """
    ##数据量原因，排除以下省份 removal of following provinces due to data scarcity
    geo_set.remove('xinjiang')
    geo_set.remove('qinghai')
    geo_set.remove('xizang')
    geo_set.remove('hebei')
    geo_set.remove('ningxia')
    print(len(geo_set))
    res_cluster = SCAN(sim_dict, geo_set, 'cnn_kmeans_4_0.5.png', threshold_=0.47, u_=3, epsl_=0.45)#run the SCAN algorithm





#computer_cluster(vec_method='cnn',cluster_method=['kmeans','spectral','dbscan'])
#get_topic()
#cluster_by_region()
