from threading import Thread
import logging
from pharma_gyan_proj.apps.documents.services.document import Document


class ParallelProcessing(Thread):
    def __init__(self):
        self.user_document = Document()

    def create_doc(self, session_info, data):
        self.user_document.fetch_document(session_info, data)

    def start_process(self, method_name, args=()):
        try:
            target = eval(f"self.{method_name}")
            args = tuple(args)
            thread = Thread(target=target, args=args)
            thread.start()
        except Exception as e:
            logging.error(f"cant create parallel process as exp :{e} for method: {method_name}, log_key: ParallelProcessing")
