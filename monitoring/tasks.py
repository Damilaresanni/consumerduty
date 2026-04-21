from celery import shared_task
from django.utils import timezone
from . nlp import run_spacy_rules
from .eval.eval import save_eval_result

from .models import Document, RuleBasedFinding, DocumentChunk
from .utils import process_pdf, chunk_text
from .vector_store import init_collection, store_chunk_embedding

from deepeval.test_case import LLMTestCase
from deepeval import evaluate
from deepeval.test_case import LLMTestCaseParams
from datetime import datetime
import json
import csv, os



from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    GEval
)

#celery decorator that assigns this document process function to a celery task
@shared_task
def process_document(document_id: int):
    #gets the document object by the document id
    doc = Document.objects.get(id=document_id)
    
    try:
        #query the document status and set it to processing
        doc.status = Document.Status.PROCCESSING
        #save the current state of the document
        doc.save()
        
        #process the pdf using a custom function process_pdf
        text_blocks  = process_pdf(doc.file.path)
        
        #adds a new line after every line in text_blocks
        text = "\n".join(block["content"] for block in text_blocks)
        
        #performs nlp spacy rules on the retrieved texts
        findings = run_spacy_rules(text)
        
        #runs a loop and create a new RuleBasedFinding object
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
        
        #chunks the text using chunk_text function
        chunks = chunk_text(text)
        
        #calls the imported init_collection fucntion
        init_collection()
        
        #loops through the text chunks and create
        # DocumentChunk instance in the database
        for idx, chunk in enumerate(chunks):
            DocumentChunk.objects.create(
                document=doc,
                index=idx,
                text=chunk,
            )
            
            #calls the store_chunk_embedding that stores text embeddings in thr database
            store_chunk_embedding(doc, idx, chunk)
        
        #access and change the status of the document to completed
        doc.status = Document.Status.COMPLETED
        #save the new state of the document
        doc.save()
   
   #excption block to catch unexpected errors
    except Exception as e:
        #set the status of document processing to failed
        doc.status = Document.Status.FAILED
        doc.error_message = str(e)
        doc.save()
        raise
    
    
    
    

@shared_task
def evalFca(query,answer,chunks,findings):
    try:
        test_case = LLMTestCase(
            input = query,
            actual_output=answer,
            expected_output="COMPLIANT",
            retrieval_context=[chunk for chunk in chunks],
            
           context = [
            f"{finding['rule_name']} with description {finding['description']} "
            f"based on FCA rule {finding['fca_rule_ref']}"
            for finding in findings[:3]
        ]
        
        )

        compliance_metric = GEval(
            name="Compliance Accuracy",
            criteria="Check if the output correctly identifies FCA compliance violations and cites the relevant rule.",
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT
            ],
            threshold=0.7
        )
        

        answer_relevancy = AnswerRelevancyMetric(threshold=0.7)
        faithfulness = FaithfulnessMetric(threshold=0.8)
        hallucination = HallucinationMetric(threshold=0.3)
        contextual_precision = ContextualPrecisionMetric(threshold=0.7)
        contextual_recall = ContextualRecallMetric(threshold=0.7)
        
        results = evaluate(
        test_cases=[test_case],
        metrics=[answer_relevancy, faithfulness, 
                compliance_metric,hallucination,
                contextual_precision,
                contextual_recall]
        )
        
        
        output = {
        "timestamp": datetime.now().isoformat(),
        "test_input": test_case.input,
        "actual_output": test_case.actual_output,
        "expected_output": test_case.expected_output,
        "retrieval_context": test_case.retrieval_context,  # PDF chunks
        "context": test_case.context,                      # FCA rule-based findings
        "results": []
        }
        
        
        
        
        save_eval_result(test_case, results, output)
        

        return("success")

        
       
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)  
        }