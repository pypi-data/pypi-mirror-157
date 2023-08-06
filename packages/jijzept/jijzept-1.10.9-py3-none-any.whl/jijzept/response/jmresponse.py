from typing import Any

import dimod
import jijmodeling as jm
from jijzept.response.base import BaseResponse


class JijModelingResponse(BaseResponse, jm.SampleSet):
    @classmethod
    def from_json_obj(cls, json_obj) -> Any:
        if "type" in json_obj.keys():
            response = cls.from_dimod_response(json_obj)
        else:
            response = cls(
                record=json_obj["record"],
                evaluation=json_obj["evaluation"],
                measuring_time=json_obj["measuring_time"],
            )
        return response

    @classmethod
    def empty_data(cls) -> Any:
        return cls(record={}, evaluation={}, measuring_time={})

    @classmethod
    def from_dimod_response(cls, json_obj):
        sampleset = cls.from_dimod_sampleset(
            dimod.SampleSet.from_serializable(json_obj)
        )
        response = cls.empty_data()
        response.record = sampleset.record
        response.evaluation = sampleset.evaluation
        response.measuring_time = sampleset.measuring_time
        return response

    def __repr__(self):
        return jm.SampleSet.__repr__(self)

    def __str__(self):
        return BaseResponse.__repr__(self) + "\n" + jm.SampleSet.__str__(self)
