pipeline {
    agent any

    environment {
        BUILD_IMAGE_NAME = "python38"
        BUILD_IMAGE_URI  = "${AWS_ACCOUNT_ID_DEV}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/python38"
        NEXUS_PROTOCOL = "http"
        NEXUS_HOSTNAME = "sonatype-nexus"
        NEEDS_BUILD = sh(script: "python project.py -nb", returnStdout: true).trim()
    }

    stages {
        stage("Configure credentials") {
            post {
                failure {
                    updateGitlabCommitStatus name: '01-Config-Cred', state: 'failed'
                }
                success {
                    updateGitlabCommitStatus name: '01-Config-Cred', state: 'success'
                }
            }
            steps {
                echo "===== Copying AWS Cli config ..."
                sh "mkdir -p ~/.aws && cp /files/awsconfig ~/.aws/config"

                sh "cat ~/.aws/config"

                echo "===== Logging into Amazon ECR ..."
                sh """
                set +x; \$(aws --profile dev ecr get-login \
                    --region \${AWS_DEFAULT_REGION} --no-include-email)
                """

                withCredentials(bindings: [usernamePassword(credentialsId: "${CREDENTIALS_ID_NEXUS}", 
                                                            usernameVariable: "NEXUS_USER", 
                                                            passwordVariable: "NEXUS_PASS"),
                                           sshUserPrivateKey(credentialsId: "${CREDENTIALS_ID_GIT_SSH}",
                                                             keyFileVariable: "GIT_KEY")])
                {
                    echo "===== Generating netrc ..."
                    sh "jenkins/gen_netrc.sh $NEXUS_USER $NEXUS_PASS"

                    echo "===== Generating pypirc ..."
                    sh "jenkins/gen_pypirc.sh $NEXUS_USER $NEXUS_PASS"

                    echo "===== Generating pip.conf ..."
                    sh "jenkins/gen_pipconf.sh $NEXUS_USER $NEXUS_PASS"

                    echo "===== Getting SSH key for git ..."
                    sh """
                    cat ${GIT_KEY} > git.pem
                    chmod 400 git.pem
                    mkdir -p /root/.ssh && cp git.pem /root/.ssh/id_rsa
                    """
                }
            }
        }

        stage("Build changelog") {
            when {
                branch 'release/*'
            }
            steps {
                echo "===== Building change log for ${GIT_BRANCH} ..."
                sh """
                python project.py -cl > CHANGELOG.md
                IVERSION=\$(python project.py -iv)
                git add CHANGELOG.md
                git commit -m "chore: release \${IVERSION}"
                git stash
                git checkout -b temp_local_branch
                git checkout master
                git merge temp_local_branch --no-ff -m "merge: auto-merge release \${IVERSION}"
                git push -u origin master
                git push origin --delete \${GIT_BRANCH}
                """
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '02-Build-Changelog', state: 'failed'
                }
                success {
                    updateGitlabCommitStatus name: '02-Build-Changelog', state: 'success'
                }
            }
        }

        stage("Configure build environment") {
            when {
                anyOf { branch 'develop'; branch 'master' }
                expression { env.NEEDS_BUILD == "True" }
            }
            steps {
                echo "===== Pulling ${BUILD_IMAGE_NAME} image from ECR ..."
                sh "docker pull ${BUILD_IMAGE_URI}"

                echo "===== Creating virtual environment ..."
                sh """
                jenkins/docker_exec.sh \
                    jenkins/create_venv.sh
                """
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '03-Config-Build-Env', state: 'failed'
                }
                success {
                    updateGitlabCommitStatus name: '03-Config-Build-Env', state: 'success'
                }
            }
        }

        stage("Bump version") {
            when {
                branch 'master'
                expression { env.NEEDS_BUILD == "True" }
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '04-Bump-Version', state: 'failed'
                }
                success {
                    updateGitlabCommitStatus name: '04-Bump-Version', state: 'success'
                }
            }
            steps {
                echo "===== Bumping version ..."
                sh "python project.py -b"
            }
        }

        stage("Unit test") {
            when {
                not {
                    branch 'release/*'
                }
                expression { env.NEEDS_BUILD == "True" }
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '05-Unit-test', state: 'failed'
                }
                success {
                    updateGitlabCommitStatus name: '05-Unit-test', state: 'success'
                }
            }
            steps {
                echo "===== Unit testing with pytest..."
                sh """
                jenkins/docker_exec.sh \
                    jenkins/pytest.sh
                """
            }
        }

        stage("Quality report") {
            when {
                not {
                    branch 'release/*'
                }
                expression { env.NEEDS_BUILD == "True" }
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '06-Quality-report', state: 'failed'
                }
                success {
                    updateGitlabCommitStatus name: '06-Quality-report', state: 'success'
                }
            }
            steps {
                withCredentials(bindings: [usernamePassword(credentialsId: "${CREDENTIALS_ID_SONAR}",
                                                            usernameVariable: "SONAR_USER", 
                                                            passwordVariable: "SONAR_PASS")])
                {
                    echo "===== Generating pylint and pytest-cov reports..."
//                     sh """cat > coverage.env <<EOF
// SONAR_LOGIN=\$SONAR_USER
// SONAR_PASSWORD=\$SONAR_PASS
// SONAR_HOST_URL=\$SONAR_URL
// EOF
//                     """

//                     sh """
//                     jenkins/docker_exec.sh \
//                          jenkins/coverage.sh
//                     """
                }
            }
        }

        stage("Build") {
            when {
                not {
                    branch 'release/*'
                }
                expression { env.NEEDS_BUILD == "True" }
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '07-Build', state: 'failed'
                }
                success {
                    updateGitlabCommitStatus name: '07-Build', state: 'success'
                }
            }
            steps {
                sh "jenkins/build.sh"
            }
        }

        stage("Push tags") {
            when {
                branch 'master'
                expression { env.NEEDS_BUILD == "True" }
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '08-Push-Tags', state: 'failed'
                }
                success {
                    updateGitlabCommitStatus name: '08-Push-Tags', state: 'success'
                }
            }
            steps {
                echo "===== Pushing tags ..."
                sh "git push origin --tags"

                echo "===== Sync changes with development branch ..."
                sh """
                VERSION=\$(python project.py -v)
                git checkout -b temp_local_branch
                git checkout develop
                git merge temp_local_branch --no-ff -m "merge: auto-merge release \${VERSION}"
                git push -u origin develop
                git checkout ${GIT_BRANCH}
                git stash
                """
            }
        }

        stage("Deploy (NEXUS)") {
            when {
                not {
                    branch 'release/*'
                }
                expression { env.NEEDS_BUILD == "True" }
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '09-Deploy-Nexus', state: 'failed'
                    notifyBuild('FAILED', 'Nexus')
                }
                success {
                    updateGitlabCommitStatus name: '09-Deploy-Nexus', state: 'success'
                    notifyBuild('SUCCESSFUL', 'Nexus')
                }
            }
            steps {
                notifyBuild('STARTED', 'Nexus')
                sh "jenkins/deploy_nexus.sh"
            }
        }

        stage("Deploy (DEV)") {
            when {
                not {
                    branch 'release/*'
                }
                expression { env.NEEDS_BUILD == "True" }
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '10-Deploy-Dev', state: 'failed'
                }
                success {
                    updateGitlabCommitStatus name: '10-Deploy-Dev', state: 'success'
                }
            }

            steps {
                sh "jenkins/deploy.sh dev"
            }
        }

        stage("Deploy (QA)") {
            when {
                branch 'master'
                expression { env.NEEDS_BUILD == "True" }
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '11-Deploy-QA', state: 'failed'
                }
                success {
                    updateGitlabCommitStatus name: '11-Deploy-QA', state: 'success'
                }
            }
            steps {
                sh "jenkins/deploy.sh qa"
            }
        }

        stage("Deploy (STAGE)") {
            when {
                branch 'master'
                expression { env.NEEDS_BUILD == "True" }
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '12-Deploy-Stage', state: 'failed'
                    notifyBuild('FAILED', 'Stage')
                }
                success {
                    updateGitlabCommitStatus name: '12-Deploy-Stage', state: 'success'
                    notifyBuild('SUCCESSFUL', 'Stage')
                }
            }
            steps {
                notifyBuild('STARTED', 'Stage')
                sh "jenkins/deploy.sh stage"
            }
        }

        stage("Deploy (PROD)") {
            when {
                branch 'master'
                expression { env.NEEDS_BUILD == "True" }
            }
            post {
                failure {
                    updateGitlabCommitStatus name: '13-Deploy-Prod', state: 'failed'
                    notifyBuild('FAILED', 'Prod')
                }
                success {
                    updateGitlabCommitStatus name: '13-Deploy-Prod', state: 'success'
                    notifyBuild('SUCCESSFUL', 'Prod')
                }
            }
            steps {
                notifyBuild('APPROVAL', 'Prod')
                timeout(time: 60, unit: "MINUTES") {
                    input message: 'Do you want to approve the deploy in production?', ok: 'Yes'
                }
                sh "jenkins/deploy.sh prod"
            }
        }

    }
}
