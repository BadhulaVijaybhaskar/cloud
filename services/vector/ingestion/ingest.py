import os
import psycopg2
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
from embed import EmbeddingService

class DataIngestionPipeline:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.connect_milvus()
        self.connect_postgres()
    
    def connect_milvus(self):
        connections.connect("default", host=os.getenv("MILVUS_HOST", "localhost"), port="19530")
    
    def connect_postgres(self):
        self.pg_conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    
    def create_collection(self, collection_name="documents"):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)
        ]
        schema = CollectionSchema(fields, "Document collection")
        collection = Collection(collection_name, schema)
        return collection
    
    def chunk_text(self, text, chunk_size=1000):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks
    
    def ingest_from_postgres(self, table_name, text_column):
        cursor = self.pg_conn.cursor()
        cursor.execute(f"SELECT id, {text_column} FROM {table_name}")
        
        collection = self.create_collection()
        
        for row in cursor.fetchall():
            doc_id, text = row
            chunks = self.chunk_text(text)
            
            for chunk in chunks:
                embedding = self.embedding_service.get_embedding(chunk)
                collection.insert([[chunk], [embedding]])
        
        collection.flush()
        cursor.close()

if __name__ == "__main__":
    pipeline = DataIngestionPipeline()
    pipeline.ingest_from_postgres("documents", "content")