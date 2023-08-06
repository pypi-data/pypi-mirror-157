import os
from abc import ABC, abstractmethod

import requests

import featurestore.core.CoreService_pb2 as pb
from featurestore.core.CoreService_pb2_grpc import CoreServiceStub


class Transformation(ABC):
    @abstractmethod
    def _initialize(self, grpc: CoreServiceStub):
        raise NotImplementedError(
            "Method `_initialize` needs to be implemented by the child class"
        )

    @abstractmethod
    def _to_proto(self):
        raise NotImplementedError(
            "Method `to_proto` needs to be implemented by the child class"
        )

    @staticmethod
    def from_proto(proto: pb.Transformation):
        if proto.HasField("mojo"):
            mojo = DriverlessAIMOJO(None)
            mojo.mojo_remote_location = proto.mojo.filename
            return mojo
        elif proto.HasField("spark_pipeline"):
            spark_pipeline = SparkPipeline(None)
            spark_pipeline.pipeline_remote_location = proto.spark_pipeline.filename
            return spark_pipeline
        elif proto.HasField("join"):
            return JoinFeatureSets(proto.join.left_key, proto.join.right_key)


class DriverlessAIMOJO(Transformation):
    def __init__(self, mojo_local_location):
        self.mojo_local_location = mojo_local_location
        self.mojo_remote_location = None

    def _initialize(self, grpc: CoreServiceStub):
        if self.mojo_remote_location is None:
            if not os.path.exists(self.mojo_local_location):
                raise Exception(
                    f"Provided file ${self.mojo_local_location} doesn't exists."
                )

            upload_response = grpc.GenerateTransformationUpload(
                pb.GenerateTransformationUploadRequest(
                    transformation_type=pb.TransformationType.TransformationMojo
                )
            )
            with open(self.mojo_local_location, "rb") as mojo_file:
                response = requests.put(
                    url=upload_response.url,
                    data=mojo_file,
                    headers={"content-type": "application/octet-stream"},
                )
                if response.status_code != 200:
                    raise Exception("DriverlessAIMOJO failed during uploading the file")
                self.mojo_remote_location = upload_response.filename

    def _to_proto(self):
        return pb.Transformation(
            mojo=pb.MojoTransformation(filename=self.mojo_remote_location)
        )


class SparkPipeline(Transformation):
    def __init__(self, pipeline_local_location):
        self.pipeline_local_location = pipeline_local_location
        self.pipeline_remote_location = None

    def _initialize(self, grpc: CoreServiceStub):
        if self.pipeline_remote_location is None:
            if not os.path.exists(self.pipeline_local_location):
                raise Exception(
                    f"Provided file ${self.pipeline_local_location} doesn't exists."
                )

            upload_response = grpc.GenerateTransformationUpload(
                pb.GenerateTransformationUploadRequest(
                    transformation_type=pb.TransformationType.TransformationSparkPipeline
                )
            )

            with open(self.pipeline_local_location, "rb") as spark_pipeline_file:
                response = requests.put(
                    url=upload_response.url,
                    data=spark_pipeline_file,
                    headers={"content-type": "application/octet-stream"},
                )
                if response.status_code != 200:
                    raise Exception("SparkPipeline failed during uploading the file")
                self.pipeline_remote_location = upload_response.filename

    def _to_proto(self):
        return pb.Transformation(
            spark_pipeline=pb.SparkPipelineTransformation(
                filename=self.pipeline_remote_location
            )
        )


class JoinFeatureSets(Transformation):
    def __init__(self, left_key, right_key):
        self.left_key = left_key
        self.right_key = right_key

    def _initialize(self, grpc: CoreServiceStub):
        pass

    def _to_proto(self):
        return pb.Transformation(
            join=pb.JoinTransformation(left_key=self.left_key, right_key=self.right_key)
        )
