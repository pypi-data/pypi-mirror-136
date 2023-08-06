from localstack.utils.aws import aws_models
xMGIA=super
xMGIi=None
xMGIu=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  xMGIA(LambdaLayer,self).__init__(arn)
  self.cwd=xMGIi
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.xMGIu.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,xMGIu,env=xMGIi):
  xMGIA(RDSDatabase,self).__init__(xMGIu,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,xMGIu,env=xMGIi):
  xMGIA(RDSCluster,self).__init__(xMGIu,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,xMGIu,env=xMGIi):
  xMGIA(AppSyncAPI,self).__init__(xMGIu,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,xMGIu,env=xMGIi):
  xMGIA(AmplifyApp,self).__init__(xMGIu,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,xMGIu,env=xMGIi):
  xMGIA(ElastiCacheCluster,self).__init__(xMGIu,env=env)
class TransferServer(BaseComponent):
 def __init__(self,xMGIu,env=xMGIi):
  xMGIA(TransferServer,self).__init__(xMGIu,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,xMGIu,env=xMGIi):
  xMGIA(CloudFrontDistribution,self).__init__(xMGIu,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,xMGIu,env=xMGIi):
  xMGIA(CodeCommitRepository,self).__init__(xMGIu,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
