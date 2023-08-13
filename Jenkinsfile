pipeline {
  agent any

  environment {
    bucketSourceId = credentials["bucketSourceId"]
    b2AppKey       = credentials["b2AppKey"]
    b2AppKeyId     = credentials["b2AppKeyId"]
    cfAccountId    = credentials["cfAccountId"]
    cfWorkerApi    = credentials["cfWorkerApi"]
    cfWorkerName   = credentials["cfWorkerName"]
  }

  stages {
    stage('build') {
      steps {
        sh '''
          docker build \
            -t ezraweb/files-cron:latest \
            --build-arg bucketSourceId="${bucketSourceId}" \
            --build-arg b2AppKey="${b2AppKey}" \
            --build-arg b2AppKeyId="${b2AppKeyId}" \
            --build-arg cfAccountId="${cfAccountId}" \
            --build-arg cfWorkerApi="${cfWorkerApi}" \
            --build-arg cfWorkerName="${cfWorkerName}" \
            .
        '''
      }
    }
  }
}
