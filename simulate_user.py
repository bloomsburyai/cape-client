from cape.client import CapeClient

document_text = "Welcome to the Cape API 0.1. Hopefully it's pretty easy to use."

def upload_cb(monitor):
    print("%s/%s" % (monitor.bytes_read, monitor.len))

c = CapeClient('http://localhost:5050/mock/full/api')
print("Logging in...")
c.login("blo", "bla")
print("Logged in: %s" % c.logged_in())
print("Uploading document via GET parameter...")
document_id1 = c.upload_document("Cape API Documentation", document_text, origin='cape_api.txt')
print("Document ID: %s" % document_id1)
print("Uploading document via file upload")
fh = open("/tmp/cape_api.txt", "w")
fh.write(document_text)
fh.close()
document_id2 = c.upload_document("Cape API Documentation", file_path="/tmp/cape_api.txt")
print("Document ID: %s" % document_id2)
print("Document IDs match: %s" % (document_id1 == document_id2))
print("Large file upload...")
fh = open("/tmp/large_cape_api.txt", "w")
fh.write(document_text * 100000)
fh.close()
document_id = c.upload_document("Large Cape API Documentation", file_path="/tmp/large_cape_api.txt", monitor_callback=upload_cb)
print("Document ID: %s" % document_id)
print("Getting user token...")
token = c.get_user_token()
print("User token: %s" % token)
print("Asking question: Is this API easy to use?")
answers = c.answer(token, 'Is this API easy to use?')
print("Answers: ")
for answer in answers:
    print("\t%s" % answer["text"])
print("Asking question: What colour is the sky?")
answers = c.answer(token, 'What colour is the sky?', offset=1)
print("Answers: ")
for answer in answers:
    print("\t%s" % answer["text"])
print("Logging out...")
c.logout()
print("Logged in: %s" % c.logged_in())
