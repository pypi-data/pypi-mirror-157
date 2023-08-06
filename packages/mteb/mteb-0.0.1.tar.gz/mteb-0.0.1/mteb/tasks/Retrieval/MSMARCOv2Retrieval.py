from ...abstasks.AbsTaskRetrieval import AbsTaskRetrieval
from ...abstasks.BeIRTask import BeIRTask


class MSMARCOv2(AbsTaskRetrieval, BeIRTask):
    @property
    def description(self):
        return {
            "name": "MSMARCOv2",
            "beir_name": "msmarco-v2",
            "reference": "https://microsoft.github.io/msmarco/TREC-Deep-Learning.html",
            "type": "Retrieval",
            "category": "s2s",
            "eval_splits": ["dev1", "dev2"],
            "eval_langs": ["en"],
            "main_score": "map",
        }
