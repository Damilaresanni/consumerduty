from celery import shared_task
from django.utils import timezone
from . nlp import run_spacy_rules

from .models import Document, RuleBasedFinding, DocumentChunk
from .utils import extract_text, chunk_text
from .vector_store import init_collection, store_chunk_embedding


@shared_task
def process_document(document_id: int):
    doc = Document.objects.get(id=document_id)
    
    try:
        doc.status =Document.Status.PROCCESSING
        doc.save()
        
        text = extract_text(doc.file.path)
        
        findings = run_spacy_rules(text)
        for f in findings:
            RuleBasedFinding.objects.create(
                document=doc, 
                rule_name=f["rule_name"],
                fca_rule_ref=f["fca_ref"],
                description=f["description"], 
                severity=f["severity"], 
                start_char=f["start"],
                end_char=f["end"], 
                snippet=f["snippet"],
            )
            
            chunks = chunk_text(text)
            
            init_collection()
            for idx, chunk in enumerate(chunks):
                DocumentChunk.objects.create(
                    document=doc,
                    index=idx,
                    text=chunk,
                )
                store_chunk_embedding(doc, idx, chunk)
                
                doc.status = Document.Status.COMPLETED
                doc.save()
                
    except Exception as e:
        doc.status = Document.Status.FAILED
        doc.error_message = str(e)
        doc.save()
        raise