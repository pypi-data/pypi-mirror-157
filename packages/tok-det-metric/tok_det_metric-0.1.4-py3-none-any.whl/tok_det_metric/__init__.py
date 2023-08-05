""" TokDet metric. """

from typing import Dict, List, Tuple

import datasets
import numpy as np
from more_itertools import chunked
from tqdm import tqdm


_CITATION = """\
@misc{havens2022td,
    title  = {TokDet metric},
    author = {Sam Havens, Aneta Melisa Stal},
    year   = {2022}
}
"""

_DESCRIPTION = """\
Tok Det is a metric used to evaluate token detection algoritms for token tagging imbalanced problems.
"""

_KWARGS_DESCRIPTION = """
Compute TokDet.
Args:
    predictions: List[List[int]]
    references: List[List[int]]
Returns:
    "tp": True Positive Count
    "fp": False Positive Count
    "fn": False Negative Count
    "precision": Precision
    "recall": Recall
    "F05": F0.5
    "F2": F2
Examples:
    >>> td_metric = datasets.load_metric("td.py")
    >>> td_metric._load_data([0, 0, 1])
    >>> td_metric._save_to(path/to/some/dir)
    >>> td_metric.compute(predictions=[0, 1, 1], references=[0, 0, 1])
    {'tp': 1, 'fp': 1, 'fn': 0, 'precision': 0.5, 'recall': 1.0, 'f05': ...}
"""


@datasets.utils.file_utils.add_start_docstrings(_DESCRIPTION, _KWARGS_DESCRIPTION)
class TokDet(datasets.Metric):
    def __init__(self, debug=False, *args, **kwargs):
        super(TokDet, self).__init__(*args, **kwargs)
        self.origs = []
        self.cors = []
        self.debug = debug

    def _load_from_generator(self, data_generator) -> None:
        inputs = []
        references = []
        for i in tqdm(range(len(data_generator))):
            sample = inputs_generator[i]
            inputs.append(sample["input_ids"])
            references.append(sample["labels"])
        return inputs, references

    def _load_data(self, origs: List[List[int]], cors: List[List[int]]):
        self.origs = origs
        self.cors = cors

    def _info(self):
        return datasets.MetricInfo(
            description=_DESCRIPTION,
            citation=_CITATION,
            inputs_description=_KWARGS_DESCRIPTION,
            features=datasets.Features(
                {
                    "predictions": datasets.Sequence(datasets.Value("int32")),
                    "references": datasets.Sequence(datasets.Value("int32")),
                }
            )
        )

    def _compare(self, o, c, p, zero_label=0):
        tp = 0
        fp = 0
        fn = 0

        assert len(o) == len(p), "length not equal!"

        for o_i, c_i, p_i in zip(o, c, p):
            # fp, tn
            if c_i == 0:
                if p_i > 0:
                    fp += 1
                # else tn do nothing
            else:
                # tp, fn
                if p_i == 0:
                    fn += 1
                elif c_i == p_i:
                    tp += 1
                else:
                    # missed category counts as fp
                    fp += 1
        
        return tp, fp, fn

    def _compute(
        self, predictions: List[List[int]], references: List[List[int]]
    ) -> Dict[str, float]:
        tp_agg, fp_agg, fn_agg = 0, 0, 0


        for o, c, p in tqdm(
            zip(self.origs, self.cors, predictions), total=len(self.origs)
        ):

            tp, fp, fn = self._compare(o, c, p)
            tp_agg += tp
            fp_agg += fp
            fn_agg += fn

        precision = tp_agg / (fp_agg + tp_agg) if fp_agg * tp_agg else 0
        recall = tp_agg / (tp_agg + fn_agg) if tp_agg * fn_agg else 0
        f05 = (
            1.25 * precision * recall / (0.25 * precision + recall)
            if precision * recall
            else 0
        )
        f2 = (
            (5 * precision * recall) / (4 * precision + recall)
            if precision * recall
            else 0
        )

        return {
            "tp": tp_agg,
            "fp": fp_agg,
            "fn": fn_agg,
            "precision": precision,
            "recall": recall,
            "f05": f05,
            "f2": f2,
        }