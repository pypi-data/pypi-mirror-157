from ...abstasks.AbsTaskRetrieval import AbsTaskRetrieval
from ...abstasks.BeIRTask import BeIRTask


class CQADupstackRetrieval(AbsTaskRetrieval, BeIRTask):
    @property
    def description(self):
        return {
            "name": "CQADupstackRetrieval",
            "beir_name": "cqadupstack",
            "description": "CQADupStack: A Benchmark Data Set for Community Question-Answering Research",
            "reference": "http://nlp.cis.unimelb.edu.au/resources/cqadupstack/",
            "type": "Retrieval",
            "category": "s2s",
            "eval_splits": ["test"],
            "eval_langs": ["en"],
            "main_score": "map",
        }
