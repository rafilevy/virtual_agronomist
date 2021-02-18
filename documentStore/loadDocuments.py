import haystack

converter = haystack.file_converter.txt.TextConverter(
                    remove_numeric_tables=False,
                    valid_languages = ["en"])

as4 = converter.convert(file_path="knowledgeBase/as4-winterBarley.txt")


processor = haystack.preprocessor.preprocessor.PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=True,
    split_by="passage",
    split_length=1,
    split_respect_sentence_boundary=False,
    split_overlap=0
)

as4Docs = processor.process(as4)
# print(as4Docs)

for i in range(0,len(as4Docs)):
    print(i)
    print(":\n")
    print(as4Docs[i])
    print("---------------")

# ! docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.6.2

from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
document_store = ElasticsearchDocumentStore(
    host="localhost",
    username="",
    password="",
    index="document"
)

document_store.delete_all_documents()
document_store.write_documents(as4Docs)

backagain = document_store.get_all_documents();

for i in range(0,len(backagain)):
    print(i)
    print(":\n")
    print(backagain[i])
    print("---------------")
