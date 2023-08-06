from ...abstasks.AbsTaskClustering import AbsTaskClustering


class TwentyNewsgroupsClustering(AbsTaskClustering):
    @property
    def description(self):
        return {
            "name": "TwentyNewsgroupsClustering",
            "hf_hub_name": "mteb/twentynewsgroups-clustering",
            "description": "Clustering of the 20 Newsgroups dataset (subject only).",
            "reference": "https://scikit-learn.org/0.19/datasets/twenty_newsgroups.html",
            "type": "Clustering",
            "category": "s2s",
            "eval_splits": ["test"],
            "eval_langs": ["en"],
            "main_score": "v_measure",
        }
