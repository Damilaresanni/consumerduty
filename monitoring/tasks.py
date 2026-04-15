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

@shared_task
def process_document(document_id: int):
    doc = Document.objects.get(id=document_id)
    
    try:
        doc.status = Document.Status.PROCCESSING
        doc.save()
        
        
        text_blocks  = process_pdf(doc.file.path)
        
        text = "\n".join(block["content"] for block in text_blocks)
        
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
    
    
    
    

@shared_task
def evalFca(query,answer,chunks,findings):
    try:
        retrieval_context=[chunk["text"] for chunk in chunks]
        print(retrieval_context)
        test_case = LLMTestCase(
            input = query,
            actual_output=answer,
            expected_output="NON_COMPLIANT. The phrase 'guaranteed 10% annual returns' violates FCA CONC 3.3.1R.",
            retrieval_context=[chunk["text"] for chunk in chunks],
            
            context = [
            f"{finding.rule_name} from: with description {finding.description} "
            f"based on FCA rule {finding.fca_rule_ref}"
            for finding in findings
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
        

        return {
                "results":results,
                "output":output,
                "status": "completed"
            }
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }