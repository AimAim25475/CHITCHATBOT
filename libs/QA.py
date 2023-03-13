from haystack.utils import convert_files_to_docs
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.pipelines import ExtractiveQAPipeline
from haystack.nodes import FARMReader, EmbeddingRetriever

import os
os.environ["CUDA_VISIBLE_DEVICES"]= "1"

host = "190.92.214.247"
index = "once"
embedding_model = 'timpal0l/mdeberta-v3-base-squad2'
model_name = 'models/deberta_iapp_lst20_CMSK_model' # p'knot
threshold = 0.35

data_dir = "context" #folder ที่เก็บ context

print("preparing qa model")
got_docs = convert_files_to_docs(dir_path=data_dir)

document_store = ElasticsearchDocumentStore(host=host,index=index,analyzer="thai",similarity="dot_product",embedding_dim=768) #embedding_dim ตามโมเดลที่เราใช้
# document_store = ElasticsearchDocumentStore(host="190.92.214.247",index="text_dataset",analyzer="thai",similarity="dot_product",embedding_dim=768)
document_store.write_documents(got_docs)
retriever = EmbeddingRetriever(document_store=document_store,max_seq_len=512,progress_bar=False, embedding_model=embedding_model) 
# sentence-transformers/clip-ViT-B-32-multilingual-v1 512
# sentence-transformers/distiluse-base-multilingual-cased-v2  512
document_store.update_embeddings(retriever,index,batch_size=8)

reader=FARMReader(model_name_or_path=model_name,use_gpu=True, max_seq_len=512, doc_stride=100, batch_size=8,progress_bar=False)
pipe = ExtractiveQAPipeline(reader, retriever)

print("preparing qa model ok")

def predict(quest, ret_tk=48, red_tk=5):
    prediction = pipe.run(
            query=quest, params={"Retriever": {"top_k": ret_tk}, "Reader": {"top_k": red_tk}}
    )
    score = prediction['answers'][0].score

    return prediction['answers'][0].answer if score >= threshold else None