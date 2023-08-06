from localstack.utils.aws import aws_models
rURYF=super
rURYQ=None
rURYu=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  rURYF(LambdaLayer,self).__init__(arn)
  self.cwd=rURYQ
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.rURYu.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,rURYu,env=rURYQ):
  rURYF(RDSDatabase,self).__init__(rURYu,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,rURYu,env=rURYQ):
  rURYF(RDSCluster,self).__init__(rURYu,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,rURYu,env=rURYQ):
  rURYF(AppSyncAPI,self).__init__(rURYu,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,rURYu,env=rURYQ):
  rURYF(AmplifyApp,self).__init__(rURYu,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,rURYu,env=rURYQ):
  rURYF(ElastiCacheCluster,self).__init__(rURYu,env=env)
class TransferServer(BaseComponent):
 def __init__(self,rURYu,env=rURYQ):
  rURYF(TransferServer,self).__init__(rURYu,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,rURYu,env=rURYQ):
  rURYF(CloudFrontDistribution,self).__init__(rURYu,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,rURYu,env=rURYQ):
  rURYF(CodeCommitRepository,self).__init__(rURYu,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
